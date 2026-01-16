import os
from dotenv import load_dotenv
from sqlalchemy import select
from sqlmodel import Session
from app.database import engine
from app.models import Memory
from app.brain import get_embedding
import numpy as np

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {'✅ SET' if DATABASE_URL else '❌ MISSING'}")
if not DATABASE_URL:
    print("❌ Create .env with DATABASE_URL=your_neon_url")
    exit(1)

print("🔄 Migrating to Neon...")

try:
    with Session(engine) as session:
        neon_memories = session.exec(select(Memory)).all()
        print(f"Neon has {len(neon_memories)} memories")
        
        if len(neon_memories) == 0:
            print("📝 Creating test memories...")
            test_memories = [
                Memory(
                    content="NVIDIA stock prices drop before earnings calls",
                    agent_id="moneytrust",
                    category="stocks",
                    importance_score=8  # ✅ REQUIRED
                ),
                Memory(
                    content="FastAPI CORS error: Add CORSMiddleware to app",
                    agent_id="sourcesage", 
                    category="coding",
                    importance_score=9   # ✅ REQUIRED
                ),
                Memory(
                    content="User prefers spicy food, avoids gluten",
                    agent_id="personal",
                    category="diet",
                    importance_score=7   # ✅ REQUIRED
                )
            ]
            
            # Generate embeddings & save
            for memory in test_memories:
                memory.embedding = get_embedding(memory.content)  # ✅ Vector embedding
                session.add(memory)
            
            session.commit()
            print("✅ Added 3 test memories to Neon!")
        else:
            print("✅ Neon already has data!")
            
except Exception as e:
    print(f"❌ Migration failed: {e}")
