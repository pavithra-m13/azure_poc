import requests
from jose import jwt, JWTError
from config.settings import JWKS_URL, AUDIENCE, TENANT_ID

# Fetch JWKS
JWKS = requests.get(JWKS_URL).json()

def verify_jwt_token(token: str, required: bool = False):
    """Verify JWT token and return payload or None/raise exception"""
    if token is None:
        if required:
            raise JWTError("Authentication required")
        return None

    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        key = next((k for k in JWKS["keys"] if k["kid"] == kid), None)
        if not key:
            if required:
                raise JWTError("Invalid signing key")
            return None

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=[
                f"https://login.microsoftonline.com/{TENANT_ID}/v2.0",
                f"https://sts.windows.net/{TENANT_ID}/"
            ]
        )
        return payload
    except JWTError as e:
        if required:
            raise JWTError(f"Invalid token: {str(e)}")
        return None