from pydantic import BaseModel
class Questions(BaseModel):
    query: str
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
class UserMessages(BaseModel):
    note: str
    user_id: str
class TokenData(BaseModel):
    username: str
    user_id: int