"""
Ultra-fast, zero-model, zero-API-key local text embedding service for AXON.
Uses scikit-learn HashingVectorizer to project text into 384-dimensional dense vectors
in milliseconds with zero PyTorch, zero LLM, and ultra-low memory.
"""
from typing import Optional
from sklearn.feature_extraction.text import HashingVectorizer

# 384-dimensional L2-normalized vectorizer matching ChromaDB index dimensions
_vectorizer = HashingVectorizer(n_features=384, alternate_sign=False, norm='l2')


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generates 384-dimensional text embeddings locally in milliseconds.
    100% offline, zero API keys, zero LLM models, ultra-low memory.
    """
    if not texts:
        return []

    matrix = _vectorizer.transform(texts)
    return matrix.toarray().tolist()