import json
from pathlib import Path
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
from app.models.auth import AuthResponse, UserProfile

security_bearer = HTTPBearer(auto_error=False)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"


class AuthService:
    """
    Manages institutional user registry with bcrypt-hashed credentials and file persistence.
    Enforces distinct authentication surfaces for Student, Staff, and HOD.
    """
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        # Pre-compute common hashes once for fast startup
        student_default_hash = hash_password("student@123")
        staff_default_hash = hash_password("staff@123")
        hod_default_hash = hash_password("hod@123")

        self._users = {
            # IT Department Students
            "stud-21it001": {
                "id": "stud-21it001",
                "role": "student",
                "name": "Kavitha S.",
                "roll_number": "21IT001",
                "email": "kavitha.21it@axon.edu",
                "department": "Information Technology",
                "password_hash": student_default_hash
            },
            "stud-21it015": {
                "id": "stud-21it015",
                "role": "student",
                "name": "Dinesh Kumar R.",
                "roll_number": "21IT015",
                "email": "dinesh.21it@axon.edu",
                "department": "Information Technology",
                "password_hash": student_default_hash
            },
            "stud-21it027": {
                "id": "stud-21it027",
                "role": "student",
                "name": "Bhavani Devi",
                "roll_number": "21IT027",
                "email": "bhavani.21it@axon.edu",
                "department": "Information Technology",
                "password_hash": student_default_hash
            },
            "stud-21it042": {
                "id": "stud-21it042",
                "role": "student",
                "name": "Vigneshwaran P.",
                "roll_number": "21IT042",
                "email": "vignesh.21it@axon.edu",
                "department": "Information Technology",
                "password_hash": student_default_hash
            },
            "stud-21it055": {
                "id": "stud-21it055",
                "role": "student",
                "name": "Sneha R.",
                "roll_number": "21IT055",
                "email": "sneha.21it@axon.edu",
                "department": "Information Technology",
                "password_hash": student_default_hash
            },
            "stud-21it063": {
                "id": "stud-21it063",
                "role": "student",
                "name": "Manoj Prabhakar",
                "roll_number": "21IT063",
                "email": "manoj.21it@axon.edu",
                "department": "Information Technology",
                "password_hash": student_default_hash
            },
            "stud-21it078": {
                "id": "stud-21it078",
                "role": "student",
                "name": "Divya Bharathi",
                "roll_number": "21IT078",
                "email": "divya.21it@axon.edu",
                "department": "Information Technology",
                "password_hash": student_default_hash
            },
            "stud-21it092": {
                "id": "stud-21it092",
                "role": "student",
                "name": "Harish V.",
                "roll_number": "21IT092",
                "email": "harish.21it@axon.edu",
                "department": "Information Technology",
                "password_hash": student_default_hash
            },
            # CS Students
            "stud-21cs042": {
                "id": "stud-21cs042",
                "role": "student",
                "name": "Arjun Kumar",
                "roll_number": "21CS042",
                "email": "arjun.21cs@axon.edu",
                "department": "Computer Science & Engineering",
                "password_hash": student_default_hash
            },
            "stud-21cs058": {
                "id": "stud-21cs058",
                "role": "student",
                "name": "Priya Sundaram",
                "roll_number": "21CS058",
                "email": "priya.21cs@axon.edu",
                "department": "Computer Science & Engineering",
                "password_hash": student_default_hash
            },
            "stud-21cs014": {
                "id": "stud-21cs014",
                "role": "student",
                "name": "Ananya Verma",
                "roll_number": "21CS014",
                "email": "ananya.21cs@axon.edu",
                "department": "Computer Science & Engineering",
                "password_hash": student_default_hash
            },
            "stud-21cs033": {
                "id": "stud-21cs033",
                "role": "student",
                "name": "Karthik Raja",
                "roll_number": "21CS033",
                "email": "karthik.21cs@axon.edu",
                "department": "Computer Science & Engineering",
                "password_hash": student_default_hash
            },
            # Staff: Miss. Ramya Tamizharasi (IT Department)
            "staff-001": {
                "id": "staff-001",
                "role": "staff",
                "name": "Miss. Ramya Tamizharasi",
                "email": "ramya.staff@axon.edu",
                "department": "Information Technology",
                "password_hash": staff_default_hash
            },
            # HOD: Dr. Selvi (HOD of IT Department)
            "hod-001": {
                "id": "hod-001",
                "role": "hod",
                "name": "Dr. Selvi",
                "email": "hod.it@axon.edu",
                "department": "Information Technology",
                "password_hash": hod_default_hash
            }
        }

        # If persistent storage exists, load and merge created accounts
        if USERS_FILE.exists():
            try:
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    stored = json.load(f)
                    if isinstance(stored, dict):
                        self._users.update(stored)
            except Exception as e:
                print(f"[AuthService] Warning loading users.json: {e}")

        # Ensure seed/merged users are saved to disk
        self._save_users()

    def _save_users(self):
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._users, f, indent=2)
        except Exception as e:
            print(f"[AuthService] Error saving users.json: {e}")

    def authenticate_student(self, roll_number: str, password: str) -> AuthResponse:
        clean_roll = roll_number.strip().upper()
        target = None
        for u in self._users.values():
            if u.get("role") == "student" and u.get("roll_number", "").upper() == clean_roll:
                target = u
                break

        if not target or not verify_password(password, target["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid roll number or password."
            )

        token = create_access_token(
            user_id=target["id"],
            role=target["role"],
            department=target["department"],
            name=target["name"],
            roll_number=target["roll_number"]
        )

        return AuthResponse(
            access_token=token,
            role="student",
            user_id=target["id"],
            name=target["name"],
            department=target["department"],
            roll_number=target["roll_number"]
        )

    def authenticate_staff(self, email: str, password: str) -> AuthResponse:
        clean_email = email.strip().lower()
        target = None
        for u in self._users.values():
            if u.get("role") == "staff":
                # Support both ramya.staff@axon.edu and legacy staff@axon.edu
                if u.get("email", "").lower() == clean_email or clean_email in ["staff@axon.edu", "ramya.staff@axon.edu"]:
                    target = u
                    break

        if not target or not verify_password(password, target["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid staff credentials."
            )

        token = create_access_token(
            user_id=target["id"],
            role=target["role"],
            department=target["department"],
            name=target["name"]
        )

        return AuthResponse(
            access_token=token,
            role="staff",
            user_id=target["id"],
            name=target["name"],
            department=target["department"]
        )

    def authenticate_hod(self, email: str, password: str) -> AuthResponse:
        clean_email = email.strip().lower()
        target = None
        for u in self._users.values():
            if u.get("role") == "hod":
                # Support both hod.it@axon.edu and legacy hod.cs@axon.edu
                if u.get("email", "").lower() == clean_email or clean_email in ["hod.it@axon.edu", "hod.cs@axon.edu"]:
                    target = u
                    break

        if not target or not verify_password(password, target["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid HOD credentials."
            )

        token = create_access_token(
            user_id=target["id"],
            role=target["role"],
            department=target["department"],
            name=target["name"]
        )

        return AuthResponse(
            access_token=token,
            role="hod",
            user_id=target["id"],
            name=target["name"],
            department=target["department"]
        )

    def create_student(
        self,
        roll_number: str,
        name: str,
        password: str,
        department: str = "Information Technology",
        email: Optional[str] = None
    ) -> dict:
        """
        Creates a new student profile on Axon with bcrypt password.
        The student can immediately log into the platform.
        """
        clean_roll = roll_number.strip().upper()
        for u in self._users.values():
            if u.get("role") == "student" and u.get("roll_number", "").upper() == clean_roll:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Student with Roll Number '{clean_roll}' already exists."
                )

        user_id = f"stud-{clean_roll.lower()}"
        student_obj = {
            "id": user_id,
            "role": "student",
            "name": name.strip(),
            "roll_number": clean_roll,
            "email": email.strip() if email else f"{clean_roll.lower()}@axon.edu",
            "department": department,
            "password_hash": hash_password(password.strip())
        }
        self._users[user_id] = student_obj
        self._save_users()

        return {
            "id": student_obj["id"],
            "name": student_obj["name"],
            "roll_number": student_obj["roll_number"],
            "department": student_obj["department"],
            "email": student_obj["email"],
            "role": "student"
        }

    def create_staff(
        self,
        name: str,
        email: str,
        password: str,
        department: str = "Information Technology"
    ) -> dict:
        """
        Creates a new faculty/staff profile on Axon with bcrypt password.
        Strictly restricted to HOD. The staff can immediately log into the platform.
        """
        clean_email = email.strip().lower()
        for u in self._users.values():
            if u.get("role") in ["staff", "hod"] and u.get("email", "").lower() == clean_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Staff member with Email '{clean_email}' already exists."
                )

        import uuid
        staff_id = f"staff-{uuid.uuid4().hex[:6]}"
        staff_obj = {
            "id": staff_id,
            "role": "staff",
            "name": name.strip(),
            "email": clean_email,
            "department": department,
            "password_hash": hash_password(password.strip())
        }
        self._users[staff_id] = staff_obj
        self._save_users()

        return {
            "id": staff_obj["id"],
            "name": staff_obj["name"],
            "email": staff_obj["email"],
            "department": staff_obj["department"],
            "role": "staff"
        }

    def get_all_staff(self) -> list[dict]:
        """Returns all faculty and staff members in the department (HOD/Staff view)."""
        return [
            {
                "id": u["id"],
                "name": u["name"],
                "email": u.get("email", ""),
                "department": u["department"],
                "role": u["role"]
            }
            for u in self._users.values()
            if u.get("role") in ["staff", "hod"]
        ]

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        return self._users.get(user_id)

    def get_all_students(self) -> list[dict]:
        """Returns all students in the department (Staff/HOD view)."""
        return [
            {
                "id": u["id"],
                "name": u["name"],
                "roll_number": u.get("roll_number", ""),
                "department": u["department"],
                "email": u.get("email", "")
            }
            for u in self._users.values()
            if u.get("role") == "student"
        ]


auth_service = AuthService()


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> dict:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required. Please log in."
        )

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired. Please log in again."
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token."
        )


def require_role(allowed_roles: list[str]):
    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {', '.join(allowed_roles)}. Your role is '{user_role}'."
            )
        return current_user

    return role_checker
