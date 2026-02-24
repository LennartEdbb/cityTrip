from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_db
from app.models import Benutzer

# Passwort hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


SECRET_KEY = "CHANGE_ME_SUPER_SECRET_123456789"
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 60 * 24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(sub: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    payload = {"sub": sub, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
) -> Benutzer:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.scalar(select(Benutzer).where(Benutzer.id == int(sub)))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_roles(*roles: str):
    def _dep(user: Benutzer = Depends(get_current_user)) -> Benutzer:
        if user.rolle not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return _dep