FROM python:3.11.8-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y postgresql-client

COPY app/ app/
COPY api/ api/
COPY Makefile .
COPY docker/ docker/
COPY init_db.py .

RUN apt-get update && \
    apt-get install -y postgresql-client procps && \
    rm -rf /var/lib/apt/lists/*


CMD ["bash", "-c", "python3 app/proxy.py & python3 api/server.py & wait"]
