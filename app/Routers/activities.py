from __future__ import annotations

from datetime import date, time
from math import radians, sin, cos, sqrt, atan2
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, or_

from app.db import get_db
from app.auth import require_roles
from app.models import (
    Aktivitaet, Location, Anschrift,
    Eintritt, Tarif,
    Zeitmodell, Einmalig, Serie, Durchgaengig,
    AktivitaetKategorie, SerieWochentag, OeffnungszeitSlot,
    KategorieEnum, WochentagEnum
)
from app.Schemas import ActivityCreateIn, ActivityOut

router = APIRouter()


# ---------- helpers ----------
def haversine_km(lat1, lon1, lat2, lon2) -> float:
    # Earth radius (km)
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def weekday_value(d: date) -> str:
    # Monday=0 .. Sunday=6
    return [
        WochentagEnum.MONTAG.value,
        WochentagEnum.DIENSTAG.value,
        WochentagEnum.MITTWOCH.value,
        WochentagEnum.DONNERSTAG.value,
        WochentagEnum.FREITAG.value,
        WochentagEnum.SAMSTAG.value,
        WochentagEnum.SONNTAG.value,
    ][d.weekday()]


def point_in_interval(t: time, start: time, end: time) -> bool:
    return start <= t <= end


def matches_datetime(act: Aktivitaet, d: date, t: Optional[time]) -> bool:
    zm = act.zeitmodell
    wd = weekday_value(d)

    if isinstance(zm, Einmalig):
        if zm.datum != d:
            return False
        return True if t is None else point_in_interval(t, zm.von, zm.bis)

    if isinstance(zm, Serie):
        if d < zm.gueltig_von:
            return False
        if zm.gueltig_bis and d > zm.gueltig_bis:
            return False

        days = [x.wochentag for x in zm.wochentage]
        if wd not in days:
            return False

        return True if t is None else point_in_interval(t, zm.von, zm.bis)

    if isinstance(zm, Durchgaengig):
        if zm.gueltig_von and d < zm.gueltig_von:
            return False
        if zm.gueltig_bis and d > zm.gueltig_bis:
            return False

        # if no slots configured -> treat as "always ok" (you can change to False if you prefer)
        if not zm.slots:
            return True

        matching_slots = [s for s in zm.slots if s.wochentag == wd]
        if not matching_slots:
            return False

        if t is None:
            return True

        return any(point_in_interval(t, s.uhrzeit_von, s.uhrzeit_bis) for s in matching_slots)

    return True


def activity_to_out(act: Aktivitaet) -> dict:
    # Kategorien
    cats = [k.kategorie for k in act.kategorien] if act.kategorien else []

    # Zeitmodell -> dict
    zm = act.zeitmodell
    if isinstance(zm, Einmalig):
        zeit_out = {
            "typ": "einmalig",
            "id": zm.id,
            "datum": zm.datum,
            "von": zm.von,
            "bis": zm.bis,
            "hinweis": zm.hinweis,
        }
    elif isinstance(zm, Serie):
        zeit_out = {
            "typ": "serie",
            "id": zm.id,
            "gueltig_von": zm.gueltig_von,
            "gueltig_bis": zm.gueltig_bis,
            "von": zm.von,
            "bis": zm.bis,
            "intervall_wochen": zm.intervall_wochen,
            "wochentage": [x.wochentag for x in zm.wochentage],
            "hinweis": zm.hinweis,
        }
    else:  # Durchgaengig
        zeit_out = {
            "typ": "durchgaengig",
            "id": zm.id,
            "gueltig_von": getattr(zm, "gueltig_von", None),
            "gueltig_bis": getattr(zm, "gueltig_bis", None),
            "slots": [
                {
                    "id": s.id,
                    "wochentag": s.wochentag,
                    "uhrzeit_von": s.uhrzeit_von,
                    "uhrzeit_bis": s.uhrzeit_bis,
                }
                for s in getattr(zm, "slots", []) or []
            ],
            "hinweis": zm.hinweis,
        }

    # Eintritt
    eintritt_out = None
    if act.eintritt:
        eintritt_out = {
            "id": act.eintritt.id,
            "kostenmodell": act.eintritt.kostenmodell,
            "hinweis": act.eintritt.hinweis,
            "tarife": [
                {
                    "id": t.id,
                    "bezeichnung": t.bezeichnung,
                    "dauer_typ": t.dauer_typ,
                    "dauer_wert": t.dauer_wert,
                    "preis": t.preis,
                    "kriterium": t.kriterium,
                    "waehrung": t.waehrung,
                }
                for t in act.eintritt.tarife
            ],
        }

    return {
        "id": act.id,
        "bezeichnung": act.bezeichnung,
        "beschreibung": act.beschreibung,
        "bemerkung": act.bemerkung,
        "barrierefrei": act.barrierefrei,
        "aktiv": act.aktiv,
        "kategorien": cats,
        "location": {
            "id": act.location.id,
            "bezeichnung": act.location.bezeichnung,
            "beschreibung": act.location.beschreibung,
            "bemerkung": act.location.bemerkung,
            "lat": act.location.lat,
            "lon": act.location.lon,
            "anschrift": {
                "id": act.location.anschrift.id,
                "strasse": act.location.anschrift.strasse,
                "hausnummer": act.location.anschrift.hausnummer,
                "ort": act.location.anschrift.ort,
                "plz": act.location.anschrift.plz,
                "land": act.location.anschrift.land,
            },
        },
        "zeitmodell": zeit_out,
        "eintritt": eintritt_out,
    }


# ---------- endpoints ----------
@router.get("", response_model=List[ActivityOut])
def list_activities(
        db: Session = Depends(get_db),
        q: Optional[str] = Query(default=None, description="Textsuche"),
        kategorie: Optional[KategorieEnum] = Query(default=None),
        barrierefrei: Optional[bool] = Query(default=None),
        aktiv: Optional[bool] = Query(default=True),
        lat: Optional[float] = Query(default=None),
        lon: Optional[float] = Query(default=None),
        radius_km: Optional[float] = Query(default=None, ge=0.1, le=200.0),
        datum: Optional[date] = Query(default=None),
        uhrzeit: Optional[time] = Query(default=None),
):
    stmt = (
        select(Aktivitaet)
        .options(
            selectinload(Aktivitaet.location).selectinload(Location.anschrift),
            selectinload(Aktivitaet.kategorien),
            selectinload(Aktivitaet.eintritt).selectinload(Eintritt.tarife),
            selectinload(Aktivitaet.zeitmodell),
        )
    )

    if aktiv is not None:
        stmt = stmt.where(Aktivitaet.aktiv == aktiv)
    if barrierefrei is not None:
        stmt = stmt.where(Aktivitaet.barrierefrei == barrierefrei)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Aktivitaet.bezeichnung.like(like), Aktivitaet.beschreibung.like(like)))

    if kategorie is not None:
        stmt = stmt.join(AktivitaetKategorie, AktivitaetKategorie.aktivitaet_id == Aktivitaet.id) \
            .where(AktivitaetKategorie.kategorie == kategorie.value)

    acts = db.scalars(stmt).all()

    # Datum/Uhrzeit Filter (Python-level für alle Zeittypen)
    if datum is not None:
        acts = [a for a in acts if a.zeitmodell and matches_datetime(a, datum, uhrzeit)]

    # Radius Filter (Python-level)
    if lat is not None and lon is not None and radius_km is not None:
        filtered = []
        for a in acts:
            if a.location.lat is None or a.location.lon is None:
                continue
            dist = haversine_km(lat, lon, a.location.lat, a.location.lon)
            if dist <= radius_km:
                filtered.append(a)
        acts = filtered

    return [activity_to_out(a) for a in acts]


@router.get("/{aktivitaet_id}", response_model=ActivityOut)
def get_activity(aktivitaet_id: int, db: Session = Depends(get_db)):
    stmt = (
        select(Aktivitaet)
        .where(Aktivitaet.id == aktivitaet_id)
        .options(
            selectinload(Aktivitaet.location).selectinload(Location.anschrift),
            selectinload(Aktivitaet.kategorien),
            selectinload(Aktivitaet.eintritt).selectinload(Eintritt.tarife),
            selectinload(Aktivitaet.zeitmodell),
        )
    )
    act = db.scalar(stmt)
    if not act:
        raise HTTPException(status_code=404, detail="Aktivität nicht gefunden")
    return activity_to_out(act)


@router.post("", response_model=ActivityOut)
def create_activity(
        data: ActivityCreateIn,
        db: Session = Depends(get_db),
        user = Depends(require_roles("Anbieter", "Admin")),
):
    # Location auswählen oder neu anlegen
    if (data.location_id is None) == (data.location is None):
        raise HTTPException(status_code=400, detail="Entweder location_id oder location angeben (genau eins).")

    if data.location_id is not None:
        loc = db.scalar(select(Location).where(Location.id == data.location_id).options(selectinload(Location.anschrift)))
        if not loc:
            raise HTTPException(status_code=404, detail="Location nicht gefunden")
    else:
        a = data.location.anschrift
        anschrift = Anschrift(
            strasse=a.strasse,
            hausnummer=a.hausnummer,
            ort=a.ort,
            plz=a.plz,
            land=a.land,
        )
        db.add(anschrift)
        db.flush()

        loc = Location(
            bezeichnung=data.location.bezeichnung,
            beschreibung=data.location.beschreibung,
            bemerkung=data.location.bemerkung,
            anschrift_id=anschrift.id,
            lat=data.location.lat,
            lon=data.location.lon,
        )
        db.add(loc)
        db.flush()

    act = Aktivitaet(
        anbieter_id=user.id,
        bezeichnung=data.bezeichnung,
        beschreibung=data.beschreibung,
        bemerkung=data.bemerkung,
        location_id=loc.id,
        barrierefrei=data.barrierefrei,
        aktiv=data.aktiv,
    )
    db.add(act)
    db.flush()

    # Kategorien
    for cat in data.kategorien:
        db.add(AktivitaetKategorie(aktivitaet_id=act.id, kategorie=cat.value))

    # Eintritt + Tarife
    if data.eintritt is not None:
        ein = Eintritt(
            aktivitaet_id=act.id,
            kostenmodell=data.eintritt.kostenmodell.value,
            hinweis=data.eintritt.hinweis,
        )
        db.add(ein)
        db.flush()

        for t in data.eintritt.tarife:
            db.add(
                Tarif(
                    eintritt_id=ein.id,
                    bezeichnung=t.bezeichnung,
                    dauer_typ=t.dauer_typ.value,
                    dauer_wert=t.dauer_wert,
                    preis=t.preis,
                    kriterium=t.kriterium,
                    waehrung=t.waehrung.value,
                )
            )

    # Zeitmodell (genau eins)
    zm_in = data.zeitmodell
    if zm_in.typ == "einmalig":
        zm = Einmalig(
            aktivitaet_id=act.id,
            hinweis=zm_in.hinweis,
            datum=zm_in.datum,
            von=zm_in.von,
            bis=zm_in.bis,
        )
        db.add(zm)

    elif zm_in.typ == "serie":
        zm = Serie(
            aktivitaet_id=act.id,
            hinweis=zm_in.hinweis,
            gueltig_von=zm_in.gueltig_von,
            gueltig_bis=zm_in.gueltig_bis,
            von=zm_in.von,
            bis=zm_in.bis,
            intervall_wochen=zm_in.intervall_wochen,
        )
        db.add(zm)
        db.flush()

        for wd in zm_in.wochentage:
            db.add(SerieWochentag(serie_id=zm.id, wochentag=wd.value))

    else:  # durchgaengig
        zm = Durchgaengig(
            aktivitaet_id=act.id,
            hinweis=zm_in.hinweis,
            gueltig_von=zm_in.gueltig_von,
            gueltig_bis=zm_in.gueltig_bis,
        )
        db.add(zm)
        db.flush()

        for s in zm_in.slots:
            db.add(
                OeffnungszeitSlot(
                    durchgaengig_id=zm.id,
                    wochentag=s.wochentag.value,
                    uhrzeit_von=s.uhrzeit_von,
                    uhrzeit_bis=s.uhrzeit_bis,
                )
            )

    db.commit()

    # frisch laden für Response
    act2 = db.scalar(
        select(Aktivitaet)
        .where(Aktivitaet.id == act.id)
        .options(
            selectinload(Aktivitaet.location).selectinload(Location.anschrift),
            selectinload(Aktivitaet.kategorien),
            selectinload(Aktivitaet.eintritt).selectinload(Eintritt.tarife),
            selectinload(Aktivitaet.zeitmodell),
        )
    )
    return activity_to_out(act2)