import os
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# Initialize local ChromaDB in the data directory
CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'chroma_db')

# Use sentence transformers for local embeddings to avoid OpenAI costs during testing
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

class VectorDB:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        
        # Collections for risks and news
        self.risks_collection = self.client.get_or_create_collection(
            name="historical_risks",
            embedding_function=sentence_transformer_ef
        )
        self.news_collection = self.client.get_or_create_collection(
            name="market_news",
            embedding_function=sentence_transformer_ef
        )
        self.project_logs_collection = self.client.get_or_create_collection(
            name="project_logs",
            embedding_function=sentence_transformer_ef
        )

    def add_historical_risk(self, risk_id: str, description: str, mitigation: str, metadata: dict):
        self.risks_collection.add(
            documents=[f"Risk: {description} | Mitigation: {mitigation}"],
            metadatas=[metadata],
            ids=[risk_id]
        )

    def add_market_news(self, news_id: str, title: str, content: str, metadata: dict):
        self.news_collection.add(
            documents=[f"Title: {title}\nContent: {content}"],
            metadatas=[metadata],
            ids=[news_id]
        )
        
    def add_project_logs(self, log_id: str, project_id: str, log_text: str):
        self.project_logs_collection.add(
            documents=[log_text],
            metadatas=[{"project_id": project_id}],
            ids=[log_id]
        )

    def search_similar_risks(self, query: str, n_results: int = 2):
        results = self.risks_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results

    def search_market_news(self, query: str, n_results: int = 2):
        results = self.news_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
        
    def get_project_context(self, project_id: str):
        # Retrieve all logs for a project to provide context
        results = self.project_logs_collection.get(
            where={"project_id": project_id}
        )
        return results

# Singleton instance
db = VectorDB()
