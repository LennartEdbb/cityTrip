from __future__ import annotations

from datetime import datetime, date, time
from enum import Enum
from typing import Optional

from sqlalchemy import (
    String, Integer, Float, Boolean,
    Date, Time, DateTime,
    ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ---------- Enums ----------
class RolleEnum(str, Enum):
    ANWENDER = "Anwender"
    ANBIETER = "Anbieter"
    ADMIN = "Admin"


class KategorieEnum(str, Enum):
    BILDUNG = "Bildung"
    ESSEN_UND_TRINKEN = "Essen_und_Trinken"
    FAMILIE = "Familie"
    KULTUR = "Kultur"
    MUSIK = "Musik"
    NACHTLEBEN = "Nachtleben"
    NATUR = "Natur"


class KostenmodellEnum(str, Enum):
    KOSTENLOS = "Kostenlos"
    GEBUEHR = "Gebühr"
    SPENDE = "Spende"
    KONSUM = "Konsum"
    MITGLIEDSCHAFT = "Mitgliedschaft"


class WaehrungEnum(str, Enum):
    EURO = "Euro"
    DOLLAR = "Dollar"
    PFUND = "Pfund"


class DauerTypEnum(str, Enum):
    STUNDE = "Stunde"
    TAG = "Tag"
    WOCHE = "Woche"
    MONAT = "Monat"
    QUARTAL = "Quartal"
    JAHR = "Jahr"


class WochentagEnum(str, Enum):
    MONTAG = "Montag"
    DIENSTAG = "Dienstag"
    MITTWOCH = "Mittwoch"
    DONNERSTAG = "Donnerstag"
    FREITAG = "Freitag"
    SAMSTAG = "Samstag"
    SONNTAG = "Sonntag"


# ---------- Benutzer ----------
class Benutzer(Base):
    __tablename__ = "benutzer"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    telefonnummer: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rolle: Mapped[str] = mapped_column(String(20), default=RolleEnum.ANWENDER.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ---------- Anschrift / Location ----------
class Anschrift(Base):
    __tablename__ = "anschrift"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    strasse: Mapped[str] = mapped_column(String(120))
    hausnummer: Mapped[str] = mapped_column(String(20))
    ort: Mapped[str] = mapped_column(String(120))
    plz: Mapped[str] = mapped_column(String(20))
    land: Mapped[str] = mapped_column(String(80))


class Location(Base):
    __tablename__ = "location"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bezeichnung: Mapped[str] = mapped_column(String(160))
    beschreibung: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    bemerkung: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)

    anschrift_id: Mapped[int] = mapped_column(ForeignKey("anschrift.id"))
    anschrift: Mapped[Anschrift] = relationship()

    # Optional fürs Suchen per Radius
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


# ---------- Aktivität + Kategorien ----------
class Aktivitaet(Base):
    __tablename__ = "aktivitaet"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    anbieter_id: Mapped[int] = mapped_column(ForeignKey("benutzer.id"))
    anbieter: Mapped[Benutzer] = relationship()

    bezeichnung: Mapped[str] = mapped_column(String(200))
    beschreibung: Mapped[Optional[str]] = mapped_column(String(4000), nullable=True)
    bemerkung: Mapped[Optional[str]] = mapped_column(String(4000), nullable=True)

    location_id: Mapped[int] = mapped_column(ForeignKey("location.id"))
    location: Mapped[Location] = relationship()

    barrierefrei: Mapped[bool] = mapped_column(Boolean, default=False)
    aktiv: Mapped[bool] = mapped_column(Boolean, default=True)

    kategorien: Mapped[list["AktivitaetKategorie"]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    eintritt: Mapped[Optional["Eintritt"]] = relationship(
        back_populates="aktivitaet",
        cascade="all, delete-orphan",
        uselist=False
    )

    zeitmodell: Mapped["Zeitmodell"] = relationship(
        back_populates="aktivitaet",
        cascade="all, delete-orphan",
        uselist=False
    )


class AktivitaetKategorie(Base):
    __tablename__ = "aktivitaet_kategorie"
    __table_args__ = (UniqueConstraint("aktivitaet_id", "kategorie", name="uq_act_cat"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    aktivitaet_id: Mapped[int] = mapped_column(ForeignKey("aktivitaet.id"))
    kategorie: Mapped[str] = mapped_column(String(40))  # KategorieEnum.value


# ---------- Eintritt / Tarife ----------
class Eintritt(Base):
    __tablename__ = "eintritt"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    aktivitaet_id: Mapped[int] = mapped_column(ForeignKey("aktivitaet.id"), unique=True)
    aktivitaet: Mapped[Aktivitaet] = relationship(back_populates="eintritt")

    kostenmodell: Mapped[str] = mapped_column(String(30))  # KostenmodellEnum.value
    hinweis: Mapped[Optional[str]] = mapped_column(String(4000), nullable=True)

    tarife: Mapped[list["Tarif"]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class Tarif(Base):
    __tablename__ = "tarif"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    eintritt_id: Mapped[int] = mapped_column(ForeignKey("eintritt.id"))

    bezeichnung: Mapped[str] = mapped_column(String(120))
    dauer_typ: Mapped[str] = mapped_column(String(20))   # DauerTypEnum.value
    dauer_wert: Mapped[int] = mapped_column(Integer, default=1)

    preis: Mapped[float] = mapped_column(Float, default=0.0)
    kriterium: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    waehrung: Mapped[str] = mapped_column(String(10), default=WaehrungEnum.EURO.value)


# ---------- Zeitmodell (Polymorph) ----------
class Zeitmodell(Base):
    __tablename__ = "zeitmodell"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    aktivitaet_id: Mapped[int] = mapped_column(ForeignKey("aktivitaet.id"), unique=True)
    aktivitaet: Mapped[Aktivitaet] = relationship(back_populates="zeitmodell")

    hinweis: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)

    typ: Mapped[str] = mapped_column(String(20))  # discriminator

    __mapper_args__ = {
        "polymorphic_on": typ,
        "polymorphic_identity": "base",
    }


class Einmalig(Zeitmodell):
    __tablename__ = "zeit_einmalig"

    id: Mapped[int] = mapped_column(ForeignKey("zeitmodell.id"), primary_key=True)
    datum: Mapped[date] = mapped_column(Date)
    von: Mapped[time] = mapped_column(Time)
    bis: Mapped[time] = mapped_column(Time)

    __table_args__ = (CheckConstraint("bis > von", name="ck_einmalig_bis_gt_von"),)

    __mapper_args__ = {"polymorphic_identity": "einmalig"}


class Serie(Zeitmodell):
    __tablename__ = "zeit_serie"

    id: Mapped[int] = mapped_column(ForeignKey("zeitmodell.id"), primary_key=True)
    gueltig_von: Mapped[date] = mapped_column(Date)
    gueltig_bis: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    von: Mapped[time] = mapped_column(Time)
    bis: Mapped[time] = mapped_column(Time)
    intervall_wochen: Mapped[int] = mapped_column(Integer, default=1)

    wochentage: Mapped[list["SerieWochentag"]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    __table_args__ = (CheckConstraint("bis > von", name="ck_serie_bis_gt_von"),)

    __mapper_args__ = {"polymorphic_identity": "serie"}


class SerieWochentag(Base):
    __tablename__ = "serie_wochentag"
    __table_args__ = (UniqueConstraint("serie_id", "wochentag", name="uq_serie_day"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    serie_id: Mapped[int] = mapped_column(ForeignKey("zeit_serie.id"))
    wochentag: Mapped[str] = mapped_column(String(15))  # WochentagEnum.value


class Durchgaengig(Zeitmodell):
    __tablename__ = "zeit_durchgaengig"

    id: Mapped[int] = mapped_column(ForeignKey("zeitmodell.id"), primary_key=True)
    gueltig_von: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gueltig_bis: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    slots: Mapped[list["OeffnungszeitSlot"]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    __mapper_args__ = {"polymorphic_identity": "durchgaengig"}


class OeffnungszeitSlot(Base):
    __tablename__ = "oeffnungszeit_slot"
    __table_args__ = (CheckConstraint("uhrzeit_bis > uhrzeit_von", name="ck_slot_bis_gt_von"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    durchgaengig_id: Mapped[int] = mapped_column(ForeignKey("zeit_durchgaengig.id"))

    wochentag: Mapped[str] = mapped_column(String(15))  # WochentagEnum.value
    uhrzeit_von: Mapped[time] = mapped_column(Time)
    uhrzeit_bis: Mapped[time] = mapped_column(Time)


# ---------- User Actions ----------
class Bewertung(Base):
    __tablename__ = "bewertung"
    __table_args__ = (
        UniqueConstraint("benutzer_id", "aktivitaet_id", name="uq_review_user_act"),
        CheckConstraint("sterne >= 1 AND sterne <= 5", name="ck_sterne_1_5"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    benutzer_id: Mapped[int] = mapped_column(ForeignKey("benutzer.id"))
    aktivitaet_id: Mapped[int] = mapped_column(ForeignKey("aktivitaet.id"))

    sterne: Mapped[int] = mapped_column(Integer)
    kommentar: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Favorit(Base):
    __tablename__ = "favorit"
    __table_args__ = (UniqueConstraint("benutzer_id", "aktivitaet_id", name="uq_fav_user_act"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    benutzer_id: Mapped[int] = mapped_column(ForeignKey("benutzer.id"))
    aktivitaet_id: Mapped[int] = mapped_column(ForeignKey("aktivitaet.id"))
    hinzugefuegt_am: Mapped[date] = mapped_column(Date, default=date.today)


class GeplanteAktivitaet(Base):
    __tablename__ = "geplante_aktivitaet"
    __table_args__ = (
        UniqueConstraint(
            "benutzer_id", "aktivitaet_id", "geplant_datum", "geplant_uhrzeit",
            name="uq_plan_unique"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    benutzer_id: Mapped[int] = mapped_column(ForeignKey("benutzer.id"))
    aktivitaet_id: Mapped[int] = mapped_column(ForeignKey("aktivitaet.id"))

    geplant_datum: Mapped[date] = mapped_column(Date)
    geplant_uhrzeit: Mapped[time] = mapped_column(Time)

    erinnerungen: Mapped[list["Erinnerung"]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class Erinnerung(Base):
    __tablename__ = "erinnerung"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    geplante_id: Mapped[int] = mapped_column(ForeignKey("geplante_aktivitaet.id"))

    erinnern_am: Mapped[date] = mapped_column(Date)
    erinnern_um: Mapped[time] = mapped_column(Time)