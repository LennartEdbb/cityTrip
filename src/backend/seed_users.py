# seed_users.py
from sqlalchemy import select
from app.db import SessionLocal
from app.models import Benutzer

# Test-Logins definieren
USERS = [
    {"name": "Test User", "email": "user@example.com", "password_hash": "TEMP", "rolle": "Anwender"},
    {"name": "Test Anbieter", "email": "Anbieter123@example.com", "password_hash": "TEMP", "rolle": "Anbieter"},
]

#  hash_password Funktion aus app/auth.py
from app.auth import hash_password

def upsert_user(db, name, email, password, rolle):
    u = db.scalar(select(Benutzer).where(Benutzer.email == email))
    if u:
        # Rolle ggf. aktualisieren, Passwort optional aktualisieren
        u.name = name
        u.rolle = rolle
        if password:
            u.password_hash = hash_password(password)
        return u

    u = Benutzer(
        name=name,
        email=email,
        password_hash=hash_password(password),
        rolle=rolle,
    )
    db.add(u)
    return u

def main():
    db = SessionLocal()
    try:
        # Passwörter hier direkt setzen (Testzweck)
        upsert_user(db, "Test User", "user@example.com", "string", "Anwender")
        upsert_user(db, "Test Anbieter", "Anbieter123@example.com", "string", "Anbieter")
        db.commit()
        print("✅ seed_users OK (user + anbieter vorhanden)")
    finally:
        db.close()

if __name__ == "__main__":
    main()