FROM python:3.12-slim

WORKDIR /app

COPY backend/shared/ /app/shared/
RUN pip install --no-cache-dir -e /app/shared/

COPY backend/ai_orchestrator/ /app/ai_orchestrator/
WORKDIR /app/ai_orchestrator

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8009

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8009"]
