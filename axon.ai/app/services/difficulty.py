from typing import Optional
from pydantic import BaseModel, Field

LEVEL_PROMPTS = {
    1: (
        "LEVEL 1 (Foundational): Focus on fundamental definitions, core terminology, "
        "basic syntax, and foundational concepts without overwhelming complexity."
    ),
    2: (
        "LEVEL 2 (Application & Concepts): Focus on practical application of concepts, standard library "
        "usage, straightforward implementations, and explaining how specific features work."
    ),
    3: (
        "LEVEL 3 (Scenario & Implementation): Present realistic coding or engineering scenarios, "
        "troubleshooting challenges, component integration, and practical trade-offs."
    ),
    4: (
        "LEVEL 4 (Deep Dive & Edge Cases): Probe into internal mechanics, memory/concurrency behavior, "
        "performance bottlenecks, non-trivial edge cases, and failure modes."
    ),
    5: (
        "LEVEL 5 (Architectural & Systems Design): Challenge on distributed scalability, high-level "
        "architecture, fault tolerance, design patterns, and systemic trade-offs."
    )
}

LEVEL_LABELS = {
    1: "Foundational",
    2: "Application",
    3: "Scenario",
    4: "Deep Dive",
    5: "Architectural"
}


class DifficultyState(BaseModel):
    current_level: int = Field(default=2, ge=1, le=5)
    score_history: list[float] = Field(default_factory=list)
    consecutive_high_scores: int = 0
    level_history: list[int] = Field(default_factory=lambda: [2])

    @property
    def level_name(self) -> str:
        return LEVEL_LABELS.get(self.current_level, "Application")

    @property
    def prompt_guideline(self) -> str:
        return LEVEL_PROMPTS.get(self.current_level, LEVEL_PROMPTS[2])


class DifficultyEngine:
    """
    Deterministic Difficulty Adaptation Engine.
    Adjusts interview question difficulty based on student answer evaluation scores.
    Rules:
    - 2 consecutive scores >= 7.5 -> Promote level (+1, max 5)
    - 1 score < 4.0 -> Demote level (-1, min 1)
    - 4.0 <= score < 7.5 -> Maintain level
    """

    PROMOTION_THRESHOLD: float = 7.5
    DEMOTION_THRESHOLD: float = 4.0
    CONSECUTIVE_REQUIRED: int = 2
    MIN_LEVEL: int = 1
    MAX_LEVEL: int = 5

    @classmethod
    def create_initial_state(cls, starting_level: int = 2) -> DifficultyState:
        bounded_level = max(cls.MIN_LEVEL, min(cls.MAX_LEVEL, starting_level))
        return DifficultyState(
            current_level=bounded_level,
            score_history=[],
            consecutive_high_scores=0,
            level_history=[bounded_level]
        )

    @classmethod
    def evaluate_transition(cls, state: DifficultyState, latest_score: float) -> tuple[DifficultyState, str]:
        """
        Evaluates the transition based on the latest turn score.
        Returns the updated state and a transition reason message.
        """
        clamped_score = max(0.0, min(10.0, float(latest_score)))
        new_scores = state.score_history + [clamped_score]
        
        current_lvl = state.current_level
        consecutive_high = state.consecutive_high_scores
        transition_reason = "hold"
        new_lvl = current_lvl

        if clamped_score >= cls.PROMOTION_THRESHOLD:
            consecutive_high += 1
            if consecutive_high >= cls.CONSECUTIVE_REQUIRED:
                if current_lvl < cls.MAX_LEVEL:
                    new_lvl = current_lvl + 1
                    transition_reason = f"promoted (Level {current_lvl} -> Level {new_lvl} after {consecutive_high} high scores)"
                else:
                    transition_reason = "retained_at_max"
                consecutive_high = 0  # Reset counter after promotion
            else:
                transition_reason = f"pending_promotion ({consecutive_high}/{cls.CONSECUTIVE_REQUIRED} high scores)"
        elif clamped_score < cls.DEMOTION_THRESHOLD:
            consecutive_high = 0
            if current_lvl > cls.MIN_LEVEL:
                new_lvl = current_lvl - 1
                transition_reason = f"demoted (Level {current_lvl} -> Level {new_lvl} due to low score {clamped_score:.1f})"
            else:
                transition_reason = "retained_at_min"
        else:
            consecutive_high = 0
            transition_reason = f"maintained (Level {current_lvl} with score {clamped_score:.1f})"

        updated_state = DifficultyState(
            current_level=new_lvl,
            score_history=new_scores,
            consecutive_high_scores=consecutive_high,
            level_history=state.level_history + [new_lvl]
        )

        return updated_state, transition_reason
