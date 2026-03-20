from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_db
from app.models import Benutzer
from app.auth import hash_password, verify_password, create_access_token
from app.Schemas import RegisterIn, UserOut, TokenOut  # falls du die so hast

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    existing = db.scalar(select(Benutzer).where(Benutzer.email == data.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = Benutzer(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        rolle="Anwender",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm liefert username + password
    user = db.scalar(select(Benutzer).where(Benutzer.email == form.username))
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(sub=str(user.id))
    return TokenOut(access_token=token, token_type="bearer")