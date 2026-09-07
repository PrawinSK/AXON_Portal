import requests
import time

BASE = "http://127.0.0.1:8000"

print("--- Starting Session ---")
t0 = time.time()
start_payload = {
    "candidate_id": "test_e2e_student",
    "student_name": "Arjun Kumar",
    "mode": "practice",
    "role_track": "Backend Systems Engineer",
    "max_questions": 2
}
r_start = requests.post(f"{BASE}/interview/start", json=start_payload, timeout=60)
assert r_start.status_code == 200, f"Start failed: {r_start.text}"
start_data = r_start.json()
session_id = start_data["session_id"]
print(f"Session started in {time.time()-t0:.1f}s: {session_id}")
print("Q1:", start_data["first_question"])

print("\n--- Submitting Turn 1 Answer ---")
t1 = time.time()
ans_1 = (
    "A connection pool manages a pool of established database connections. "
    "Clients reuse connections instead of renegotiating TCP handshakes. "
    "If max pool is too small, requests queue; if too large, DB memory saturates."
)
r_turn1 = requests.post(f"{BASE}/interview/{session_id}/answer", json={"answer": ans_1}, timeout=60)
assert r_turn1.status_code == 200, f"Turn 1 failed: {r_turn1.text}"
turn1_data = r_turn1.json()
print(f"Turn 1 evaluated in {time.time()-t1:.1f}s. Score: {turn1_data['evaluation']['score']}/10")
print("Q2:", turn1_data["next_question"])

print("\n--- Submitting Turn 2 Answer ---")
t2 = time.time()
ans_2 = (
    "For database caching, we can use Redis Cache-Aside pattern. "
    "We query cache first; on miss, fetch from DB and populate cache with TTL. "
    "On DB write, delete the key in Redis to invalidate stale data."
)
r_turn2 = requests.post(f"{BASE}/interview/{session_id}/answer", json={"answer": ans_2}, timeout=60)
assert r_turn2.status_code == 200, f"Turn 2 failed: {r_turn2.text}"
turn2_data = r_turn2.json()
print(f"Turn 2 completed in {time.time()-t2:.1f}s. is_completed: {turn2_data['is_completed']}")

print("\n--- Concluding Session ---")
t3 = time.time()
r_conc = requests.post(f"{BASE}/interview/{session_id}/conclude", timeout=60)
assert r_conc.status_code == 200, f"Conclude failed: {r_conc.text}"
conc_data = r_conc.json()
print(f"Synthesis completed in {time.time()-t3:.1f}s.")
print(f"Overall Score: {conc_data['overall_score']}/10")
print("Domain scores:", conc_data["domain_scores"])
print(f"Roadmap weeks: {len(conc_data['roadmap'])}")

print("\n==========================================")
print("HTTP INTERVIEW SESSION TEST PASSED 100%!")
print("==========================================")
