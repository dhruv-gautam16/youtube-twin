from openai import OpenAI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import logging

logger = logging.getLogger(__name__)

class EmbeddingsManager:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.embedding_model = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
        self.embeddings_cache = {}
    
    def create_embeddings(self, transcript_data):
        """Create embeddings for all transcript chunks"""
        chunks = transcript_data['chunks']
        chunks_with_embeddings = []
        
        logger.info(f"Creating embeddings for {len(chunks)} chunks")
        
        texts = [chunk['text'] for chunk in chunks]
        
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.embedding_model
            )
            
            for i, chunk in enumerate(chunks):
                chunk_with_embedding = chunk.copy()
                chunk_with_embedding['embedding'] = response.data[i].embedding
                chunks_with_embeddings.append(chunk_with_embedding)
            
            logger.info(f"Successfully created {len(chunks_with_embeddings)} embeddings")
            return chunks_with_embeddings
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise
    
    def get_query_embedding(self, query):
        """Get embedding for a query string"""
        try:
            response = self.client.embeddings.create(
                input=query,
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting query embedding: {str(e)}")
            raise
    
    def find_relevant_chunks(self, query, chunks_with_embeddings, top_k=5):
        """Find most relevant chunks using cosine similarity"""
        try:
            query_embedding = self.get_query_embedding(query)
            
            chunk_embeddings = [chunk['embedding'] for chunk in chunks_with_embeddings]
            similarities = cosine_similarity(
                [query_embedding],
                chunk_embeddings
            )[0]
            
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            relevant_chunks = []
            for idx in top_indices:
                chunk = chunks_with_embeddings[idx].copy()
                chunk['similarity'] = float(similarities[idx])
                relevant_chunks.append(chunk)
            
            logger.info(f"Found {len(relevant_chunks)} relevant chunks for query")
            return relevant_chunks
            
        except Exception as e:
            logger.error(f"Error finding relevant chunks: {str(e)}")
            raise
