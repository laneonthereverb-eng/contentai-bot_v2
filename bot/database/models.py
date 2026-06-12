from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import enum

from bot.config import DATABASE_URL

Base = declarative_base()

class UserRole(enum.Enum):
    FREE = "free"
    START = "start"
    BUSINESS = "business"
    AGENCY = "agency"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.FREE)
    generations_today = Column(Integer, default=0)
    last_generation_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class GenerationHistory(Base):
    __tablename__ = "generation_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    template_name = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    result = Column(String, nullable=False)
    is_liked = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session