from typing import Any
from app.models.interview import SynthesisResponse


class SessionSynthesizer:
    """
    Synthesizes overall interview session performance algorithmically without external LLMs.
    Computes multidimensional radar scores, identifies critical strengths/gaps,
    and generates an actionable remedial roadmap.
    """

    ROADMAP_CATALOG = {
        "machine_learning": [
            {
                "week": 1,
                "focus": "Mathematical Foundations & Regression",
                "action_items": [
                    "Derive Ordinary Least Squares (OLS) closed-form solution vs Gradient Descent.",
                    "Implement Linear & Logistic Regression from scratch in NumPy with vectorization.",
                    "Analyze R2 vs Adjusted R2 and practice residual error diagnostics."
                ]
            },
            {
                "week": 2,
                "focus": "Regularization & Generalization Diagnostics",
                "action_items": [
                    "Implement L1 Lasso and L2 Ridge loss penalties; plot parameter shrinkage paths.",
                    "Run 5-Fold Stratified Cross-Validation on noisy datasets to evaluate the Bias-Variance tradeoff.",
                    "Build confusion matrix metrics and tune classification decision thresholds using ROC-AUC."
                ]
            }
        ],
        "data_structures": [
            {
                "week": 1,
                "focus": "Memory Locality & Pointer Structures",
                "action_items": [
                    "Benchmark CPU cache miss rates of contiguous Arrays vs dynamically allocated Linked Lists.",
                    "Implement a Hash Table with open addressing (quadratic probing) and dynamic rehashing.",
                    "Solve 15 sliding window and two-pointer array problems."
                ]
            },
            {
                "week": 2,
                "focus": "Hierarchical & Graph Algorithms",
                "action_items": [
                    "Implement BST insert, delete, and balance check functions from scratch.",
                    "Implement BFS and DFS graph traversals; solve cycle detection and topological sorting.",
                    "Analyze time and space complexity tradeoffs across iterative and recursive implementations."
                ]
            }
        ],
        "python": [
            {
                "week": 1,
                "focus": "Advanced Python Internals & Metaprogramming",
                "action_items": [
                    "Master Closures, first-class functions, and write parameterized decorators with @functools.wraps.",
                    "Analyze CPython memory management, object reference counts, and the Global Interpreter Lock (GIL).",
                    "Replace memory-heavy list operations with Generator expressions and iterators."
                ]
            },
            {
                "week": 2,
                "focus": "Asynchronous Architecture & Concurrency",
                "action_items": [
                    "Build an asynchronous scraper using asyncio and aiohttp with semaphore rate limiting.",
                    "Benchmark CPU-bound multiprocessing pools vs I/O-bound multithreading workloads.",
                    "Inspect event loop internals and task scheduling routines."
                ]
            }
        ],
        "default": [
            {
                "week": 1,
                "focus": "Core Principles & Algorithmic Rigor",
                "action_items": [
                    "Review theoretical foundations of topics with scores below 7.0.",
                    "Write clean, modular code with precise Big-O time and space complexity analysis."
                ]
            },
            {
                "week": 2,
                "focus": "Systematic Problem Solving & Mock Interviews",
                "action_items": [
                    "Practice structured technical explanations emphasizing trade-offs and edge cases.",
                    "Build a mini-project consolidating topics identified in the assessment."
                ]
            }
        ]
    }

    def synthesize(
        self,
        session_id: str,
        mode: str,
        qa_history: list[dict],
        target_skill: str = None
    ) -> SynthesisResponse:
        """
        Synthesizes the complete interview record into a structured SynthesisResponse.
        """
        if not qa_history:
            return SynthesisResponse(
                session_id=session_id,
                mode=mode,
                overall_score=5.0,
                technical_depth=5.0,
                logical_reasoning=5.0,
                communication_clarity=5.0,
                domain_scores={"general": 5.0},
                strengths=["Completed initial interview registration"],
                weaknesses=["No interview turns completed"],
                roadmap=self.ROADMAP_CATALOG["default"],
                tasks_auto_closed=[]
            )

        scores = [float(h["evaluation"].score) for h in qa_history if h.get("evaluation")]
        if not scores:
            scores = [5.0]

        # 1. Overall Score (Weighted average giving more prominence to later/harder turns)
        weights = [1.0 + (i * 0.05) for i in range(len(scores))]
        overall_score = round(sum(s * w for s, w in zip(scores, weights)) / sum(weights), 1)

        # 2. Domain breakdown scores
        domain_buckets: dict[str, list[float]] = {}
        for h in qa_history:
            topic = h.get("topic", "technical").replace("_", " ").title()
            score = float(h["evaluation"].score) if h.get("evaluation") else 5.0
            domain_buckets.setdefault(topic, []).append(score)

        domain_scores = {
            dom: round(sum(vals) / len(vals), 1)
            for dom, vals in domain_buckets.items()
        }

        # 3. Technical Depth (Performance on Medium & Hard turns)
        advanced_scores = [
            float(h["evaluation"].score)
            for h in qa_history
            if h.get("difficulty_level", 2) >= 3 and h.get("evaluation")
        ]
        if advanced_scores:
            technical_depth = round(sum(advanced_scores) / len(advanced_scores), 1)
        else:
            technical_depth = round(sum(scores) / len(scores), 1)

        # 4. Logical Reasoning (Consistency and score progression)
        improving_bonus = 0.5 if len(scores) >= 3 and scores[-1] >= scores[0] else 0.0
        logical_reasoning = round(min(10.0, (sum(scores) / len(scores)) + improving_bonus), 1)

        # 5. Communication Clarity (Average word count and answer structure)
        word_counts = [len((h.get("answer") or "").split()) for h in qa_history]
        avg_words = sum(word_counts) / max(1, len(word_counts))
        if avg_words >= 50:
            comm_score = 8.5
        elif avg_words >= 30:
            comm_score = 7.5
        elif avg_words >= 15:
            comm_score = 6.0
        else:
            comm_score = 4.0
        communication_clarity = round(comm_score, 1)

        # 6. Strengths and Weaknesses
        strengths = []
        weaknesses = []

        for dom, avg in domain_scores.items():
            if avg >= 7.0:
                strengths.append(f"Demonstrated solid command over {dom} concepts ({avg}/10)")
            elif avg < 6.0:
                weaknesses.append(f"Needs deeper foundational review in {dom} ({avg}/10)")

        if not strengths:
            strengths.append("Demonstrated consistent effort across interview turns")
            strengths.append("Clear familiarity with fundamental definitions")
        if not weaknesses:
            weaknesses.append("Explore deeper edge-case optimizations and architectural scaling")

        # 7. Targeted Roadmap
        # Pick the lowest scoring domain to customize the roadmap
        lowest_dom = min(domain_scores, key=domain_scores.get).lower().replace(" ", "_") if domain_scores else "default"
        roadmap = self.ROADMAP_CATALOG.get(lowest_dom, self.ROADMAP_CATALOG["default"])

        # 8. Auto-close tasks if in graded mode
        tasks_closed = []
        if mode == "graded" and target_skill:
            skill_norm = target_skill.lower()
            matched = False
            for dom, score in domain_scores.items():
                if skill_norm in dom.lower():
                    if score >= 7.0:
                        tasks_closed.append(f"Auto-closed task: {target_skill} (Domain Score: {score}/10)")
                    matched = True
                    break
            if not matched and overall_score >= 7.0:
                tasks_closed.append(f"Auto-closed task: {target_skill} (Overall Performance: {overall_score}/10)")

        return SynthesisResponse(
            session_id=session_id,
            mode=mode,
            overall_score=overall_score,
            technical_depth=technical_depth,
            logical_reasoning=logical_reasoning,
            communication_clarity=communication_clarity,
            domain_scores=domain_scores,
            strengths=strengths[:3],
            weaknesses=weaknesses[:3],
            roadmap=roadmap,
            tasks_auto_closed=tasks_closed
        )


session_synthesizer = SessionSynthesizer()
