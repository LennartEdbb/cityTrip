from __future__ import annotations

from datetime import date, time
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.db import get_db
from app.auth import get_current_user
from app.models import (
    Benutzer, Aktivitaet,
    Favorit, Bewertung, GeplanteAktivitaet, Erinnerung
)

router = APIRouter()


# ---------- Profile (personal info) ----------
class ActivitySummary(BaseModel):
    id: int
    bezeichnung: str


class ProfileOut(BaseModel):
    name: str
    rolle: str
    email: str
    favorites: List[ActivitySummary] = Field(default_factory=list)
    my_activities: List[ActivitySummary] = Field(default_factory=list)


@router.get("/profile", response_model=ProfileOut)
def get_profile(
        db: Session = Depends(get_db),
        user: Benutzer = Depends(get_current_user),
):
    # Favorites -> join to Aktivitaet to return simple summary
    favs = db.scalars(select(Favorit).where(Favorit.benutzer_id == user.id)).all()
    favorite_acts: List[ActivitySummary] = []
    for f in favs:
        act = db.scalar(select(Aktivitaet).where(Aktivitaet.id == f.aktivitaet_id))
        if act:
            favorite_acts.append(ActivitySummary(id=act.id, bezeichnung=act.bezeichnung))

    # Activities created by this user (anbieter)
    my_acts = db.scalars(select(Aktivitaet).where(Aktivitaet.anbieter_id == user.id)).all()
    my_activities = [ActivitySummary(id=a.id, bezeichnung=a.bezeichnung) for a in my_acts]

    return ProfileOut(name=user.name, rolle=user.rolle, email=user.email, favorites=favorite_acts, my_activities=my_activities)

# ---------- Schemas (lokal, damit es sofort läuft) ----------
class FavoriteOut(BaseModel):
    id: int
    aktivitaet_id: int
    hinzugefuegt_am: date


class ReviewIn(BaseModel):
    aktivitaet_id: int
    sterne: int = Field(ge=1, le=5)
    kommentar: Optional[str] = None


class ReviewOut(BaseModel):
    id: int
    aktivitaet_id: int
    sterne: int
    kommentar: Optional[str] = None


class PlanIn(BaseModel):
    aktivitaet_id: int
    geplant_datum: date
    geplant_uhrzeit: time


class PlanOut(BaseModel):
    id: int
    aktivitaet_id: int
    geplant_datum: date
    geplant_uhrzeit: time


class ReminderIn(BaseModel):
    erinnern_am: date
    erinnern_um: time


class ReminderOut(BaseModel):
    id: int
    geplante_id: int
    erinnern_am: date
    erinnern_um: time


# ---------- Helpers ----------
def ensure_activity_exists(db: Session, aktivitaet_id: int) -> None:
    act = db.scalar(select(Aktivitaet.id).where(Aktivitaet.id == aktivitaet_id))
    if not act:
        raise HTTPException(status_code=404, detail="Aktivität nicht gefunden")


# ---------- Favorites ----------
@router.get("/favorites", response_model=List[FavoriteOut])
def list_favorites(
        db: Session = Depends(get_db),
        user: Benutzer = Depends(get_current_user),
):
    favs = db.scalars(select(Favorit).where(Favorit.benutzer_id == user.id)).all()
    return [FavoriteOut(id=f.id, aktivitaet_id=f.aktivitaet_id, hinzugefuegt_am=f.hinzugefuegt_am) for f in favs]


@router.post("/favorites/{aktivitaet_id}", response_model=FavoriteOut)
def add_favorite(
        aktivitaet_id: int,
        db: Session = Depends(get_db),
        user: Benutzer = Depends(get_current_user),
):
    ensure_activity_exists(db, aktivitaet_id)

    existing = db.scalar(
        select(Favorit).where(
            Favorit.benutzer_id == user.id,
            Favorit.aktivitaet_id == aktivitaet_id
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="Schon als Favorit gespeichert")

    fav = Favorit(benutzer_id=user.id, aktivitaet_id=aktivitaet_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return FavoriteOut(id=fav.id, aktivitaet_id=fav.aktivitaet_id, hinzugefuegt_am=fav.hinzugefuegt_am)


@router.delete("/favorites/{aktivitaet_id}")
def remove_favorite(
        aktivitaet_id: int,
        db: Session = Depends(get_db),
        user: Benutzer = Depends(get_current_user),
):
    res = db.execute(
        delete(Favorit).where(
            Favorit.benutzer_id == user.id,
            Favorit.aktivitaet_id == aktivitaet_id
        )
    )
    db.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Favorit nicht gefunden")
    return {"ok": True}


# ---------- Reviews (upsert) ----------
@router.get("/reviews", response_model=List[ReviewOut])
def list_reviews(
        db: Session = Depends(get_db),
        user: Benutzer = Depends(get_current_user),
):
    reviews = db.scalars(select(Bewertung).where(Bewertung.benutzer_id == user.id)).all()
    return [
        ReviewOut(
            id=r.id, aktivitaet_id=r.aktivitaet_id, sterne=r.sterne, kommentar=r.kommentar
        )
        for r in reviews
    ]


@router.post("/reviews", response_model=ReviewOut)
def create_or_update_review(
        data: ReviewIn,
        db: Session = Depends(get_db),
        user: Benutzer = Depends(get_current_user),
):
    ensure_activity_exists(db, data.aktivitaet_id)

    existing = db.scalar(
        select(Bewertung).where(
            Bewertung.benutzer_id == user.id,
            Bewertung.aktivitaet_id == data.aktivitaet_id
        )
    )

    if existing:
        existing.sterne = data.sterne
        existing.kommentar = data.kommentar
        db.commit()
        db.refresh(existing)
        return ReviewOut(
            id=existing.id,
            aktivitaet_id=existing.aktivitaet_id,
            sterne=existing.sterne,
            kommentar=existing.kommentar,
        )

    r = Bewertung(
        benutzer_id=user.id,
        aktivitaet_id=data.aktivitaet_id,
        sterne=data.sterne,
        kommentar=data.kommentar
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return ReviewOut(id=r.id, aktivitaet_id=r.aktivitaet_id, sterne=r.sterne, kommentar=r.kommentar)


@router.delete("/reviews/{aktivitaet_id}")
def delete_review(
        aktivitaet_id: int,
        db: Session = Depends(get_db),
        user: Benutzer = Depends(get_current_user),
):
    res = db.execute(
        delete(Bewertung).where(
            Bewertung.benutzer_id == user.id,
            Bewertung.aktivitaet_id == aktivitaet_id
        )
    )
    db.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Bewertung nicht gefunden")
    return {"ok": True}


# ---------- Plans ----------
@router.get("/plans", response_model=List[PlanOut])
def list_plans(
        db: Session = Depends(get_db),
        user: Benutzer = Depends(get_current_user),
):
    plans = db.scalars(select(GeplanteAktivitaet).where(GeplanteAktivitaet.benutzer_id == user.id)).all()
    return [
        PlanOut(
            id=p.id,
            aktivitaet_id=p.aktivitaet_id,
            geplant_datum=p.geplant_datum,
            geplant_uhrzeit=p.geplant_uhrzeit
        )
        for p in plans
    ]


@router.post("/plans", response_model=PlanOut)
def add_plan(
        data: PlanIn,
        db: Session = Depends(get_db),
        user: Benutzer = Depends(get_current_user),
):
    ensure_activity_exists(db, data.aktivitaet_id)

    existing = db.scalar(
        select(GeplanteAktivitaet).where(
            GeplanteAktivitaet.benutzer_id == user.id,
            GeplanteAktivitaet.aktivitaet_id == data.aktivitaet_id,
            GeplanteAktivitaet.geplant_datum == data.geplant_datum,
            GeplanteAktivitaet.geplant_uhrzeit == data.geplant_uhrzeit
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="Plan existiert bereits")

    p = GeplanteAktivitaet(
        benutzer_id=user.id,
        aktivitaet_id=data.aktivitaet_id,
        geplant_datum=data.geplant_datum,
        geplant_uhrzeit=data.geplant_uhrzeit
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return PlanOut(id=p.id, aktivitaet_id=p.aktivitaet_id, geplant_datum=p.geplant_datum, geplant_uhrzeit=p.geplant_uhrzeit)


@router.delete("/plans/{plan_id}")
def delete_plan(
        plan_id: int,
        db: Session = Depends(get_db),
        user: Benutzer = Depends(get_current_user),
):
    plan = db.scalar(select(GeplanteAktivitaet).where(GeplanteAktivitaet.id == plan_id))
    if not plan or plan.benutzer_id != user.id:
        raise HTTPException(status_code=404, detail="Plan nicht gefunden")

    db.delete(plan)
    db.commit()
    return {"ok": True}


# ---------- Reminders ----------
@router.get("/plans/{plan_id}/reminders", response_model=List[ReminderOut])
def list_reminders(
        plan_id: int,
        db: Session = Depends(get_db),
        user: Benutzer = Depends(get_current_user),
):
    plan = db.scalar(select(GeplanteAktivitaet).where(GeplanteAktivitaet.id == plan_id))
    if not plan or plan.benutzer_id != user.id:
        raise HTTPException(status_code=404, detail="Plan nicht gefunden")

    rems = db.scalars(select(Erinnerung).where(Erinnerung.geplante_id == plan_id)).all()
    return [ReminderOut(id=r.id, geplante_id=r.geplante_id, erinnern_am=r.erinnern_am, erinnern_um=r.erinnern_um) for r in rems]


@router.post("/plans/{plan_id}/reminders", response_model=ReminderOut)
def add_reminder(
        plan_id: int,
        data: ReminderIn,
        db: Session = Depends(get_db),
        user: Benutzer = Depends(get_current_user),
):
    plan = db.scalar(select(GeplanteAktivitaet).where(GeplanteAktivitaet.id == plan_id))
    if not plan or plan.benutzer_id != user.id:
        raise HTTPException(status_code=404, detail="Plan nicht gefunden")

    r = Erinnerung(geplante_id=plan_id, erinnern_am=data.erinnern_am, erinnern_um=data.erinnern_um)
    db.add(r)
    db.commit()
    db.refresh(r)
    return ReminderOut(id=r.id, geplante_id=r.geplante_id, erinnern_am=r.erinnern_am, erinnern_um=r.erinnern_um)


@router.delete("/reminders/{reminder_id}")
def delete_reminder(
        reminder_id: int,
        db: Session = Depends(get_db),
        user: Benutzer = Depends(get_current_user),
):
    r = db.scalar(select(Erinnerung).where(Erinnerung.id == reminder_id))
    if not r:
        raise HTTPException(status_code=404, detail="Erinnerung nicht gefunden")

    # Sicherheitscheck: Erinnerung muss zu einem Plan des Users gehören
    plan = db.scalar(select(GeplanteAktivitaet).where(GeplanteAktivitaet.id == r.geplante_id))
    if not plan or plan.benutzer_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db.delete(r)
    db.commit()
    return {"ok": True}