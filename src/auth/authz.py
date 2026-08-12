#authorization
from database.define_tables import APIKey
from fastapi import HTTPException, Depends, status
from .authn import get_api_key

def require_scope(required_scope: str):
    def dependency(api_key: APIKey = Depends(get_api_key)) -> APIKey:
        if required_scope not in (api_key.scopes or []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scope: {required_scope}",
            )
        return api_key
    return dependency


