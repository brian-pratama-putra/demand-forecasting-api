import hashlib
import secrets
import string

def generate_checksum(p_payload: str) -> str:
    return hashlib.sha256(p_payload.encode()).hexdigest()

def generate_random(p_length: int) -> str:
    v_characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(v_characters) for _ in range(p_length))
