from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import engine
from app.models import Base

from app.Routers.auth import router as auth_router
from app.Routers.activities import router as activities_router
from app.Routers.user_actions import router as user_actions_router
from app.Routers.locations import router as locations_router
from app.Routers.meta import router as meta_router


app = FastAPI(title="CityTrip API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(activities_router, prefix="/activities", tags=["activities"])
app.include_router(user_actions_router, prefix="/me", tags=["user-actions"])
app.include_router(locations_router, prefix="/locations", tags=["locations"])
app.include_router(meta_router, prefix="/meta", tags=["meta"])