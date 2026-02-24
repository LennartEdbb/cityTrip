from fastapi import FastAPI
from app.db import engine
from app.models import Base

from app.Routers.auth import router as auth_router
from app.Routers.activities import router as activities_router
from app.Routers.user_actions import router as user_actions_router

app = FastAPI(title="CityTrip API")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(activities_router, prefix="/activities", tags=["activities"])
app.include_router(user_actions_router, prefix="/me", tags=["user-actions"])