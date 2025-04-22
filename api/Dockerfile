# === Dockerfile for FastAPI API ===
FROM python:3.13.2-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire api folder into the container
COPY . /app/api

# Set working directory to /app/api so requirements.txt is available
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir -r /app/api/requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
