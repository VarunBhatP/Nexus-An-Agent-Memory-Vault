from datetime import datetime, timezone
from fastapi import APIRouter, FastAPI, Depends, HTTPException, Security, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware  # ← ADD THIS
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

# Define SessionDep FIRST
load_dotenv()
SessionDep = Annotated[Session, Depends(get_session)]

# PUBLIC ROUTER (No Authentication)
templates = Jinja2Templates(directory="templates")
public_router = APIRouter()

@public_router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@public_router.get("/memories/search", response_model=List[Memory])
def public_search_memories(
    session: SessionDep,
    q: str = Query(..., description="Search query"),
    top_k: int = Query(5, ge=1, le=20),
    min_similarity: float = Query(0.3, ge=0.0, le=1.0)  # NEW!
):
    query_vector = get_embedding(q)
    query = select(Memory).where(Memory.embedding.is_not(None))
    memories = session.exec(query).all()
    
    similarities = [
        (memory, cosine_similarity(query_vector, memory.embedding))
        for memory in memories
    ]
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # ONLY return relevant memories (above threshold)
    relevant = [(mem, score) for mem, score in similarities if score > min_similarity]
    return [mem for mem, score in relevant[:top_k]]


# API Key Authentication (for admin routes)
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

# Main app (NO global auth)
app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount public routes (frontend + search)
app.include_router(public_router)

# ===================================
# ADMIN API ROUTES (Add auth manually if needed)
# ===================================
@app.post("/memories/", response_model=Memory)
def create_memory(memory_in: MemoryCreate, session: SessionDep):
    db_memory = Memory.model_validate(memory_in)
    vector = get_embedding(db_memory.content)
    db_memory.embedding = vector
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
    query = select(Memory)
    if category:
        query = query.where(Memory.category == category)
    if q:
        query = query.where(col(Memory.content).contains(q))
    memories = session.exec(query.offset(offset).limit(limit)).all()
    return memories

@app.get("/memories/{memory_id}", response_model=Memory)
def read_memory(memory_id: int, session: SessionDep):
    memory = session.get(Memory, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

@app.patch("/memories/{memory_id}", response_model=Memory)
def update_memory(memory_id: int, memory_update: MemoryUpdate, session: SessionDep):
    db_memory = session.get(Memory, memory_id)
    if not db_memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    memory_data = memory_update.model_dump(exclude_unset=True)
    for key, value in memory_data.items():
        setattr(db_memory, key, value)
    db_memory.updated_at = datetime.now(timezone.utc)
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
