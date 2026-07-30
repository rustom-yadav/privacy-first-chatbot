from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# to set Base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # App General Settings
    APP_NAME: str = "Privacy-First-Chatbot"
    DEBUG: bool = True
    PORT: int = 8000

    # Storage Paths
    UPLOAD_DIR: Path = BASE_DIR / "uploaded_docs"
    CHROMA_DB_DIR: Path = BASE_DIR / "chroma_db"

    # AI Configs (Local defaults)
    OLLAMA_HOST: str = "http://localhost:11434"
    LLM_MODEL: str = "llama3.2"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100

    # Retrieval Pipeline Configs
    RETRIEVER_K: int = 20          # per-retriever fetch count
    ENSEMBLE_TOP_N: int = 15       # final chunk count after RRF fusion
    MAX_HISTORY_TURNS: int = 10    # max conversation turns (1 turn = 1 human + 1 AI)

    # override form .env files variables
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore extra variables
    )


settings = Settings()

# Ensure directories exist locally
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
