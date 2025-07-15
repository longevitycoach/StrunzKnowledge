#!/bin/bash
# Reconstruct FAISS indices from chunks during Docker build

echo "Reconstructing FAISS indices from chunks..."

cd data/faiss_indices/chunks

# Reconstruct combined_index.faiss
if [ -f "combined_index.faiss.metadata.json" ]; then
    echo "Reconstructing combined_index.faiss..."
    python reconstruct_combined_index.faiss.py
fi

# Reconstruct combined_metadata.json
if [ -f "combined_metadata.json.metadata.json" ]; then
    echo "Reconstructing combined_metadata.json..."
    python reconstruct_combined_metadata.json.py
fi

# Create combined directory and copy files with correct names
mkdir -p ../combined
cp ../combined_index.faiss ../combined/index.faiss 2>/dev/null || true
cp ../combined_metadata.json ../combined/metadata.json 2>/dev/null || true

echo "Reconstruction complete!"
ls -lh ../combined/