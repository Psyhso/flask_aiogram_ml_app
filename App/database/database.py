import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))  # Добавляем App в пути

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

# Путь к вашей существующей SQLite базе данных
DATABASE_URL = "sqlite+aiosqlite:///bot_base.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Чтобы видеть SQL-запросы в консоли
    connect_args={"check_same_thread": False}  # Обязательно для SQLite
)

sync_engine = create_engine(
    "sqlite:///bot_base.db",
    echo=True,
    connect_args={"check_same_thread": False}
)

SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)


session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)