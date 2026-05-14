from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.database import engine, Base
from app.routers import advertisements


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Advertisement Service",
    description="Сервис объявлений купли/продажи",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(advertisements.router)
