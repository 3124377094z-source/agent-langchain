from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_config import get_db
from agent.react_agent import agent_chat
from schemas import Questions
from db.db_model import User
from db.crud import get_current_user
from fastapi.responses import StreamingResponse
from db import crud
from utils.logger_handler import logger
router = APIRouter(prefix="/agent", tags=["chat"])
@router.post("/react_agent")
async def chat(question:Questions, current_user: User = Depends(get_current_user)):
    try:
        result = agent_chat.execute_stream(question.query,current_user)
        return StreamingResponse(
            result,
            media_type="text/plain; charset=utf-8",
        )
    except Exception as e:
        logger.exception(e)
        raise