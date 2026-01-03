from sqlmodel import SQLModel, create_engine, Session

# 1. Define the database file name (SQLite is just a file!)
sqlite_file_name = "nexus.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# 2. Create the engine (The connection manager)
# connect_args={"check_same_thread": False} is needed specifically for SQLite
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

# 3. Function to create tables (We call this later in main.py)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# 4. Dependency: Provides a session (connection) to each request
def get_session():
    with Session(engine) as session:
        yield session
