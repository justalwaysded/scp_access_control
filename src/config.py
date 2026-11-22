from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "security.db"
EVENTS_PATH = BASE_DIR / "config" / "events.json"