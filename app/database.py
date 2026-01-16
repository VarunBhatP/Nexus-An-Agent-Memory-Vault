from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Define the database 
db_url = os.getenv("DATABASE_URL")

# 2. Create the engine
connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}

engine = create_engine(db_url, connect_args=connect_args)

# 3. Function to create tables (We call this later in main.py)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# 4. Dependency: Provides a session (connection) to each request
def get_session():
    with Session(engine) as session:
        yield session
