import io
import re
from typing import List, Dict, Any
from fastapi import HTTPException, UploadFile, status
import pandas as pd
import fitz  # PyMuPDF


class MCQParserService:
    """
    Parses MCQ questions from Excel (.xlsx, .xls, .csv) and PDF documents.
    Extracts question text, choices (A, B, C, D), correct answer (if provided),
    and explanation.
    """

    async def validate_and_read_file(self, file: UploadFile) -> bytes:
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Question file exceeds maximum limit of 50 MiB."
            )
        return content

    def parse_mcqs(self, filename: str, content: bytes) -> List[Dict[str, Any]]:
        lower_name = filename.lower()
        if lower_name.endswith((".xlsx", ".xls", ".csv")):
            return self._parse_spreadsheet(filename, content)
        elif lower_name.endswith(".pdf"):
            return self._parse_pdf(content)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported question file format. Please upload an Excel (.xlsx, .xls, .csv) or PDF file."
            )

    def _parse_spreadsheet(self, filename: str, content: bytes) -> List[Dict[str, Any]]:
        try:
            if filename.lower().endswith(".csv"):
                df = pd.read_csv(io.BytesIO(content))
            else:
                df = pd.read_excel(io.BytesIO(content))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse Excel spreadsheet: {str(e)}"
            )

        col_map = {}
        for col in df.columns:
            clean = str(col).strip().lower().replace(" ", "_")
            if "question" in clean or clean in ["q", "prompt"]:
                col_map[col] = "question_text"
            elif clean in ["a", "opt_a", "option_a", "choice_a"]:
                col_map[col] = "option_a"
            elif clean in ["b", "opt_b", "option_b", "choice_b"]:
                col_map[col] = "option_b"
            elif clean in ["c", "opt_c", "option_c", "choice_c"]:
                col_map[col] = "option_c"
            elif clean in ["d", "opt_d", "option_d", "choice_d"]:
                col_map[col] = "option_d"
            elif "answer" in clean or clean in ["ans", "correct", "key"]:
                col_map[col] = "correct_answer"
            elif "explanation" in clean or clean in ["solution", "reason"]:
                col_map[col] = "explanation"
            elif "topic" in clean or clean in ["subject", "category"]:
                col_map[col] = "topic"

        df = df.rename(columns=col_map)
        records: List[Dict[str, Any]] = []

        for _, row in df.iterrows():
            q_text = str(row.get("question_text", "")).strip()
            if not q_text or q_text.lower() == "nan":
                continue

            options = []
            for opt_key in ["option_a", "option_b", "option_c", "option_d"]:
                val = str(row.get(opt_key, "")).strip()
                if val and val.lower() != "nan":
                    options.append(val)

            # Check if options were combined in a single column
            if len(options) < 2 and "options" in row:
                raw_opts = str(row["options"]).split(";")
                options = [o.strip() for o in raw_opts if o.strip()]

            if len(options) < 2:
                continue

            ans = str(row.get("correct_answer", "")).strip()
            if ans.lower() == "nan":
                ans = ""
            elif ans.upper() in ["A", "B", "C", "D"]:
                idx = {"A": 0, "B": 1, "C": 2, "D": 3}[ans.upper()]
                if idx < len(options):
                    ans = options[idx]

            explanation = str(row.get("explanation", "")).strip()
            if explanation.lower() == "nan":
                explanation = ""

            topic = str(row.get("topic", "General Computer Science")).strip()
            if topic.lower() == "nan":
                topic = "General Computer Science"

            records.append({
                "question_text": q_text,
                "options": options,
                "correct_answer": ans,
                "explanation": explanation,
                "topic": topic
            })

        return records

    def _parse_pdf(self, content: bytes) -> List[Dict[str, Any]]:
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            full_text = ""
            for page in doc:
                full_text += page.get_text("text") + "\n"
            doc.close()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read PDF question file: {str(e)}"
            )

        # Parse text blocks into questions
        lines = [l.strip() for l in full_text.split("\n") if l.strip()]
        records: List[Dict[str, Any]] = []

        current_q: Dict[str, Any] = {}
        for line in lines:
            # Check for new question pattern: e.g. "1. What is..." or "Q1. What is..."
            q_match = re.match(r"^(?:Q\s*[\d]+[\.:\)]|\d+[\.:\)])\s*(.+)", line, re.IGNORECASE)
            opt_match = re.match(r"^[(\[]?([A-Da-d])[)\]\.:\-]\s*(.+)", line)
            ans_match = re.match(r"^(?:Answer|Ans|Correct(?:\s*Answer)?)\s*[:=\-]\s*([A-Za-z0-9\s\.\-]+)", line, re.IGNORECASE)

            if q_match:
                if current_q and current_q.get("question_text") and len(current_q.get("options", [])) >= 2:
                    records.append(current_q)
                current_q = {
                    "question_text": q_match.group(1).strip(),
                    "options": [],
                    "correct_answer": "",
                    "explanation": "",
                    "topic": "General IT / Computer Science"
                }
            elif opt_match and current_q:
                current_q["options"].append(opt_match.group(2).strip())
            elif ans_match and current_q:
                ans_val = ans_match.group(1).strip()
                # If answer is a letter like 'A', find matching option if possible
                if len(ans_val) == 1 and ans_val.upper() in ["A", "B", "C", "D"]:
                    idx = ord(ans_val.upper()) - ord("A")
                    if idx < len(current_q["options"]):
                        current_q["correct_answer"] = current_q["options"][idx]
                    else:
                        current_q["correct_answer"] = ans_val.upper()
                else:
                    current_q["correct_answer"] = ans_val
            elif current_q and not current_q["options"]:
                # Append multi-line question text
                current_q["question_text"] += " " + line

        if current_q and current_q.get("question_text") and len(current_q.get("options", [])) >= 2:
            records.append(current_q)

        return records


mcq_parser = MCQParserService()
