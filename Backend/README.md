# AI Knowledge Inbox - Backend

FastAPI backend providing RAG content ingestion, text chunking, Gemini vector embeddings, in-memory cosine retrieval, and question answering.

> For full architectural documentation, system design tradeoffs, and assignment checklist, see the root [README.md](../README.md).

---

## 🚀 How to Run the Backend

From the `Backend/` directory:

```powershell
# 1. Install dependencies (creates .venv and installs all packages)
uv sync

# 2. (Optional) Copy environment template and add your GEMINI_API_KEY
cp .env.example .env

# 3. Run the FastAPI server with uv
uv run python -m uvicorn ai_knowledge_inbox.main:app --app-dir src --reload --port 8000
```

* **Base API**: http://127.0.0.1:8000
* **Interactive Swagger Docs**: http://127.0.0.1:8000/docs
* **Health Check**: http://127.0.0.1:8000/health
