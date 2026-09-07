from fastapi import APIRouter, Depends, HTTPException, status
from app.models.auth import TaskCreateRequest, TaskResponse
from app.services.task_service import task_service
from app.services.auth_service import auth_service, require_role, get_current_user

router = APIRouter(prefix="/tasks", tags=["Remediation Tasks"])


@router.get("/my-tasks", response_model=list[TaskResponse])
def get_my_tasks(current_user: dict = Depends(require_role(["student"]))):
    """
    Returns remediation tasks assigned specifically to the authenticated student.
    Strict student profile boundary: cannot view other students' tasks.
    """
    student_id = current_user.get("sub")
    return task_service.get_student_tasks(student_id)


@router.get("/all", response_model=list[TaskResponse])
def get_all_tasks(current_user: dict = Depends(require_role(["staff", "hod"]))):
    """
    Returns all assigned remediation tasks across the department.
    Restricted to Staff and HOD.
    """
    return task_service.get_all_tasks()


@router.post("/assign", response_model=TaskResponse)
def assign_task(
    payload: TaskCreateRequest,
    current_user: dict = Depends(require_role(["staff", "hod"]))
):
    """
    Allows Staff or HOD to assign a targeted remediation task to a student.
    """
    student = auth_service.get_user_by_id(payload.student_id)
    if not student or student.get("role") != "student":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{payload.student_id}' not found."
        )

    task = task_service.create_task(
        student_id=student["id"],
        student_name=student["name"],
        assigned_by_name=f"{current_user.get('name')} ({current_user.get('role').upper()})",
        assigned_by_role=current_user.get("role"),
        target_skill=payload.target_skill,
        description=payload.description,
        due_date=payload.due_date
    )
    return task


@router.get("/students")
def get_department_students(current_user: dict = Depends(require_role(["staff", "hod"]))):
    """
    Returns comprehensive profile list of all students for Staff and HOD oversight.
    Includes technical readiness, weak skills, and remediation task stats.
    """
    students = auth_service.get_all_students()
    result = []
    
    # Enrich with interview performance metrics & active tasks
    for s in students:
        tasks = task_service.get_student_tasks(s["id"])
        pending_tasks = [t for t in tasks if t.status != "completed"]
        
        # Student specific metrics for demonstration
        if s["id"] == "stud-21it001":
            metrics = {
                "overall_score": 8.7,
                "readiness_band": "Placement Ready",
                "radar": {"depth": 8.8, "logic": 8.6, "communication": 8.7},
                "weak_skills": ["Microservices Circuit Breaker", "gRPC Protocol"],
                "interviews_completed": 4
            }
        elif s["id"] == "stud-21it015":
            metrics = {
                "overall_score": 7.8,
                "readiness_band": "Placement Ready",
                "radar": {"depth": 7.5, "logic": 8.0, "communication": 7.9},
                "weak_skills": ["Database Sharding", "Redis Caching"],
                "interviews_completed": 3
            }
        elif s["id"] == "stud-21it027":
            metrics = {
                "overall_score": 8.2,
                "readiness_band": "Placement Ready",
                "radar": {"depth": 8.4, "logic": 8.0, "communication": 8.2},
                "weak_skills": ["Kafka Partitioning", "Event Sourcing"],
                "interviews_completed": 3
            }
        elif s["id"] == "stud-21it042":
            metrics = {
                "overall_score": 6.9,
                "readiness_band": "Needs Work",
                "radar": {"depth": 6.5, "logic": 7.0, "communication": 7.2},
                "weak_skills": ["Distributed Idempotency", "Docker Networking"],
                "interviews_completed": 2
            }
        elif s["id"] == "stud-21it055":
            metrics = {
                "overall_score": 8.5,
                "readiness_band": "Placement Ready",
                "radar": {"depth": 8.6, "logic": 8.4, "communication": 8.5},
                "weak_skills": ["API Rate Limiting", "JWT Refresh Flows"],
                "interviews_completed": 4
            }
        elif s["id"] == "stud-21it078":
            metrics = {
                "overall_score": 8.8,
                "readiness_band": "Placement Ready",
                "radar": {"depth": 9.0, "logic": 8.6, "communication": 8.8},
                "weak_skills": ["Event-Driven CDC", "Debezium Invalidation"],
                "interviews_completed": 5
            }
        elif s["id"] == "stud-21cs042":
            metrics = {
                "overall_score": 8.4,
                "readiness_band": "Placement Ready",
                "radar": {"depth": 8.5, "logic": 8.0, "communication": 8.8},
                "weak_skills": ["Redis Invalidation", "Distributed Idempotency"],
                "interviews_completed": 4
            }
        elif s["id"] == "stud-21cs058":
            metrics = {
                "overall_score": 7.2,
                "readiness_band": "Needs Work",
                "radar": {"depth": 6.8, "logic": 7.5, "communication": 7.2},
                "weak_skills": ["System Design", "PostgreSQL Indexing"],
                "interviews_completed": 2
            }
        elif s["id"] == "stud-21cs014":
            metrics = {
                "overall_score": 8.9,
                "readiness_band": "Placement Ready",
                "radar": {"depth": 9.0, "logic": 8.8, "communication": 9.0},
                "weak_skills": ["Kafka Partitioning"],
                "interviews_completed": 5
            }
        else:
            metrics = {
                "overall_score": 7.5,
                "readiness_band": "Enrolled Candidate",
                "radar": {"depth": 7.2, "logic": 7.5, "communication": 7.8},
                "weak_skills": ["System Architecture", "API Caching"],
                "interviews_completed": 1
            }
            
        result.append({
            **s,
            "metrics": metrics,
            "tasks_count": len(tasks),
            "pending_tasks_count": len(pending_tasks)
        })
        
    return result
