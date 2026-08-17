from datetime import timezone, datetime, timedelta
import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, status,Header
from schemas import UserCreate, UserMessages
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_config import get_db
from db import crud
from db.crud import get_current_user
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from config.settings import settings
from utils.logger_handler import logger
from jose import jwt, JWTError
from db.db_redis import get_redis_client
from db.db_model import User
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
async def login(form_data: OAuth2PasswordRequestForm = Depends() ,db:AsyncSession = Depends(get_db),redis_client:redis.Redis = Depends(get_redis_client)):
    user = await crud.login_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="用户名或密码错误")
    token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await crud.create_token(data={"sub": str(user.id), "username": user.username},
                                            expires_delta=token_expires
                                            )
    refresh_token = await crud.create_refresh_token(data={"sub": str(user.id)})
    user_id = str(user.id)
    await redis_client.set(f"refresh:token:{user_id}",value="1",ex = settings.REFRESH_TOKEN_EXPIRE_DAYS*86400)
    return {
        "message":"登录成功",
        "user_id":str(user.id),
        "access_token":access_token,
        "refresh_token":refresh_token,
    }
@router.post("/refresh")
async def refresh(refresh_token: str = Header(..., alias="Refresh"), db: AsyncSession = Depends(get_db),redis_client:redis.Redis = Depends(get_redis_client)):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(status_code=401, detail="非刷新Token")
        # redis refresh_token检查
        saved_token = await redis_client.get(f"refresh:token:{user_id}")
        if not saved_token:
            raise HTTPException(
                status_code=401,
                detail="refresh token已进入黑名单，现在失效"
            )
        if not user_id:
            raise HTTPException(status_code=401, detail="无效的Token载荷")
    except JWTError as e:
        logger.warning("JWT 解码失败: %s", e)
        raise HTTPException(status_code=401, detail="Token无效或已过期")
    user = await crud.get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    access_token = await crud.create_token(
        data={"sub": str(user.id), "username": user.username}
    )
    return {
        "message": "success",
        "new_token": access_token
    }
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")
@router.post("/logout")
async def logout(redis_client:redis.Redis=Depends(get_redis_client),token: str = Depends(oauth2_scheme)):
    token_data = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    exp = token_data.get("exp")
    now = datetime.now(timezone.utc).timestamp()
    expire = int(exp-now)
    user_id = token_data.get("sub")
    if expire > 0:
        await redis_client.set(f"blacklist:{token}",value="1",ex=expire)
    await redis_client.delete(f"refresh:token:{user_id}")
    return {
        "message": "退出成功",
        "expire":exp
    }
# 获取用户信息
@router.get("/info")
async def info(user: User = Depends(get_current_user)):
    return {
        "message":"success",
        "user_id":user.id,
        "username":user.username
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