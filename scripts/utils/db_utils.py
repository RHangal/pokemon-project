import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables once
load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def get_root_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def get_csv_path(filename):
    return os.path.join(get_root_path(), "data", filename)
