FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app/backend
COPY database/schema /app/database/schema
COPY database/sql/010_analytics_views.sql /app/database/sql/010_analytics_views.sql

EXPOSE 8000

CMD ["sh", "-c", "python -m backend.app.db.bootstrap && uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
