import asyncio
import pytest
import httpx
from app.main import app
from app.core.security import create_access_token


@pytest.fixture
def auth_tokens():
    student_token = create_access_token(
        user_id="11234003",
        role="student",
        department="Information Technology",
        name="Canonical Student",
        roll_number="11234003"
    )
    staff_token = create_access_token(
        user_id="staff-001",
        role="staff",
        department="Information Technology",
        name="Miss. Ramya Tamizharasi"
    )
    return {
        "student": student_token,
        "staff": staff_token
    }


def test_mcq_session_lifecycle_and_strikes(auth_tokens):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            student_headers = {"Authorization": f"Bearer {auth_tokens['student']}"}
            
            # 1. Start MCQ Session
            res = await client.post("/mcq/session/start", headers=student_headers)
            assert res.status_code == 200, res.text
            session_data = res.json()
            session_id = session_data["session_id"]
            assert session_data["total_questions"] == 20
            assert len(session_data["questions"]) == 20
            assert session_data["strikes"] == 0

            # 2. Strike 1
            res = await client.post(f"/mcq/session/{session_id}/strike", headers=student_headers)
            assert res.status_code == 200
            strike_data = res.json()
            assert strike_data["strikes"] == 1
            assert strike_data["is_disqualified"] is False

            # 3. Strike 2
            res = await client.post(f"/mcq/session/{session_id}/strike", headers=student_headers)
            assert res.status_code == 200
            assert res.json()["strikes"] == 2
            assert res.json()["is_disqualified"] is False

            # 4. Strike 3 -> Disqualification
            res = await client.post(f"/mcq/session/{session_id}/strike", headers=student_headers)
            assert res.status_code == 200
            strike3_data = res.json()
            assert strike3_data["strikes"] == 3
            assert strike3_data["is_disqualified"] is True
            assert strike3_data["status"] == "disqualified"

            # 5. Attempt Submit when disqualified -> HTTP 403
            res = await client.post(
                f"/mcq/session/{session_id}/submit",
                headers=student_headers,
                json={"answers": {}}
            )
            assert res.status_code == 403
            assert "disqualified" in res.json().get("error", "").lower() or "disqualified" in res.json().get("detail", "").lower()

    asyncio.run(run())


def test_mcq_successful_submission_and_results(auth_tokens):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            student_headers = {"Authorization": f"Bearer {auth_tokens['student']}"}
            staff_headers = {"Authorization": f"Bearer {auth_tokens['staff']}"}

            # 1. Start new session
            res = await client.post("/mcq/session/start", headers=student_headers)
            assert res.status_code == 200
            session_data = res.json()
            session_id = session_data["session_id"]
            first_q = session_data["questions"][0]

            # 2. Submit answers
            sample_choice = first_q["choices"][0]["text"]
            answers = {first_q["id"]: sample_choice}
            res = await client.post(
                f"/mcq/session/{session_id}/submit",
                headers=student_headers,
                json={"answers": answers}
            )
            assert res.status_code == 200
            submit_data = res.json()
            assert submit_data["status"] == "completed"
            assert "score" in submit_data
            assert "percentage" in submit_data
            assert len(submit_data["breakdown"]) == 20

            # 3. Staff fetches all results
            res_all = await client.get("/mcq/results/all", headers=staff_headers)
            assert res_all.status_code == 200
            results_list = res_all.json()
            assert any(r["session_id"] == session_id for r in results_list)

            # 4. Student fetches their own results
            res_my = await client.get("/mcq/results/my", headers=student_headers)
            assert res_my.status_code == 200
            my_list = res_my.json()
            assert any(r["session_id"] == session_id for r in my_list)

    asyncio.run(run())


def test_mcq_upload_permission(auth_tokens):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            student_headers = {"Authorization": f"Bearer {auth_tokens['student']}"}
            staff_headers = {"Authorization": f"Bearer {auth_tokens['staff']}"}

            # Student cannot upload (403 Forbidden)
            csv_file = ("questions.csv", b"question,option_a,option_b,option_c,option_d,answer\nWhat?,A,B,C,D,A", "text/csv")
            res = await client.post("/mcq/upload", headers=student_headers, files={"file": csv_file})
            assert res.status_code == 403

            # Staff can upload
            res = await client.post("/mcq/upload", headers=staff_headers, files={"file": csv_file})
            assert res.status_code == 200
            upload_data = res.json()
            assert upload_data["status"] == "success"
            assert upload_data["questions_parsed"] == 1

    asyncio.run(run())


def test_mcq_verification_and_batch_management(auth_tokens):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            student_headers = {"Authorization": f"Bearer {auth_tokens['student']}"}
            staff_headers = {"Authorization": f"Bearer {auth_tokens['staff']}"}

            # 1. Upload a test batch as Staff
            csv_content = (
                "question,option_a,option_b,option_c,option_d,answer\n"
                "What is Python?,Language,Snake,Car,Plane,A\n"
                "What is FastAPI?,Framework,Fruit,Tool,City,A\n"
            )
            res_up = await client.post(
                "/mcq/upload",
                headers=staff_headers,
                files={"file": ("batch_test.csv", csv_content.encode("utf-8"), "text/csv")}
            )
            assert res_up.status_code == 200
            up_data = res_up.json()
            batch_id = up_data["batch_id"]
            assert batch_id != ""

            # 2. Get batches list
            res_batches = await client.get("/mcq/batches", headers=staff_headers)
            assert res_batches.status_code == 200
            batches = res_batches.json()
            matched_batch = next((b for b in batches if b["batch_id"] == batch_id), None)
            assert matched_batch is not None
            assert matched_batch["total_questions"] == 2

            # 3. Get questions by batch
            res_q = await client.get(f"/mcq/questions?batch_id={batch_id}", headers=staff_headers)
            assert res_q.status_code == 200
            q_list = res_q.json()
            assert len(q_list) == 2
            # Newly uploaded should have is_approved = False
            assert q_list[0]["is_approved"] is False

            # Student should NOT have access to these admin endpoints
            student_check = await client.get("/mcq/batches", headers=student_headers)
            assert student_check.status_code == 403

            # 4. Toggle approval for first question
            target_q = q_list[0]
            res_app = await client.patch(f"/mcq/questions/{target_q['id']}/approve", headers=staff_headers)
            assert res_app.status_code == 200
            assert res_app.json()["is_approved"] is True

            # 5. Edit question details
            res_edit = await client.put(
                f"/mcq/questions/{target_q['id']}",
                headers=staff_headers,
                json={
                    "question_text": "Updated Python Question?",
                    "options": ["Language", "Snake", "Car", "Plane"],
                    "correct_answer": "Language",
                    "explanation": "Python is a high-level language.",
                    "topic": "Python Programming",
                    "is_approved": True
                }
            )
            assert res_edit.status_code == 200
            assert res_edit.json()["question_text"] == "Updated Python Question?"

            # 6. Delete single question
            second_q = q_list[1]
            res_del_single = await client.delete(f"/mcq/questions/{second_q['id']}", headers=staff_headers)
            assert res_del_single.status_code == 200
            assert res_del_single.json()["deleted_count"] == 1

            # 7. Delete entire batch
            res_del_batch = await client.delete(f"/mcq/batches/{batch_id}", headers=staff_headers)
            assert res_del_batch.status_code == 200
            assert res_del_batch.json()["deleted_count"] >= 1

            # Verify batch questions are now 0
            res_q_after = await client.get(f"/mcq/questions?batch_id={batch_id}", headers=staff_headers)
            assert res_q_after.status_code == 200
            assert len(res_q_after.json()) == 0

    asyncio.run(run())

