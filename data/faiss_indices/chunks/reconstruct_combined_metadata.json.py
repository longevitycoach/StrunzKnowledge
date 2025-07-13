#!/usr/bin/env python3
"""Reconstruct combined_metadata.json from chunks"""
import json

# Read metadata
with open("combined_metadata.json.metadata.json", 'r') as f:
    metadata = json.load(f)

# Reconstruct file
with open("../combined_metadata.json", 'wb') as out:
    for chunk in metadata["chunks"]:
        with open(chunk, 'rb') as f:
            out.write(f.read())

print(f"Reconstructed {metadata['original_file']} ({metadata['original_size'] / 1024 / 1024:.2f} MB)")
