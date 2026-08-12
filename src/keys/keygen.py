import secrets
import hashlib


def generate_key(prefix: str = "sk_live") -> tuple[str, str]:

    """
    Returns (raw_key, key_hash).
    raw_key  -> shown to the client ONCE, never stored.
    key_hash -> stored in the database.
    """

    raw_key = f"{prefix}_{secrets.token_urlsafe(32)}" 
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    return raw_key, key_hash