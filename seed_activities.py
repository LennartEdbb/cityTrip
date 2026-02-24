import os
import urllib.parse
import requests

BASE_URL = "http://127.0.0.1:8000"
PROVIDER_EMAIL = "Anbieter123@example.com"
PROVIDER_PASSWORD = "string"

def login() -> str:
    r = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": PROVIDER_EMAIL, "password": PROVIDER_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    if r.status_code != 200:
        print("LOGIN FAIL:", r.status_code, r.text)
        raise SystemExit(1)
    return r.json()["access_token"]

def create_activity(token: str, payload: dict) -> None:
    r = requests.post(
        f"{BASE_URL}/activities",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    if r.status_code >= 400:
        print("\n❌ ERROR", r.status_code, r.text)
        return
    data = r.json()
    print(f"✅ created id={data['id']} | {data['bezeichnung']}")

def signature(payload: dict) -> str:
    title = (payload.get("bezeichnung") or "").strip()
    loc_name = ((payload.get("location") or {}).get("bezeichnung") or "").strip()
    zm = payload.get("zeitmodell") or {}
    ztyp = zm.get("typ")

    if ztyp == "einmalig":
        when = f"{zm.get('datum')}|{zm.get('von')}"
    elif ztyp == "serie":
        when = f"{zm.get('gueltig_von')}|{zm.get('von')}|{','.join(zm.get('wochentage', []))}"
    else:
        # durchgaengig: typ reicht in der Regel
        when = "durchgaengig"

    return f"{title}||{loc_name}||{ztyp}||{when}"

def exists_by_signature(token: str, payload: dict) -> bool:
    q = urllib.parse.quote(payload["bezeichnung"])
    r = requests.get(
        f"{BASE_URL}/activities?q={q}&aktiv=true",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    r.raise_for_status()

    sig = signature(payload)
    for a in r.json():
        resp_payload = {
            "bezeichnung": a.get("bezeichnung"),
            "location": {"bezeichnung": (a.get("location") or {}).get("bezeichnung")},
            "zeitmodell": a.get("zeitmodell") or {},
        }
        if signature(resp_payload) == sig:
            return True
    return False

def main():
    if not PROVIDER_PASSWORD:
        print("❌ Bitte PROVIDER_PASSWORD als Environment Variable setzen.")
        print('   PowerShell: $env:PROVIDER_PASSWORD="DEINPASSWORT"')
        raise SystemExit(1)

    token = login()
    print("Logged in, token OK")

    # --------- 10 Durchgängige Orte ---------
    places = [
        ("Café Sonnenschein", "Essen_und_Trinken", "Hauptstraße", "12", "Bad Oeynhausen", "32545", 52.207, 8.805, "Konsum",
         [("Montag","09:00:00","18:00:00"),("Dienstag","09:00:00","18:00:00"),("Mittwoch","09:00:00","18:00:00"),("Donnerstag","09:00:00","18:00:00"),("Freitag","09:00:00","18:00:00"),("Samstag","10:00:00","16:00:00")],
         "Sonntag geschlossen"),
        ("Kino Central", "Kultur", "Bahnhofstraße", "20", "Bad Oeynhausen", "32545", 52.204, 8.807, "Gebühr",
         [("Montag","15:00:00","23:00:00"),("Dienstag","15:00:00","23:00:00"),("Mittwoch","15:00:00","23:00:00"),("Donnerstag","15:00:00","23:00:00"),("Freitag","15:00:00","23:59:00"),("Samstag","12:00:00","23:59:00"),("Sonntag","12:00:00","23:00:00")],
         "Tickets im Hinweis"),
        ("Arcade Arena", "Nachtleben", "Industriestraße", "7", "Löhne", "32584", 52.190, 8.700, "Gebühr",
         [("Freitag","18:00:00","23:59:00"),("Samstag","14:00:00","23:59:00"),("Sonntag","14:00:00","20:00:00")],
         "Eintritt oder Tagespass"),
        ("Stadtbibliothek", "Bildung", "Bücherweg", "3", "Bad Oeynhausen", "32545", 52.206, 8.803, "Kostenlos",
         [("Dienstag","10:00:00","18:00:00"),("Mittwoch","10:00:00","18:00:00"),("Donnerstag","10:00:00","18:00:00"),("Freitag","10:00:00","18:00:00"),("Samstag","10:00:00","14:00:00")],
         "Ausweis vor Ort"),
        ("Bowling Center Strike", "Nachtleben", "Sportallee", "8", "Herford", "32052", 52.115, 8.675, "Gebühr",
         [("Montag","16:00:00","22:00:00"),("Dienstag","16:00:00","22:00:00"),("Mittwoch","16:00:00","22:00:00"),("Donnerstag","16:00:00","22:00:00"),("Freitag","16:00:00","23:59:00"),("Samstag","12:00:00","23:59:00"),("Sonntag","12:00:00","20:00:00")],
         "Reservierung empfohlen"),
        ("Schwimmbad AquaFun", "Familie", "Wasserstraße", "1", "Bad Oeynhausen", "32545", 52.209, 8.810, "Gebühr",
         [("Montag","10:00:00","20:00:00"),("Dienstag","10:00:00","20:00:00"),("Mittwoch","10:00:00","20:00:00"),("Donnerstag","10:00:00","20:00:00"),("Freitag","10:00:00","20:00:00"),("Samstag","10:00:00","18:00:00"),("Sonntag","10:00:00","18:00:00")],
         "Tageskarte oder Monatskarte"),
        ("Kletterhalle Peak", "Natur", "Kletterweg", "4", "Herford", "32052", 52.120, 8.680, "Gebühr",
         [("Montag","14:00:00","22:00:00"),("Dienstag","14:00:00","22:00:00"),("Mittwoch","14:00:00","22:00:00"),("Donnerstag","14:00:00","22:00:00"),("Freitag","14:00:00","22:00:00"),("Samstag","10:00:00","20:00:00"),("Sonntag","10:00:00","18:00:00")],
         "Leihschuhe vor Ort"),
        ("Eisdiele Gelato", "Essen_und_Trinken", "Marktstraße", "9", "Löhne", "32584", 52.194, 8.706, "Konsum",
         [("Mittwoch","12:00:00","20:00:00"),("Donnerstag","12:00:00","20:00:00"),("Freitag","12:00:00","21:00:00"),("Samstag","12:00:00","21:00:00"),("Sonntag","12:00:00","20:00:00")],
         "Saisonbetrieb"),
        ("Escape Room MissionX", "Kultur", "Rätselstraße", "6", "Herford", "32052", 52.118, 8.671, "Gebühr",
         [("Donnerstag","16:00:00","22:00:00"),("Freitag","16:00:00","23:00:00"),("Samstag","12:00:00","23:00:00"),("Sonntag","12:00:00","20:00:00")],
         "Online buchen im Hinweis"),
    ]

    through = []
    for (name, cat, street, hn, city, plz, lat, lon, kosten, slots, hint) in places:
        through.append({
            "bezeichnung": name,
            "beschreibung": f"{name} – Beispielort",
            "bemerkung": None,
            "kategorien": [cat],
            "barrierefrei": True,
            "aktiv": True,
            "location": {
                "bezeichnung": name,
                "beschreibung": None,
                "bemerkung": None,
                "anschrift": {"strasse": street, "hausnummer": hn, "ort": city, "plz": plz, "land": "Deutschland"},
                "lat": lat,
                "lon": lon
            },
            "zeitmodell": {
                "typ": "durchgaengig",
                "gueltig_von": None,
                "gueltig_bis": None,
                "slots": [{"wochentag": d, "uhrzeit_von": v, "uhrzeit_bis": b} for (d, v, b) in slots],
                "hinweis": hint
            },
            "eintritt": {
                "kostenmodell": kosten,
                "hinweis": hint,
                "tarife": (
                    [
                        {"bezeichnung":"Tageskarte","dauer_typ":"Tag","dauer_wert":1,"preis":10.0,"kriterium":"Standard","waehrung":"Euro"},
                        {"bezeichnung":"Monatskarte","dauer_typ":"Monat","dauer_wert":1,"preis":35.0,"kriterium":"Standard","waehrung":"Euro"}
                    ] if name in ("Schwimmbad AquaFun",) else
                    [
                        {"bezeichnung":"Standard","dauer_typ":"Tag","dauer_wert":1,"preis":12.0,"kriterium":"Eintritt","waehrung":"Euro"}
                    ] if kosten == "Gebühr" and name not in ("Schwimmbad AquaFun",) else
                    []
                )
            }
        })

    # --------- 10 Serien (Kurse) ---------
    series = [
        ("VHS Englisch B1", "Bildung", "Schulstraße", "5", "Bad Oeynhausen", "32545", 52.206, 8.806,
         "2026-03-02", "2026-06-15", ["Montag"], "18:00:00", "19:30:00", "Gebühr", 89.0, "Kursgebühr"),
        ("Yoga Kurs", "Natur", "Sportallee", "2", "Herford", "32052", 52.116, 8.676,
         "2026-01-08", "2026-04-30", ["Donnerstag"], "18:30:00", "19:30:00", "Gebühr", 75.0, "Standard"),
        ("Kochkurs Italienisch", "Essen_und_Trinken", "Küchenweg", "1", "Bad Oeynhausen", "32545", 52.208, 8.804,
         "2026-02-04", "2026-05-27", ["Mittwoch"], "17:30:00", "19:30:00", "Gebühr", 120.0, "inkl. Zutaten"),
        ("Python Grundlagen", "Bildung", "IT-Straße", "9", "Löhne", "32584", 52.192, 8.708,
         "2026-03-10", "2026-06-30", ["Dienstag"], "18:00:00", "20:00:00", "Gebühr", 99.0, "Standard"),
        ("Tanzkurs Anfänger", "Kultur", "Tanzallee", "4", "Herford", "32052", 52.117, 8.673,
         "2026-04-01", "2026-07-31", ["Freitag"], "19:00:00", "20:30:00", "Gebühr", 110.0, "Paar/Single"),
        ("Fotografie Walk", "Natur", "Parkweg", "10", "Bad Oeynhausen", "32545", 52.205, 8.808,
         "2026-05-01", "2026-09-30", ["Samstag"], "10:00:00", "12:00:00", "Spende", 0.0, "Spende willkommen"),
        ("Sprachcafé Deutsch", "Bildung", "Bücherweg", "3", "Bad Oeynhausen", "32545", 52.206, 8.803,
         "2026-01-12", "2026-12-15", ["Dienstag"], "16:00:00", "17:30:00", "Kostenlos", 0.0, "Eintritt frei"),
        ("Kinder Malen", "Familie", "Kunststraße", "7", "Löhne", "32584", 52.193, 8.705,
         "2026-02-01", "2026-06-01", ["Sonntag"], "11:00:00", "12:30:00", "Gebühr", 49.0, "Material inkl."),
        ("Fitness Bootcamp", "Natur", "Sportpark", "1", "Herford", "32052", 52.114, 8.678,
         "2026-03-01", "2026-08-31", ["Mittwoch"], "18:00:00", "19:00:00", "Gebühr", 59.0, "Standard"),
        ("Git & GitHub Workshop", "Bildung", "IT-Straße", "9", "Löhne", "32584", 52.192, 8.708,
         "2026-09-01", "2026-11-30", ["Montag"], "18:00:00", "19:30:00", "Gebühr", 69.0, "Standard"),
    ]

    serie_payloads = []
    for (name, cat, street, hn, city, plz, lat, lon,
         von_d, bis_d, wdays, von_t, bis_t, kosten, preis, krit) in series:
        serie_payloads.append({
            "bezeichnung": name,
            "beschreibung": f"{name} – Beispielkurs",
            "bemerkung": None,
            "kategorien": [cat],
            "barrierefrei": False,
            "aktiv": True,
            "location": {
                "bezeichnung": name + " Ort",
                "beschreibung": None,
                "bemerkung": None,
                "anschrift": {"strasse": street, "hausnummer": hn, "ort": city, "plz": plz, "land": "Deutschland"},
                "lat": lat,
                "lon": lon
            },
            "zeitmodell": {
                "typ": "serie",
                "gueltig_von": von_d,
                "gueltig_bis": bis_d,
                "wochentage": wdays,
                "von": von_t,
                "bis": bis_t,
                "intervall_wochen": 1,
                "hinweis": "Anmeldung/Infos im Hinweis"
            },
            "eintritt": {
                "kostenmodell": kosten,
                "hinweis": "Infos/Anmeldung: https://example.com",
                "tarife": ([] if kosten in ("Kostenlos", "Spende") else [
                    {"bezeichnung": krit, "dauer_typ": "Monat", "dauer_wert": 1, "preis": float(preis), "kriterium": "Standard", "waehrung": "Euro"}
                ])
            }
        })

    # --------- 10 Einmalige Events übers Jahr ---------
    events = [
        ("Neujahrsmarkt", "Kultur", "2026-01-10", "11:00:00", "16:00:00", "Kostenlos"),
        ("Winter-Filmnacht", "Kultur", "2026-02-07", "19:30:00", "22:30:00", "Gebühr"),
        ("Frühlingsfestival", "Musik", "2026-03-21", "14:00:00", "20:00:00", "Kostenlos"),
        ("Ostermarkt", "Familie", "2026-04-04", "10:00:00", "15:00:00", "Kostenlos"),
        ("Open-Air Konzert", "Musik", "2026-06-13", "18:00:00", "22:00:00", "Gebühr"),
        ("Sommer Open-Air Kino", "Kultur", "2026-07-18", "21:00:00", "23:30:00", "Gebühr"),
        ("Street Food Night", "Essen_und_Trinken", "2026-08-22", "16:00:00", "22:00:00", "Konsum"),
        ("Kulturabend Innenstadt", "Kultur", "2026-09-12", "17:00:00", "21:00:00", "Kostenlos"),
        ("Halloween Party", "Nachtleben", "2026-10-31", "20:00:00", "23:59:00", "Gebühr"),
        ("Weihnachtsmarkt", "Familie", "2026-12-05", "15:00:00", "21:00:00", "Kostenlos"),
    ]

    event_payloads = []
    for i, (name, cat, d, v, b, kosten) in enumerate(events, start=1):
        event_payloads.append({
            "bezeichnung": name,
            "beschreibung": f"{name} – Beispiel-Event",
            "bemerkung": None,
            "kategorien": [cat],
            "barrierefrei": True,
            "aktiv": True,
            "location": {
                "bezeichnung": f"{name} Location",
                "beschreibung": None,
                "bemerkung": None,
                "anschrift": {"strasse": "Eventplatz", "hausnummer": str(i), "ort": "Bad Oeynhausen", "plz": "32545", "land": "Deutschland"},
                "lat": 52.205 + (i * 0.001),
                "lon": 8.805 + (i * 0.001)
            },
            "zeitmodell": {
                "typ": "einmalig",
                "datum": d,
                "von": v,
                "bis": b,
                "hinweis": "Details im Hinweis"
            },
            "eintritt": {
                "kostenmodell": kosten,
                "hinweis": ("Ticket nötig: https://example.com" if kosten == "Gebühr" else "Infos: https://example.com"),
                "tarife": ([] if kosten in ("Kostenlos", "Konsum") else [
                    {"bezeichnung": "Standard", "dauer_typ": "Tag", "dauer_wert": 1, "preis": 20.0, "kriterium": "Erwachsene", "waehrung": "Euro"}
                ])
            }
        })

    activities = event_payloads + serie_payloads + through

    for a in activities:
        if exists_by_signature(token, a):
            print(f"⏭️  skip (exists): {a['bezeichnung']}")
            continue
        create_activity(token, a)


if __name__ == "__main__":
    main()