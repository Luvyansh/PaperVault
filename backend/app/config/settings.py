from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", "../.env"],  # check backend/.env first, then root/.env
        env_file_encoding="utf-8",
        extra="ignore"                 # ignore extra fields like POSTGRES_USER etc
    )

    # The full database connection string — this is what SQLAlchemy uses
    database_url: str = "postgresql://papervault:papervault@127.0.0.1:5433/papervault"

    # Redis connection — used by Celery for task queue
    redis_url: str = "redis://127.0.0.1:6379/0"

    # Qdrant vector database connection
    qdrant_url: str = "http://127.0.0.1:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "papers"

    # Which arxiv categories to fetch papers from
    arxiv_categories: str = "cs.*,physics.*,math.*,q-bio.*,q-fin.*,stat.*,eess.*,econ.*"
    arxiv_max_results_per_category: int = 100

    # LLM config — "local" uses Ollama, "cloud" uses Google AI Studio
    llm_mode: str = "local"
    google_ai_api_key: str = ""

    @property
    def category_list(self) -> list[str]:
        # Converts the comma string "cs.AI,cs.CL" into a Python list ["cs.AI", "cs.CL"]
        return [c.strip() for c in self.arxiv_categories.split(",")]


@lru_cache
def get_settings() -> Settings:
    # lru_cache means this only runs ONCE — same Settings object reused everywhere
    # Without this, every file would re-read .env on every call — slow and wasteful
    return Settings()