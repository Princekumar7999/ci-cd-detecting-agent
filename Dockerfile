FROM python:3.11-slim

WORKDIR /app

# Install git and docker client (for sibling containers)
RUN apt-get update && apt-get install -y git docker.io && rm -rf /var/lib/apt/lists/*

# Copy requirements from backend folder
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

EXPOSE 8000

CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"
