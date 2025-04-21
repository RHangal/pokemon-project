# 🌟 Pokémon Data Engineering Pipeline

This project sets up a PostgreSQL-based pipeline to ingest, normalize, and populate structured Pokémon data using both local and containerized options.

## 🔧 Features

- Normalized PostgreSQL schema (3NF)
- Full ingestion pipeline for CSV data
- Junction and foreign key table linking
- Automatic sprite linking from Azure Blob Storage
- Atomic operations for safe rollback
- Dual support: run locally or via Docker container

---

## 🌐 Requirements

- Python 3.10+
- PostgreSQL (hosted locally or on Azure)
- Azure Blob Storage (for sprite linking)
- pip (for dependency management)
- Optional: Docker for containerized setup

---

## 📂 Directory Structure

```bash
pokemon_project/
├── data/                        # All input CSV files
├── db_schema/                  # SQL schema and creation scripts
│   ├── sql/
│       ├── tables/
│       └── views/
├── scripts/
│   ├── data_ingest/         # All ingestion Python scripts
│   └── sql/                 # SQL tables and view creation scripts
├── setup/
│   ├── pipeline_scripts/     # Scripts to run in sequence
│   └── run_full_pipeline.py  # Executes all steps atomically
├── .env                        # Environment config (not committed)
├── requirements.txt            # All Python dependencies
├── Dockerfile                  # Containerized setup
└── docker_setup.sh              # One-liner to run container setup
```

---

### 1. Create your `.env` file

```dotenv
DB_NAME=pokemon
DB_USER=your_user
DB_PASSWORD=your_pass
DB_HOST=your_host
DB_PORT=5432
AZURE_CONNECTION_STRING="your_blob_connection_string"
```

## 🚀 Quickstart (Local Setup)

### 2. Set up Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the pipeline

```bash
python3 -m setup.run_full_pipeline
```

---

## 🧱 Quickstart (Docker Setup)

### 1. Make sure you have your `.env` ready in the root directory

### 2. Build the Docker image

```bash
bash docker_setup.sh
```

This will:

- Build the container image
- Install all dependencies
- Run the full pipeline inside the container

---

## 🚪 Manual Setup (Step-by-Step)

Use the individual scripts in:

```bash
scripts/data_ingest
scripts/sql
```

All scripts support atomic operations and detailed logging.

---

## 🕹️ Jupyter / Dev Testing

If you plan to use Jupyter:

```bash
python -m ipykernel install --user --name=pokemon_venv
```

Then use `pokemon_venv` as your kernel.
