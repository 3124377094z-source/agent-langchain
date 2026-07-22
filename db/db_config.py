from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from config.settings import settings
from db.db_model import Base
from fastapi import FastAPI
from contextlib import asynccontextmanager
# SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./users.db"
async_engine = create_async_engine(
    settings.DATABASE_URL,
)

async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行建表
    await create_tables()
    yield
    # 关闭时释放连接池
    await async_engine.dispose()

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()