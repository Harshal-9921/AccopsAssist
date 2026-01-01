import os
from fastapi import Header, HTTPException

ADMIN_SECRET = "admin123"

def verify_admin(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth format")

    token = authorization.replace("Bearer ", "")

    if token != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Unauthorized admin access")
