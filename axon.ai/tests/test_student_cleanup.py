import asyncio
import pytest
import httpx
from app.main import app
from app.core.security import create_access_token
from app.services.auth_service import auth_service


@pytest.fixture
def hod_token():
    return create_access_token(
        user_id="hod-001",
        role="hod",
        department="Information Technology",
        name="Dr. Selvi"
    )


@pytest.fixture
def student_token():
    return create_access_token(
        user_id="11234003",
        role="student",
        department="Information Technology",
        name="Canonical Student",
        roll_number="11234003"
    )


def test_student_cleanup_rbac_and_behavior(hod_token, student_token):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 1. Non-HOD (student) cannot trigger cleanup
            res_unauthorized = await client.post(
                "/auth/students/cleanup",
                headers={"Authorization": f"Bearer {student_token}"}
            )
            assert res_unauthorized.status_code == 403

            # 2. HOD triggers cleanup
            res_cleanup = await client.post(
                "/auth/students/cleanup",
                headers={"Authorization": f"Bearer {hod_token}"}
            )
            assert res_cleanup.status_code == 200
            data = res_cleanup.json()
            assert data["status"] == "success"
            assert "11234003" in data["message"]

            # 3. Check student list: only 11234003 should remain
            students = auth_service.get_all_students()
            assert len(students) == 1
            assert students[0]["roll_number"] == "11234003"

            # 4. Verify login with student@123 succeeds
            login_res = await client.post("/auth/student/login", json={
                "roll_number": "11234003",
                "password": "student@123"
            })
            assert login_res.status_code == 200
            assert login_res.json()["role"] == "student"

    asyncio.run(run())
