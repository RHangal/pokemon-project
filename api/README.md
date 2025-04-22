# Pokémon API

This FastAPI application exposes endpoints to query Pokémon data and competitive factors from a PostgreSQL database hosted on Azure.

## 📁 Structure

The API supports:

- `/pokemon` – Fetch Pokémon by IDs (up to 50)
- `/competitive` – Query competitive stats by IDs
- `/competitive/filter` – Powerful filter-based query over types, stats, abilities, usage, etc.
- `/sql` - Select only SQL querying for power-users
- `/graphql` – Optional GraphQL wrapper for flexible queries

## ⚙️ Setup

### 1. Create `.env.api`

Make a `.env.api` file in this directory with the following variables:

```env
API_DB_NAME=your_database_name
API_DB_USER=your_readonly_user
API_DB_PASSWORD=your_password
API_DB_HOST=your_db_host
API_DB_PORT=5432
ENV=production
ENV=production is required to ensure .env.api isn't loaded inside containers. Locally, it’s used to load environment variables.
```

### 2. Build the Docker image

Make sure you’re in the root of the project when building:

```bash
docker build -t pokemon-api ./api
```

### 3. Run the container locally

```bash
docker run --rm -p 8000:8000 --env-file ./api/.env.api pokemon-api
```

The API will be available at:
http://localhost:8000

You can access the interactive Swagger docs at:
http://localhost:8000/docs

### 🐳 Deploying to Azure Container Apps

Once your image is tested and tagged, you can push it to Azure Container Registry (ACR) and deploy it via the Azure portal or CI/CD.

See the main project README for full deployment steps.

### 📦 Dependencies

Dependencies are listed in api/requirements.txt. The image is built using python:3.13.2-slim and includes system packages like gcc and libpq-dev for psycopg2.

### 📎 Notes

CORS is enabled for all origins (\*) for now, but you may want to restrict it before production use.

Database access must be publicly allowed (via Azure Portal) for container access.
