from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    chroma_persist_dir: str = "./chroma_db"
    max_upload_size_mb: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()