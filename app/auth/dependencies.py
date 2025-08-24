from typing import Optional
from fastapi import Depends, HTTPException, Request
from jose import JWTError
from auth.jwt_auth import verify_jwt_token

def get_bearer_token(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        return auth.split(" ")[1]
    return None

def verify_token_required(token: str = Depends(get_bearer_token)):
    """Required token verification - raises exception if no token or invalid"""
    try:
        return verify_jwt_token(token, required=True)
    except JWTError as e:
        #pass  
        raise HTTPException(status_code=401, detail=str(e))

def get_context(user=Depends(verify_token_required)):
    """Context that allows both authenticated and non-authenticated requests"""
    return {"user": user}