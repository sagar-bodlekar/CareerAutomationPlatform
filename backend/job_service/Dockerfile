FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for scraping (chromium, beautifulsoup, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy shared package and service code
COPY shared/ /app/shared/
COPY job_service/ /app/job_service/
WORKDIR /app/job_service

# Install service dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8004

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
