import fitz  # PyMuPDF
import re

SECTION_HEADERS = {
    "education": [
        "education",
        "academic background",
        "academic qualification",
        "qualification",
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
        "internship",
        "internships",
    ],

    "projects": [
        "projects",
        "project",
        "academic projects",
        "personal projects",
        "major projects",
        "minor projects",
    ],

    "skills": [
        "skills",
        "technical skills",
        "core competencies",
        "technologies",
        "technical expertise",
        "tech stack",
    ],

    "certifications": [
        "certifications",
        "certificates",
        "licenses",
        "courses",
        "training",
    ],
}


class ResumeParsingError(Exception):
    pass


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise ResumeParsingError(f"Could not open PDF: {e}")

    if doc.page_count == 0:
        raise ResumeParsingError("PDF has no pages")

    full_text = ""

    for page in doc:
        full_text += page.get_text("text") + "\n"

    doc.close()

    if not full_text.strip():
        raise ResumeParsingError("PDF contains no extractable text")

    return full_text


def extract_contact_info(text: str) -> dict:
    email_match = re.search(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        text,
    )

    phone_match = re.search(
        r"(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}",
        text,
    )

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    name = lines[0] if lines else "Unknown"

    return {
        "name": name,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
    }


def split_into_sections(text: str) -> dict:
    lines = text.split("\n")

    sections = {
        "personal_information": []
    }

    current_section = "personal_information"

    for line in lines:

        clean = line.strip().lower()

        if not clean:
            continue

        matched = False

        for section_name, keywords in SECTION_HEADERS.items():

            # Match if any keyword appears in the heading
            if any(keyword in clean for keyword in keywords):
                current_section = section_name
                sections.setdefault(current_section, [])
                matched = True
                break

        if not matched:
            sections.setdefault(current_section, []).append(line)

    return {
        section: "\n".join(content).strip()
        for section, content in sections.items()
        if "\n".join(content).strip()
    }