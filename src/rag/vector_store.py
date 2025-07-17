"""
Fixed vector store that handles the actual metadata structure
"""
import faiss
import numpy as np
import json
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    # Use lightweight alternative if sentence-transformers not available
    from ..mcp.lightweight_embeddings import SentenceTransformer
    logger.warning("Using lightweight embeddings instead of sentence-transformers")


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
            if idx < 0 or idx >= len(self.documents):  # FAISS returns -1 for empty slots
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
    
    def load_index(self) -> bool:
        """Load index and metadata from disk - handles both old and new formats."""
        # Try different possible locations and filenames
        possible_paths = [
            (self.index_path / "index.faiss", self.index_path / "metadata.json"),
            (self.index_path.parent / "combined_index.faiss", self.index_path.parent / "combined_metadata.json"),
            (Path("data/faiss_indices") / "combined_index.faiss", Path("data/faiss_indices") / "combined_metadata.json"),
        ]
        
        for index_file, metadata_file in possible_paths:
            if index_file.exists() and metadata_file.exists():
                logger.info(f"Found index files at: {index_file}")
                break
        else:
            logger.info("No existing index found in any expected location")
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(index_file))
            logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            
            # Load metadata
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Handle different metadata formats
            if 'documents' in metadata and isinstance(metadata['documents'], list):
                # New format or converted format
                self.documents = []
                for i, doc_data in enumerate(metadata['documents']):
                    # Handle different document formats
                    if 'id' in doc_data:
                        # Standard format
                        doc = Document(
                            id=doc_data['id'],
                            content=doc_data.get('content', doc_data.get('text', '')),
                            metadata=doc_data.get('metadata', {})
                        )
                    else:
                        # Old format - create ID from index
                        doc = Document(
                            id=f"doc_{i}",
                            content=doc_data.get('text', doc_data.get('content', '')),
                            metadata=doc_data.get('metadata', {})
                        )
                        # Add title to metadata if present
                        if 'title' in doc_data:
                            doc.metadata['title'] = doc_data['title']
                    
                    self.documents.append(doc)
                    self.id_to_idx[doc.id] = i
                
                # Get dimension from metadata or index
                if 'dimension' in metadata:
                    self.dimension = metadata['dimension']
                elif 'embedding_dim' in metadata:
                    self.dimension = metadata['embedding_dim']
                else:
                    self.dimension = self.index.d
                
                logger.info(f"Loaded {len(self.documents)} documents from metadata")
                return True
            else:
                logger.error("Unexpected metadata format")
                return False
                
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store."""
        return {
            'total_documents': len(self.documents),
            'active_documents': len([d for d in self.documents if not d.metadata.get('deleted')]),
            'index_size': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'index_type': type(self.index).__name__ if self.index else None
        }