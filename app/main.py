from fastapi import FastAPI

from app.core.config import settings
from app.core.db import engine, Base
from app.api.endpoints import charity_project_router, donation_router

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description
)

app.include_router(
    charity_project_router,
    prefix="/charity_project",
    tags=["charity_projects"]
)
app.include_router(
    donation_router,
    prefix="/donation",
    tags=["donations"]
)


@app.on_event("startup")
async def startup():
    """Создание таблиц при запуске приложения."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    """Закрытие соединения с БД при остановке приложения."""
    await engine.dispose()


@app.get("/")
async def root():
    return {"message": "Благотворительный фонд поддержки котиков QRKot"}
