from database.connection import SessionLocal, engine, Base
from fastapi import HTTPException
from database.define_tables import APIKey

from .keygen import generate_key

Base.metadata.create_all(bind=engine)

def issue_key(client_name: str, scopes: list[str]):
    """
    Issues a new API key for the given client name and scopes:
    The raw key is printed to the console and will not be stored in the database.
    The hashed key is stored in the database for future validation.
    """
    db = SessionLocal()
    raw_key, key_hash = generate_key()

    record = APIKey(client_name=client_name, key_hash=key_hash, scopes=scopes)

    db.add(record)
    try:
        db.commit()
    except Exception:
        print("Failed to save the key in the database. Rolling back the transaction.")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save metadata in the database")

    db.close()

    return raw_key

if __name__ == "__main__":
    key = issue_key("github-actions", scopes=["predictions:create", "predictions:read", "models:create","models:read"])
    print(key)