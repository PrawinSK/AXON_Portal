from typing import Optional
from pydantic import BaseModel, Field


class StudentLoginRequest(BaseModel):
    roll_number: str = Field(..., description="Student ERP Roll Number (e.g. 21CS042, 21IT001)")
    password: str = Field(..., description="Student password")


class StaffLoginRequest(BaseModel):
    email: str = Field(..., description="Staff official email address")
    password: str = Field(..., description="Staff password")


class HODLoginRequest(BaseModel):
    email: str = Field(..., description="HOD official email address")
    password: str = Field(..., description="HOD password")


class StudentCreateRequest(BaseModel):
    roll_number: str = Field(..., description="Institutional Roll Number (e.g. 21IT105)")
    name: str = Field(..., description="Student Full Name")
    password: str = Field(..., description="Initial student password")
    department: Optional[str] = "Information Technology"
    email: Optional[str] = None


class StaffCreateRequest(BaseModel):
    name: str = Field(..., description="Faculty Full Name (e.g. Mr. K. Anbarasan)")
    email: str = Field(..., description="Faculty Official Email Address")
    password: str = Field(..., description="Initial faculty password")
    department: Optional[str] = "Information Technology"


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    name: str
    department: str
    roll_number: Optional[str] = None


class UserProfile(BaseModel):
    user_id: str
    name: str
    role: str
    department: str
    email: Optional[str] = None
    roll_number: Optional[str] = None


class TaskCreateRequest(BaseModel):
    student_id: str
    target_skill: str
    description: str
    due_date: Optional[str] = "2026-10-15"


class TaskResponse(BaseModel):
    id: str
    student_id: str
    student_name: str
    assigned_by_name: str
    assigned_by_role: str
    target_skill: str
    description: str
    status: str  # 'assigned', 'in_progress', 'completed'
    due_date: Optional[str] = None
    created_at: str
