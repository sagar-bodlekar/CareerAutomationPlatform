FROM python:3.12-slim

WORKDIR /app

COPY shared/ /app/shared/
COPY match_service/ /app/match_service/
WORKDIR /app/match_service

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8005

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
