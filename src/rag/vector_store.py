import faiss
import numpy as np
import json
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Document with metadata."""
    id: str
    content: str
    metadata: Dict
    embedding: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary, excluding embedding."""
        d = asdict(self)
        d.pop('embedding', None)
        return d


class FAISSVectorStore:
    """FAISS-based vector store for the knowledge base."""
    
    def __init__(self, 
                 index_path: str = "data/processed/faiss_index",
                 embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                 dimension: int = 384):
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        self.dimension = dimension
        self.index = None
        self.documents = []
        self.id_to_idx = {}
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedder = SentenceTransformer(embedding_model)
        
        # Load existing index if available
        self.load_index()
    
    def create_index(self, index_type: str = "Flat"):
        """Create a new FAISS index."""
        if index_type == "Flat":
            # Exact search, best quality
            self.index = faiss.IndexFlatIP(self.dimension)
        elif index_type == "IVF":
            # Faster search with some quality tradeoff
            quantizer = faiss.IndexFlatIP(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
        else:
            raise ValueError(f"Unknown index type: {index_type}")
        
        logger.info(f"Created FAISS {index_type} index with dimension {self.dimension}")
    
    def add_documents(self, documents: List[Dict]) -> int:
        """Add documents to the vector store."""
        if self.index is None:
            self.create_index()
        
        new_docs = []
        embeddings = []
        
        for doc_data in documents:
            # Create document
            doc_id = doc_data.get('id', f"doc_{len(self.documents) + len(new_docs)}")
            doc = Document(
                id=doc_id,
                content=doc_data['content'],
                metadata=doc_data.get('metadata', {})
            )
            
            # Generate embedding
            embedding = self._embed_text(doc.content)
            doc.embedding = embedding
            
            new_docs.append(doc)
            embeddings.append(embedding)
        
        if new_docs:
            # Add to FAISS index
            embeddings_array = np.array(embeddings).astype('float32')
            
            # Normalize for inner product
            faiss.normalize_L2(embeddings_array)
            
            # Get starting index
            start_idx = len(self.documents)
            
            # Add to index
            if hasattr(self.index, 'train') and not self.index.is_trained:
                # Train IVF index if needed
                self.index.train(embeddings_array)
            
            self.index.add(embeddings_array)
            
            # Update document storage
            for i, doc in enumerate(new_docs):
                idx = start_idx + i
                self.documents.append(doc)
                self.id_to_idx[doc.id] = idx
            
            logger.info(f"Added {len(new_docs)} documents to the vector store")
            
            # Save index
            self.save_index()
        
        return len(new_docs)
    
    def search(self, 
               query: str, 
               k: int = 5, 
               filter_metadata: Optional[Dict] = None) -> List[Tuple[Document, float]]:
        """Search for similar documents."""
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Vector store is empty")
            return []
        
        # Embed query
        query_embedding = self._embed_text(query)
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, min(k * 2, self.index.ntotal))
        
        # Filter and collect results
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < 0:  # FAISS returns -1 for empty slots
                continue
                
            doc = self.documents[idx]
            
            # Apply metadata filter if provided
            if filter_metadata:
                match = all(
                    doc.metadata.get(key) == value 
                    for key, value in filter_metadata.items()
                )
                if not match:
                    continue
            
            results.append((doc, float(score)))
            
            if len(results) >= k:
                break
        
        return results
    
    def _embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text."""
        # Truncate very long texts
        max_length = 512
        if len(text) > max_length * 4:  # Rough character to token ratio
            text = text[:max_length * 4]
        
        embedding = self.embedder.encode(text, convert_to_numpy=True)
        return embedding
    
    def save_index(self):
        """Save index and metadata to disk."""
        if self.index is None:
            return
        
        # Save FAISS index
        index_file = self.index_path / "index.faiss"
        faiss.write_index(self.index, str(index_file))
        
        # Save documents and metadata
        metadata = {
            'documents': [doc.to_dict() for doc in self.documents],
            'id_to_idx': self.id_to_idx,
            'dimension': self.dimension,
            'created_at': datetime.now().isoformat()
        }
        
        metadata_file = self.index_path / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved vector store to {self.index_path}")
    
    def load_index(self) -> bool:
        """Load index and metadata from disk."""
        index_file = self.index_path / "index.faiss"
        metadata_file = self.index_path / "metadata.json"
        
        if not index_file.exists() or not metadata_file.exists():
            logger.info("No existing index found")
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(index_file))
            
            # Load metadata
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Restore documents
            self.documents = []
            for doc_data in metadata['documents']:
                doc = Document(
                    id=doc_data['id'],
                    content=doc_data['content'],
                    metadata=doc_data['metadata']
                )
                self.documents.append(doc)
            
            self.id_to_idx = metadata['id_to_idx']
            self.dimension = metadata['dimension']
            
            logger.info(f"Loaded vector store with {len(self.documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            return False
    
    def delete_document(self, doc_id: str) -> bool:
        """Mark a document as deleted (FAISS doesn't support true deletion)."""
        if doc_id in self.id_to_idx:
            idx = self.id_to_idx[doc_id]
            # Mark as deleted in metadata
            self.documents[idx].metadata['deleted'] = True
            self.save_index()
            return True
        return False
    
    def clear(self):
        """Clear all documents from the store."""
        self.index = None
        self.documents = []
        self.id_to_idx = {}
        
        # Remove saved files
        for file in self.index_path.glob("*"):
            file.unlink()
        
        logger.info("Cleared vector store")
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store."""
        return {
            'total_documents': len(self.documents),
            'active_documents': len([d for d in self.documents if not d.metadata.get('deleted')]),
            'index_size': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'index_type': type(self.index).__name__ if self.index else None
        }