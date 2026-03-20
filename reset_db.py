# reset_db.py
from sqlalchemy import text
from app.db import SessionLocal
from app import models


def main():
    db = SessionLocal()
    try:
        # Löschen in sinnvoller Reihenfolge (FK-Abhängigkeiten)
        delete_models = [
            models.Erinnerung,
            models.GeplanteAktivitaet,
            models.Favorit,
            models.Bewertung,
            models.Benutzer,

            models.OeffnungszeitSlot,
            models.SerieWochentag,
            models.Durchgaengig,
            models.Serie,
            models.Einmalig,
            models.Zeitmodell,

            models.Tarif,
            models.Eintritt,

            models.AktivitaetKategorie,
            models.Aktivitaet,

            models.Location,
            models.Anschrift,
        ]

        for m in delete_models:
            db.query(m).delete()  # OK für SQLite/dev

        db.commit()
        print("✅ Reset OK: Alle Daten außer Benutzer wurden gelöscht.")

        # Optional: (falls sqlite_sequence existiert) IDs zurücksetzen
        try:
            db.execute(text("DELETE FROM sqlite_sequence"))
            db.commit()
        except Exception:
            pass

    finally:
        db.close()


if __name__ == "__main__":
    main()