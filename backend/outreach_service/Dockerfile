FROM python:3.12-slim

WORKDIR /app

COPY shared/ /app/shared/
COPY outreach_service/ /app/outreach_service/
WORKDIR /app/outreach_service

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8006

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8006"]
