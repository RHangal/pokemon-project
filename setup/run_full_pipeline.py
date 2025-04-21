import os
import importlib.util
from scripts.utils.db_utils import get_db_connection

# Directory holding all numbered pipeline scripts
PIPELINE_DIR = os.path.join(os.path.dirname(__file__), "pipeline_scripts")


def run_pipeline_scripts():
    # Get sorted script paths
    scripts = sorted(f for f in os.listdir(PIPELINE_DIR) if f.endswith(".py") and f != "__init__.py")

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("BEGIN;")
        print("🚀 Started full pipeline transaction.")

        for script in scripts:
            script_path = os.path.join(PIPELINE_DIR, script)
            print(f"\n📂 Executing: {script}")

            spec = importlib.util.spec_from_file_location("pipeline_module", script_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            # Expecting `run(cur)` in each script
            if hasattr(mod, "run"):
                mod.run(cur)
            else:
                raise Exception(f"{script} does not define a run(cur) function.")

        conn.commit()
        print("\n✅ Full pipeline completed successfully.")

    except Exception as e:
        if conn:
            conn.rollback()
            print("\n❌ Pipeline failed. Rolled back all changes.")
        print(f"💥 Error: {e}")
        raise

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("🔒 DB connection closed.")


if __name__ == "__main__":
    run_pipeline_scripts()

