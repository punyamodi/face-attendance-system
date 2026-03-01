from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database.connection import create_tables
from app.routes import attendance, pages, persons, stream, subjects, training


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.faces_dir.mkdir(parents=True, exist_ok=True)
    settings.models_dir.mkdir(parents=True, exist_ok=True)
    create_tables()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)
app.include_router(persons.router)
app.include_router(subjects.router)
app.include_router(attendance.router)
app.include_router(stream.router)
app.include_router(training.router)
