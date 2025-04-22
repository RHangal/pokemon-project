import os
import psycopg2
from dotenv import load_dotenv

# Only load .env if running locally
if os.getenv("ENV") != "production":
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.api"))

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("API_DB_NAME"),
        user=os.getenv("API_DB_USER"),
        password=os.getenv("API_DB_PASSWORD"),
        host=os.getenv("API_DB_HOST"),
        port=os.getenv("API_DB_PORT")
    )
  

