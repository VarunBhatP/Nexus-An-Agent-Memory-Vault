# Nexus AI Memory 🧠

**Live Demo:** https://nexus-api-258a.onrender.com

Semantic memory search for agentic AI systems. Shared memory across different agents.

## Features
- Vector embeddings + cosine similarity
- Neon Postgres (persistent)
- Public search UI
- Authenticated admin API

##  Run Locally

### **Prerequisites**
- bash
- Python 3.11+
- Git
- Neon Postgres account (free): neon.tech

### **Steps**
1. Clone & Install
- bash
- git clone https://github.com/VarunBhatP/Nexus-An-Agent-Memory-Vault
- cd nexus-ai-memory
- pip install -r requirements.txt

2. Setup Neon Postgres (2 mins)
- neon.tech → Sign up → Create project "nexus-memory"
- Copy DATABASE_URL (looks like: postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require)

3. Environment Variables
Create .env file as in .env.example file, also create a vitual environment and activate it.

4. Migrate Database
- python migrate.py
5. Run Server
- uvicorn app.main:app --reload
6. Test
- Frontend: http://localhost:8000/
- API Docs: http://localhost:8000/docs
- Add Memory: POST /memories/ (use /docs)
- Search: Type "NVIDIA" in frontend

##Production
- Persistent Neon Postgres (FREE forever)
- Docker ready
- Render deployment (FREE tier)
- Shared memory across AI agents
API Usage (For Agents)
bash
# Add memory
curl -X POST "http://localhost:8000/memories/" \
  -H "NEXUS_API_KEY: your-key" \
  -d '{"content": "NVIDIA Q4 earnings", "agent_id": "moneytrust", "category": "stocks", "importance_score": 8}'

# Semantic search
curl "http://localhost:8000/memories/search?q=NVIDIA"

## Deploy Steps
1. git init
2. git add . 
3. git commit -m "Nexus AI Memory MVP"
4. GitHub → New repo → Push
5. DELETE .env from project
6. render.com → Sign up → New → Web Service → Docker
7. Connect GitHub repo
8. Environment Variables:
   DATABASE_URL=your_neon_url
   NEXUS_API_KEY=supersecret123
9. Deploy → 3 minutes → LIVE!

## Test Live Deployment:
- https://nexus-api-258a.onrender.com/ → Frontend works
- https://nexus-api-258a.onrender.com/docs → API docs
- POST memory → Persists in Neon
- Search "Tesla" → Returns moneytrust memory
