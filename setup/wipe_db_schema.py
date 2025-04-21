from scripts.utils.db_utils import get_db_connection

def run(cur):
    cur.execute("""
        DO $$
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
    """)

if __name__ == "__main__":
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("BEGIN;")
        run(cur)
        conn.commit()
        print("✅ All tables dropped.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to drop tables: {e}")
    finally:
        cur.close()
        conn.close()

