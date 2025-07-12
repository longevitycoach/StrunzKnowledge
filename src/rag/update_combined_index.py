#!/usr/bin/env python3
"""
Update the combined FAISS index with new forum data
"""

import json
import logging
from pathlib import Path
from datetime import datetime
import faiss
import shutil

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def update_combined_index():
    """Update combined index with new forum data."""
    data_dir = Path("data")
    index_dir = data_dir / "faiss_indices"
    
    # Backup existing combined index
    combined_index_file = index_dir / "combined_index.faiss"
    combined_metadata_file = index_dir / "combined_metadata.json"
    
    if combined_index_file.exists():
        backup_file = index_dir / f"combined_index_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.faiss"
        backup_meta = index_dir / f"combined_metadata_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy(combined_index_file, backup_file)
        shutil.copy(combined_metadata_file, backup_meta)
        logging.info(f"Backed up existing combined index to {backup_file}")
    
    # Load all indices
    indices = {}
    metadatas = {}
    
    # Load news index
    news_index_file = index_dir / "news" / "news_index_20250712_202935.faiss"
    if news_index_file.exists():
        indices['news'] = faiss.read_index(str(news_index_file))
        with open(news_index_file.with_suffix('.json'), 'r') as f:
            metadatas['news'] = json.load(f)
        logging.info(f"Loaded news index: {metadatas['news']['total_documents']} documents")
    
    # Load books index
    books_index_file = index_dir / "books" / "books_index_20250712_205242.faiss"
    if books_index_file.exists():
        indices['books'] = faiss.read_index(str(books_index_file))
        with open(books_index_file.with_suffix('.json'), 'r') as f:
            metadatas['books'] = json.load(f)
        logging.info(f"Loaded books index: {metadatas['books']['total_documents']} documents")
    
    # Load new forum index
    forum_index_file = index_dir / "forum" / "forum_index_20250712_211508.faiss"
    if forum_index_file.exists():
        indices['forum'] = faiss.read_index(str(forum_index_file))
        with open(forum_index_file.with_suffix('.json'), 'r') as f:
            metadatas['forum'] = json.load(f)
        logging.info(f"Loaded forum index: {metadatas['forum']['total_documents']} documents")
    
    # Create new combined index
    if indices:
        # Get dimension from first index
        dim = next(iter(indices.values())).d
        combined_index = faiss.IndexFlatL2(dim)
        
        # Combine all documents
        all_documents = []
        
        for source, metadata in metadatas.items():
            # Add source type to each document
            for doc in metadata['documents']:
                doc['metadata']['content_type'] = source
                all_documents.append(doc)
            
            # Add vectors to combined index
            if source in indices:
                vectors = indices[source].reconstruct_n(0, indices[source].ntotal)
                combined_index.add(vectors)
        
        # Save combined index
        faiss.write_index(combined_index, str(combined_index_file))
        
        # Save combined metadata
        combined_metadata = {
            'documents': all_documents,
            'total_documents': len(all_documents),
            'embedding_model': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
            'embedding_dim': dim,
            'created_date': datetime.now().isoformat(),
            'sources': list(metadatas.keys()),
            'source_counts': {source: meta['total_documents'] for source, meta in metadatas.items()}
        }
        
        with open(combined_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(combined_metadata, f, ensure_ascii=False, indent=2)
        
        logging.info(f"\n✅ Combined index updated successfully!")
        logging.info(f"Total documents: {combined_metadata['total_documents']}")
        for source, count in combined_metadata['source_counts'].items():
            logging.info(f"  - {source}: {count} documents")

if __name__ == "__main__":
    update_combined_index()