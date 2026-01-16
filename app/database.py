import os
from typing import Generator
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
load_dotenv()
# Neon DATABASE_URL or fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL")

# Simple SYNC engine (works with SQLite + Postgres)
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set True for SQL debug logs
    pool_pre_ping=True,  # Validates connections
)

def create_db_and_tables():
    """Create all tables"""
    print(f"🔍 Using DATABASE_URL: {DATABASE_URL}")
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Database session dependency"""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
