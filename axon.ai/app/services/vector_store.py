import chromadb

from app.core.config import settings
from app.services.embeddings import embed_texts


_client = None


def get_client():
    global _client

    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir
        )

    return _client


def get_collection():
    return get_client().get_or_create_collection(
        name="resume_embeddings",
        metadata={
            "hnsw:space": "cosine"
        }
    )


def delete_candidate_vectors(candidate_id: str):
    collection = get_collection()

    existing = collection.get(
        where={"candidate_id": candidate_id}
    )

    if existing and existing.get("ids"):
        collection.delete(
            ids=existing["ids"]
        )


def store_chunks(chunks: list[dict]):
    if not chunks:
        return

    collection = get_collection()

    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]
    metadata = [c["metadata"] for c in chunks]

    embeddings = embed_texts(texts)

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadata
    )


def query_chunks(
    candidate_id: str,
    query_text: str,
    top_k: int = 3
):
    collection = get_collection()

    query_embedding = embed_texts([query_text])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={
            "candidate_id": candidate_id
        }
    )

    output = []

    if results["documents"] and results["documents"][0]:

        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            output.append({
                "chunk_text": doc,
                "section": meta["section"],
                "score": 1 - dist
            })

    return output