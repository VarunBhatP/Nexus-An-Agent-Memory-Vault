from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Annotated, List 
from .database import create_db_and_tables, get_session
from .models import Memory, MemoryCreate, MemoryBase
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables() 
    yield

app = FastAPI(lifespan=lifespan)

# Helper type for the DB session (saves typing "Depends(get_session)" everywhere)
SessionDep = Annotated[Session, Depends(get_session)]

@app.post("/memories/", response_model=Memory)
def create_memory(memory_in: MemoryCreate, session: SessionDep):
    # 1. Convert Pydantic model to DB model
    db_memory = Memory.model_validate(memory_in)
    
    # 2. Add the DB model (NOT the Pydantic one)
    session.add(db_memory)
    session.commit()
    session.refresh(db_memory)
    return db_memory


@app.get("/memories/", response_model=List[Memory])
def read_memories(
    session: SessionDep, 
    offset: int = 0, 
    limit: int = 100,
    category: str | None = None
):
    """
    Retrieves memories with filtering and pagination.
    """
    query = select(Memory)
    
    if category:
        query = query.where(Memory.category == category)
        
    # Apply offset/limit for pagination
    memories = session.exec(query.offset(offset).limit(limit)).all()
    return memories

@app.get("/memories/{memory_id}", response_model=Memory)
def read_memory(memory_id: int, session: SessionDep):
    """
    Finds a specific memory by ID.
    """
    memory = session.get(Memory, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

@app.patch("/memories/{memory_id}", response_model=Memory)
def update_memory(memory_id: int, memory_update: Memory, session: SessionDep):
    # 1. Find the existing memory
    db_memory = session.get(Memory, memory_id)
    if not db_memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    # 2. Update logic: Only update fields that were sent
    # exclude_unset=True means "ignore fields the user didn't send"
    memory_data = memory_update.model_dump(exclude_unset=True)
    
    for key, value in memory_data.items():
        setattr(db_memory, key, value) # Update the object

    # 3. Save
    session.add(db_memory)
    session.commit()
    session.refresh(db_memory)
    return db_memory


@app.delete("/memories/{memory_id}")
def delete_memory(memory_id: int, session: SessionDep):
    memory = session.get(Memory, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    session.delete(memory)
    session.commit()
    return {"ok": True}
