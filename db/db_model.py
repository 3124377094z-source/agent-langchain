from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, func, ForeignKey
from datetime import datetime
class Base(DeclarativeBase):
    pass
class User(Base):
    __tablename__ = 'user'
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:Mapped[str] = mapped_column(String(64), unique=True, index=True)
    username:Mapped[str] = mapped_column(String(64), index=True)
    password:Mapped[str] = mapped_column(String(64), index=True)
    email:Mapped[str] = mapped_column(String(100),unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        index=True,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        index=True,
        nullable=False
    )
class UserMessages(Base):
    __tablename__ = "user_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey(User.user_id),
        unique=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        index=True,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        index=True,
        nullable=False
    )
    note: Mapped[str] = mapped_column(String(200), nullable=True)
