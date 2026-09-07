from app.services.embeddings import embed_texts

texts = [
    "Python Developer",
    "Java Spring Boot",
    "React Project"
]

vectors = embed_texts(texts)

print("Total vectors:", len(vectors))
print("Vector length:", len(vectors[0]))
print(vectors[0][:10])   # First 10 values