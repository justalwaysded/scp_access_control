from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "security.db"
EVENTS_PATH = BASE_DIR / "config" / "events.json"

CLASS_TO_DIGIT = {
    'A': '1',
    'B': '2',
    'C': '3',
    'D': '4',
    'E': '5'
}

DIGIT_TO_CLASS = {
    digit: access_class
    for access_class, digit in CLASS_TO_DIGIT.items()
}

EMPLOYEES_SCHEMA = ''' 
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
'''