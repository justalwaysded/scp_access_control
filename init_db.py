import os
import sqlite3

from src.config import DATA_DIR, DB_PATH, EMPLOYEES_SCHEMA

def init_database():
    os.makedirs(DATA_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # CREATE TABLE IF NOT EXISTS doesn't change an existing table, so we add missing columns below.
    cursor.execute(EMPLOYEES_SCHEMA)
    cursor.execute("PRAGMA table_info(employees)")
    columns = [row[1] for row in cursor.fetchall()]

    if "failed_attempts" not in columns:
        cursor.execute("ALTER TABLE employees ADD COLUMN failed_attempts INTEGER NOT NULL DEFAULT 0")

    if "window_started_at" not in columns:
        cursor.execute("ALTER TABLE employees ADD COLUMN window_started_at TEXT")

    if "locked_until" not in columns:
        cursor.execute("ALTER TABLE employees ADD COLUMN locked_until TEXT")

    cursor.execute("PRAGMA table_info(employees)")
    columns = {row[1] for row in cursor.fetchall()}

    required = {
        "site",
        "department",
        "emp_id",
        "name",
        "clearance_level",
        "access_class",
        "pin_hash",
        "failed_attempts", 
        "window_started_at", 
        "locked_until"
        }

    missing = required - columns

    if missing:
        conn.rollback()
        conn.close()
        raise RuntimeError(f"Unable to add columns: {missing}")

    conn.commit()
    conn.close()
    print(f"[SUCCESS] db initialized: {DB_PATH}")

if __name__ == "__main__":
    init_database()
    