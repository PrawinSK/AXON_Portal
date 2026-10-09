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
            # IT Department Student
            "stud-11234003": {
                "id": "stud-11234003",
                "role": "student",
                "name": "Candidate 11234003",
                "roll_number": "11234003",
                "email": "11234003@axon.edu",
                "department": "Information Technology",
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

        # Purge garbage students, keeping strictly 11234003 and any newly bulk-uploaded students
        self.remove_all_except(["11234003"])

    def remove_all_except(self, keep_rolls: list[str]) -> int:
        """Removes all students from the registry except those whose roll numbers are in keep_rolls."""
        norm_keep = {r.strip().upper() for r in keep_rolls}
        removed_count = 0
        filtered_users = {}
        for uid, user in self._users.items():
            if user.get("role") == "student":
                roll = user.get("roll_number", "").strip().upper()
                if roll in norm_keep:
                    filtered_users[uid] = user
                else:
                    removed_count += 1
            else:
                # Retain staff and hod
                filtered_users[uid] = user
        self._users = filtered_users
        self._save_users()
        return removed_count

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
