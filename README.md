# 🧠 AI Knowledge Inbox

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_19_+_TypeScript-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![TailwindCSS](https://img.shields.io/badge/UI-Tailwind_CSS_v4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Gemini](https://img.shields.io/badge/AI-Google_Gemini-4285F4.svg?logo=google&logoColor=white)](https://aistudio.google.com)

A personal knowledge inbox and production-grade **Retrieval-Augmented Generation (RAG)** pipeline. Users can ingest plain-text notes or live web URLs, and ask questions across their saved content with fast, grounded answers synthesized from vector-retrieved context.

---

## ✨ Key Features

* **Multi-Source Ingestion**: Save quick personal notes or scrape full web articles server-side.
* **Resilient Web Scraping**: Strips HTML tags, navigation, scripts, and includes an automated reader fallback for bot-protected or JavaScript-rendered pages (e.g. `openai.com`).
* **Semantic Chunking & Dense Embeddings**: 400-character sliding window with 50-character overlap paired with Google's `gemini-embedding-001` (768-dimensional dense vectors).
* **In-Memory Vector Search**: Sub-millisecond cosine similarity ranking over document chunks without heavy database overhead.
* **Fast Grounded Synthesis**: Generates conversational answers in ~1.2 seconds using Google Gemini 3.5 Flash Lite, backed by cited sources and relevance scores.
* **Production Error Handling & Offline Mode**: Standardized API error responses that mask technical traces from clients, plus a built-in fallback evaluation mode that allows testing even without an active API key.

---

## 📑 Table of Contents
1. [Architecture & Component Breakdown](#-architecture--component-breakdown)
2. [Quickstart & Run Guide](#-quickstart--run-guide)
3. [API Specification](#-api-specification)
4. [System Design Highlights](#-system-design-highlights)

---

## 🏗️ Architecture & Component Breakdown

The application follows a clean 3-tier modular architecture with strict separation of concerns:

### 1. Frontend Layer (React 19 + TypeScript + Tailwind CSS)
* **IngestCard**: User interface for submitting text notes or web URLs with live feedback.
* **InboxList**: Filterable live list of indexed documents (`All`, `Note`, `URL`) with timestamps.
* **QueryCard**: Question input interface with instant input clearing, synthesized answers, and source cards.
* **API Client (`api.ts`)**: Centralized HTTP client with automatic network failure handling and error sanitization.

### 2. Backend API Layer (FastAPI)
* **`POST /ingest`**: Ingestion endpoint that validates, scrapes, chunks, embeds, and stores documents.
* **`GET /items`**: Retrieves all indexed documents from memory, sorted newest first.
* **`POST /query`**: Semantic search endpoint that embeds the question, computes cosine similarity, and synthesizes grounded answers.
* **`GET /health`**: Uptime monitoring and health check endpoint.

### 3. Core Business Services
* **Web Scraper (`services/scraper.py`)**: Fetches HTML server-side, cleans scripts/styles, and includes automated reader fallback for bot-protected pages.
* **Text Chunker (`services/chunker.py`)**: 400-character sliding window with 50-character overlap to preserve semantic context across boundaries.
* **Embedding Service (`services/embedding.py`)**: Generates 768-dimensional dense vector embeddings using Google's `gemini-embedding-001`.
* **RAG Engine (`services/rag.py`)**: Performs in-memory cosine similarity retrieval and synthesizes answers using Gemini 3.5 Flash Lite (~1.2s response time).
* **Storage Repository (`storage.py`)**: Thread-safe in-memory vector store and document repository.
* **Global Error Handlers (`error_handlers.py`)**: Centralized exception handlers ensuring internal stack traces and vendor JSON are never exposed to the client.

### Component Mapping

| Layer | Component / File | Purpose & Responsibilities |
| :--- | :--- | :--- |
| **Frontend** | [`IngestCard.tsx`](Frontend/src/components/IngestCard.tsx) | Note creation and URL scraping forms with auto-reset and feedback |
| | [`QueryCard.tsx`](Frontend/src/components/QueryCard.tsx) | RAG question interface, instant input clearing, and cited sources |
| | [`InboxList.tsx`](Frontend/src/components/InboxList.tsx) | Filterable saved item feed (`all`, `note`, `url`) with live counter |
| | [`api.ts`](Frontend/src/services/api.ts) | Centralized fetch client with network error and validation interceptor |
| **Backend API** | [`routes/ingest.py`](Backend/src/ai_knowledge_inbox/routes/ingest.py) | Ingestion pipeline orchestration (`POST /ingest`, returns `HTTP 201`) |
| | [`routes/query.py`](Backend/src/ai_knowledge_inbox/routes/query.py) | Semantic search & RAG synthesis endpoint (`POST /query`) |
| | [`routes/items.py`](Backend/src/ai_knowledge_inbox/routes/items.py) | Returns all indexed documents sorted newest first (`GET /items`) |
| | [`routes/health.py`](Backend/src/ai_knowledge_inbox/routes/health.py) | Uptime and service health check (`GET /health`) |
| **Core Services** | [`services/scraper.py`](Backend/src/ai_knowledge_inbox/services/scraper.py) | Server-side web scraper with automated reader fallback for Cloudflare |
| | [`services/chunker.py`](Backend/src/ai_knowledge_inbox/services/chunker.py) | Sliding window chunker (400 chars, 50 overlap) for context integrity |
| | [`services/embedding.py`](Backend/src/ai_knowledge_inbox/services/embedding.py) | Google `gemini-embedding-001` (768-dim embeddings) |
| | [`services/rag.py`](Backend/src/ai_knowledge_inbox/services/rag.py) | Cosine similarity ranking + Gemini 3.5 Flash synthesis |
| | [`error_handlers.py`](Backend/src/ai_knowledge_inbox/error_handlers.py) | Centralized global error handling (no leaked internal traces) |
| | [`storage.py`](Backend/src/ai_knowledge_inbox/storage.py) | Thread-safe singleton repository for in-memory document & vector storage |

---

## 🚀 Quickstart & Run Guide

### 1. Prerequisites
* **Python >= 3.13** and **[uv](https://docs.astral.sh/uv/)** installed.
* **Node.js >= 18** and **npm** installed.
* A **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/) *(optional: a keyless fallback mode is built-in for instant evaluation)*.

### 2. Install Dependencies

You can install all dependencies for both Backend and Frontend with a single command from the root directory:

```powershell
npm run install:all
```

*(Or install them individually by folder):*

* **Backend dependencies (`uv`):**
  ```powershell
  cd Backend
  uv sync
  ```
* **Frontend dependencies (`npm`):**
  ```powershell
  cd Frontend
  npm install
  ```
* **Root runner dependency:**
  ```powershell
  npm install
  ```

### 3. Configure Environment

Copy the example environment file:
```powershell
cp Backend/.env.example Backend/.env
```

In `Backend/.env`:
```env
# Google Gemini API Key from https://aistudio.google.com/
GEMINI_API_KEY=AIzaSy...your_gemini_api_key_here
PORT=8000
```

### 4. Running the Application

#### Option A: Run Both Together (Recommended — Single Command)
From the root directory:

```powershell
npm run dev
```

> **What this does:**
> - Launches **FastAPI Backend** on `http://127.0.0.1:8000` (color-coded in **cyan**).
> - Launches **React Frontend** on `http://localhost:5173` (color-coded in **magenta**).
> - Starts both hot-reloaders simultaneously. Pressing `Ctrl + C` gracefully terminates both servers together.

#### Option B: Run Backend and Frontend Individually

**To run the Backend:**
```powershell
cd Backend
uv run python -m uvicorn ai_knowledge_inbox.main:app --app-dir src --reload --port 8000
```
*(Backend API available at `http://127.0.0.1:8000` | Swagger Docs at `http://127.0.0.1:8000/docs`)*

**To run the Frontend:**
```powershell
cd Frontend
npm run dev
```
*(Frontend web application available at `http://localhost:5173`)*

---

## 📡 API Specification

### 1. `POST /ingest`
Ingests a plain text note or scrapes a web URL server-side, chunks the content, generates vector embeddings, and indexes them.

**Request (Text Note):**
```json
{
  "source_type": "note",
  "content": "RAG connects large language models to private data for factual, cited answers.",
  "title": "What is RAG?"
}
```

**Request (Web URL):**
```json
{
  "source_type": "url",
  "url": "https://openai.com/index/chatgpt/"
}
```

**Response (HTTP 201 Created):**
```json
{
  "message": "Note ingested and embedded successfully",
  "item": {
    "id": "c1f7b82e-9d21-4f3e-8c7a-112233445566",
    "source_type": "note",
    "title": "What is RAG?",
    "content": "RAG connects large language models...",
    "source_url": null,
    "created_at": "2026-10-20T12:00:00Z"
  },
  "chunks_created": 3
}
```

---

### 2. `GET /items`
Retrieves all saved notes and URLs from the inbox, sorted newest first.

**Response (HTTP 200 OK):**
```json
{
  "items": [
    {
      "id": "c1f7b82e-9d21-4f3e-8c7a-112233445566",
      "source_type": "note",
      "title": "What is RAG?",
      "content": "...",
      "source_url": null,
      "created_at": "2026-10-20T12:00:00Z"
    }
  ],
  "total": 1
}
```

---

### 3. `POST /query`
Embeds the user's question, calculates cosine similarity against all chunks, retrieves top matches, and prompts Google Gemini to answer with citations.

**Request:**
```json
{
  "question": "What is RAG?",
  "top_k": 3
}
```

**Response (HTTP 200 OK):**
```json
{
  "question": "What is RAG?",
  "answer": "RAG (Retrieval-Augmented Generation) connects language models to external data...",
  "sources": [
    {
      "source_id": 1,
      "item_id": "c1f7b82e-9d21-4f3e-8c7a-112233445566",
      "title": "What is RAG?",
      "source_url": null,
      "snippet": "RAG connects large language models to private data...",
      "similarity_score": 0.8942
    }
  ]
}
```

---

### 4. 🛡️ Global Error Response Specification
Every error across the backend returns a uniform, structured JSON payload:

```json
{
  "success": false,
  "detail": "Human-readable explanation of what went wrong",
  "message": "Human-readable explanation of what went wrong",
  "status_code": 400,
  "error_type": "ValidationError | ClientError | ServerError | InternalServerError",
  "path": "/query"
}
```
The React frontend transparently extracts `detail`/`message` and displays dismissible alerts with actionable guidance.

---

## 💡 System Design Highlights

* **Chunking Strategy**: Character-based chunking (400 characters) with a 50-character sliding overlap. The overlap ensures that critical sentences spanning across chunk boundaries are not fragmented, preserving semantic meaning in both vectors.
* **Vector Store**: In-memory repository eliminating external database overhead and Docker dependencies for sub-millisecond retrieval. For production scale (1M+ vectors), this naturally migrates to an HNSW vector index (pgvector, Qdrant, or Pinecone) and asynchronous background ingestion queues (Celery/Redis).
* **Anti-Hallucination Grounding**: Context snippets are strictly bounded in the system instruction, ensuring the model only synthesizes claims supported by retrieved sources.
* **Scraper Resilience**: Handles both standard HTML websites and Cloudflare-protected SPAs via direct `httpx` extraction with automated reader fallback.
