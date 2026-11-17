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
    os.makedirs('data', exist_ok=True)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'data', 'security.db')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                site TEXT,
                department TEXT,
                emp_id TEXT,
                name TEXT,
                clearance_level INTEGER,
                access_class TEXT,
                pin_hash TEXT,
                PRIMARY KEY (site, department, emp_id)
            )
        ''')

# text data; employees: 15420412934, 19110075323, 15420429532
    # employees_data = [
    #     ('15', '42', '04129', 'Dr. Bright', 4, 'C', gen_salt_hash('1234')),
    #     ('19', '11', '00753', 'Agent S.', 3, 'B', gen_salt_hash('5555')),
    #     ('15', '42', '04295', 'Infr. Eng. Alex', 2, 'C', gen_salt_hash('9876'))
    # ]

    # cursor.executemany('''
    # INSERT OR REPLACE INTO employees
    # (site, department, emp_id, name, clearance_level, access_class, pin_hash)
    # VALUES (?, ?, ?, ?, ?, ?, ?)

    # ''', employees_data)

    conn.commit()
    conn.close()
    print(f"[SUCCESS] db initialized: {DB_PATH}")

if __name__ == "__main__":
    init_database()
    