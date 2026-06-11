FROM python:3.12-slim

WORKDIR /app

COPY shared/ /app/shared/
COPY application_service/ /app/application_service/
WORKDIR /app/application_service

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8007

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"]
