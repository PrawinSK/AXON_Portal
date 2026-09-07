from app.services.chunker import create_chunks

sections = {
    "education": "B.Tech IT",
    "skills": "Python, Java, React",
    "projects": "Axon AI Recruiter"
}

chunks = create_chunks("123", sections)

for c in chunks:
    print(c)