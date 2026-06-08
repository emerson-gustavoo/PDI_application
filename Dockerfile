FROM python:3.12-slim

WORKDIR /app

# Dependencias primeiro (cache de build)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Codigo da aplicacao
COPY app ./app

# A app escuta na 8000 dentro do container
EXPOSE 8000

# O banco SQLite vive em /data (volume persistente, ver docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
