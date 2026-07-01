import os
from typing import List, Dict
from .embeddings import EmbeddingGenerator
from .vector_store import VectorStore

class MedicalRetriever:
    def __init__(self, knowledge_base_path: str = 'data/knowledge_base'):
        self.knowledge_base_path = knowledge_base_path
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.is_initialized = False
    
    def initialize(self):
        if not self.is_initialized:
            self._load_or_create_index()
            self.is_initialized = True
    
    def _load_or_create_index(self):
        index_path = 'faiss_index/medical_kb'
        
        if os.path.exists(f"{index_path}.index"):
            self.vector_store.load(index_path)
        else:
            self._build_index()
            self.vector_store.save(index_path)
    
    def _build_index(self):
        documents = []
        metadata = []
        
        if not os.path.exists(self.knowledge_base_path):
            return
        
        for filename in os.listdir(self.knowledge_base_path):
            if filename.endswith('.txt'):
                filepath = os.path.join(self.knowledge_base_path, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                chunks = self._chunk_text(content, chunk_size=500)
                for chunk in chunks:
                    documents.append(chunk)
                    metadata.append({
                        'source': filename,
                        'topic': filename.replace('.txt', '')
                    })
        
        if documents:
            embeddings = self.embedding_generator.generate_embeddings(documents)
            self.vector_store.add_documents(embeddings, documents, metadata)
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def retrieve(self, query: str, k: int = 3) -> List[Dict]:
        if not self.is_initialized:
            self.initialize()
        
        query_embedding = self.embedding_generator.generate_single_embedding(query)
        results = self.vector_store.search(query_embedding, k)
        return results
