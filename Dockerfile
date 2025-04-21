# === Base Image ===
FROM python:3.13.2-slim

# === Working Directory ===
WORKDIR /app

# === Install System Dependencies ===
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# === Copy Only Necessary Project Files ===
COPY data/ ./data/
COPY db_schema/ ./db_schema/
COPY scripts/utils/ ./scripts/utils/
COPY setup/ ./setup/
COPY requirements.txt ./
COPY .env .env

# === Install Python Dependencies ===
RUN pip install --no-cache-dir -r requirements.txt

# === Default Command ===
CMD ["python3", "-m", "setup.run_full_pipeline"]

