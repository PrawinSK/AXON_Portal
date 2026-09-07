import sys
import os
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx
from app.main import app

async def test_rbac_and_auth_flow():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        print("--- 1. Testing Student Login (IT Student) ---")
        res = await client.post("/auth/student/login", json={
            "roll_number": "21IT001",
            "password": "student@123"
        })
        assert res.status_code == 200, f"Student login failed: {res.text}"
        student_data = res.json()
        assert student_data["role"] == "student"
        assert student_data["roll_number"] == "21IT001"
        assert student_data["name"] == "Kavitha S."
        student_token = student_data["access_token"]
        student_headers = {"Authorization": f"Bearer {student_token}"}
        print("[PASS] IT Student (Kavitha S. - 21IT001) authenticated successfully with JWT.")

        print("--- 2. Testing Staff Login (Miss. Ramya Tamizharasi) ---")
        res = await client.post("/auth/staff/login", json={
            "email": "ramya.staff@axon.edu",
            "password": "staff@123"
        })
        assert res.status_code == 200, f"Staff login failed: {res.text}"
        staff_data = res.json()
        assert staff_data["role"] == "staff"
        assert staff_data["name"] == "Miss. Ramya Tamizharasi"
        assert staff_data["department"] == "Information Technology"
        staff_token = staff_data["access_token"]
        staff_headers = {"Authorization": f"Bearer {staff_token}"}
        print("[PASS] Staff (Miss. Ramya Tamizharasi) authenticated successfully with JWT.")

        print("--- 3. Testing HOD Login (Dr. Selvi - HOD of IT) ---")
        res = await client.post("/auth/hod/login", json={
            "email": "hod.it@axon.edu",
            "password": "hod@123"
        })
        assert res.status_code == 200, f"HOD login failed: {res.text}"
        hod_data = res.json()
        assert hod_data["role"] == "hod"
        assert hod_data["name"] == "Dr. Selvi"
        assert hod_data["department"] == "Information Technology"
        hod_token = hod_data["access_token"]
        hod_headers = {"Authorization": f"Bearer {hod_token}"}
        print("[PASS] HOD (Dr. Selvi - HOD of IT) authenticated successfully with JWT.")

        print("--- 4. Testing Invalid Login ---")
        res = await client.post("/auth/student/login", json={
            "roll_number": "21IT001",
            "password": "wrongpassword"
        })
        assert res.status_code == 401
        print("[PASS] Wrong password rejected with 401.")

        print("--- 5. Testing Key Pool Access Restrictions ---")
        # Unauthenticated -> 401
        res = await client.get("/interview/pool/status")
        assert res.status_code == 401, f"Expected 401 for unauthenticated, got {res.status_code}"

        # Student -> 403 Forbidden
        res = await client.get("/interview/pool/status", headers=student_headers)
        assert res.status_code == 403, f"Expected 403 for student accessing pool, got {res.status_code}"

        # Staff -> 403 Forbidden
        res = await client.get("/interview/pool/status", headers=staff_headers)
        assert res.status_code == 403, f"Expected 403 for staff accessing pool, got {res.status_code}"

        # HOD -> 200 OK
        res = await client.get("/interview/pool/status", headers=hod_headers)
        assert res.status_code == 200, f"Expected 200 for HOD accessing pool, got {res.status_code}"
        pool_info = res.json()
        assert pool_info["total_keys"] == 50
        print(f"[PASS] Pool status securely restricted: HOD access allowed ({pool_info['total_keys']} keys), Student & Staff forbidden (403).")

        print("--- 6. Testing Staff/HOD Creating New Student ---")
        res = await client.post("/auth/students/create", headers=staff_headers, json={
            "roll_number": "21IT105",
            "name": "Suresh Kumar M.",
            "password": "student@123",
            "department": "Information Technology"
        })
        assert res.status_code == 200, f"Student creation failed: {res.text}"
        new_student = res.json()
        assert new_student["roll_number"] == "21IT105"
        assert new_student["name"] == "Suresh Kumar M."
        print(f"[PASS] Staff successfully created student profile: {new_student['name']} ({new_student['roll_number']})")

        # Now test newly created student immediately signing in!
        res = await client.post("/auth/student/login", json={
            "roll_number": "21IT105",
            "password": "student@123"
        })
        assert res.status_code == 200, f"Newly created student failed to login: {res.text}"
        new_stud_data = res.json()
        assert new_stud_data["name"] == "Suresh Kumar M."
        print(f"[PASS] Newly created student logged in successfully!")

        # Student trying to create another student -> 403 Forbidden
        res = await client.post("/auth/students/create", headers=student_headers, json={
            "roll_number": "21IT999",
            "name": "Hacker",
            "password": "pass"
        })
        assert res.status_code == 403
        print(f"[PASS] Student prevented from creating student accounts (403 Forbidden).")

        print("--- 7. Testing Department Student Directory ---")
        res = await client.get("/tasks/students", headers=hod_headers)
        assert res.status_code == 200
        students_list = res.json()
        assert len(students_list) >= 12
        print(f"[PASS] HOD/Staff retrieved {len(students_list)} students in department directory.")

        print("\nALL UPDATED RBAC & STUDENT REGISTRATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(test_rbac_and_auth_flow())
