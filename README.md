# 🛡️ Privacy-First Chatbot

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-black?style=for-the-badge&logo=next.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=for-the-badge)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)

Welcome to the **Privacy-First Chatbot** — a fully local, Retrieval-Augmented Generation (RAG) chat application. Upload a PDF, ask questions about it, and get grounded answers with source attribution — without any of your data ever leaving your machine.

This is a monorepo containing two services:

- **[`client/`](./client/README.md)** — A Next.js 16 + React 19 + Tailwind CSS v4 frontend chat interface.
- **[`api/`](./api/README.md)** — A FastAPI + LangChain + ChromaDB + Ollama backend RAG engine.

Both are orchestrated together via Docker Compose, along with **Ollama** for fully local LLM inference.

---

## ✨ Features

- **🔒 Privacy-First Design** — PDF processing, embeddings, chat history, and LLM inference all run locally. No data is sent to a cloud AI provider.
- **💬 Real-time Chat with Source Attribution** — Ask questions and get AI answers backed by the exact filename and page number they came from.
- **📄 PDF Document Management** — Upload, list, and delete indexed PDF documents from a polished sidebar UI.
- **🧠 Hybrid RAG Retrieval** — Combines semantic similarity, MMR diversity search, and BM25 keyword search for high-quality context.
- **💾 Persistent Sessions** — Chat history persists in SQLite database in the backend.
- **🎨 Premium Dark UI** — Glassmorphism, smooth animations, and an emerald accent theme.
- **🏥 Health Monitoring** — The client indicator checks whether the API is online or down.
- **🐳 One-Command Setup** — Spin up the frontend, backend, database, and local LLM together with a single Docker Compose command.

---

## 🏛️ Architecture

```text
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│   client    │──────▶│     api     │──────▶│   ollama    │
│  (Next.js)  │  HTTP  │  (FastAPI)  │  HTTP  │  (Local LLM)│
│  :3000      │        │   :8000     │        │   :11434    │
└─────────────┘        └──────┬──────┘        └─────────────┘
                              │
                    ┌─────────┴─────────┐
                    │ ChromaDB (vectors)│
                    │ SQLite (sessions) │
                    └────────────────────┘
```

The `client` talks only to the `api`. The `api` handles PDF ingestion, embeddings, hybrid retrieval, and forwards prompts to `ollama` for generation — all within your local Docker network.

---

## 🚀 Getting Started

> **💡 Recommendation:** The easiest way to run the entire application is with **Docker Compose** — it starts the frontend, backend, ChromaDB storage, and Ollama (and automatically pulls the configured model) with a single command.
>
> If Ollama is already running on your machine and you want to run the application without Docker, you can start the complete application without Docker by running `pnpm run dev` from the project root. The command uses `concurrently` to launch and manage the frontend and backend together.
>
> If you'd rather run each service manually for development (hot-reload, debugging, etc.), see the [`client/README.md`](./client/README.md) and [`api/README.md`](./api/README.md) guides.

### 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** ([install guide](https://docs.docker.com/get-docker/))
- *(Optional if you want to run the application without Docker)* **Node.js** (v24 LTS), **pnpm** (v12.x), **Python** (v3.12+), **uv**, and **Ollama** installed locally.

### ⚙️ 1. Environment Setup

Copy the sample environment file at the project root to create your local configuration:

```bash
cp sample.env .env
```

Inside `.env`, you will find the variables used by `docker-compose.yml`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
OLLAMA_HOST=http://ollama:11434
LLM_MODEL=llama3.2
```

> **Note:** You can change these values in your `.env` file whenever needed. To use a different Ollama model, update `LLM_MODEL` to the model you want to run. If you are running the project with Docker on a VPS, set `ALLOWED_ORIGINS` to the exact URL you use to open the frontend in your browser, such as `http://YOUR_VPS_IP:3000` or `https://yourdomain.com`. Also set `NEXT_PUBLIC_API_URL` to your backend URL so the frontend connects to the correct API and the backend allows the correct frontend URL through CORS.

### 🐳 2. Running with Docker Compose (Recommended)

From the project root:

```bash
docker compose up -d --build
```

This will:

1. Build and start the **`api`** container on port `8000`.
2. Build and start the **`client`** container on port `3000`.
3. Start an **`ollama`** container on port `11434` for local LLM inference.
4. Run a one-off **`ollama-pull-model`** job that waits for Ollama to be ready and automatically pulls the model set in `LLM_MODEL`.
5. Persist data across restarts using named volumes for Ollama models, ChromaDB vectors, uploaded documents, and the SQLite database.

Once everything is up, open **[http://localhost:3000](http://localhost:3000)** in your browser.

To stop everything:

```bash
docker compose down
```

To stop everything **and** wipe all persisted data (models, vectors, uploads, sessions):

```bash
docker compose down -v
```

### 🛠️ Running Without Docker (Manual Dev Mode)

For active development with hot-reload on both services:

1. **Start Ollama locally** and pull the model matching `LLM_MODEL` in `api/.env`:

   ```bash
   ollama serve
   ollama pull llama3.2
   ```

2. **Run the API** (see [`api/README.md`](./api/README.md) for full details):

   ```bash
   cd api
   uv sync
   uv run uvicorn main:app --reload --port 8000
   ```

3. **Run the Client** in a separate terminal (see [`client/README.md`](./client/README.md) for full details):

   ```bash
   cd client
   pnpm install
   pnpm run dev
   ```

4. **Access the App:** Open **[http://localhost:3000](http://localhost:3000)**.

> **Important:** In manual mode, Ollama must already be running on your machine, and the model you pulled must exactly match `LLM_MODEL` in `api/.env`. Docker Compose handles this automatically — manual mode does not.

---

## 🌐 How to Use the App

1. **Check Connection:** Confirm the health status indicator in the sidebar shows a green "Connected" state.
2. **Upload a PDF:** Click the upload zone in the sidebar, or drag and drop a PDF file.
3. **Ask Questions:** Type a question about the document in the chat input and press Enter.
4. **View Sources:** Click "Show Sources" on any AI response to see the exact filename and page it was drawn from.
5. **New Chat:** Click "New Chat" in the sidebar to start a fresh conversation session.

For endpoint-level testing (Swagger UI, request/response formats, session management), see the [`api/README.md`](./api/README.md#-how-to-use-the-api).

---

## 🏗️ Tech Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| **Frontend** | Next.js 16 + React 19 | Chat UI built on the App Router |
| **Frontend** | TypeScript | Type-safe application code |
| **Frontend** | Tailwind CSS v4 | Utility-first, premium dark-theme styling |
| **Backend** | FastAPI + Uvicorn + SlowApi (Rate Limiting) | REST API and ASGI server |
| **Backend** | LangChain | RAG orchestration and document processing |
| **Backend** | ChromaDB | Persistent vector store for document chunks |
| **Backend** | BM25 | Keyword-based hybrid retrieval |
| **Backend** | SQLite | Persistent anonymous chat-session history |
| **AI** | Ollama | Fully local LLM inference |
| **AI** | Hugging Face Sentence Transformers | Local document embeddings |
| **Infra** | Docker Compose | One-command orchestration of all services |
| **Tooling** | pnpm v12 / uv | Package management for client / api |

---

## 📁 Project Structure

```text
.
├── client/                  # Next.js frontend — see client/README.md
│   ├── src/
│   ├── Dockerfile
│   └── sample.env
├── api/                     # FastAPI backend — see api/README.md
│   ├── main.py
│   ├── app/
│   ├── Dockerfile
│   └── sample.env
├── docker-compose.yml        # Orchestrates client, api, ollama & model pull
├── sample.env                 # Root environment variable reference
└── README.md                  # You are here
```

---

## 📚 Further Reading

- [`client/README.md`](./client/README.md) — Frontend setup, standalone Docker build, and project structure.
- [`api/README.md`](./api/README.md) — Backend setup, API usage via Swagger UI, and project structure.
