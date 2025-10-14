FROM python:3.11-slim

WORKDIR /app

# Install netcat for waiting logic
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["bash", "-c", "until nc -z db 5432; do echo '⏳ Waiting for database...'; sleep 2; done; alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
