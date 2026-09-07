from fastapi import APIRouter, Depends
from app.models.auth import (
    StudentLoginRequest,
    StaffLoginRequest,
    HODLoginRequest,
    StudentCreateRequest,
    StaffCreateRequest,
    AuthResponse
)
from app.services.auth_service import auth_service, get_current_user, require_role

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/student/login", response_model=AuthResponse)
def login_student(payload: StudentLoginRequest):
    """Authenticates student using institutional Roll Number and Password."""
    return auth_service.authenticate_student(payload.roll_number, payload.password)


@router.post("/staff/login", response_model=AuthResponse)
def login_staff(payload: StaffLoginRequest):
    """Authenticates staff member using institutional Email and Password."""
    return auth_service.authenticate_staff(payload.email, payload.password)


@router.post("/hod/login", response_model=AuthResponse)
def login_hod(payload: HODLoginRequest):
    """Authenticates HOD using institutional Email and Password."""
    return auth_service.authenticate_hod(payload.email, payload.password)


@router.post("/students/create")
def create_student(
    payload: StudentCreateRequest,
    current_user: dict = Depends(require_role(["staff", "hod"]))
):
    """
    Allows Staff or HOD to register a new student with Roll Number and Password.
    The created profile is immediately active and can log into Axon.
    """
    return auth_service.create_student(
        roll_number=payload.roll_number,
        name=payload.name,
        password=payload.password,
        department=payload.department or "Information Technology",
        email=payload.email
    )


@router.post("/staff/create")
def create_staff(
    payload: StaffCreateRequest,
    current_user: dict = Depends(require_role(["hod"]))
):
    """
    Allows HOD to register a new faculty/staff member with Email and Password.
    Strictly restricted to HOD. The created faculty member can immediately log in.
    """
    return auth_service.create_staff(
        name=payload.name,
        email=payload.email,
        password=payload.password,
        department=payload.department or "Information Technology"
    )


@router.get("/staff/all")
def get_all_staff(current_user: dict = Depends(require_role(["staff", "hod"]))):
    """
    Returns list of all faculty/staff members in the department.
    Accessible to both Staff and HOD.
    """
    return auth_service.get_all_staff()


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Returns the authenticated user's verified token claims."""
    return current_user
