#!/bin/bash

# === Ensure .env is configured ===
if [ ! -f .env ]; then
  echo "❌ .env file not found. Please create one before running this setup."
  exit 1
fi

# === Build Docker Image ===
echo "🐳 Building Docker image..."
docker build -t pokemon-pipeline -f setup/Dockerfile .

# === Run Container ===
echo "🚀 Running pipeline container..."
docker run --rm pokemon-pipeline

