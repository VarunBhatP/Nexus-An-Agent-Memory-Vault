# models.py
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, JSON, Column
from typing import List, Optional

# 1. The Base Schema (Shared fields)
class MemoryBase(SQLModel):
    agent_id: str
    content: str
    category: Optional[str] = "general"
    importance_score: int = Field(ge=1, le=10) # <--- Validation lives here!

# 2. The Database Table (Adds ID)
class Memory(MemoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    embedding: Optional[List[float]] = Field(default=None, sa_column=Column(JSON))

# 3. The Create Model (What user sends)
# We don't need to add anything extra here, it just inherits the score limits.
class MemoryCreate(MemoryBase):
    pass
class MemoryUpdate(SQLModel):
    # All fields are optional because the user might only want to update ONE thing.
    content: Optional[str] = None
    category: Optional[str] = None
    importance_score: Optional[int] = None
    # Note: NO id, NO created_at, NO updated_at here!

