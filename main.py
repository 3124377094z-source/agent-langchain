from fastapi import  FastAPI

from db.db_config import lifespan
from routers import agent_router,user
app = FastAPI(lifespan=lifespan)
app.include_router(agent_router.router)
app.include_router(user.router)