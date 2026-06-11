FROM ollama/ollama:latest

# Copy model pull script
COPY pull-models.sh /pull-models.sh

# Expose Ollama API port
EXPOSE 11434

# Default entrypoint
ENTRYPOINT ["ollama", "serve"]
