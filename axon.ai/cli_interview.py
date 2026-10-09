import sys
from app.services.interview_manager import interview_manager
from app.services.keyword_engine import question_selector


def run_cli_interview():
    print("=" * 70)
    print("  AXON — OFFLINE KEYWORD-CHAIN INTERVIEW ENGINE")
    print("  (Zero LLM • Zero API Keys • 100% Algorithmic Recommendation)")
    print("=" * 70)

    role_track = input("\nEnter target role/topic (default: machine_learning): ").strip()
    if not role_track:
        role_track = "machine_learning"

    num_q_input = input("Enter max questions (default: 10): ").strip()
    max_questions = int(num_q_input) if num_q_input.isdigit() else 10

    print("\nStarting session...")
    session_id, first_question, topic = interview_manager.start_session(
        candidate_id="cli_user",
        student_name="Candidate",
        mode="practice",
        role_track=role_track,
        max_questions=max_questions
    )

    current_q = first_question
    for turn in range(1, max_questions + 1):
        stage, levels = question_selector.get_target_stage(turn)
        print("\n" + "-" * 70)
        print(f"📋 Question {turn}/{max_questions} [Stage: {stage.upper()} • Difficulty Levels: {levels}]")
        print(f"👉 {current_q}")
        print("-" * 70)

        answer = input("\nYour Answer: ").strip()
        if not answer:
            answer = "I am not familiar with this topic."

        evaluation, next_q, is_completed = interview_manager.submit_answer(session_id, answer)

        print(f"\n📊 Evaluation:")
        print(f"  • Score:        {evaluation.score} / 10.0")
        print(f"  • Accuracy:     {evaluation.technical_accuracy}")
        print(f"  • Improvement:  {evaluation.areas_for_improvement}")
        print(f"  • Feedback:     {evaluation.feedback}")

        if is_completed or not next_q:
            break

        current_q = next_q

    print("\n" + "=" * 70)
    print("📈 FINAL INTERVIEW PERFORMANCE SYNTHESIS")
    print("=" * 70)
    synthesis = interview_manager.conclude_session(session_id)

    print(f"\n  Overall Score:        {synthesis.overall_score} / 10.0")
    print(f"  Technical Depth:      {synthesis.technical_depth} / 10.0")
    print(f"  Logical Reasoning:    {synthesis.logical_reasoning} / 10.0")
    print(f"  Communication:        {synthesis.communication_clarity} / 10.0")
    print(f"\n  Domain Scores:")
    for dom, s in synthesis.domain_scores.items():
        bar = "█" * int(s) + "░" * (10 - int(s))
        print(f"    {dom:24s} [{bar}] {s}/10")

    print(f"\n  Strengths:")
    for st in synthesis.strengths:
        print(f"    ✅ {st}")

    print(f"\n  Areas for Improvement:")
    for wk in synthesis.weaknesses:
        print(f"    ⚠️  {wk}")

    print(f"\n  Personalized Learning Roadmap:")
    for item in synthesis.roadmap:
        print(f"    Week {item['week']}: {item['focus']}")
        for a in item.get("action_items", []):
            print(f"      • {a}")

    print("\n" + "=" * 70)
    print("Interview Completed Successfully!")
    print("=" * 70)


if __name__ == "__main__":
    run_cli_interview()
