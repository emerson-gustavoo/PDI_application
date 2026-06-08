"""Configuracao da aplicacao, carregada de variaveis de ambiente (.env)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    secret_key: str = "dev-secret-key-troque-em-producao"
    database_url: str = "sqlite:///./mentorpdi.db"

    # Integracao com IA
    ai_provider: str = "anthropic"          # anthropic | gemini | mock

    # Anthropic (Claude)
    anthropic_api_key: str = ""
    ai_model: str = "claude-sonnet-4-20250514"

    # Google Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"


settings = Settings()
