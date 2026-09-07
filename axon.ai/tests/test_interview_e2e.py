import uuid
from app.services.chunker import create_chunks
from app.services.vector_store import store_chunks
from app.services.interview_manager import interview_manager
from app.services.key_pool import key_pool

def test_full_interview_cycle():
    print("\n--- Step 1: Pre-loading candidate resume into ChromaDB ---")
    candidate_id = f"test_cand_{uuid.uuid4().hex[:8]}"
    sections = {
        "skills": "Python, FastAPI, Docker, PostgreSQL, Redis, Kubernetes, Microservices architecture.",
        "experience": "Senior Backend Intern at TechCorp. Built scalable RESTful APIs handling 5,000 requests/sec. Implemented Redis caching to cut database latency by 45%.",
        "projects": "Axon AI Assessment Engine: Created an autonomous interview system using ChromaDB vector store and Gemini 3.6 Flash LLMs."
    }
    
    chunks = create_chunks(candidate_id, sections)
    store_chunks(chunks)
    print(f"Stored {len(chunks)} chunks for candidate {candidate_id}")

    print("\n--- Step 2: Starting Interview Session ---")
    session_id, first_q, topic = interview_manager.start_session(
        candidate_id=candidate_id,
        student_name="Rahul Sharma",
        mode="practice",
        role_track="Backend Systems Engineer",
        target_skill="Redis Caching",
        max_questions=2
    )
    print(f"Session Created: {session_id}")
    print(f"Topic: {topic}")
    print(f"First Question: {first_q}")
    assert len(first_q) > 10, "First question should not be empty"

    print("\n--- Step 3: Submitting Answer Turn 1 ---")
    answer_1 = (
        "In our microservice architecture, we used Redis as a write-through and cache-aside store for hot API endpoints. "
        "We implemented exponential TTL expiration to avoid cache thundering herds, and serialized payloads using Protocol Buffers "
        "to reduce network overhead."
    )
    eval_1, next_q, is_completed_1 = interview_manager.submit_answer(session_id, answer_1)
    print(f"Turn 1 Score: {eval_1.score}/10")
    print(f"Turn 1 Feedback: {eval_1.feedback}")
    print(f"Next Question: {next_q}")
    assert 1.0 <= eval_1.score <= 10.0, "Score should be valid between 1 and 10"
    assert next_q is not None, "Turn 2 question should be generated"
    assert not is_completed_1, "Session should not be completed yet"

    print("\n--- Step 4: Submitting Answer Turn 2 ---")
    answer_2 = (
        "To handle data consistency and cache invalidation, we listen to PostgreSQL Change Data Capture (CDC) events via Debezium, "
        "and publish invalidation messages to Redis pub/sub topics so all service replicas purge stale keys within milliseconds."
    )
    eval_2, next_q_2, is_completed_2 = interview_manager.submit_answer(session_id, answer_2)
    print(f"Turn 2 Score: {eval_2.score}/10")
    print(f"Turn 2 Completed. is_completed: {is_completed_2}")
    assert is_completed_2 is True, "Session reached max_questions (2) and should be completed"

    print("\n--- Step 5: Concluding Session & Synthesis ---")
    synthesis = interview_manager.conclude_session(session_id)
    print(f"Overall Score: {synthesis.overall_score}/10")
    print(f"Technical Depth: {synthesis.technical_depth}/10")
    print(f"Logical Reasoning: {synthesis.logical_reasoning}/10")
    print(f"Communication Clarity: {synthesis.communication_clarity}/10")
    print(f"Domain Scores: {synthesis.domain_scores}")
    print(f"Strengths: {synthesis.strengths}")
    print(f"Learning Roadmap (Weeks): {len(synthesis.roadmap)}")
    
    assert synthesis.overall_score > 0, "Overall score must be populated"
    assert len(synthesis.roadmap) >= 1, "Learning roadmap must have at least 1 week"

    print("\n--- Step 6: Checking Key Pool Health ---")
    pool_status = key_pool.get_pool_status()
    print(f"Key Pool Status: {pool_status}")
    assert pool_status["total_requests_served"] >= 3, "At least 3 LLM calls should have been logged"

    print("\n==========================================")
    print("ALL END-TO-END INTERVIEW TESTS PASSED SUCCESSFULLY!")
    print("==========================================")

if __name__ == "__main__":
    test_full_interview_cycle()
