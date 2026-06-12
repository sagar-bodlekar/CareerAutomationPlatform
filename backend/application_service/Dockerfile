FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy shared library and install it first
COPY shared/ /app/shared/
RUN pip install --no-cache-dir -e /app/shared/

# Install service Python dependencies (filtering out editable paths that need project metadata)
COPY application_service/requirements.txt .
RUN grep -v "^-e" requirements.txt > /tmp/requirements-base.txt && \
    pip install --no-cache-dir -r /tmp/requirements-base.txt

# Copy service code
COPY application_service/app/ ./app/

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

EXPOSE 8007

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"]
