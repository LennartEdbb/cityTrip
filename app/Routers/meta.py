from fastapi import APIRouter
from app.models import (
    KategorieEnum, KostenmodellEnum, WaehrungEnum, DauerTypEnum, WochentagEnum, RolleEnum
)
from app.Schemas import MetaEnumsOut

router = APIRouter()

@router.get("/enums", response_model=MetaEnumsOut)
def get_enums():
    return MetaEnumsOut(
        kategorien=[e.value for e in KategorieEnum],
        kostenmodelle=[e.value for e in KostenmodellEnum],
        waehrungen=[e.value for e in WaehrungEnum],
        dauertypen=[e.value for e in DauerTypEnum],
        wochentage=[e.value for e in WochentagEnum],
        rollen=[e.value for e in RolleEnum],
    )