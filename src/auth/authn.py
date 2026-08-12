#authentication
import hashlib
from datetime import datetime, timezone
from fastapi import Security, HTTPException, status, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database.define_tables import APIKey
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(
    key: str = Security(api_key_header),
    db: Session = Depends(get_db),
) -> APIKey:
    if key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    key_hash = hashlib.sha256(key.encode()).hexdigest()
    record = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()

    if record is None or record.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key",
        )

    record.last_used_at = datetime.now(timezone.utc)
    db.commit()

    return record