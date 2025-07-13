#!/usr/bin/env python3
"""Reconstruct combined_index.faiss from chunks"""
import json

# Read metadata
with open("combined_index.faiss.metadata.json", 'r') as f:
    metadata = json.load(f)

# Reconstruct file
with open("../combined_index.faiss", 'wb') as out:
    for chunk in metadata["chunks"]:
        with open(chunk, 'rb') as f:
            out.write(f.read())

print(f"Reconstructed {metadata['original_file']} ({metadata['original_size'] / 1024 / 1024:.2f} MB)")
