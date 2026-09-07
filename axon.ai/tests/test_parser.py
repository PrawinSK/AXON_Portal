import sys
from pathlib import Path

# Add the app/services directory to Python's import path
services_path = Path(__file__).resolve().parent.parent / "app" / "services"
sys.path.insert(0, str(services_path))

from pdf_parser import split_into_sections


test_resume = """
Prawin
prawin@example.com
+91 9876543210

EDUCATION
B.Tech Information Technology
Dr. Sivanthi Adithanar College of Engineering

EXPERIENCE
AI/ML Intern
Built REST APIs during my internship.
Developed a RAG pipeline using LangChain.
Worked on an AI Interviewer project.


PROJECTS
Axon AI Interviewer
Built a resume-based AI interviewer using RAG.

SKILLS
Python
Java
FastAPI
LangChain
ChromaDB

CERTIFICATIONS
Google Data Analytics
ChatGPT for Everyone
"""


sections = split_into_sections(test_resume)


print("\n========== PARSED SECTIONS ==========\n")

for section_name, content in sections.items():
    print(f"\n--- {section_name.upper()} ---")
    print(content)

print("\n=====================================\n")