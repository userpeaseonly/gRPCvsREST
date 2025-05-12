# Dockerfile
FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies for psycopg2 (PostgreSQL adapter)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app .

CMD ["python", "products.py"]
