from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    grok_api_key: str = ""
    grok_api_base: str = "https://api.groq.com/openai/v1"
    grok_model: str = "llama-3.3-70b-versatile"
    gemini_model: str = "gemini-3.5-flash"
    gemini_fallback_models: list[str] = [
        "gemini-3.5-flash",
        "gemini-flash-latest",
        "gemini-3.5-flash-lite",
        "gemini-3.7-flash",
        "gemini-3.8-flash"
    ]
    gemini_keys_file: str = ".env.keys"
    chroma_persist_dir: str = "./chroma_db"
    max_upload_size_mb: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()