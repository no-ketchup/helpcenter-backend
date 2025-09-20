from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

from app.core import settings   # ← updated

engine = create_async_engine(settings.DATABASE_URL_ASYNC, echo=settings.DEBUG, future=True)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def get_session():
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)