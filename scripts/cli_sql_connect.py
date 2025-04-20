import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to DB
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cur = conn.cursor()
print("✅ Connected to database. Type SQL statements below (end with semicolon `;`)")

# Multiline query input
buffer = []
while True:
    try:
        line = input("sql> ").strip()
        if line.lower() in ("exit", "quit"):
            break

        buffer.append(line)

        if line.endswith(";"):
            query = " ".join(buffer)
            buffer.clear()

            try:
                cur.execute(query)
                if cur.description:  # SELECT statement
                    rows = cur.fetchall()
                    for row in rows:
                        print(row)
                else:
                    print("✅ Query executed.")
                conn.commit()
            except Exception as e:
                print(f"❌ Error: {e}")
                conn.rollback()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted. Exiting.")
        break

cur.close()
conn.close()
print("🔒 Connection closed.")

