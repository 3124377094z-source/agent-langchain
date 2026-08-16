# from passlib.context import CryptContext
# context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# def hash_password(password):
#     return context.hash(password)
# def verify_password(plain_password, hashed_password):
#     return context.verify(plain_password, hashed_password)
from passlib.context import CryptContext

# 使用 pbkdf2_sha256，这是最常用的方案
context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    """生成密码哈希"""
    return context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return context.verify(plain_password, hashed_password)