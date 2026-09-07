from app.services.llm_service import generate_interview_question

context = """
Skills

Python
Java
FastAPI

Projects

Axon AI Recruiter
"""

question = generate_interview_question(
    context,
    "Python"
)

print(question)