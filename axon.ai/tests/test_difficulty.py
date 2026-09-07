from app.services.difficulty import DifficultyEngine, DifficultyState

def test_difficulty_engine():
    state = DifficultyEngine.create_initial_state(starting_level=2)
    assert state.current_level == 2
    assert state.level_name == "Application"

    # Turn 1: High score 8.0 -> pending promotion
    state, msg = DifficultyEngine.evaluate_transition(state, 8.0)
    assert state.current_level == 2
    assert state.consecutive_high_scores == 1
    assert "pending_promotion" in msg

    # Turn 2: High score 8.5 -> promoted to Level 3
    state, msg = DifficultyEngine.evaluate_transition(state, 8.5)
    assert state.current_level == 3
    assert state.consecutive_high_scores == 0
    assert "promoted" in msg

    # Turn 3: Moderate score 6.0 -> hold at Level 3
    state, msg = DifficultyEngine.evaluate_transition(state, 6.0)
    assert state.current_level == 3
    assert state.consecutive_high_scores == 0
    assert "maintained" in msg

    # Turn 4: Low score 3.0 -> demoted to Level 2
    state, msg = DifficultyEngine.evaluate_transition(state, 3.0)
    assert state.current_level == 2
    assert "demoted" in msg

    # Turn 5: Low score 2.0 -> demoted to Level 1
    state, msg = DifficultyEngine.evaluate_transition(state, 2.0)
    assert state.current_level == 1
    assert "demoted" in msg

    # Turn 6: Low score 1.0 -> lower boundary (stays at Level 1)
    state, msg = DifficultyEngine.evaluate_transition(state, 1.0)
    assert state.current_level == 1
    assert "retained_at_min" in msg

    # Climb to Level 5
    state, _ = DifficultyEngine.evaluate_transition(state, 9.0)
    state, _ = DifficultyEngine.evaluate_transition(state, 9.0)
    assert state.current_level == 2

    state, _ = DifficultyEngine.evaluate_transition(state, 9.0)
    state, _ = DifficultyEngine.evaluate_transition(state, 9.0)
    assert state.current_level == 3

    state, _ = DifficultyEngine.evaluate_transition(state, 9.0)
    state, _ = DifficultyEngine.evaluate_transition(state, 9.0)
    assert state.current_level == 4

    state, _ = DifficultyEngine.evaluate_transition(state, 9.0)
    state, _ = DifficultyEngine.evaluate_transition(state, 9.0)
    assert state.current_level == 5

    # Exceeding Level 5 -> upper boundary (stays at Level 5)
    state, _ = DifficultyEngine.evaluate_transition(state, 9.5)
    state, msg = DifficultyEngine.evaluate_transition(state, 9.5)
    assert state.current_level == 5
    assert "retained_at_max" in msg

    print("Difficulty Engine unit tests passed successfully!")

if __name__ == "__main__":
    test_difficulty_engine()
