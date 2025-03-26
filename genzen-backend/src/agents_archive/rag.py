import boto3
import pickle
import cohere
import os
from dotenv import load_dotenv
import time
from langchain_qdrant import QdrantVectorStore
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.schema import Document
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams
from langchain_community.embeddings import FastEmbedEmbeddings
from typing import List
load_dotenv()

class RAGPipeline:
    def __init__(self):
        self.base_retriever = None
        self.cohere_client = None
        self.embeddings_model = None
        self.qdrant_client = None
        self.vector_store = None
    
    def initialize_rag_pipeline(self):
        # Initialize the S3 client
        s3 = boto3.client('s3')

        # Download the pre-chunked text document file from S3
        s3.download_file(
            Bucket='my-genzen-bucket',
            Key='data/data--contextual-retrieval-2025-02-15-41.pkl',  # Path where the embeddings are saved in S3
            Filename='/tmp/text_chunks.pkl'  # Temporary local path to save the file
        )
        
        # Load the embeddings from the downloaded file
        with open('/tmp/text_chunks.pkl', 'rb') as f:
            text_chunks = pickle.load(f)
        
        documents = text_chunks['documents']  # List of Document objects
        print(f"✅ Loaded {len(documents)} documents from S3")

        # Setup BM25 retriever
        bm25_retriever = BM25Retriever.from_documents(documents)
        bm25_retriever.k = 10 #top k most relevant documents, as ranked by the BM25 score.

        # Setup vector retriever
        self.embeddings_model = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")
        self.qdrant_client = QdrantClient(path="/tmp/qdrant_data")

        # Check if the collection already exists
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
        
        # Index the documents with Qdrant on the fly
        print("Indexing documents into Qdrant...")
        self.vector_store = QdrantVectorStore(
            embedding = self.embeddings_model,
            client= self.qdrant_client,
            collection_name="my_collection"
        )
        # Insert the embeddings into the vector store
        self.vector_store.add_documents(documents)
        
        # Setup the Qdrant retriever
        qdrant_retriever = self.vector_store.as_retriever(search_kwargs={"k": 10})
        
        # Fusion of retrievers BM25+ vector DB
        print("Setting up the retriever ensemble (BM25 + Qdrant)...")

        fusion_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, qdrant_retriever],
            weights=[0.2, 0.8]
        )

        self.base_retriever = fusion_retriever
        self.cohere_client = cohere.Client(os.getenv("COHERE_API_KEY"))

        print("RAG pipeline initialized with Qdrant + BM25 + RankFusion.")

    def retrieve_with_rerank(self, query: str, final_k: int = 5) -> List[Document]:
        # Step 1: Retrieve more documents than needed for reranking
        initial_results: List[Document] = self.base_retriever.invoke(query)
        if not initial_results:
            print("⚠️ No documents retrieved for query:", query)
            return []

        print(f"Retrieved {len(initial_results)} docs, reranking top {final_k}...")

        documents = [doc.page_content for doc in initial_results]

        # Step 2: Rerank using Cohere
        response = self.cohere_client.rerank(
            model="rerank-english-v3.0",
            query=query,
            documents=documents,
            top_n=min(final_k, len(documents))  # Prevent index errors
        )

        #time.sleep(0.1)  # Optional: adjust for your API plan

        # Step 3: Get top reranked documents
        reranked_docs = [initial_results[r.index] for r in response.results]
        print(f"✅ Reranked and returning {len(reranked_docs)} documents.")
        
        return reranked_docs

#test if the above class/functions work
if __name__ == "__main__":
    #Create instance of RAGPipeline class
    rag_pipeline = RAGPipeline()
    
    # Initialize the RAG pipeline (loads data from S3, etc.)
    rag_pipeline.initialize_rag_pipeline()

    # Test retrieve with rerank
    query = "How do I get better sleep?"
    top_docs = rag_pipeline.retrieve_with_rerank(query, final_k=5)

    # Print the reranked documents
    print("Top reranked documents:")
    for doc in top_docs:
        print(doc.page_content)
    