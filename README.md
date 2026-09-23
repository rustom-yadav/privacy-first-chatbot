# 🛡️ Privacy-First Chatbot

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge\&logo=docker\&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-black?style=for-the-badge\&logo=next.js\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=for-the-badge)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge\&logo=typescript\&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)

Welcome to the **Privacy-First Chatbot** — a fully local, Retrieval-Augmented Generation (RAG) chat application. Upload a PDF, ask questions about it, and get grounded answers with source attribution — without any of your data ever leaving your machine.

This is a monorepo containing two services:

* **[`client/`](./client/README.md)** — A Next.js 16 + React 19 + Tailwind CSS v4 frontend chat interface.
* **[`api/`](./api/README.md)** — A FastAPI + LangChain + ChromaDB + SQLite + Ollama backend RAG engine.

Both are orchestrated together via Docker Compose or pnpm concurrently along with **Ollama** for fully local LLM inference.

---

## ✨ Features

* **🔒 Privacy-First Design** — PDF processing, embeddings, chat history, and LLM inference all run locally. No data is sent to a cloud AI provider.

* **💬 Real-time Chat with Source Attribution** — Ask questions and get AI answers backed by the exact filename and page number they came from.

* **📄 PDF Document Management** — Upload, list, and delete indexed PDF documents from a polished sidebar UI.

* **🧠 Hybrid RAG Retrieval** — Combines semantic similarity, MMR diversity search, and BM25 keyword search for high-quality context.

* **💾 Persistent Sessions** — Chat history persists in SQLite database in the backend.

* **🎨 Premium Dark UI** — Glassmorphism, smooth animations, and an emerald accent theme.

* **🏥 Health Monitoring** — The client indicator checks whether the API is online or down.

* **🐳 One-Command Setup** — Spin up the frontend, backend, database, and local LLM together with a single docker command or with pnpm command.

---

## 🏛️ Architecture

```text
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│   client    │──────▶│     api     │──────▶│   ollama    │
│  (Next.js)  │  HTTP  │  (FastAPI)  │  HTTP  │  (Local LLM)│
│    :3000    │        │    :8000    │        │   :11434    │
└─────────────┘        └──────┬──────┘        └─────────────┘
                              │
                    ┌─────────┴─────────┐
                    │ ChromaDB (vectors)│
                    │ SQLite (sessions) │
                    └───────────────────┘
```

The `client` talks only to the `api`. The `api` handles PDF ingestion, embeddings, hybrid retrieval, and forwards prompts to `ollama` for generation — all within your Local or VPS machine.

---

## 🚀 Getting Started

Follow these step-by-step instructions to get the Privacy-First Chatbot running on your machine (Local or VPS).

### 📥 1. Clone the Repository

First, clone the code to your machine and open the folder. This step is required for all methods:

```bash
git clone https://github.com/rustom-yadav/privacy-first-chatbot.git

cd privacy-first-chatbot
```

---

### 🐳 Option A: Running with Docker (Easiest)

**Prerequisites:**

* **Docker** ([install guide](https://docs.docker.com/get-docker/))

#### Step 1: Environment Setup

Create the required environment file by copying the sample template for the root directory:

```bash
cp sample.env .env
```

> **Note:** If you are running the project on a VPS, set `ALLOWED_ORIGINS` in your `.env` to the exact URL you use to open the frontend, e.g., `https://yourdomain.com`.

#### Step 2: Start the App

To run the app without manually starting local servers and models, run:

```bash
docker compose up -d --build
```

This single command will:

1. Start the API (port 8000) and Client (port 3000).
2. Start an Ollama container and automatically pull the model specified in your `.env` (default: `llama3.2`).
3. Start the vector database (ChromaDB) and persist data.

Once it's up, open **http://localhost:3000** in your browser!

To stop everything:

```bash
docker compose down
```

---

### 🛠️ Option B: Running with pnpm (Manual Dev Mode)

**Prerequisites:**

* **Node.js** (v24 LTS)
* **pnpm** (v12.x)
* **Python** (v3.12+)
* **uv** (Python package manager)
* **Ollama** ([download here](https://ollama.com/download)) installed and running locally.

#### Step 1: Environment Setup

Create the required environment files for the API and Client:

```bash
cp client/sample.env client/.env.local
cp api/sample.env api/.env
```

> **Note:** If you are running the project on a VPS, set `ALLOWED_ORIGINS` in `api/.env` to the exact URL you use to open the frontend.

#### Step 2: Install Dependencies

We have created a single setup command that installs all dependencies for the entire project (Root, Client, and API) at once. Run this from the root directory:

```bash
pnpm run setup
```

#### Step 3: Start Ollama & Pull Model

Ensure the Ollama app is running on your laptop. Then, pull the model you specified in your `.env` files (default is `llama3.2`):

```bash
ollama serve
ollama pull llama3.2
```

> **Note:** The model pulled here MUST exactly match the `LLM_MODEL` variable in your `.env` files.

#### Step 4: Start the App

From the project root, simply run:

```bash
pnpm run dev
```

*This command uses `concurrently` to start both the Next.js frontend and the FastAPI backend side-by-side.*

#### Step 5: Access the App

Open **http://localhost:3000** in your browser!

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

| Layer        | Technology                                  | Purpose                                     |
| ------------ | ------------------------------------------- | ------------------------------------------- |
| **Frontend** | Next.js 16 + React 19                       | Chat UI built on the App Router             |
| **Frontend** | TypeScript                                  | Type-safe application code                  |
| **Frontend** | Tailwind CSS v4                             | Utility-first, premium dark-theme styling   |
| **Backend**  | FastAPI + Uvicorn + SlowApi (Rate Limiting) | REST API and ASGI server                    |
| **Backend**  | LangChain                                   | RAG orchestration and document processing   |
| **Backend**  | ChromaDB                                    | Persistent vector store for document chunks |
| **Backend**  | BM25                                        | Keyword-based hybrid retrieval              |
| **Backend**  | SQLite                                      | Persistent anonymous chat-session history   |
| **AI**       | Ollama                                      | Fully local LLM inference                   |
| **AI**       | Hugging Face Sentence Transformers          | Local document embeddings                   |
| **Infra**    | Docker Compose                              | One-command orchestration of all services   |
| **Tooling**  | pnpm v12 / uv                               | Package management for client / api         |

---

## 📁 Project Structure

```text
.
├── client/                   # Next.js frontend — see client/README.md
│   ├── src/
│   ├── Dockerfile
│   └── sample.env
├── api/                      # FastAPI backend — see api/README.md
│   ├── main.py
│   ├── app/
│   ├── Dockerfile
│   └── sample.env
├── docker-compose.yml        # Orchestrates client, api, ollama & model pull
├── sample.env                # Root environment variable reference
└── README.md                 # You are here
```

---

## 📚 Further Reading

* [`client/README.md`](./client/README.md) — Frontend setup, standalone Docker build, and project structure.
* [`api/README.md`](./api/README.md) — Backend setup, API usage via Swagger UI, and project structure.

---

## Author

**Rustom Yadav**

[rustomyadav@outlook.com](mailto:rustomyadav@outlook.com)
