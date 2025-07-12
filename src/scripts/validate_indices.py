#!/usr/bin/env python3
"""
Validate FAISS indices after updates
"""

import json
import logging
from pathlib import Path
import faiss
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndexValidator:
    def __init__(self):
        self.data_dir = Path("data")
        self.indices_dir = self.data_dir / "faiss_indices"
        
    def validate_faiss_index(self, index_path, metadata_path):
        """Validate a FAISS index and its metadata."""
        try:
            # Load FAISS index
            index = faiss.read_index(str(index_path))
            logger.info(f"Loaded index: {index_path.name}")
            logger.info(f"  - Index type: {type(index).__name__}")
            logger.info(f"  - Dimensions: {index.d}")
            logger.info(f"  - Total vectors: {index.ntotal}")
            
            # Load metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            doc_count = len(metadata.get('documents', []))
            logger.info(f"  - Metadata documents: {doc_count}")
            
            # Validate consistency
            if index.ntotal != doc_count:
                logger.error(f"Mismatch: {index.ntotal} vectors != {doc_count} documents")
                return False
            
            # Test search functionality
            if index.ntotal > 0:
                # Create a random query vector
                query_vector = np.random.random((1, index.d)).astype('float32')
                
                # Perform search
                k = min(5, index.ntotal)
                distances, indices = index.search(query_vector, k)
                
                logger.info(f"  - Search test successful (k={k})")
                logger.info(f"  - Distance range: {distances[0].min():.3f} - {distances[0].max():.3f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Validation failed for {index_path}: {e}")
            return False
    
    def validate_all_indices(self):
        """Validate all FAISS indices."""
        success = True
        
        # Find all index files
        index_files = list(self.indices_dir.rglob("*.faiss"))
        
        if not index_files:
            logger.error("No FAISS index files found!")
            return False
        
        logger.info(f"Validating {len(index_files)} index files...")
        
        for index_path in index_files:
            metadata_path = index_path.with_suffix('.json')
            
            if not metadata_path.exists():
                logger.error(f"Missing metadata file: {metadata_path}")
                success = False
                continue
            
            if not self.validate_faiss_index(index_path, metadata_path):
                success = False
        
        # Validate combined index specifically
        combined_index = self.indices_dir / "combined_index.faiss"
        if combined_index.exists():
            logger.info("\nValidating combined index...")
            combined_metadata = self.indices_dir / "combined_metadata.json"
            if not self.validate_faiss_index(combined_index, combined_metadata):
                success = False
        
        return success
    
    def generate_validation_report(self):
        """Generate a validation report."""
        report = {
            "validation_timestamp": str(Path.cwd() / "data" / "last_validation.json"),
            "indices": []
        }
        
        index_files = list(self.indices_dir.rglob("*.faiss"))
        
        for index_path in index_files:
            metadata_path = index_path.with_suffix('.json')
            
            try:
                index = faiss.read_index(str(index_path))
                
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                report["indices"].append({
                    "name": index_path.name,
                    "path": str(index_path),
                    "dimensions": index.d,
                    "vectors": index.ntotal,
                    "documents": len(metadata.get('documents', [])),
                    "created": metadata.get('created_date', 'unknown'),
                    "source": metadata.get('source', 'unknown'),
                    "status": "valid"
                })
                
            except Exception as e:
                report["indices"].append({
                    "name": index_path.name,
                    "path": str(index_path),
                    "status": "invalid",
                    "error": str(e)
                })
        
        # Save report
        report_path = self.data_dir / "validation_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Validation report saved to {report_path}")
        return report

def main():
    validator = IndexValidator()
    
    # Validate all indices
    if validator.validate_all_indices():
        logger.info("✅ All indices validated successfully!")
        
        # Generate detailed report
        validator.generate_validation_report()
        
        exit(0)  # Success
    else:
        logger.error("❌ Index validation failed!")
        exit(1)  # Failure

if __name__ == "__main__":
    main()