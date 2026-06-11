FROM python:3.12-slim

WORKDIR /app

COPY backend/shared/ /app/shared/
RUN pip install --no-cache-dir -e /app/shared/

COPY backend/notification_service/ /app/notification_service/
WORKDIR /app/notification_service

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8011

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8011"]
