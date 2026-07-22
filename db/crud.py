from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from db.db_config import get_db
from db.db_model import User,UserMessages
from sqlalchemy import select
from schemas import UserCreate,TokenData
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from config.settings import settings
from db import security
# async def get_user_ids(session: AsyncSession = Depends(get_db)):
#     stmt = select(User.user_id)
#     result = await session.execute(stmt)
#     return result.scalars().all()
async def get_user_by_id(session: AsyncSession, user_id: int):
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
async def get_user_by_name(session: AsyncSession, name: str):
    stmt = select(User).where(User.username == name)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
async def create_user(session: AsyncSession, user:UserCreate) -> User:
    password = secrets.hash_password(user.password)
    user_id = secrets.token_hex(16)
    user_obj = User(
        username=user.username,
        email=user.email,
        password=password,
        user_id=user_id,
    )
    session.add(user_obj)
    await session.commit()
    await session.refresh(user_obj)
    return user_obj
async def login_user(session:AsyncSession, username:str, password:str):
    user = await get_user_by_name(session, username)
    if not user:
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    return user
async def create_token(data:dict , expires_delta:timedelta|None = None):
    to_encode = data.copy() # 复制数据
    expires = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15)) #设置有效期时间，
    to_encode.update({"exp": expires})# 注入过期时间
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
async def verify_token(token:str)-> TokenData|None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])# JWT库中的解码方法jwt.decode()
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        if not user_id or not username:
            raise JWTError
        return TokenData(user_id=int(user_id), username=username)
    except JWTError:
        return None
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")# 实现OAuth2密码授权模式的一个安全工具
async def get_current_user(
        token: str = Depends(oauth2_scheme),#
        db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token 验证失败",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = await verify_token(token)
    if not token_data:
        raise credentials_exception
    user = await get_user_by_id(db, token_data.user_id)
    if not user:
        raise credentials_exception
    return user
async def write_messages(db: AsyncSession, messages:str,user_id:str):
    objet_user = UserMessages(note=messages,
                              user_id=user_id
                              )
    db.add(objet_user)
    await db.commit()
    await db.refresh(objet_user)
    return objet_user
# 查询用户信息
async def get_user_note(session: AsyncSession,user_id:str) -> str:
    stmt = select(UserMessages).where(UserMessages.id == user_id)
    result = await session.execute(stmt)
    record = result.scalar_one_or_none()
    return record.note