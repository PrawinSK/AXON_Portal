import unittest
from app.services.interview_manager import interview_manager
from app.services.keyword_engine import question_selector, KeywordExtractor
from app.services.evaluator import answer_evaluator
from app.services.synthesizer import session_synthesizer


class TestKeywordEngine(unittest.TestCase):

    def setUp(self):
        self.extractor = KeywordExtractor()

    def test_keyword_extraction_phrase(self):
        text = (
            "Linear regression is a regression ML algorithm and it uses the line formula "
            "of Y = mc+b, also it can be evaluated by R square test and accuracy."
        )
        extracted = self.extractor.extract(text)
        keywords = [k for k, _ in extracted]
        
        print("\n[Test] Extracted keywords from answer:", keywords[:6])
        self.assertIn("r_squared", keywords)
        self.assertIn("linear_regression", keywords)
        self.assertIn("y_equals_mx_plus_b", keywords)

    def test_staged_difficulty_assignment(self):
        # Turns 1-5 -> Easy
        for turn in range(1, 6):
            stage, levels = question_selector.get_target_stage(turn)
            self.assertEqual(stage, "easy")
            self.assertEqual(levels, [1, 2])

        # Turns 6-12 -> Medium
        for turn in range(6, 13):
            stage, levels = question_selector.get_target_stage(turn)
            self.assertEqual(stage, "medium")
            self.assertEqual(levels, [3])

        # Turns 13+ -> Hard
        for turn in range(13, 26):
            stage, levels = question_selector.get_target_stage(turn)
            self.assertEqual(stage, "hard")
            self.assertEqual(levels, [4, 5])

    def test_interview_session_simulation_with_user_scenario(self):
        print("\n" + "=" * 70)
        print("SIMULATING INTERVIEW USING USER'S EXACT SCENARIO")
        print("=" * 70)

        # 1. Start Session
        session_id, first_q, topic = interview_manager.start_session(
            candidate_id="cand_test_001",
            student_name="Prawin",
            mode="practice",
            role_track="machine_learning",
            max_questions=15
        )
        print(f"\nTurn 1 (Easy Stage): {first_q}")
        self.assertIn("Linear Regression", first_q)

        # 2. Turn 1 Answer (User's exact example)
        answer_1 = (
            "Linear regression is a regression ML algorithm. It uses the line formula of Y = mc+b. "
            "Also it can be evaluated by R square test, Mean Squared Error, and accuracy metrics."
        )
        eval_1, next_q_2, is_completed_1 = interview_manager.submit_answer(session_id, answer_1)
        print(f"\nTurn 1 Answer Evaluation:")
        print(f"  Score: {eval_1.score}/10")
        print(f"  Accuracy: {eval_1.technical_accuracy}")
        print(f"  Improvement: {eval_1.areas_for_improvement}")
        print(f"  Feedback: {eval_1.feedback}")
        self.assertGreaterEqual(eval_1.score, 7.0)

        # 3. Verify Turn 2 is chained from Turn 1 keywords
        session_state = interview_manager.get_session_state(session_id)
        print(f"\nTurn 2 Question (Stage: Easy): {next_q_2}")
        print(f"  Chained Reason: {interview_manager._sessions[session_id].chain_history[-1]}")
        # Next question should probe R² or related concept mentioned
        self.assertTrue(
            "r-squared" in next_q_2.lower() or "r2" in next_q_2.lower() or "error" in next_q_2.lower() or "squared" in next_q_2.lower()
        )

        # 4. Turn 2 Answer mentioning overfitting
        answer_2 = (
            "R-squared measures the proportion of variance explained by features. "
            "However, adding more features always inflates R2, which can cause overfitting. "
            "Adjusted R-squared penalizes extra features."
        )
        eval_2, next_q_3, is_completed_2 = interview_manager.submit_answer(session_id, answer_2)
        print(f"\nTurn 3 Question: {next_q_3}")
        print(f"  Chained Reason: {interview_manager._sessions[session_id].chain_history[-1]}")

        # 5. Simulate progression into Medium stage (Turns 6-12)
        print("\nProgressing turns through Medium stage (Turns 6-12)...")
        for turn_num in range(3, 8):
            eval_turn, next_q, is_done = interview_manager.submit_answer(
                session_id,
                "Overfitting is prevented using regularization like L1 Lasso and L2 Ridge, along with cross-validation."
            )
            stage, _ = question_selector.get_target_stage(turn_num + 1)
            print(f"  Turn {turn_num + 1} (Stage: {stage.title()}): {next_q[:70]}...")

        # Verify that turn 7 is in the medium stage
        session_rec = interview_manager._sessions[session_id]
        self.assertEqual(session_rec.current_stage, "medium")

        # 6. Conclude Interview
        synthesis = interview_manager.conclude_session(session_id)
        print("\n" + "=" * 70)
        print("SESSION SYNTHESIS REPORT (100% Offline / Zero LLM):")
        print("=" * 70)
        print(f"  Overall Score:        {synthesis.overall_score}/10")
        print(f"  Technical Depth:      {synthesis.technical_depth}/10")
        print(f"  Logical Reasoning:    {synthesis.logical_reasoning}/10")
        print(f"  Communication:        {synthesis.communication_clarity}/10")
        print(f"  Domain Breakdown:     {synthesis.domain_scores}")
        print(f"  Strengths:            {synthesis.strengths}")
        print(f"  Weaknesses:           {synthesis.weaknesses}")
        print(f"  Roadmap Weeks:        {len(synthesis.roadmap)} weeks generated")
        for item in synthesis.roadmap:
            print(f"    - Week {item['week']}: {item['focus']}")

        self.assertGreater(synthesis.overall_score, 0)
        self.assertTrue(len(synthesis.roadmap) >= 2)
        print("\nAll assertions passed successfully!")


if __name__ == "__main__":
    unittest.main()
