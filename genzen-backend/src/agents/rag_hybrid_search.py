import boto3
import pickle
import cohere
# import time
from langchain_qdrant import QdrantVectorStore
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.schema import Document
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Filter, FieldCondition, MatchAny
from langchain_community.embeddings import FastEmbedEmbeddings


from src.utils.config_setting import Settings

settings = Settings()

class RAGPipeline:
    def __init__(self):
        self.chunks = None
        self.base_retriever = None
        self.cohere_client = None
        self.embeddings_model = None
        self.qdrant_client = None
        self.vector_store = None
        self.categories = None
        self.filtered_retriever = None
        self.initial_k = None
        self.bm25_weight = None
        self.qdrant_weight = None
    
    def initialize_rag_pipeline(self, initial_k = 25, bm25_weight = 0.5, qdrant_weight = 0.5):
        # Initialize the S3 client
        s3 = boto3.client('s3')

        # Download the pre-chunked text document file from S3
        s3.download_file(
            Bucket=settings.S3_BUCKET_NAME,
            Key=settings.S3_BUCKET_EMBEDDINGS_KEY,  # Path where the embeddings are saved in S3
            Filename=f"{settings.S3_BUCKET_TEMP_PATH}/text_chunks.pkl"  # Temporary local path to save the file
        )
        
        # Load the embeddings from the downloaded file
        with open('/tmp/text_chunks.pkl', 'rb') as f:
            self.chunks = pickle.load(f)
        
        self.initial_k = initial_k
        self.bm25_weight = bm25_weight
        self.qdrant_weight = qdrant_weight
        # Setup BM25 retriever
        bm25_retriever = BM25Retriever.from_documents(self.chunks)
        bm25_retriever.k = self.initial_k #top k most relevant documents, as ranked by the BM25 score.

        # Setup vector retriever
        self.embeddings_model = FastEmbedEmbeddings(model_name=settings.EMBEDDING_MODEL)
        self.qdrant_client = QdrantClient(path=f"{settings.S3_BUCKET_TEMP_PATH}/qdrant_data")

        # Check if the collection already exists
        # Avoid adding repeated documents into vectorstore if collection already exists
        add_documents = False
        try:
            self.qdrant_client.get_collection(collection_name="my_collection")
            print("⚠️ Collection exists. Skipping creation.")
        except ValueError:
            # If the collection does not exist, create it
            print("⚠️ Collection does not exist. Creating new collection.")
            self.qdrant_client.create_collection(
                collection_name="my_collection",
                vectors_config=VectorParams(size=768, distance='Cosine')  # Adjusted size to 768 based on your embeddings model
            )
            print("✅ Created new Qdrant collection with updated dimensions")
            add_documents = True
        
        # Index the documents with Qdrant on the fly
        print("Indexing documents into Qdrant...")
        self.vector_store = QdrantVectorStore(
            embedding = self.embeddings_model,
            client= self.qdrant_client,
            collection_name="my_collection"
        )

        # Insert the embeddings into the vector store
        if add_documents:
            self.vector_store.add_documents(self.chunks)
        
        print("# docs in Qdrant collection: ", self.qdrant_client.get_collection(collection_name="my_collection").points_count)

        # Setup the Qdrant retriever
        qdrant_retriever = self.vector_store.as_retriever(search_kwargs={"k": self.initial_k})
        
        # Fusion of retrievers BM25+ vector DB
        print("Setting up the retriever ensemble (BM25 + Qdrant)...")

        fusion_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, qdrant_retriever],
            weights=[self.bm25_weight, self.qdrant_weight]
        )

        self.base_retriever = fusion_retriever
        self.cohere_client = cohere.Client(settings.COHERE_API_KEY)

        print("RAG pipeline initialized with Qdrant + BM25 + RankFusion.")

    def filter_docs_by_category(self, selected_categories): 
        if selected_categories is None or "Other" in selected_categories:
            return self.chunks
        return [doc for doc in self.chunks if any(category in doc.metadata["categories"] for category in selected_categories)]


    def retrieve_with_rerank(self, query: str, final_k: int = 10, selected_categories: list = None) -> List[Document]:
        
        # If there are no selected categories or user selects Other, use base retriever to search for documents in entire vector database
        if selected_categories is None or "Other" in selected_categories:
            initial_results: List[Document] = self.base_retriever.invoke(query)
        else:
        # Otherwise (re)instantiate retrievers on documents that has at least 1 category in list of selected categories
            if self.categories is None or set(self.categories) != set(selected_categories):
                self.categories = selected_categories
                # filter qdrant retrieved docs to categories
                filter_criteria = Filter(
                                      must=[  # 'must' is a required field in Qdrant's filtering model
                                            FieldCondition(
                                                key="metadata.categories",
                                                match=MatchAny(any=selected_categories)  # Matches any category in the select list
                                            )
                                        ]
                                    )
                filtered_qdrant_retriever = self.vector_store.as_retriever(search_kwargs={"filter": filter_criteria, 
                                                                                          "k": self.initial_k})
                # create new BM25 retriever on filtered docs in categories
                filtered_docs = self.filter_docs_by_category(selected_categories)
                filtered_bm25_retriever = BM25Retriever.from_documents(filtered_docs)
                filtered_bm25_retriever.k = self.initial_k
                self.filtered_retriever = EnsembleRetriever(
                    retrievers=[filtered_bm25_retriever, filtered_qdrant_retriever],
                    weights=[self.bm25_weight, self.qdrant_weight]
                )
            
            initial_results = self.filtered_retriever.invoke(query)

        if not initial_results:
            print("⚠️ No documents retrieved for query:", query)
            return []

        print(f"Retrieved {len(initial_results)} docs, reranking top {final_k}...")

        documents = [doc.page_content for doc in initial_results]

        # Step 2: Rerank using Cohere
        response = self.cohere_client.rerank(
            model=settings.RERANK_MODEL,
            query=query,
            documents=documents,
            top_n=min(final_k, len(documents))  # Prevent index errors
        )

        #time.sleep(0.1)  # Optional: adjust for your API plan

        # Step 3: Get top reranked documents
        reranked_docs = [initial_results[r.index] for r in response.results]
        print(f"✅ Reranked and returning {len(reranked_docs)} documents.")
        
        # Remove context from content 
        for doc in reranked_docs:
            doc.page_content = doc.page_content.replace(doc.metadata["contextualized_content"], "").strip()
        return reranked_docs

#test if the above class/functions work
if __name__ == "__main__":
    #Create instance of RAGPipeline class
    rag_pipeline = RAGPipeline()
    
    # Initialize the RAG pipeline (loads data from S3, etc.)
    rag_pipeline.initialize_rag_pipeline()

    # Test retrieve with rerank
    query = "How do I find a mentor? I feel so behind and failing"
    selected_categories = ["career"]
    top_docs = rag_pipeline.retrieve_with_rerank(query, final_k=10, selected_categories = selected_categories)

    # Print the reranked documents
    print("Top reranked documents:")
    for doc in top_docs:
        print(doc.page_content)
        print("\n")
    