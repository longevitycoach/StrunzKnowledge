#!/bin/bash
# Test requirements in a clean environment to catch conflicts before deployment

echo "Testing requirements in a clean virtual environment..."

# Create a temporary virtual environment
python3 -m venv test-env

# Activate it
source test-env/bin/activate

# Try to install requirements
echo "Installing requirements-prod.txt..."
pip install --no-cache-dir -r requirements-prod.txt

if [ $? -eq 0 ]; then
    echo "✅ Success! All dependencies resolved correctly."
    echo "Installed versions:"
    pip freeze | grep -E "pydantic|langchain|fastmcp"
else
    echo "❌ Failed! Dependency conflicts detected."
fi

# Cleanup
deactivate
rm -rf test-env