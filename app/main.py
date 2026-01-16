
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, Security, Query
from sqlmodel import Session, col, select
from typing import Annotated, List
import numpy as np
from app.brain import cosine_similarity, get_embedding 
from .database import create_db_and_tables, get_session
from .models import Memory, MemoryCreate, MemoryUpdate
from contextlib import asynccontextmanager
from fastapi.security.api_key import APIKeyHeader
import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key(
    api_key_header: str = Depends(APIKeyHeader(name="NEXUS_API_KEY", auto_error=True)),
):
    expected_api_key = os.getenv("NEXUS_API_KEY")  
    if api_key_header == expected_api_key:
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables() 
    yield

app = FastAPI(
                lifespan=lifespan,
                dependencies=[Security(get_api_key)],
            )

# Helper type for the DB session (saves typing "Depends(get_session)" everywhere)
SessionDep = Annotated[Session, Depends(get_session)]

@app.post("/memories/", response_model=Memory)
def create_memory(memory_in: MemoryCreate, session: SessionDep):
    # Convert Pydantic model to DB model
    db_memory = Memory.model_validate(memory_in)
    # Generate Vector
    vector = get_embedding(db_memory.content)
    # Save it
    db_memory.embedding = vector
    # Add the DB model (NOT the Pydantic one)
    session.add(db_memory)
    session.commit()
    session.refresh(db_memory)
    return db_memory


@app.get("/memories/", response_model=List[Memory])
def read_memories(
    session: SessionDep, 
    offset: int = 0, 
    limit: int = 100,
    category: str | None = None,
    q: str | None = None
):
    """
    Retrieves memories with filtering and pagination.
    """
    query = select(Memory)
    
    if category:
        query = query.where(Memory.category == category)

    if q:
        query = query.where(col(Memory.content).contains(q))  

    # Apply offset/limit for pagination
    memories = session.exec(query.offset(offset).limit(limit)).all()
    return memories
@app.get("/memories/search", response_model=List[Memory])
def search_memories(   
    session: SessionDep, 
    q: str = Query(..., description="Search query"),
    top_k: int = Query(5, ge=1, le=20)
):
    query_vector = get_embedding(q)
    query = select(Memory).where(Memory.embedding.is_not(None))
    memories = session.exec(query).all()
    
    similarities = [
        (memory, cosine_similarity(query_vector, memory.embedding))
        for memory in memories
    ]
    similarities.sort(key=lambda x: x[1], reverse=True)
    return [mem for mem, score in similarities[:top_k]]

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
def update_memory(memory_id: int, memory_update: MemoryUpdate, session: SessionDep):
    # 1. Find the existing memory
    db_memory = session.get(Memory, memory_id)
    if not db_memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    # 2. Update logic: Only update fields that were sent
    # exclude_unset=True means "ignore fields the user didn't send"
    memory_data = memory_update.model_dump(exclude_unset=True)
    for key, value in memory_data.items():
        setattr(db_memory, key, value)
    
    # NEW: Manually update the timestamp
    db_memory.updated_at = datetime.now(timezone.utc) # Update the object

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





