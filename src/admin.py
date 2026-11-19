import os   
import sqlite3
import sys
import pandas as pd
import getpass

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from init_db import gen_salt_hash
from init_db import init_database

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'security.db')
LOG_PATH = os.path.join(DATA_DIR, 'auth.log')

# class mapping to transform from a letter to a digit 

def build_barcode(site, department, emp_id, access_class, clearance) -> str:
    reversed_class_mapping = {'A': '1', 'B': '2', 'C': '3', 'D': '4', 'E': '5'}
    employee_class = reversed_class_mapping.get(access_class, '5')
    ready_barcode = f"{site}{department}{emp_id}{employee_class}{clearance}"
    return ready_barcode

def clear_screen():
    # screen clear for windows ('cls') and linux/macOS ('clear')
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("\nPress RETURN to continue...")

def register_employee():
    clear_screen()
    print("\n--- NEW EMPLOYEE REGISTRATION ---\n")

    while True:    
        site = input("Site number (example, 15): ").strip()
        
        if site.isdigit() and len(site) == 2:
            break
        print("[ERROR] Site number must contain exactly two digits.")

    while True:    
        department = input("The number of the department (example, 42): ").strip()
        if department.isdigit() and len(department) == 2:
            break
        print("[ERROR] Department number must contain exactly two digits.")

    while True:
        emp_id = input("Employee's ID (example, 04129): ").strip()
        if emp_id.isdigit() and len(emp_id) == 5:
            # doppelganger check
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 1 FROM employees 
                WHERE site = ? AND department = ? AND emp_id = ?
            ''', (site, department, emp_id))
            exists = cursor.fetchone()
            conn.close()

            if exists:
                print(f"[ERROR] Employee with Site {site}, Dept {department} and ID {emp_id} already exists!")
                continue
            break
        print("[ERROR] Employee ID must contain exactly five digits.")

    name = input("Employee's name: ").strip()
    
    while True:
        access_class = input("Access class (A-E): ").strip().upper()
        
        if access_class.isalpha() and len(access_class) == 1 and 'A' <= access_class <= 'E':
            break
        print("[ERROR] Access class must contain a single letter from A to E.")


    while True:
        clearance = input("Clearance level (1-5): ").strip()
        if clearance.isdigit() and 1 <= int(clearance) <= 5:
            break
        print("[ERROR] Clearance level must contain a digit from 1 to 5.")

    while True:
        pin = getpass.getpass("New PIN-Code: ").strip()
        confirm_pin = getpass.getpass("Confirm PIN-Code: ").strip()

        if not pin:
            print("PIN-Code can't be empty. Try again.\n")
            continue

        if pin == confirm_pin:
            print("PIN-Code is set up successfully.")
            break
        else:
            print("PIN-Code doesn't match. Try again.")

    pin_hash = gen_salt_hash(pin)
    barcode = build_barcode(site, department, emp_id, access_class, clearance)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor() 
    
    cursor.execute('''
        INSERT INTO employees (site, department, emp_id, name, clearance_level, access_class, pin_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (site, department, emp_id, name, int(clearance), access_class, pin_hash))
    conn.commit()
    conn.close()

    print(f"\n[OK] Employee registered successfully.")
    print(f"[CARD] Generated barcode: {barcode}")

    pause()

def list_employee():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT site, department, emp_id, name, clearance_level, access_class FROM employees", conn)
    conn.close()

    if df.empty:
        print("DB is empty.")
        pause()
        return

    clear_screen() 
    df['barcode'] = df.apply(
        lambda row: build_barcode(
            row['site'], row['department'], row['emp_id'], row['access_class'], row['clearance_level']
        ),
        axis=1,
    )
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', 1000)

    print("\n--- EMPLOYEE REGISTRY ---\n")
    print(df.to_string(index=False))

    pause()

def add_example_employees():
    # Prepare or update the schema before adding test employees.
    init_database()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    employees_data = [
        ('15', '42', '04129', 'Dr. Bright', 4, 'C', gen_salt_hash('1234')),
        ('19', '11', '00753', 'Agent S.', 3, 'B', gen_salt_hash('5555')),
        ('15', '42', '04295', 'Infr. Eng. Alex', 2, 'C', gen_salt_hash('9876'))
    ]

    cursor.executemany('''
        INSERT OR REPLACE INTO employees
        (site, department, emp_id, name, clearance_level, access_class, pin_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', employees_data)
    
    conn.commit()
    conn.close()
    print("[SUCCESS] Example employees added.")
    pause()

def clear_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM employees')
    conn.commit()
    conn.close()
    print("[INFO] Employee registry cleared.")
    pause()

def main_menu():
    while True:
        clear_screen()
        print('''
        === SCP FOUNDATION SECURITY CLI ===
        1. List Employees
        2. Register Employees
        3. Exit
        4. (dev) add example employees
        5. (dev) clear database
        6. (dev) initialize database
        ''')

        choice = input("\nChoose action (1-6): ").strip()

        if choice == '1':
            list_employee()
        elif choice == '2':
            register_employee()
        elif choice == '3':
            print("[INFO] Exiting CLI Utility...")
            break
        elif choice == '4':
            add_example_employees()
        elif choice == '5':
            clear_database()
        elif choice == '6':
            init_database()
            pause()
        else:
            print("[ERROR] Invalid choice. Enter a digit from 1 to 6.")
            pause()
            


if __name__ == "__main__":
    main_menu()