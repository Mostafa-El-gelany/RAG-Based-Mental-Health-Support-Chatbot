from ..core.constants import EMBEDDING_MODEL, COLLECTION_NAME
import os
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from dotenv import load_dotenv
load_dotenv()
class Rag:
    def __init__(self):
        self.embedding_model = SentenceTransformer(
            EMBEDDING_MODEL
        )
        self.client = QdrantClient(
            url=os.getenv("QDRANT_CLUSTER_ENDPOINT"),
            api_key=os.getenv("QDRANT_API_KEY")
        )


    def search_top_k(self, user_prompt, top_k=5):
        # Step A: Convert the user's prompt into a vector embedding
        query_vector = self.embedding_model.encode(user_prompt, normalize_embeddings=True).tolist()

        # Step B: Query Qdrant
        search_results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
            with_payload=True  # Ensure we fetch the context, response, and chunk
        ).points
        
        return search_results
