import os
import hashlib
import sqlite3



def gen_salt_hash(pin: str) -> str:
    salt = os.urandom(16).hex()

    hash_obj = hashlib.pbkdf2_hmac('sha256', pin.encode(), salt.encode(), 100000)
    return f"{salt}${hash_obj.hex()}"

if __name__ == "__main__":
    test_pin = "1234"
    hashed_pin = gen_salt_hash(test_pin)
    print(f"Original PIN: {test_pin}")
    print(f"Salted and Hashed PIN: {hashed_pin}")

def init_database():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    os.makedirs(DATA_DIR, exist_ok=True)
    DB_PATH = os.path.join(DATA_DIR, 'security.db')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # CREATE TABLE IF NOT EXISTS doesn't change an existing table, so we add missing columns below.
    cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS employees (
                site TEXT,
                department TEXT,
                emp_id TEXT,
                name TEXT,
                clearance_level INTEGER,
                access_class TEXT,
                pin_hash TEXT,
                failed_attempts INTEGER NOT NULL DEFAULT 0,
                window_started_at TEXT,
                locked_until TEXT,
                PRIMARY KEY (site, department, emp_id)
            )
        ''')
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
    