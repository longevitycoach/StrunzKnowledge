#!/usr/bin/env python3
"""
Split large FAISS index and metadata files into smaller chunks for GitHub storage
"""

import os
import json
import numpy as np
from pathlib import Path

def split_file(filepath, chunk_size_mb=40):
    """Split a file into chunks of specified size."""
    chunk_size = chunk_size_mb * 1024 * 1024  # Convert to bytes
    
    file_size = os.path.getsize(filepath)
    print(f"File: {filepath}")
    print(f"Size: {file_size / 1024 / 1024:.2f} MB")
    
    if file_size <= chunk_size:
        print(f"File is already under {chunk_size_mb} MB, no need to split")
        return
    
    # Read file in binary mode
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Calculate number of chunks needed
    num_chunks = (file_size + chunk_size - 1) // chunk_size
    print(f"Will split into {num_chunks} chunks")
    
    # Create output directory
    output_dir = Path(filepath).parent / "chunks"
    output_dir.mkdir(exist_ok=True)
    
    # Split into chunks
    base_name = Path(filepath).name
    for i in range(num_chunks):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, file_size)
        chunk_data = data[start:end]
        
        chunk_file = output_dir / f"{base_name}.part{i:03d}"
        with open(chunk_file, 'wb') as f:
            f.write(chunk_data)
        
        chunk_size_mb = len(chunk_data) / 1024 / 1024
        print(f"Created {chunk_file.name}: {chunk_size_mb:.2f} MB")
    
    # Create metadata file for reconstruction
    metadata = {
        "original_file": base_name,
        "original_size": file_size,
        "num_chunks": num_chunks,
        "chunk_size": chunk_size,
        "chunks": [f"{base_name}.part{i:03d}" for i in range(num_chunks)]
    }
    
    metadata_file = output_dir / f"{base_name}.metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Created metadata file: {metadata_file.name}")
    
    # Create reconstruction script
    reconstruct_script = output_dir / f"reconstruct_{base_name}.py"
    with open(reconstruct_script, 'w') as f:
        f.write(f'''#!/usr/bin/env python3
"""Reconstruct {base_name} from chunks"""
import json

# Read metadata
with open("{base_name}.metadata.json", 'r') as f:
    metadata = json.load(f)

# Reconstruct file
with open("../{base_name}", 'wb') as out:
    for chunk in metadata["chunks"]:
        with open(chunk, 'rb') as f:
            out.write(f.read())

print(f"Reconstructed {{metadata['original_file']}} ({{metadata['original_size'] / 1024 / 1024:.2f}} MB)")
''')
    
    os.chmod(reconstruct_script, 0o755)
    print(f"Created reconstruction script: {reconstruct_script.name}")

def main():
    """Split FAISS indices and metadata files."""
    data_dir = Path("data/faiss_indices")
    
    # Files to potentially split
    files_to_check = [
        data_dir / "combined_index.faiss",
        data_dir / "combined_metadata.json",
    ]
    
    for filepath in files_to_check:
        if filepath.exists():
            print(f"\n{'='*50}")
            split_file(filepath, chunk_size_mb=40)
        else:
            print(f"File not found: {filepath}")

if __name__ == "__main__":
    main()