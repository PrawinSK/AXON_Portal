import hashlib
import datetime
from datetime import datetime, timezone

def create_chunks(candidate_id: str, sections: dict, source: str = "resume_upload") -> list[dict]:

    chunks = []
    timestamp = datetime.now(timezone.utc).isoformat()

    for section, text in sections.items():

        if not text.strip():
            continue

        chunk_id = hashlib.sha256(
            f"{candidate_id}:{section}:{text}".encode()
        ).hexdigest()[:16]

        chunks.append({
            "chunk_id": chunk_id,
            "text": text,
            "metadata": {
                "candidate_id": candidate_id,
                "chunk_id": chunk_id,
                "section": section,
                "source": source,
                "timestamp": timestamp
            }
        })

    return chunks