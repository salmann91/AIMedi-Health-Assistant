import faiss
import numpy as np
import pickle
import os
from typing import List, Dict

class VectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.texts = []
        self.metadata = []
    
    def add_documents(self, embeddings: np.ndarray, texts: List[str], metadata: List[Dict]):
        """Add documents to the vector store"""
        if embeddings is None or len(embeddings) == 0:
            raise ValueError("Embeddings cannot be empty")
        
        embeddings = embeddings.astype('float32')
        self.index.add(embeddings)
        self.texts.extend(texts)
        self.metadata.extend(metadata)
    
    def search(self, query_embedding: np.ndarray, k: int = 3) -> List[Dict]:
        """Search for similar documents"""
        if query_embedding is None or len(query_embedding) == 0:
            return []
        
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        try:
            distances, indices = self.index.search(query_embedding, k)
        except Exception as e:
            print(f"Error during vector search: {e}")
            return []
        
        results = []
        for i, idx in enumerate(indices[0]):
            if 0 <= idx < len(self.texts):
                results.append({
                    'text': self.texts[idx],
                    'metadata': self.metadata[idx],
                    'distance': float(distances[0][i])
                })
        
        return results
    
    def save(self, path: str):
        """Save vector store to disk"""
        try:
            safe_path = os.path.normpath(path)
            os.makedirs(os.path.dirname(safe_path) or '.', exist_ok=True)
            faiss.write_index(self.index, safe_path + ".index")
            with open(safe_path + ".pkl", 'wb') as f:
                pickle.dump({'texts': self.texts, 'metadata': self.metadata}, f)
        except Exception as e:
            print(f"Error saving vector store: {e}")
            raise

    def load(self, path: str):
        """Load vector store from disk"""
        try:
            safe_path = os.path.normpath(path)
            index_path = safe_path + ".index"
            pkl_path = safe_path + ".pkl"

            if not os.path.exists(index_path) or not os.path.exists(pkl_path):
                raise FileNotFoundError(f"Vector store files not found at {safe_path}")

            self.index = faiss.read_index(index_path)
            with open(pkl_path, 'rb') as f:
                data = pickle.load(f)  # nosec - trusted local file written by this app
                self.texts = data.get('texts', [])
                self.metadata = data.get('metadata', [])
        except Exception as e:
            print(f"Error loading vector store: {e}")
            raise
