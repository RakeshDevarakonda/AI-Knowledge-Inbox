# 🧠 AI Knowledge Inbox (Production-Ready RAG Pipeline)

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_19_+_TypeScript-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![TailwindCSS](https://img.shields.io/badge/UI-Tailwind_CSS_v4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Gemini](https://img.shields.io/badge/AI-Google_Gemini-4285F4.svg?logo=google&logoColor=white)](https://aistudio.google.com)

A personal knowledge inbox application built as a clean, production-grade **Retrieval-Augmented Generation (RAG)** pipeline. Users can save short text notes or web URLs, and ask questions across their indexed content with grounded answers and source citations.

---

## 📑 Table of Contents
1. [Architecture & Component Design](#-architecture--component-design)
2. [Single-Command Quickstart](#-single-command-quickstart)
3. [Interactive Services & URLs](#-interactive-services--urls)
4. [API Specification](#-api-specification)
5. [Complete Assignment Checklist](#-complete-assignment-checklist)
6. [Tradeoffs & System Design Rationale](#-tradeoffs--system-design-rationale-interview-deep-dive)
7. [Project Directory Layout](#-project-directory-layout)

---

## 🏗️ Architecture & Component Design

The application follows a clean 3-tier modular architecture with clear separation of concerns:

### 1. Frontend Layer (React 19 + TypeScript + Tailwind CSS)
* **IngestCard**: User interface for submitting text notes or web URLs with live feedback.
* **InboxList**: Filterable live list of indexed documents (`All`, `Note`, `URL`) with timestamps.
* **QueryCard**: Question input interface with instant input clearing, synthesized answers, and expandable source snippets.
* **API Client (`api.ts`)**: Centralized HTTP client with automatic network failure handling and error sanitization.

### 2. Backend API Layer (FastAPI)
* **`POST /ingest`**: Ingestion endpoint that validates, scrapes, chunks, embeds, and stores documents.
* **`GET /items`**: Retrieves all indexed documents from memory, sorted newest first.
* **`POST /query`**: Semantic search endpoint that embeds the question, computes cosine similarity, and synthesizes grounded answers.
* **`GET /health`**: Uptime monitoring and health check endpoint.

### 3. Core Business Services
* **Web Scraper (`services/scraper.py`)**: Fetches HTML server-side, cleans scripts/styles, and includes automated reader fallback for bot-protected pages (like Cloudflare).
* **Text Chunker (`services/chunker.py`)**: 400-character sliding window with 50-character overlap to preserve semantic context across chunk boundaries.
* **Embedding Service (`services/embedding.py`)**: Generates 768-dimensional dense vector embeddings using Google's `gemini-embedding-001`.
* **RAG Engine (`services/rag.py`)**: Performs in-memory cosine similarity retrieval and synthesizes answers using Gemini 3.5 Flash Lite (~1.2s response time).
* **Storage Repository (`storage.py`)**: Thread-safe in-memory vector store and document repository.
* **Global Error Handlers (`error_handlers.py`)**: Centralized exception handlers ensuring internal stack traces and vendor JSON are never exposed to the client.

### 🧩 Component Breakdown

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

## 🚀 Single-Command Quickstart

### 1. Prerequisites
- **Python >= 3.13** and **[uv](https://docs.astral.sh/uv/)** installed.
- **Node.js >= 18** and **npm** installed.
- A free **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).

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
  *(Creates `.venv` and installs FastAPI, Google GenAI SDK, BeautifulSoup, httpx, and uvicorn).*

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
Copy the example environment file and add your key(s):
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

#### Option A: Run Both Together (Recommended - Single Command)
From the root directory (`E:\AI Knowledge Inbox`), run:

```powershell
npm run dev
```

> **What this does:**
> - Launches **FastAPI Backend** on `http://127.0.0.1:8000` (color-coded in **cyan**).
> - Launches **React Frontend** on `http://localhost:5173` (color-coded in **magenta**).
> - Starts both hot-reloaders simultaneously.
> - Pressing `Ctrl + C` gracefully terminates both servers together!

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

## 🌐 Interactive Services & URLs

When running, the following endpoints are available:

| Service | URL | Purpose |
| :--- | :--- | :--- |
| **Frontend Web App** | **[http://localhost:5173](http://localhost:5173)** | User interface for note/URL ingestion and Q&A |
| **Interactive Swagger Docs** | **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** | Interactive OpenAPI testing console |
| **Health Check** | **[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)** | Uptime and readiness monitor |

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
  "url": "https://en.wikipedia.org/wiki/FastAPI"
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
  "answer": "RAG (Retrieval-Augmented Generation) connects language models to external data [1]...",
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
Every error across the entire backend API (validation errors, 400s, 404s, 500s, or external AI API failures) returns a uniform, structured JSON payload:

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

## ✅ Complete Assignment Checklist

### 1. Content Ingestion
- [x] **Add plain-text notes through the UI**: `IngestCard.tsx` provides note textarea and optional title.
- [x] **Ingest URLs through the UI**: `IngestCard.tsx` provides URL input field.
- [x] **Fetch URL content on the backend**: `scraper.py` uses `httpx` with Wikimedia-compliant headers.
- [x] **Store raw content**: Full content preserved in `storage.py`.
- [x] **Store metadata**: UUID, timestamps, `source_type`, and `source_url` stored.
- [x] **Validate inputs**: Pydantic models validate inputs and reject empty submissions.
- [x] **Handle ingestion failures**: Gracefully catches 404s, network errors, and empty webpages with HTTP 400.

### 2. RAG Pipeline
- [x] **Chunk the content**: `chunker.py` segments content.
- [x] **Use intentional chunking**: 400-char chunks with 50-char sliding overlap to preserve boundary context.
- [x] **Generate embeddings**: `embedding.py` uses Gemini `gemini-embedding-001`.
- [x] **Store vectors**: In-memory store keeps vectors indexed with document IDs.
- [x] **Embed the question**: Questions are vectorized using the same embedding model.
- [x] **Retrieve relevant chunks**: Cosine similarity scans and ranks all chunks.
- [x] **Use similarity ranking**: Returns top $K$ chunks sorted descending by similarity.
- [x] **Build the LLM prompt**: Grounded prompt with numbered `[1]`, `[2]` context blocks.
- [x] **Generate a grounded answer**: `gemini-2.5-flash` answers strictly using provided context.
- [x] **Return citations**: Returns source title, snippet quote, and percentage match.
- [x] **Handle missing context**: Explicit prompt fallback when facts are not in the inbox.
- [x] **Avoid unnecessary re-embedding**: Chunks are embedded once at ingestion; questions embedded once per query.

### 3. Backend API Design
- [x] **POST /ingest**: Returns HTTP 201 Created.
- [x] **GET /items**: Returns HTTP 200 OK.
- [x] **POST /query**: Returns HTTP 200 OK.
- [x] **Request/Response schemas**: Fully typed with Pydantic in `schemas.py`.
- [x] **Sensible status codes**: 201, 200, 400, 500 appropriately used.
- [x] **Handle external failures**: Try/except blocks prevent server crashes on API drops.
- [x] **Separate responsibilities**: Zero god files (`routes/`, `services/`, `schemas.py`, `storage.py`).
- [x] **Secure configuration**: Secrets loaded from `.env`, `.env.example` provided.
- [x] **Avoid exposing secrets**: Client never receives API credentials.

### 4. Frontend
- [x] **Add-note interface**: Intuitive form in `IngestCard.tsx`.
- [x] **Add-URL interface**: URL ingestion with helper hints.
- [x] **Saved-items list**: Filterable inbox feed (All / Notes / URLs) with timestamps.
- [x] **Question interface**: Search input with "Ask AI" trigger.
- [x] **Display answer**: Formatted text card showing Gemini's response.
- [x] **Display citations**: Expandable cards showing title, snippet, and similarity score.
- [x] **Show loading states**: Clear loading indicators during scraping, embedding, and answering.
- [x] **Show useful errors**: Styled error alerts for validation and server errors.
- [x] **Use React hooks appropriately**: `useState` and `useEffect` with clean dependency tracking.
- [x] **Consistent state**: Saving a new item immediately refreshes the inbox list.

### 5. Debuggability & Code Quality
- [x] **Structured logging**: Python standard `logging` configured with timestamps and log levels.
- [x] **Useful error messages**: Descriptive error details for debugging.
- [x] **Separate concerns**: Modular React components and FastAPI routers.
- [x] **Avoid copy-paste code**: Centralized `api.ts` client and shared types.
- [x] **Clear names and types**: TypeScript strict types and Pydantic schemas.
- [x] **Manageable dependencies**: Minimal lightweight packages (`fastapi`, `httpx`, `bs4`, `google-genai`).
- [x] **Setup instructions**: Complete quickstart with single-command `npm run dev`.

---

## 💡 Tradeoffs & System Design Rationale (Interview Deep-Dive)

### 1. Chunking Strategy Rationale
- **Approach**: Character-based chunking with fixed window (400 characters) and a 50-character sliding overlap.
- **Why Overlap Matters**: If an important sentence is split in half across a chunk boundary, semantic search queries could miss it. The 50-character overlap guarantees that boundary context is preserved in both chunks.
- **Why 400 Characters**: Smaller chunks improve semantic retrieval precision (avoiding "diluted" embeddings) and ensure that only the most relevant snippets are passed to the LLM prompt.

### 2. Vector Store Choice: In-Memory vs Database
- **Why In-Memory for this Prototype**:
  - Eliminates external dependencies, Docker containers, file locking issues, and complex migrations.
  - Sub-millisecond lookup and similarity calculation in pure Python.
  - Directly matches the assignment's emphasis on *"simplicity without bloat"*.
- **The Tradeoff**: Ephemeral storage — data resets on server restart, and memory usage scales linearly with data.

### 3. Cosine Similarity vs Other Metrics
- **Why Cosine Similarity**: It measures the angle between two high-dimensional vectors, completely ignoring document length. This prevents long, verbose paragraphs from artificially scoring higher than short, concise ones.
- **Formula**: $\text{sim}(\mathbf{A}, \mathbf{B}) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$.

### 4. Top-K Retrieval & Token Limits
- **Top-K Selection**: Defaulting to $K=3$ balances providing sufficient context to the LLM without diluting the prompt or inflating inference latency.
- **Token Limits & Cost**: Passing entire 20-page web articles would consume tens of thousands of prompt tokens, increase costs, and increase the risk of the model getting confused by irrelevant sections ("lost in the middle" phenomenon).

### 5. Grounding & Citation Accuracy
- **Prompt Isolation**: Gemini is instructed: *"Answer based strictly on the provided context snippets. If the answer cannot be found, say 'I couldn't find the answer in your saved inbox.' Cite sources using [1], [2]."*
- This prevents hallucinations and anchors every claim directly back to a retrieved chunk.

### 6. What Breaks at Scale?
- **Linear Scan Bottleneck ($O(N)$)**:
  - With 100 chunks, calculating cosine similarity across all chunks takes $< 1\text{ ms}$.
  - With 1,000,000 chunks, computing 1 million 768-dimensional dot products in a single Python process spikes CPU and takes several seconds per query.
- **Memory Consumption**:
  - Storing 1,000,000 vectors of 768 floats (each float64 = 8 bytes) consumes $\approx 6\text{ GB}$ of RAM for embeddings alone.
- **Synchronous Ingestion Block**:
  - Scraping large websites with 50+ chunks synchronously blocks the HTTP thread for 5–10 seconds.

### 7. Production Changes (How to Scale)
1. **Approximate Nearest Neighbors (ANN)**:
   - Replace linear scan with an **HNSW (Hierarchical Navigable Small World)** index (e.g., via **Qdrant**, **Pinecone**, or **PostgreSQL with `pgvector`**), reducing query time from $O(N)$ to $O(\log N)$ ($< 10\text{ ms}$ for 10M vectors).
2. **Asynchronous Ingestion with Queues**:
   - Use a message queue (RabbitMQ / Redis Queue / Celery / SQS) where `POST /ingest` returns `202 Accepted` immediately, and background workers handle scraping, chunking, and embedding.
3. **Hybrid Search (Dense + Sparse)**:
   - Combine semantic vector search (Gemini) with lexical keyword search (BM25) to catch exact acronyms, names, or product IDs that semantic models might occasionally miss.

### 8. URL-Fetching Risks & Mitigation
- **SSRF (Server-Side Request Forgery)**: Malicious users could enter `http://169.254.169.254` (cloud metadata) or `http://localhost:8000` to probe internal networks. In production, an IP whitelist/blacklist blocks loopback and private IP ranges.
- **Infinite Redirects & Hangs**: Mitigated using strict HTTP client timeouts (12 seconds) and `follow_redirects=True` with redirect limits.
- **Dynamic JavaScript Sites**: Simple scrapers cannot execute client-rendered SPAs. In production, a headless browser service (Playwright / Puppeteer) or specialized reader API handles dynamic content.

### 9. Evaluation Frameworks
To objectively measure RAG quality in production, use the **RAG Triad** (via libraries like **Ragas** or **TruLens**):
1. **Context Relevance**: Are the retrieved top-$K$ chunks actually relevant to the question?
2. **Groundedness (Faithfulness)**: Is the LLM answer strictly derived from the context, or did it invent facts?
3. **Answer Relevance**: Did the LLM actually answer what the user asked?

---

## 📁 Project Directory Layout

### Root Level
* `package.json`: Manages the unified single-command runner (`npm run dev`) via concurrently.
* `README.md`: Complete system architecture, quickstart, API specs, and technical tradeoff rationale.

### Backend (`Backend/`)
* `pyproject.toml`: Python project configuration and dependency management via `uv`.
* `.env.example`: Environment configuration template (`GEMINI_API_KEY`, `PORT`).
* `src/ai_knowledge_inbox/main.py`: FastAPI application factory, CORS middleware, and lifecycle banners.
* `src/ai_knowledge_inbox/config.py`: Environment loader and structured logging configuration.
* `src/ai_knowledge_inbox/schemas.py`: Pydantic request and response schemas for all endpoints.
* `src/ai_knowledge_inbox/storage.py`: Thread-safe in-memory vector store and document repository.
* `src/ai_knowledge_inbox/error_handlers.py`: Global exception handlers and client error sanitization.
* `src/ai_knowledge_inbox/routes/`: Modular REST route handlers (`ingest.py`, `query.py`, `items.py`, `health.py`).
* `src/ai_knowledge_inbox/services/`: Core logic (`scraper.py`, `chunker.py`, `embedding.py`, `rag.py`).

### Frontend (`Frontend/`)
* `vite.config.ts`: Vite build configuration with Tailwind CSS v4 integration.
* `src/App.tsx`: Main application layout, state orchestrator, and connection monitor.
* `src/types/index.ts`: Strict TypeScript interfaces for documents, citations, and API responses.
* `src/services/api.ts`: Centralized fetch client with network error and validation normalization.
* `src/components/`: Modular React components (`Header.tsx`, `IngestCard.tsx`, `QueryCard.tsx`, `InboxList.tsx`).
