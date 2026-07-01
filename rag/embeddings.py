from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
import streamlit as st

@st.cache_resource(show_spinner=False)
def _load_model(model_name: str):
    return SentenceTransformer(model_name)

class EmbeddingGenerator:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = _load_model(model_name)
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    def generate_single_embedding(self, text: str) -> np.ndarray:
        embedding = self.model.encode([text], convert_to_numpy=True)
        return embedding[0]
