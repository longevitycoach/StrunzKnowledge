"""
Lightweight embedding service to replace heavy sentence-transformers
Uses TF-IDF for semantic search instead of neural embeddings
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from pathlib import Path
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class LightweightEmbeddings:
    """Lightweight alternative to sentence-transformers using TF-IDF"""
    
    def __init__(self, max_features: int = 10000):
        """
        Initialize lightweight embeddings
        
        Args:
            max_features: Maximum number of features for TF-IDF
        """
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words='german',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95
        )
        self.is_fitted = False
        
    def fit(self, texts: List[str]):
        """Fit the vectorizer on texts"""
        logger.info(f"Fitting TF-IDF on {len(texts)} documents")
        self.vectorizer.fit(texts)
        self.is_fitted = True
        
    def transform(self, texts: List[str]) -> np.ndarray:
        """Transform texts to embeddings"""
        if not self.is_fitted:
            raise ValueError("Vectorizer must be fitted before transform")
        return self.vectorizer.transform(texts).toarray()
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings (compatible with sentence-transformers API)"""
        if isinstance(texts, str):
            texts = [texts]
        
        if not self.is_fitted:
            # For single text encoding, use pre-fitted model
            raise ValueError("Model must be fitted first")
            
        return self.transform(texts)
    
    def similarity(self, query_embedding: np.ndarray, doc_embeddings: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity"""
        return cosine_similarity(query_embedding.reshape(1, -1), doc_embeddings).flatten()
    
    def save(self, path: Path):
        """Save fitted vectorizer"""
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted vectorizer")
        
        with open(path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
            
    def load(self, path: Path):
        """Load fitted vectorizer"""
        with open(path, 'rb') as f:
            self.vectorizer = pickle.load(f)
            self.is_fitted = True
            
    @property
    def embedding_dimension(self) -> int:
        """Get embedding dimension"""
        if not self.is_fitted:
            return 0
        return len(self.vectorizer.get_feature_names_out())


class HybridEmbeddings:
    """Hybrid approach using both TF-IDF and simple word embeddings"""
    
    def __init__(self, embedding_file: Optional[Path] = None):
        """
        Initialize hybrid embeddings
        
        Args:
            embedding_file: Path to pre-trained word embeddings (optional)
        """
        self.tfidf = LightweightEmbeddings(max_features=5000)
        self.word_embeddings = {}
        
        if embedding_file and embedding_file.exists():
            self._load_word_embeddings(embedding_file)
            
    def _load_word_embeddings(self, path: Path):
        """Load pre-trained word embeddings"""
        # This would load GloVe or similar lightweight embeddings
        # For now, using random embeddings as placeholder
        pass
        
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode using hybrid approach"""
        if isinstance(texts, str):
            texts = [texts]
            
        # Use TF-IDF for now
        return self.tfidf.encode(texts)
        
    def fit(self, texts: List[str]):
        """Fit the model"""
        self.tfidf.fit(texts)


# Singleton instance to replace sentence-transformers
_embedding_model = None

def get_embedding_model() -> LightweightEmbeddings:
    """Get or create embedding model instance"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = LightweightEmbeddings()
    return _embedding_model


# Drop-in replacement for sentence-transformers
class SentenceTransformer:
    """Mock SentenceTransformer API for compatibility"""
    
    def __init__(self, model_name: str = None):
        self.model = get_embedding_model()
        self.model_name = model_name or "tfidf-lightweight"
        
    def encode(self, sentences: List[str], **kwargs) -> np.ndarray:
        """Encode sentences"""
        return self.model.encode(sentences)
        
    @property
    def get_sentence_embedding_dimension(self) -> int:
        """Get embedding dimension"""
        return self.model.embedding_dimension or 768  # Default dimension