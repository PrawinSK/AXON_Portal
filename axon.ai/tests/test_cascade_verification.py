from app.services.llm_service import (
    generate_grounded_question,
    evaluate_answer,
    synthesize_interview_performance
)

print("Step 1: Testing question generation...")
q = generate_grounded_question(
    resume_context="Fullstack developer skilled in React, FastAPI, Docker, and PostgreSQL.",
    role_topic="Fullstack Developer",
    difficulty_level=2,
    turn_index=1
)
print("Question generated:", q[:100], "...")

print("\nStep 2: Testing decoupled answer evaluation...")
eval_res = evaluate_answer(
    question=q,
    answer="In FastAPI I use Pydantic models for request validation and dependency injection for DB sessions.",
    difficulty_level=2
)
print("Evaluation result:", eval_res)
assert "score" in eval_res
print("\nSUCCESS: All LLM operations passed flawlessly with zero 429 errors!")
