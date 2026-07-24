from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.config import settings
from app.routes import chat, document 

app = FastAPI(
    title=settings.APP_NAME,
    description="Secure, local RAG pipeline using FastAPI, LangChain, and Ollama or HuggingFace Transformers",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS Middleware Setup
# connecting between client(3000) and api(8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Client URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers Mapping (Clean and Isolated)
app.include_router(document.router, prefix="/api/document", tags=["Document Ingestion (RAG)"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Chatbot"])

@app.get("/", tags=["Health Check"])
def health_check():
    return {
        "status": "healthy", 
        "app": settings.APP_NAME, 
        "local_llm": settings.LLM_MODEL
    }

if __name__ == "__main__":
    #  framework trigger to run in Script mode 
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)