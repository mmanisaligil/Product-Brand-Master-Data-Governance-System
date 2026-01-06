FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY backend/alembic.ini ./alembic.ini
COPY backend/migrations ./migrations
COPY backend/entrypoint.sh ./entrypoint.sh
COPY data /data

ENV PYTHONPATH=/app

CMD ["./entrypoint.sh"]
