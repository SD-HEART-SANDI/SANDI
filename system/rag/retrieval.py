"""
File Name: retrieval.py
Purpose: Retreive top results that matches with user query
Goals: 
- Embed query for semantic values
- Call search for vector database to look for top results
- Return ranked results
Architecture Decision:
- Acts between Embedding Service and Vector Database
"""
import numpy as np
from system.config import settings
from system.rag.embeddings import EmbeddingService
from system.rag.vector_db import VectorDatabase

class Retrieval: 
  #Dependency Injection
  def __init__(self, embedding_service: EmbeddingService, vector_db: VectorDatabase):
    self.embedding_service = embedding_service
    self.vector_db = vector_db

  def embed_query(self, user_input: str):
      
      if user_input is None:
          raise ValueError("VALIDATION: User query is empty/invalid")
      
      embeded_query = self.embedding_service.embed_query(user_input)
      print(f"Embedded query value: {embeded_query}")
      return embeded_query

  def retrieve(self, embeded_query: np.ndarray):
    return self.vector_db.search(query_vector=embeded_query,top_k=settings.TOP_K)
      