# BACS - Barcode-centered ACS (Access Control System)
---
BACS is a Barcode-centered Access Control System written on Python, it uses hierarchy-based barcodes as an identification, implying its use with various modules such as scanners and electronic locks. Database management and interaction are made with `sqlite3` and `pandas`, and the authentication functions use `hashlib`.

## Project Topic
---
The initial project idea partially came from a game, based on SCP Foundation, a fictional secret organization and collaborative online fiction project. The game itself is a horror with clearance levels and electronic keys mechanics. 

## Installing and Virtual Environment
---
### Windows

#### Requirements
- Windows 10 or newer
- Python 3.10 or newer
- Git

Install check:

```powershell
python --version
git --version
```

#### Installing

1. Download the project
   
```powershell
git clone https://github.com/justalwaysded/scp_access_control.git
cd scp_access_control
```

2.  Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks execution, allow script execution for current user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser Remotesigned
```

3. After the activation install the requirements:

```powershell
pip install -r requirements.txt
```

### Linux

#### Requirements
- Python 3.10 or newer
- Git

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip git
```

#### Install

1. Clone the repo:

```bash
git clone https://github.com/justalwaysded/scp_access_control.git
cd scp_access_control
```

2. Activate and install the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install the requirements:

```bash
pip install -r requirements.txt
```

## Database Initialization
---
To initialize the database `security.db`, run the following file:

For Windows:

```powershell
python -m init_db
```

For Linux:

```bash
python3 -m init_db
```

## Admin Utility
---
To run the admin utility, run the following:

For Windows:

```powershell
python -m src.admin
```

For Linux:

```bash
python3 -m src.admin
```

## Auth Terminal
---

To run the Authentication Terminal, run the following:

For Windows:

```powershell
python -m src.auth_system
```

For Linux:

```bash
python3 -m src.auth_system
```

## Barcode format
---
At example we'll have the following barcode: `15420412943`. We split it into categories:
`SS DD EEEEE C L`, where: 
`SS` - Site number;
`DD` - Department number;
`EEEEE` - Employee ID;
`C` - Access Class;
`L` - Clearance Level;

## Events
---
There are events, listed in `config/events.json`:
### "SECURITY_INCIDENT"
- "ERR_01": "INVALID_BARCODE_FORMAT"
- "ERR_02": "UNKNOWN_EMPLOYEE_ID"
- "ERR_03": "CARD_DATA_MISMATCHED_TAMPERING"
- "ERR_04": "INVALID_PIN_ATTEMPT"

### "ACCESS_DENIED"
- "ERR_05": "LOCKED_LOGIN"

### "ACCESS_GRANTED"
- "LOGIN_GRANTED"

### "DATABASE_ERROR"
- "DB_UNAVAILABLE": "DATABASE IS UNAVAILABLE"

## Running tests
---
Install developer requirements and run `pytest`:

For Windows:

```powershell
pip install -r requirements-dev.txt
py -m pytest -q
```

For Linux:
```bash
pip install -r requirements-dev.txt
python3 -m pytest -q
```