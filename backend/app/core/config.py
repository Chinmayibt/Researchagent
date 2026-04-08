from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openalex_email: str | None = Field(default=None, alias="OPENALEX_EMAIL")
    crossref_mailto: str | None = Field(default=None, alias="CROSSREF_MAILTO")
    source_timeout_seconds: int = Field(default=15, alias="SOURCE_TIMEOUT_SECONDS")
    openrouter_api_key: str | None = Field(default=None, alias="OPENROUTER_API_KEY")
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    cache_ttl_seconds: int = Field(default=1800, alias="CACHE_TTL_SECONDS")
    groq_model: str = Field(default="llama-3.1-8b-instant", alias="GROQ_MODEL")
    langgraph_max_retries: int = Field(default=2, alias="LANGGRAPH_MAX_RETRIES")
    langgraph_max_concurrency: int = Field(default=4, alias="LANGGRAPH_MAX_CONCURRENCY")

    neo4j_uri: str | None = Field(default=None, alias="NEO4J_URI")
    neo4j_user: str | None = Field(default=None, alias="NEO4J_USER")
    neo4j_password: str | None = Field(default=None, alias="NEO4J_PASSWORD")
    neo4j_database: str = Field(default="neo4j", alias="NEO4J_DATABASE")

    object_store_endpoint_url: str | None = Field(default=None, alias="OBJECT_STORE_ENDPOINT_URL")
    object_store_bucket: str | None = Field(default=None, alias="OBJECT_STORE_BUCKET")
    object_store_region: str = Field(default="us-east-1", alias="OBJECT_STORE_REGION")
    object_store_access_key_id: str | None = Field(default=None, alias="OBJECT_STORE_ACCESS_KEY_ID")
    object_store_secret_access_key: str | None = Field(default=None, alias="OBJECT_STORE_SECRET_ACCESS_KEY")

    faiss_index_path: str = Field(default="reports/faiss.index", alias="FAISS_INDEX_PATH")
    faiss_metadata_path: str = Field(default="reports/faiss_meta.json", alias="FAISS_METADATA_PATH")
    max_pdf_pages_per_paper: int = Field(default=12, alias="MAX_PDF_PAGES_PER_PAPER")
    max_assets_per_paper: int = Field(default=30, alias="MAX_ASSETS_PER_PAPER")
    max_pipeline_papers: int = Field(default=40, alias="MAX_PIPELINE_PAPERS")
    default_max_papers: int = Field(default=30, alias="DEFAULT_MAX_PAPERS")
    default_max_iterations: int = Field(default=3, alias="DEFAULT_MAX_ITERATIONS")
    request_timeout_seconds: int = Field(default=25, alias="REQUEST_TIMEOUT_SECONDS")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
