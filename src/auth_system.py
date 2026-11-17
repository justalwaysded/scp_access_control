import hashlib
import hmac
import sqlite3
import os
import datetime
import getpass
import json
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from datetime import datetime
from src.parser import parse_barcode
from src.admin import pause
from src.admin import clear_screen

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'security.db')

LOG_PATH = os.path.join(BASE_DIR, 'data', 'auth.log')
ERRORS_PATH = os.path.join(BASE_DIR, 'config', 'errors.json')

with open(ERRORS_PATH, "r", encoding="utf-8") as f:
    ERROR_CATALOG = json.load(f)

def log_security_incident(card_id: str, error_id: str, details: str = ""):
    # writes security incidents in a protected log file
    os.makedirs((os.path.join(BASE_DIR, 'data')), exist_ok=True)
    err = ERROR_CATALOG.get(error_id, {
        "code": "UNKNOWN ERROR",
        "severity": "HIGH",
        "message": "Unknown security incident."
    })

    log_record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error_id": error_id,
        "code": err["code"],
        "severity": err["severity"],
        "card_id": card_id,
        "details": details
    }

    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_record, ensure_ascii=False) + "\n")
    
    print(f"\n[ALERT | {error_id} | {err['severity']}] {err['message']}")
    print("This incident will be reported.")

def verify_pin(stored_password: str, provided_pin: str) -> bool:
    """Checks pin with a hash from the db"""
    try:
        salt, stored_hash = stored_password.split('$')
    except ValueError:
        return False

    new_hash = hashlib.pbkdf2_hmac(
        'sha256',
        provided_pin.encode('utf-8'),
        salt.encode('utf-8'),
        100_000
    ).hex()

    return hmac.compare_digest(stored_hash, new_hash)

def authenticate_user(raw_barcode: str) -> bool:
    clean_code = raw_barcode.strip()

    try:
        card = parse_barcode(clean_code)
    except ValueError as e:
        log_security_incident(clean_code, "ERR_01", str(e))
        pause()
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT name, clearance_level, access_class, pin_hash 
    FROM employees
    WHERE site = ? AND department = ? AND emp_id = ?
    ''', (card["site"], card["department"], card["emp_id"]))

    record = cursor.fetchone()
    conn.close()

    # case: employee not found
    if not record:
        log_security_incident(clean_code, "ERR_02")
        pause()
        return False

    name, db_clearance, db_class, db_pin_hash = record

    # case: data tempering check
    if card["clearance"] != db_clearance or card["class"] != db_class:
        log_security_incident(clean_code, "ERR_03")
        pause()
        return False

    print(f"\n[SCAN OK] Employee: {name} | Class: {db_class} | Clearance: {db_clearance}")
    entered_pin = getpass.getpass("Enter PIN: ")

    if not verify_pin(db_pin_hash, entered_pin):
        log_security_incident(clean_code, "ERR_04")
        pause()
        return False

    print(f"\n[GRANTED] Access granted. Welcome, {name}.")
    pause()
    return True

if __name__ == "__main__":
    while True:
        clear_screen()    
        print("=== SCP FOUNDATION ACCESS CONTROL TERMINAL ===")
        scanned_input = input("Tap the card (enter 11-digit code, or 'q' to exit): ").strip()

        if scanned_input.lower() == 'q':
            print("[INFO] Shutting down terminal...")
            break
        
        authenticate_user(scanned_input)
