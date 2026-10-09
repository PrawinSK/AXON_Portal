import io
import re
from typing import List, Dict, Any
from fastapi import HTTPException, UploadFile, status
import pandas as pd
import fitz  # PyMuPDF
from app.services.auth_service import auth_service

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MiB
MAX_RECORDS = 300


class StudentBulkUploadService:
    """
    Parses and bulk registers students from Excel (.xlsx, .xls, .csv) and PDF files.
    Enforces a strict 50 MiB file size limit (HTTP 413) and a maximum of 300 records per batch.
    """

    async def validate_and_read_file(self, file: UploadFile) -> bytes:
        """Validates file size <= 50 MiB and reads raw bytes."""
        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of 50 MiB (received {len(content) / (1024 * 1024):.2f} MiB)."
            )
        return content

    def parse_records(self, filename: str, content: bytes) -> List[Dict[str, str]]:
        """Extracts student records from Excel or PDF byte stream."""
        lower_name = filename.lower()
        if lower_name.endswith((".xlsx", ".xls", ".csv")):
            return self._parse_spreadsheet(filename, content)
        elif lower_name.endswith(".pdf"):
            return self._parse_pdf(content)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format. Please upload an Excel (.xlsx, .xls, .csv) or PDF document."
            )

    def _parse_spreadsheet(self, filename: str, content: bytes) -> List[Dict[str, str]]:
        """Parses tabular spreadsheet into normalized student records."""
        try:
            if filename.lower().endswith(".csv"):
                df = pd.read_csv(io.BytesIO(content))
            else:
                df = pd.read_excel(io.BytesIO(content))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse spreadsheet file: {str(e)}"
            )

        # Standardize column headers
        col_map = {}
        for col in df.columns:
            cleaned = str(col).strip().lower().replace(" ", "_").replace(".", "")
            if any(k in cleaned for k in ["roll", "reg_no", "regno", "id", "roll_no", "roll_number"]):
                col_map[col] = "roll_number"
            elif any(k in cleaned for k in ["name", "student_name", "candidate"]):
                col_map[col] = "name"
            elif any(k in cleaned for k in ["dept", "department", "branch"]):
                col_map[col] = "department"
            elif any(k in cleaned for k in ["pass", "password", "pwd"]):
                col_map[col] = "password"
            elif any(k in cleaned for k in ["email", "mail"]):
                col_map[col] = "email"

        df = df.rename(columns=col_map)
        records: List[Dict[str, str]] = []

        for _, row in df.iterrows():
            roll = str(row.get("roll_number", "")).strip()
            name = str(row.get("name", "")).strip()
            # Clean floating point suffixes from Excel (e.g. 11234003.0)
            if roll.endswith(".0"):
                roll = roll[:-2]
            if not roll or roll.lower() == "nan":
                continue
            if not name or name.lower() == "nan":
                name = f"Student {roll}"

            dept = str(row.get("department", "")).strip()
            if not dept or dept.lower() == "nan":
                dept = "Information Technology"

            password = str(row.get("password", "")).strip()
            if not password or password.lower() == "nan":
                password = "student@123"

            email = str(row.get("email", "")).strip()
            if not email or email.lower() == "nan":
                email = f"{roll.lower()}@axon.edu"

            records.append({
                "roll_number": roll,
                "name": name,
                "department": dept,
                "password": password,
                "email": email
            })

        return records

    def _parse_pdf(self, content: bytes) -> List[Dict[str, str]]:
        """Parses text tables/lines from PDF files into student records."""
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            lines: List[str] = []
            for page in doc:
                text = page.get_text("text")
                for line in text.split("\n"):
                    clean = line.strip()
                    if clean:
                        lines.append(clean)
            doc.close()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read PDF document: {str(e)}"
            )

        records: List[Dict[str, str]] = []
        for line in lines:
            if any(h in line.lower() for h in ["roll number", "roll_no", "student name", "department", "s.no"]):
                continue

            parts = [p.strip() for p in re.split(r"[,|\t;]+", line) if p.strip()]
            if len(parts) >= 2:
                roll_idx = -1
                for idx, p in enumerate(parts):
                    if re.match(r"^[0-9A-Za-z]{5,15}$", p) and any(c.isdigit() for c in p):
                        roll_idx = idx
                        break

                if roll_idx != -1:
                    roll = parts[roll_idx]
                    other_parts = [p for i, p in enumerate(parts) if i != roll_idx]
                    name = other_parts[0] if len(other_parts) > 0 else f"Student {roll}"
                    dept = other_parts[1] if len(other_parts) > 1 else "Information Technology"
                    password = other_parts[2] if len(other_parts) > 2 else "student@123"

                    records.append({
                        "roll_number": roll,
                        "name": name,
                        "department": dept,
                        "password": password,
                        "email": f"{roll.lower()}@axon.edu"
                    })

        return records

    def process_and_create(self, records: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Validates records, enforces max 300 records cap, and adds students to the portal.
        """
        if not records:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid student records could be extracted from the uploaded document."
            )

        if len(records) > MAX_RECORDS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum allowed batch size is {MAX_RECORDS} students. Upload contains {len(records)} records."
            )

        added = []
        skipped = []
        errors = []

        existing_rolls = {
            u.get("roll_number", "").upper()
            for u in auth_service._users.values()
            if u.get("role") == "student"
        }

        for rec in records:
            roll = rec["roll_number"].strip().upper()
            if not roll or len(roll) < 3:
                skipped.append({"record": rec, "reason": "Invalid roll number format"})
                continue

            if roll in existing_rolls:
                skipped.append({"record": rec, "reason": f"Roll number {roll} already exists"})
                continue

            try:
                created = auth_service.create_student(
                    roll_number=roll,
                    name=rec["name"],
                    password=rec["password"],
                    department=rec["department"],
                    email=rec.get("email")
                )
                existing_rolls.add(roll)
                added.append(created)
            except Exception as e:
                errors.append({"roll_number": roll, "error": str(e)})

        return {
            "total_extracted": len(records),
            "added_count": len(added),
            "skipped_count": len(skipped),
            "errors_count": len(errors),
            "added_students": added,
            "skipped": skipped,
            "errors": errors
        }


student_bulk_service = StudentBulkUploadService()
