from __future__ import annotations

from datetime import date, time
from typing import Optional, List, Union, Literal
from pydantic import BaseModel, EmailStr, ConfigDict, Field


from app.models import (
    KategorieEnum, KostenmodellEnum, WaehrungEnum, DauerTypEnum, WochentagEnum
)

# ---------------- Auth ----------------
class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    rolle: str


# ---------------- Address / Location ----------------
class AnschriftIn(BaseModel):
    strasse: str
    hausnummer: str
    ort: str
    plz: str
    land: str

class AnschriftOut(AnschriftIn):
    model_config = ConfigDict(from_attributes=True)
    id: int

class LocationIn(BaseModel):
    bezeichnung: str
    beschreibung: Optional[str] = None
    bemerkung: Optional[str] = None
    anschrift: AnschriftIn
    lat: Optional[float] = None
    lon: Optional[float] = None

class LocationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    bezeichnung: str
    beschreibung: Optional[str] = None
    bemerkung: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    anschrift: AnschriftOut


# ---------------- Eintritt / Tarife ----------------
class TarifIn(BaseModel):
    bezeichnung: str
    dauer_typ: DauerTypEnum
    dauer_wert: int = 1
    preis: float = 0.0
    kriterium: Optional[str] = None
    waehrung: WaehrungEnum = WaehrungEnum.EURO

class TarifOut(TarifIn):
    model_config = ConfigDict(from_attributes=True)
    id: int

class EintrittIn(BaseModel):
    kostenmodell: KostenmodellEnum
    hinweis: Optional[str] = None
    tarife: List[TarifIn] = Field(default_factory=list)

class EintrittOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    kostenmodell: str
    hinweis: Optional[str] = None
    tarife: List[TarifOut] = Field(default_factory=list)


# ---------------- Zeitmodelle ----------------
class ZeitEinmaligIn(BaseModel):
    typ: Literal["einmalig"]
    datum: date
    von: time
    bis: time
    hinweis: Optional[str] = None

class ZeitSerieIn(BaseModel):
    typ: Literal["serie"]
    gueltig_von: date
    gueltig_bis: Optional[date] = None
    wochentage: List[WochentagEnum]
    von: time
    bis: time
    intervall_wochen: int = 1
    hinweis: Optional[str] = None

class SlotIn(BaseModel):
    wochentag: WochentagEnum
    uhrzeit_von: time
    uhrzeit_bis: time

class ZeitDurchgaengigIn(BaseModel):
    typ: Literal["durchgaengig"]
    gueltig_von: Optional[date] = None
    gueltig_bis: Optional[date] = None
    slots: List[SlotIn] = Field(default_factory=list)
    hinweis: Optional[str] = None

ZeitmodellIn = Union[ZeitEinmaligIn, ZeitSerieIn, ZeitDurchgaengigIn]


# Output-Varianten (passen zu deinem activity_to_out dict)
class ZeitEinmaligOut(BaseModel):
    typ: Literal["einmalig"]
    id: int
    datum: date
    von: time
    bis: time
    hinweis: Optional[str] = None

class ZeitSerieOut(BaseModel):
    typ: Literal["serie"]
    id: int
    gueltig_von: date
    gueltig_bis: Optional[date] = None
    von: time
    bis: time
    intervall_wochen: int
    wochentage: List[WochentagEnum] = Field(default_factory=list)
    hinweis: Optional[str] = None

class SlotOut(BaseModel):
    id: int
    wochentag: WochentagEnum
    uhrzeit_von: time
    uhrzeit_bis: time

class ZeitDurchgaengigOut(BaseModel):
    typ: Literal["durchgaengig"]
    id: int
    gueltig_von: Optional[date] = None
    gueltig_bis: Optional[date] = None
    slots: List[SlotOut] = Field(default_factory=list)
    hinweis: Optional[str] = None

ZeitmodellOut = Union[ZeitEinmaligOut, ZeitSerieOut, ZeitDurchgaengigOut]


# ---------------- Activity (DAS fehlte dir) ----------------
class ActivityCreateIn(BaseModel):
    bezeichnung: str
    beschreibung: Optional[str] = None
    bemerkung: Optional[str] = None
    kategorien: List[KategorieEnum] = Field(default_factory=list)
    barrierefrei: bool = False
    aktiv: bool = True

    # entweder existierende Location oder neue:
    location_id: Optional[int] = None
    location: Optional[LocationIn] = None

    zeitmodell: ZeitmodellIn
    eintritt: Optional[EintrittIn] = None


class ActivityOut(BaseModel):
    id: int
    bezeichnung: str
    beschreibung: Optional[str] = None
    bemerkung: Optional[str] = None
    anbieter : str
    anbieterID: int
    barrierefrei: bool
    aktiv: bool
    kategorien: List[str] = Field(default_factory=list)

    location: LocationOut
    zeitmodell: ZeitmodellOut
    eintritt: Optional[EintrittOut] = None

    # --- Update Schemas ---
class AnschriftUpdateIn(BaseModel):
    strasse: Optional[str] = None
    hausnummer: Optional[str] = None
    ort: Optional[str] = None
    plz: Optional[str] = None
    land: Optional[str] = None

class LocationUpdateIn(BaseModel):
    bezeichnung: Optional[str] = None
    beschreibung: Optional[str] = None
    bemerkung: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    anschrift: Optional[AnschriftUpdateIn] = None

class ActivityUpdateIn(BaseModel):
    bezeichnung: Optional[str] = None
    beschreibung: Optional[str] = None
    bemerkung: Optional[str] = None
    kategorien: Optional[List[KategorieEnum]] = None
    barrierefrei: Optional[bool] = None
    aktiv: Optional[bool] = None

    # beim Update nur Location wechseln (separates Location-Update über /locations)
    location_id: Optional[int] = None

    # optional: komplett ersetzen / entfernen
    zeitmodell: Optional[ZeitmodellIn] = None
    eintritt: Optional[EintrittIn] = None

# --- Meta ---
class MetaEnumsOut(BaseModel):
    kategorien: List[str] = Field(default_factory=list)
    kostenmodelle: List[str] = Field(default_factory=list)
    waehrungen: List[str] = Field(default_factory=list)
    dauertypen: List[str] = Field(default_factory=list)
    wochentage: List[str] = Field(default_factory=list)
    rollen: List[str] = Field(default_factory=list)