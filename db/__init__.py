# db/__init__.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncAttrs
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as sync_sessionmaker

from utils.env_data import Config as cf


class Base(AsyncAttrs, DeclarativeBase):
    pass


class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None

    def __getattr__(self, name):
        return getattr(self._session, name)

    def init(self):
        self._engine = create_async_engine(
            cf.db.DB_URL,
            future=True,
            echo=False,
            isolation_level="AUTOCOMMIT"
        )
        self._session = sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)()

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


# ASYNC (Bot uchun)
db = AsyncDatabaseSession()
db.init()  # ✅ Init qilish

# ✅ ASYNC ENGINE (SQLADMIN uchun)
async_engine = create_async_engine(
    cf.db.DB_URL,
    future=True,
    echo=False
)


# ✅ SYNC (Flask-Admin uchun - agar kerak bo'lsa)
def get_sync_engine():
    """Sync engine for queries"""
    sync_url = cf.db.DB_URL.replace('postgresql+asyncpg', 'postgresql+psycopg2')
    return create_engine(sync_url, echo=False)


def get_sync_session():
    """Sync session for statistics queries"""
    engine = get_sync_engine()
    Session = sync_sessionmaker(bind=engine)
    return Session()