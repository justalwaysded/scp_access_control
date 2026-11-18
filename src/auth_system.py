import hashlib
import hmac
import sqlite3
import os
import getpass
import json
import sys

from datetime import datetime, timedelta

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.parser import parse_barcode
from src.admin import pause
from src.admin import clear_screen



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'security.db')

LOG_PATH = os.path.join(BASE_DIR, 'data', 'auth.log')

EVENTS_PATH = os.path.join(BASE_DIR, 'config', 'events.json')

with open(EVENTS_PATH, "r", encoding="utf-8") as f:
    EVENT_CATALOG = json.load(f)

def log_event(event_id: str, card_id: str, details: str = "", emp_id: str | None = None):
    os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
    dt_now = datetime.now().strftime("%Y-%m-%d")
    dynamic_log_path = os.path.join(BASE_DIR, 'data', f'auth_{dt_now}.log')

    event_data = EVENT_CATALOG.get(event_id)
    if event_data is None:
        raise ValueError(f"Unknown event ID: {event_id}")
    log_record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event_id": event_id,
        "event_type": event_data["event_type"],
        "code": event_data.get("code"),
        "severity": event_data.get("severity"),
        "card_id": card_id,
        "emp_id": emp_id,
    }

    if details:
        log_record["details"] = details

    with open(dynamic_log_path, "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_record, ensure_ascii=False) + "\n")
    
    if event_id != "LOGIN_GRANTED":
        print(event_data["message"])

def verify_pin(stored_password: str, provided_pin: str) -> bool:
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

    # Compare hashes using a function designed to be resistant to timing analysis.
    return hmac.compare_digest(stored_hash, new_hash)

def authenticate_user(raw_barcode: str) -> bool:
    clean_code = raw_barcode.strip()

    try:
        card = parse_barcode(clean_code)
    except ValueError as e:
        log_event("ERR_01", clean_code, details=str(e))
        pause()
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT 
        name, 
        clearance_level, 
        access_class, 
        pin_hash, 
        locked_until,
        failed_attempts,
        window_started_at 
    FROM 
        employees
    WHERE 
        site = ? 
    AND 
        department = ? 
    AND 
        emp_id = ?
    ''', (card["site"], card["department"], card["emp_id"]))

    record = cursor.fetchone()
    conn.close()

    # case

    # case: employee not found
    if not record:
        log_event("ERR_02", clean_code)
        pause()
        return False

    name, db_clearance, db_class, db_pin_hash, locked_until, failed_attempts, window_started_at = record

    # case: data tempering check
    if card["clearance"] != db_clearance or card["class"] != db_class:
        log_event("ERR_03", clean_code, emp_id=card["emp_id"])
        pause()
        return False

    # Decline only if the previously set blocking period has not yet expired.
    if locked_until is not None:
        unlock_time = datetime.fromisoformat(locked_until)
        if datetime.now() < unlock_time:    
            log_event("ERR_05", clean_code, emp_id=card["emp_id"])
            pause()
            return False

    print(f"\n[SCAN OK] Employee: {name} | Class: {db_class} | Clearance: {db_clearance}")
    while True:
        entered_pin = getpass.getpass("Enter PIN: ")

        if verify_pin(db_pin_hash, entered_pin):
            break
        else:
            now = datetime.now()

            # If more than 10 minutes have passed since the first error, begin a new counting window.
            if window_started_at is None or now - datetime.fromisoformat(window_started_at) > timedelta(minutes=10):
                failed_attempts = 0
                window_started_at = now.isoformat()
            failed_attempts += 1

            if failed_attempts >= 5:
                locked_until = (now + timedelta(minutes=15)).isoformat()

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
            UPDATE employees
            SET failed_attempts = ?, window_started_at = ?, locked_until = ?
            WHERE site = ? AND department = ? AND emp_id = ?
            ''', (failed_attempts, window_started_at, locked_until, card["site"], card["department"], card["emp_id"]))
            conn.commit()
            conn.close()
            
            log_event("ERR_04", clean_code, emp_id=card["emp_id"])
            
            if failed_attempts >= 5:
                log_event("ERR_05", clean_code, emp_id=card["emp_id"])
                pause()
                return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE employees
    SET failed_attempts = 0, window_started_at = NULL, locked_until = NULL
    WHERE site = ? AND department = ? AND emp_id = ?
    ''', (card["site"], card["department"], card["emp_id"]))
    conn.commit()
    conn.close()

    log_event("LOGIN_GRANTED", clean_code, emp_id=card["emp_id"])
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
