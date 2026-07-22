from fastapi import APIRouter, Depends, HTTPException, status
from schemas import UserCreate, UserMessages
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_config import get_db
from db import crud
from fastapi.security import OAuth2PasswordRequestForm
from config.settings import settings
from datetime import timedelta

from utils.logger_handler import logger

router = APIRouter(prefix="/user", tags=["user"])
@router.post("/register")
async def register(user_create:UserCreate,db:AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_name(db, user_create.username)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该用户已存在")
    new_user = await crud.create_user(db, user_create)
    return {
        "message":"注册成功",
        "id": new_user.id,
        "username": new_user.username,
    }
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends() ,db:AsyncSession = Depends(get_db)):
    user = await crud.login_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="用户名或密码错误")
    token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await crud.create_token(data={"sub": str(user.id), "username": user.username},
                                            expires_delta=token_expires
                                            )
    return {
        "message":"登录成功",
        "access_token":access_token,
    }
@router.post("/messages")
async def create_messages(user_message:UserMessages,db:AsyncSession = Depends(get_db)):
    try:
        user_messages = await crud.write_messages(db, user_message.note, user_message.user_id)
        return {
            "messages":"消息填写成功",
            "用户信息":user_messages
        }
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,)