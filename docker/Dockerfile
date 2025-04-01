FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопировать директории по отдельности в корень /app
COPY app/ app/
COPY api/ api/
COPY Makefile .
COPY docker/ docker/


CMD ["bash", "-c", "python3 app/proxy.py & python3 api/server.py & wait"]
