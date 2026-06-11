#!/bin/bash
# Pre-pull recommended Ollama models for the Career Platform
# Usage: bash docker/ollama/pull-models.sh

set -e

echo "Pulling recommended Ollama models..."
echo "====================================="

# Lightweight model (runs on 8GB RAM)
echo "Pulling llama3.2:8b (lightweight, runs on 8GB RAM)..."
ollama pull llama3.2:8b

# Medium model (runs on 16GB RAM)
echo "Pulling mistral-small (medium, runs on 16GB RAM)..."
ollama pull mistral-small

# Optional: larger models for better quality (require more RAM)
echo ""
echo "To pull additional models:"
echo "  ollama pull llama3.2:70b    # Best quality, needs 48GB+ RAM"
echo "  ollama pull qwen2.5:32b     # Great for code/matching, needs 24GB+ RAM"
echo "  ollama pull gemma3:12b      # Efficient, needs 16GB+ RAM"
echo ""
echo "Done! Models are ready for use."
echo "Test with: curl http://localhost:11434/api/generate -d '{\"model\":\"llama3.2:8b\",\"prompt\":\"Hello\"}'"
