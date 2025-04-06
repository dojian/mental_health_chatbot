import boto3
import pickle
import cohere
from typing import List, Callable
from langchain_core.tools import tool
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
    """A Retrieval-Augmented Generation (RAG) pipeline that integrates BM25 and Qdrant vector retrieval 
    with Cohere's reranking model for improved document retrieval and ranking."""
    
    def __init__(self):
        """Initializes the RAGPipeline with default values for retrievers, embeddings, and configuration settings."""
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
    
    def initialize_embeddings(self):
        """Downloads chunks from S3, loads them, and indexes into Qdrant if necessary."""
        s3 = boto3.client('s3')

        # Download the pre-chunked text document file from S3
        s3.download_file(
            Bucket=settings.S3_BUCKET_NAME,
            Key=settings.S3_BUCKET_EMBEDDINGS_KEY,  # Path where the embeddings are saved in S3
            Filename=f"{settings.S3_BUCKET_CHUNK_TEMP_PATH}/text_chunks.pkl"  # Temporary local path to save the file
        )
        
        # Load the embeddings from the downloaded file
        with open(f"{settings.S3_BUCKET_CHUNK_TEMP_PATH}/text_chunks.pkl", 'rb') as f:
            self.chunks = pickle.load(f)

        # Setup vector retriever
        self.embeddings_model = FastEmbedEmbeddings(model_name=settings.EMBEDDING_MODEL)
        self.qdrant_client = QdrantClient(path=f"{settings.S3_BUCKET_CHUNK_TEMP_PATH}/qdrant_data")

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
                vectors_config=VectorParams(size=768, distance='Cosine')
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
    
    def initialize_retrievers(self, initial_k = 25, bm25_weight = 0.5, qdrant_weight = 0.5):
        """Initializes the hybrid retriever pipeline after embeddings have been loaded and stored."""
        assert self.chunks is not None, "Chunks must be loaded before initializing retrievers."
        
        self.initial_k = initial_k
        self.bm25_weight = bm25_weight
        self.qdrant_weight = qdrant_weight
        
        # Setup BM25 retriever
        bm25_retriever = BM25Retriever.from_documents(self.chunks)
        bm25_retriever.k = self.initial_k #top k most relevant documents, as ranked by the BM25 score.
        print(f"BM25 retriever setup with k={self.initial_k}")

        # Setup the Qdrant retriever
        qdrant_retriever = self.vector_store.as_retriever(search_kwargs={"k": self.initial_k})
        print(f"Qdrant retriever setup with k={self.initial_k}")

        # Fusion of retrievers BM25+ vector DB
        print("Setting up the retriever ensemble (BM25 + Qdrant)...")

        fusion_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, qdrant_retriever],
            weights=[self.bm25_weight, self.qdrant_weight]
        )

        self.base_retriever = fusion_retriever
        # Check that the base retriever has been correctly set
        if self.base_retriever:
            print("✅ base_retriever has been initialized successfully.")
        else:
            print("❌ base_retriever is not initialized.")

        self.cohere_client = cohere.Client(settings.COHERE_API_KEY)
        print("Cohere client initialized.")

        print("RAG retriever initialized with Qdrant and BM25 RankFusion.")

    # def filter_docs_by_category(self, selected_categories): 
    #     """Filters documents based on selected categories.
        
    #     Args:
    #         selected_categories (list): List of categories to filter documents by.
        
    #     Returns:
    #         List[Document]: Filtered list of documents.
    #     """
    #     if selected_categories is None or "Other" in selected_categories:
    #         return self.chunks
    #     return [doc for doc in self.chunks if any(category in doc.metadata["categories"] for category in selected_categories)]


    def retrieve_with_rerank(self, query: str, final_k: int = 10) -> List[Document]: #removed selected_categories (list, optional): Categories to filter results.
        """Retrieves and reranks documents based on a user query using Cohere's reranking model.
        
        Args:
            query (str): The query string.
            final_k (int): Number of top documents to return after reranking.
        
        Returns:
            List[Document]: The top reranked documents.
        """
        # Always use the base retriever (no filtering by categories)
        initial_results: List[Document] = self.base_retriever.invoke(query)

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

        # Step 3: Get top reranked documents
        reranked_docs = [initial_results[r.index] for r in response.results]
        print(f"✅ Reranked and returning {len(reranked_docs)} documents.")
        
        # Remove context from content 
        for doc in reranked_docs:
            doc.page_content = doc.page_content.replace(doc.metadata["contextualized_content"], "").strip()
        return reranked_docs

# #test if the above class/functions work
# if __name__ == "__main__":
#     #Create instance of RAGPipeline class
#     rag_pipeline = RAGPipeline()
    
#     # Initialize the RAG pipeline (loads data from S3, etc.)
#     rag_pipeline.initialize_rag_pipeline()

#     # Test retrieve with rerank
#     query = "my major is finance. How do I find a mentor? I feel so behind and failing"
#     top_docs = rag_pipeline.retrieve_with_rerank(query, final_k=10)

#     # Print the reranked documents
#     print("Top reranked documents:")
#     for doc in top_docs:
#         print(doc.page_content)
#         print("\n")
    