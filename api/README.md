# 🛡️ Privacy-First Chatbot API

Welcome to the backend API of the **Privacy-First Chatbot**. This project provides a 100% local, secure Retrieval-Augmented Generation (RAG) pipeline. No data ever leaves your machine!

## 🚀 Getting Started Step-by-Step

Follow these simple steps to run the project on your machine.

### Step 1: Clone the Repository
First, clone the project to your local computer and navigate into the `api` folder:
```bash
git clone [privacy-first-chatbot](https://github.com/rustom-yadav/privacy-first-chatbot.git)
cd Privacy_First_Chatbot/api
```

### Step 2: Set Up Environment Variables
We need an environment file to store configuration. Copy the sample file to create your own:
```bash
cp sample.env .env
```

### Step 3: Install & Start Ollama (Required)
Because this chatbot guarantees privacy by running entirely on your machine, you need **Ollama** to run the AI models.
1. Download and install from [ollama.com](https://ollama.com/download).
2. Start the Ollama application.
3. Open your terminal and download a model (like `llama3.2`):
   ```bash
   ollama pull llama3.2
   ```
   > ⚠️ **IMPORTANT**: Whichever model you pull here (e.g., `llama3.2`), make sure the exact same name is set as the `LLM_MODEL` variable in your `.env` file! Otherwise, the application will not be able to generate answers.

*(Note: Ollama must be running on your main computer's OS, not inside Docker).*

---

### Step 4: Run the Application (Choose Option A or B)

#### Option A: Run using Docker (Recommended)
Docker is the easiest way to run the API. It packages Python, all libraries, and settings into a single container so you don't have to worry about installation errors or "it works on my machine" issues.

1. **Build the image:**
   This reads the `Dockerfile` and builds the app.
   ```bash
   docker build -t privacy-chatbot-api .
   ```

2. **Run the container:**
   The command depends on your Operating System because the container needs to talk to Ollama running on your host machine.

   **For Mac and Windows (using Docker Desktop with WSL2):**
   *(We use `host.docker.internal` to let the container reach your host's localhost).*
   ```bash
   docker run -p 8000:8000 \
     -e OLLAMA_HOST=http://host.docker.internal:11434 \
     -v $(pwd)/chroma_db:/app/chroma_db \
     -v $(pwd)/uploaded_docs:/app/uploaded_docs \
     privacy-chatbot-api
   ```

   **For Linux:**
   *(Linux Docker can share the host network directly using `--network="host"`).*
   ```bash
   docker run --network="host" \
     -v $(pwd)/chroma_db:/app/chroma_db \
     -v $(pwd)/uploaded_docs:/app/uploaded_docs \
     privacy-chatbot-api
   ```

#### Option B: Run Without Docker (Local Setup)
If you don't want to use Docker, you can run the Python app directly.

1. **Install Dependencies:**
   Make sure you have [uv](https://docs.astral.sh/uv/) installed, then run:
   ```bash
   uv sync
   ```
2. **Activate the Virtual Environment:**
   - Linux/Mac/WSL: `source .venv/bin/activate`
   - Pure Windows (CMD/PowerShell): `.venv\Scripts\activate`
3. **Start the Server:**
   ```bash
   uvicorn main:app --reload
   ```

---

## 🌐 How to Use (Swagger UI)
Once your server is running (via Docker or locally), you can test everything directly in your browser:

1. Open **[http://localhost:8000/docs](http://localhost:8000/docs)**
2. **Health Check (`GET /health`)**: Click "Try it out" and execute to ensure the API connects to Ollama successfully.
3. **Upload Document (`POST /api/document/upload`)**: Upload a PDF file. The system will save it and generate search embeddings.
4. **Chat (`POST /api/chat/message`)**: Send a question. The AI will search your uploaded PDF and answer based on your private document!
