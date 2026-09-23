# 🛡️ Privacy-First Chatbot — API (Backend)

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-RAG-1C3C3C?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

Welcome to the backend of the **Privacy-First Chatbot**. This is a FastAPI-based, local RAG API built with Python 3.12, LangChain, ChromaDB, and Ollama. It accepts PDFs, indexes their text locally, and answers questions using the relevant document context without sending your data to a cloud AI provider.

---

## ✨ Features

- **🔒 Privacy-First Design** — PDF processing, embeddings, chat history, and LLM inference stay on your machine.
- **📄 PDF Document Management** — Upload, list, replace, and delete indexed PDF documents.
- **🧠 Hybrid RAG Retrieval** — Combines semantic similarity, MMR diversity search, and BM25 keyword search to find useful context.
- **💬 Session-Based Chat** — Creates anonymous chat sessions and preserves their history in SQLite across server restarts.
- **🔎 Source Attribution** — Returns the filename and page number behind every answer.
- **💾 Local Persistence** — Stores document vectors in ChromaDB and chat history in SQLite.
- **🏥 Health Monitoring** — Reports whether the API can reach Ollama and ChromaDB.
- **🛡️ API Protection** — Validates PDFs, sanitizes filenames, limits request sizes, restricts CORS, and rate-limits chat and upload routes.

---

## 🚀 Getting Started

Follow these instructions to run the API in isolation for development or production.

### 📂 1. Navigate and Environment Setup

First, navigate to the API folder and create your local configuration. This step is required for all methods:

```bash
cd api
cp sample.env .env
```

Inside `.env`, you will find:

```env
PORT=8000
OLLAMA_HOST=http://localhost:11434
LLM_MODEL=llama3.2
EMBEDDING_MODEL=all-MiniLM-L6-v2
ALLOWED_ORIGINS=["http://localhost:3000"]
```

> **Note:** Adjust `OLLAMA_HOST`, `LLM_MODEL`, and `ALLOWED_ORIGINS` if your local setup uses different values.

### 🧠 2. Ensure Ollama is Running (Required)

Regardless of whether you run the API via Docker or locally, your machine **must** have Ollama running at port `11434`.

1. Download and install [Ollama](https://ollama.com/download).
2. Start Ollama and pull the model you set in your `.env` (default is `llama3.2`):

```bash
ollama serve
ollama pull llama3.2
```

---

### 🐳 Option A: Running with Docker (Standalone)

If you want to build and run _only_ the API via Docker:

**Prerequisites:**

* **Docker** ([install guide](https://docs.docker.com/get-docker/))

#### Step 1: Build the Image

```bash
docker build -t privacy-chatbot-api .
```

#### Step 2: Run the Container

> **Note:** The container automatically fixes ownership of mounted folders at startup. Docker creates them when needed, so you do not need to create or `chown` them manually.

**On macOS or Windows (Git Bash / WSL):**

```bash
docker run --rm -p 8000:8000 \
  --env-file .env \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  -v "${PWD}/chroma_db:/app/chroma_db" \
  -v "${PWD}/uploaded_docs:/app/uploaded_docs" \
  -v "${PWD}/local_db:/app/local_db" \
  privacy-chatbot-api
```

**On Linux:**

```bash
docker run --rm --network host \
  --env-file .env \
  -e OLLAMA_HOST=http://localhost:11434 \
  -v "${PWD}/chroma_db:/app/chroma_db" \
  -v "${PWD}/uploaded_docs:/app/uploaded_docs" \
  -v "${PWD}/local_db:/app/local_db" \
  privacy-chatbot-api
```

> **Note:** `--network host` exposes the app directly on the host's network, so `-p 8000:8000` is not needed on Linux.

#### Step 3: Access the API

Open **http://localhost:8000/docs** to use Swagger UI, or use **http://localhost:8000/redoc** for ReDoc.

---

### 🛠️ Option B: Running Locally (Manual Dev Mode)

If you are developing the API, running it locally provides automatic reloads and direct access to the interactive API documentation.

**Prerequisites:**

* **Python** (v3.12 or newer)
* **uv** ([installation guide](https://docs.astral.sh/uv/))

#### Step 1: Install Dependencies

Make sure you have [uv](https://docs.astral.sh/uv/) installed.

```bash
uv sync
```

#### Step 2: Start the Development Server

```bash
uv run uvicorn main:app --reload --port 8000
```

#### Step 3: Access the API

Open **http://localhost:8000/docs** to use Swagger UI, or use **http://localhost:8000/redoc** for ReDoc.

---

## 🌐 How to Use the API

1. **Open Swagger UI:** Go to **[http://localhost:8000/docs](http://localhost:8000/docs)**
   after the server starts. Each endpoint is grouped under **Health Check**,
   **Document Ingestion (RAG)**, or **AI Chatbot**.
2. **Check API Health:** Expand `GET /health`, click **Try it out**, then
   **Execute**. Confirm that the response reports both Ollama and ChromaDB as
   available before uploading a document.
3. **Upload a PDF:** Expand `POST /api/document/upload`, click **Try it out**,
   choose a text-based PDF in the `file` field, then click **Execute**. A
   successful response includes the filename and the number of indexed chunks.
   The API extracts the text, splits it into chunks, creates local Hugging Face
   embeddings, and saves them in ChromaDB.
4. **Confirm the Document:** Run `GET /api/document/list` from Swagger UI. The
   response shows every indexed filename and its chunk count.
5. **Ask a Question:** Open `POST /api/chat`, click **Try it out**, and replace
   the request body with:

   ```json
   {
     "query": "What are the main points in this document?"
   }
   ```

   Click **Execute**. The API combines similarity, MMR, and BM25 retrieval,
   then sends the relevant context to Ollama for a grounded answer.
6. **Continue or Clear a Session:** Copy the `session_id` returned by the chat
   response into the next chat request to retain conversation context. To remove
   that history, use `DELETE /api/chat/history` and provide the same `session_id`
   as its query parameter.
7. **Review Sources and Clean Up:** Each chat response includes `sources` with
   the supporting filename and page numbers. Use `DELETE /api/document/{filename}`
   when you want to remove an indexed PDF and its stored vectors.

---

## 🏗️ Tech Stack

| Technology | Purpose |
| --- | --- |
| **Python 3.12+** | Backend runtime |
| **FastAPI** | API framework with automatic OpenAPI documentation |
| **Uvicorn** | ASGI server for running the FastAPI application |
| **LangChain** | Document processing and RAG orchestration |
| **Ollama** | Fully local LLM inference |
| **ChromaDB** | Persistent vector database for document chunks |
| **Hugging Face Sentence Transformers** | Local document embeddings |
| **BM25** | Keyword-based document retrieval |
| **pypdf** | PDF text extraction |
| **SQLite** | Persistent anonymous chat-session history |
| **uv** | Python dependency and environment management |
| **Docker** | Standalone containerized API deployment |

---

## 📁 Project Structure

```text
api/
├── main.py                  # FastAPI app, middleware, routes, and health check
├── app/
│   ├── config.py            # Environment-backed settings and local storage paths
│   ├── exceptions.py        # Application-specific errors
│   ├── middleware/          # Request logging, rate limiting, and error handling
│   ├── models/
│   │   └── schemas.py       # Request and response models
│   ├── routes/
│   │   ├── chat.py          # Chat and session-history endpoints
│   │   └── document.py      # PDF upload, list, and delete endpoints
│   └── services/
│       ├── rag_service.py   # PDF ingestion, chunking, embeddings, and ChromaDB
│       ├── llm_service.py   # Hybrid retrieval and Ollama answer generation
│       ├── bm25_retriever.py  # Keyword retrieval index
│       └── session_service.py # SQLite chat-session persistence
├── Dockerfile               # Multi-stage API image
├── pyproject.toml           # Python dependencies and tooling
├── sample.env               # Environment variable reference
└── uv.lock                  # Locked Python dependencies
```
