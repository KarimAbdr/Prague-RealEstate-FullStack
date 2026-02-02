from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.db.models import Base

DATABASE_URL = "sqlite:///./data/realty.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_session() -> Session:
    return SessionLocal()