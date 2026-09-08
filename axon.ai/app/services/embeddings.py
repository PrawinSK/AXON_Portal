import os
from app.services.key_pool import key_pool


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generates text embeddings via Google Gemini API using key_pool rotation.
    Replaces heavy local PyTorch / sentence_transformers models to fit on Render's 512MB RAM tier.
    """
    if not texts:
        return []

    def call_embedding(client) -> list[list[float]]:
        res = client.models.embed_content(
            model="gemini-embedding-001",
            contents=texts
        )
        return [e.values for e in res.embeddings]

    return key_pool.execute(call_embedding)