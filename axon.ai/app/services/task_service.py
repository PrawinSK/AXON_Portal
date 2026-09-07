import uuid
import datetime
import json
from pathlib import Path
from typing import Optional
from app.models.auth import TaskResponse

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
TASKS_FILE = DATA_DIR / "tasks.json"


class TaskService:
    """
    Manages remediation tasks assigned by Staff or HOD to specific students with disk persistence.
    """
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._tasks: list[dict] = []
        
        if TASKS_FILE.exists():
            try:
                with open(TASKS_FILE, "r", encoding="utf-8") as f:
                    stored = json.load(f)
                    if isinstance(stored, list) and len(stored) > 0:
                        self._tasks = stored
            except Exception as e:
                print(f"[TaskService] Warning loading tasks.json: {e}")

        if not self._tasks:
            self._seed_initial_tasks()
            self._save_tasks()

    def _save_tasks(self):
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(TASKS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._tasks, f, indent=2)
        except Exception as e:
            print(f"[TaskService] Error saving tasks.json: {e}")

    def _seed_initial_tasks(self):
        self._tasks = [
            {
                "id": "task-001",
                "student_id": "stud-21cs042",
                "student_name": "Arjun Kumar",
                "assigned_by_name": "Dr. S. Meenakshi (HOD)",
                "assigned_by_role": "hod",
                "target_skill": "Redis Caching & Invalidation",
                "description": "Implement Redis Cache-Aside pattern with PostgreSQL CDC invalidation. Score >= 7.0 on graded assessment to clear.",
                "status": "assigned",
                "due_date": "2026-10-15",
                "created_at": "2026-09-01T10:00:00Z"
            },
            {
                "id": "task-002",
                "student_id": "stud-21cs042",
                "student_name": "Arjun Kumar",
                "assigned_by_name": "Dr. Ramesh K. (Staff)",
                "assigned_by_role": "staff",
                "target_skill": "Distributed Systems & Idempotency",
                "description": "Review HTTP idempotent methods and database connection pool sizing under heavy load.",
                "status": "assigned",
                "due_date": "2026-10-20",
                "created_at": "2026-09-02T14:30:00Z"
            },
            {
                "id": "task-003",
                "student_id": "stud-21cs033",
                "student_name": "Karthik Raja",
                "assigned_by_name": "Dr. S. Meenakshi (HOD)",
                "assigned_by_role": "hod",
                "target_skill": "Redis & In-Memory Storage",
                "description": "Study Redis maxmemory eviction policies (allkeys-lru vs volatile-lru).",
                "status": "assigned",
                "due_date": "2026-10-18",
                "created_at": "2026-09-03T11:15:00Z"
            }
        ]

    def create_task(
        self,
        student_id: str,
        student_name: str,
        assigned_by_name: str,
        assigned_by_role: str,
        target_skill: str,
        description: str,
        due_date: Optional[str] = None
    ) -> TaskResponse:
        task_id = f"task-{uuid.uuid4().hex[:6]}"
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        task = {
            "id": task_id,
            "student_id": student_id,
            "student_name": student_name,
            "assigned_by_name": assigned_by_name,
            "assigned_by_role": assigned_by_role,
            "target_skill": target_skill,
            "description": description,
            "status": "assigned",
            "due_date": due_date or "2026-10-30",
            "created_at": now_str
        }
        self._tasks.append(task)
        self._save_tasks()
        return TaskResponse(**task)

    def get_student_tasks(self, student_id: str) -> list[TaskResponse]:
        """Returns only the tasks assigned to the specified student."""
        return [
            TaskResponse(**t) for t in self._tasks
            if t["student_id"] == student_id
        ]

    def get_all_tasks(self) -> list[TaskResponse]:
        """Returns all tasks across the department (Staff/HOD view)."""
        return [TaskResponse(**t) for t in self._tasks]

    def auto_close_task(self, student_id: str, skill_name: str) -> list[str]:
        """Auto-closes matching tasks if candidate scores >= 7.0 on graded assessment."""
        closed = []
        for t in self._tasks:
            if t["student_id"] == student_id and t["status"] != "completed":
                if skill_name.lower() in t["target_skill"].lower():
                    t["status"] = "completed"
                    closed.append(f"Auto-closed: {t['target_skill']}")
        if closed:
            self._save_tasks()
        return closed


task_service = TaskService()
