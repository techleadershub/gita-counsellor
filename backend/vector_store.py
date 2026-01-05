from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from typing import List, Dict, Any
import os
try:
    from .config import VECTOR_DB_CONFIG, LLM_CONFIG
    from .models import VerseChunk
except ImportError:
    from config import VECTOR_DB_CONFIG, LLM_CONFIG
    from models import VerseChunk

class VectorStore:
    def __init__(self):
        # Support both local (path) and Docker/Railway (url) modes
        if "url" in VECTOR_DB_CONFIG:
            # Docker/Railway mode - connect via URL
            self.client = QdrantClient(
                url=VECTOR_DB_CONFIG["url"],
                timeout=30
            )
        elif "path" in VECTOR_DB_CONFIG:
            # Local development mode - embedded Qdrant
            self.client = QdrantClient(path=VECTOR_DB_CONFIG["path"])
        else:
            raise ValueError("VECTOR_DB_CONFIG must have either 'url' or 'path'")
        
        self.collection_name = VECTOR_DB_CONFIG["collection_name"]
        
        # Ensure collection exists
        self._ensure_collection()
        
        # Initialize Embeddings (Always OpenAI for consistency)
        api_key = LLM_CONFIG.get("openai_key")
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=api_key,
            check_embedding_ctx_length=False
        )
        
        self.vectorstore = Qdrant(
            client=self.client,
            collection_name=self.collection_name,
            embeddings=self.embeddings,
        )

    def _ensure_collection(self):
        collections = self.client.get_collections()
        exists = any(c.name == self.collection_name for c in collections.collections)
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1536,  # text-embedding-3-small dimension
                    distance=models.Distance.COSINE
                )
            )

    def add_chunks(self, chunks: List[VerseChunk]):
        texts = [chunk.to_text_for_embedding() for chunk in chunks]
        metadatas = [chunk.dict() for chunk in chunks]
        self.vectorstore.add_texts(texts=texts, metadatas=metadatas)

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        # Generate embedding manually
        query_vector = self.embeddings.embed_query(query)
        
        # Direct client search
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True,
            with_vectors=False
        ).points
        
        # Map Qdrant ScoredPoint to our response format
        # LangChain Qdrant stores data as: payload['page_content'] and payload['metadata']
        formatted_results = []
        for r in results:
            payload = r.payload if hasattr(r, 'payload') and r.payload else {}
            if not isinstance(payload, dict):
                payload = {}
            
            # Extract metadata (LangChain stores chunk.dict() under 'metadata' key)
            metadata = payload.get("metadata", {})
            if not isinstance(metadata, dict):
                metadata = {}
            
            # Extract verse_id from metadata
            verse_id = metadata.get("verse_id", "") or payload.get("verse_id", "")
            
            # Get content for display (page_content contains the embedded text)
            content = payload.get("page_content", "") or metadata.get("translation", "") or ""
            
            # Include full metadata in chunk for backward compatibility
            chunk_data = {
                **metadata,  # All verse data (verse_id, chapter, translation, etc.)
                "page_content": payload.get("page_content", "")
            }
            
            formatted_results.append({
                "chunk": chunk_data,
                "score": r.score,
                "content": content,
                "verse_id": verse_id  # Add verse_id directly for easier access
            })
        
        return formatted_results

    def reset_db(self):
        """WARNING: Deletes all data"""
        self.client.delete_collection(self.collection_name)
        self._ensure_collection()

