from fastapi import  FastAPI
from contextlib import asynccontextmanager
from db.db_config import create_tables,async_engine
from db.db_redis import redis_connect
from routers import agent_router,user
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行建表
    await create_tables()
    app.state.redis = await redis_connect()
    print("redis启动")
    yield
    # 关闭时释放连接池
    await async_engine.dispose()
    await app.state.redis.close()
app = FastAPI(lifespan=lifespan,debug=True)
app.include_router(agent_router.router)
app.include_router(user.router)