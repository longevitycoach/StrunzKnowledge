import logging
from typing import List, Dict, Optional
from pathlib import Path
import requests
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class DoclingProcessor:
    """Process documents using Docling OCR for high-fidelity text extraction."""
    
    def __init__(self, docling_url: str = "http://localhost:8080/docling"):
        self.docling_url = docling_url
        self.session = requests.Session()
        
    def is_available(self) -> bool:
        """Check if Docling service is available."""
        try:
            response = self.session.get(f"{self.docling_url}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            logger.warning("Docling service is not available")
            return False
    
    def process_markdown_files(self, input_dir: str = "data/processed", 
                            output_dir: str = "data/processed/docling") -> List[Dict]:
        """Process markdown files through Docling for enhanced text extraction."""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if not self.is_available():
            logger.error("Docling service is not available. Using original text.")
            return self._fallback_processing(input_path, output_path)
        
        processed_docs = []
        markdown_files = list(input_path.glob("*.md"))
        
        for md_file in markdown_files:
            logger.info(f"Processing {md_file.name} with Docling")
            
            try:
                # Read markdown content
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Process with Docling
                processed = self._process_with_docling(content, md_file.name)
                
                if processed:
                    # Save processed content
                    output_file = output_path / f"{md_file.stem}_processed.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(processed, f, ensure_ascii=False, indent=2)
                    
                    processed_docs.append(processed)
                    logger.info(f"Successfully processed {md_file.name}")
                else:
                    logger.warning(f"Failed to process {md_file.name} with Docling")
                    
            except Exception as e:
                logger.error(f"Error processing {md_file.name}: {e}")
        
        return processed_docs
    
    def _process_with_docling(self, content: str, filename: str) -> Optional[Dict]:
        """Send content to Docling service for processing."""
        try:
            # Prepare request
            payload = {
                "content": content,
                "filename": filename,
                "options": {
                    "extract_tables": True,
                    "extract_metadata": True,
                    "language": "de",
                    "preserve_formatting": True
                }
            }
            
            # Send to Docling
            response = self.session.post(
                f"{self.docling_url}/process",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Enhance result with metadata
                enhanced_result = {
                    "filename": filename,
                    "processed_at": datetime.now().isoformat(),
                    "original_length": len(content),
                    "processed_text": result.get("text", content),
                    "metadata": result.get("metadata", {}),
                    "tables": result.get("tables", []),
                    "sections": self._extract_sections(result.get("text", content))
                }
                
                return enhanced_result
            else:
                logger.error(f"Docling returned status {response.status_code}: {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Request to Docling failed: {e}")
            return None
    
    def _extract_sections(self, text: str) -> List[Dict]:
        """Extract logical sections from processed text."""
        sections = []
        current_section = {"title": "Introduction", "content": "", "start_pos": 0}
        
        lines = text.split('\n')
        current_pos = 0
        
        for line in lines:
            # Detect section headers (lines starting with #)
            if line.strip().startswith('#'):
                # Save previous section if it has content
                if current_section["content"].strip():
                    current_section["end_pos"] = current_pos
                    sections.append(current_section)
                
                # Start new section
                title = line.strip().lstrip('#').strip()
                current_section = {
                    "title": title,
                    "content": "",
                    "start_pos": current_pos
                }
            else:
                current_section["content"] += line + '\n'
            
            current_pos += len(line) + 1
        
        # Add last section
        if current_section["content"].strip():
            current_section["end_pos"] = current_pos
            sections.append(current_section)
        
        return sections
    
    def _fallback_processing(self, input_path: Path, output_path: Path) -> List[Dict]:
        """Fallback processing when Docling is not available."""
        processed_docs = []
        markdown_files = list(input_path.glob("*.md"))
        
        for md_file in markdown_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic processing without Docling
                processed = {
                    "filename": md_file.name,
                    "processed_at": datetime.now().isoformat(),
                    "original_length": len(content),
                    "processed_text": content,
                    "metadata": {
                        "processing_method": "fallback",
                        "docling_available": False
                    },
                    "sections": self._extract_sections(content)
                }
                
                # Save processed content
                output_file = output_path / f"{md_file.stem}_processed.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(processed, f, ensure_ascii=False, indent=2)
                
                processed_docs.append(processed)
                
            except Exception as e:
                logger.error(f"Error in fallback processing for {md_file.name}: {e}")
        
        return processed_docs