# models.py
from sqlmodel import SQLModel, Field
from typing import Optional

# 1. The Base Schema (Shared fields)
class MemoryBase(SQLModel):
    agent_id: str
    content: str
    category: Optional[str] = "general"
    importance_score: int = Field(ge=1, le=10) # <--- Validation lives here!

# 2. The Database Table (Adds ID)
class Memory(MemoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

# 3. The Create Model (What user sends)
# We don't need to add anything extra here, it just inherits the score limits.
class MemoryCreate(MemoryBase):
    pass
