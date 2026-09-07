from sentence_transformers import SentenceTransformer

_model = None


def get_model():
    global _model

    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True
    )

    return embeddings.tolist()