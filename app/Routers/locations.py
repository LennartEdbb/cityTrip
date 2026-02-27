from __future__ import annotations

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, delete, or_

from app.db import get_db
from app.auth import require_roles
from app.models import Location, Anschrift, Aktivitaet
from app.Schemas import LocationIn, LocationOut, LocationUpdateIn

router = APIRouter()


@router.get("", response_model=List[LocationOut])
def list_locations(
        db: Session = Depends(get_db),
        q: Optional[str] = Query(default=None, description="Suche in Bezeichnung/Beschreibung"),
        ort: Optional[str] = Query(default=None, description="Filter nach Ort"),
):
    stmt = select(Location).options(selectinload(Location.anschrift))

    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Location.bezeichnung.like(like), Location.beschreibung.like(like)))

    if ort:
        stmt = stmt.join(Anschrift).where(Anschrift.ort == ort)

    return db.scalars(stmt).all()


@router.get("/{location_id}", response_model=LocationOut)
def get_location(location_id: int, db: Session = Depends(get_db)):
    loc = db.scalar(
        select(Location)
        .where(Location.id == location_id)
        .options(selectinload(Location.anschrift))
    )
    if not loc:
        raise HTTPException(status_code=404, detail="Location nicht gefunden")
    return loc


@router.post("", response_model=LocationOut)
def create_location(
        data: LocationIn,
        db: Session = Depends(get_db),
        _user=Depends(require_roles("Anbieter", "Admin")),
):
    a = data.anschrift
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
        bezeichnung=data.bezeichnung,
        beschreibung=data.beschreibung,
        bemerkung=data.bemerkung,
        anschrift_id=anschrift.id,
        lat=data.lat,
        lon=data.lon,
    )
    db.add(loc)
    db.commit()

    # für Response inklusive Anschrift neu laden
    loc = db.scalar(
        select(Location)
        .where(Location.id == loc.id)
        .options(selectinload(Location.anschrift))
    )
    return loc


@router.put("/{location_id}", response_model=LocationOut)
def update_location(
        location_id: int,
        data: LocationUpdateIn,
        db: Session = Depends(get_db),
        _user=Depends(require_roles("Anbieter", "Admin")),
):
    loc = db.scalar(
        select(Location)
        .where(Location.id == location_id)
        .options(selectinload(Location.anschrift))
    )
    if not loc:
        raise HTTPException(status_code=404, detail="Location nicht gefunden")

    for field in ("bezeichnung", "beschreibung", "bemerkung", "lat", "lon"):
        if field in data.model_fields_set:
            setattr(loc, field, getattr(data, field))

    if data.anschrift is not None:
        a = loc.anschrift
        for field in ("strasse", "hausnummer", "ort", "plz", "land"):
            if field in data.anschrift.model_fields_set:
                setattr(a, field, getattr(data.anschrift, field))

    db.commit()
    db.refresh(loc)
    return loc


@router.delete("/{location_id}")
def delete_location(
        location_id: int,
        db: Session = Depends(get_db),
        _user=Depends(require_roles("Anbieter", "Admin")),
):
    # blocken, wenn Location noch in Aktivitäten benutzt wird
    used = db.scalar(select(Aktivitaet.id).where(Aktivitaet.location_id == location_id))
    if used:
        raise HTTPException(
            status_code=409,
            detail="Location wird noch von Aktivitäten verwendet. Bitte erst Activities ändern/löschen."
        )

    loc = db.scalar(select(Location).where(Location.id == location_id))
    if not loc:
        raise HTTPException(status_code=404, detail="Location nicht gefunden")

    anschrift_id = loc.anschrift_id

    db.execute(delete(Location).where(Location.id == location_id))

    # Anschrift nur löschen, wenn keine andere Location sie nutzt
    still_used = db.scalar(select(Location.id).where(Location.anschrift_id == anschrift_id))
    if not still_used:
        db.execute(delete(Anschrift).where(Anschrift.id == anschrift_id))

    db.commit()
    return {"ok": True}