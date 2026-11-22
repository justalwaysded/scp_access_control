import hashlib
import hmac
import os

PBKDF2_ITERATIONS = 100_000

def verify_pin(stored_password: str, provided_pin: str) -> bool:
    try:
        salt, stored_hash = stored_password.split('$')
    except ValueError:
        return False

    new_hash = hashlib.pbkdf2_hmac(
        'sha256',
        provided_pin.encode('utf-8'),
        salt.encode('utf-8'),
        PBKDF2_ITERATIONS
    ).hex()

    # Compare hashes using a function designed to be resistant to timing analysis.
    return hmac.compare_digest(stored_hash, new_hash)

def gen_salt_hash(pin: str) -> str:
    salt = os.urandom(16).hex()

    hash_obj = hashlib.pbkdf2_hmac('sha256', pin.encode(), salt.encode(), PBKDF2_ITERATIONS)
    return f"{salt}${hash_obj.hex()}"
