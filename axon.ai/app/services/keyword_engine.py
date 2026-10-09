import json
import re
import math
from collections import Counter
from typing import Optional

from app.services.question_bank import get_db_connection, DB_PATH


class KeywordExtractor:
    """
    Extracts high-signal technical keywords and normalized phrases from student answers
    and resume context, scoring them by specificity.
    """

    STOPWORDS = {
        "the", "a", "an", "is", "are", "was", "were", "it", "its", "be", "been",
        "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
        "can", "may", "might", "shall", "to", "of", "in", "for", "on", "with", "at",
        "by", "from", "as", "into", "about", "between", "through", "and", "but", "or",
        "not", "no", "so", "if", "then", "than", "that", "this", "these", "those",
        "we", "they", "them", "their", "you", "your", "he", "she", "my", "me", "i",
        "also", "very", "just", "like", "used", "using", "use", "uses", "called",
        "basically", "actually", "really", "way", "things", "something", "example",
        "means", "when", "where", "which", "what", "how", "why", "there",
        "more", "most", "some", "any", "each", "every", "all", "both", "well"
    }

    # High-value normalized concepts (Phrases -> Standard Keys)
    PHRASE_PATTERNS = [
        # ML & Math
        (r'r[\s\-]?(?:squared?|2|²)\s*(?:score|test|value)?', 'r_squared'),
        (r'\br[\s\-]*(?:squared?|2|²)\b', 'r_squared'),
        (r'r2\b', 'r_squared'),
        (r'mean\s+squared\s+error', 'mse'),
        (r'mean\s+absolute\s+error', 'mae'),
        (r'root\s+mean\s+squared?\s+error', 'rmse'),
        (r'linear\s+regression', 'linear_regression'),
        (r'logistic\s+regression', 'logistic_regression'),
        (r'gradient\s+descent', 'gradient_descent'),
        (r'learning\s+rate', 'learning_rate'),
        (r'cross[\s\-]validation', 'cross_validation'),
        (r'k[\s\-]fold', 'k_fold'),
        (r'bias[\s\-]variance', 'bias_variance'),
        (r'f1[\s\-]?score', 'f1_score'),
        (r'auc[\s\-]?roc', 'auc_roc'),
        (r'confusion\s+matrix', 'confusion_matrix'),
        (r'decision\s+tree', 'decision_tree'),
        (r'random\s+forest', 'random_forest'),
        (r'overfitting', 'overfitting'),
        (r'regularization', 'regularization'),
        (r'l1\s*(?:lasso)?', 'l1_lasso'),
        (r'lasso\b', 'l1_lasso'),
        (r'l2\s*(?:ridge)?', 'l2_ridge'),
        (r'ridge\b', 'l2_ridge'),
        (r'elastic\s+net', 'elastic_net'),
        (r'y\s*=\s*m\s*[x×\*c]?\s*[+\+]\s*[bc]', 'y_equals_mx_plus_b'),
        (r'y\s*=\s*[βb]₀\s*[+\+]\s*[βb]₁', 'y_equals_mx_plus_b'),
        (r'least\s+squares?', 'least_squares'),
        (r'vanishing\s+gradient', 'vanishing_gradient'),
        (r'backpropagation', 'backpropagation'),
        # DSA
        (r'linked\s+list', 'linked_list'),
        (r'hash\s+(?:table|map)', 'hash_table'),
        (r'binary\s+(?:search\s+)?tree', 'binary_search_tree'),
        (r'red[\s\-]black\s+tree', 'red_black_tree'),
        (r'avl\s+tree', 'avl_tree'),
        (r'dynamic\s+programming', 'dynamic_programming'),
        (r'breadth[\s\-]first\s+search', 'bfs'),
        (r'depth[\s\-]first\s+search', 'dfs'),
        (r'time\s+complexity', 'time_complexity'),
        (r'space\s+complexity', 'space_complexity'),
        (r'big[\s\-]?o', 'time_complexity'),
        # Python
        (r'global\s+interpreter\s+lock', 'gil'),
        (r'list\s+comprehension', 'list_comprehension'),
        (r'event\s+loop', 'event_loop'),
        (r'functools\.wraps', 'functools_wraps')
    ]

    HIGH_VALUE_TERMS = {
        "r_squared", "mse", "mae", "rmse", "linear_regression", "logistic_regression",
        "gradient_descent", "overfitting", "underfitting", "regularization", "l1_lasso",
        "l2_ridge", "elastic_net", "cross_validation", "bias_variance", "precision",
        "recall", "f1_score", "auc_roc", "confusion_matrix", "sigmoid", "adam", "rmsprop",
        "vanishing_gradient", "resnet", "backpropagation", "hash_table", "linked_list",
        "binary_search_tree", "red_black_tree", "avl_tree", "dynamic_programming",
        "bfs", "dfs", "quicksort", "gil", "asyncio", "event_loop", "closure", "decorator"
    }

    def extract(self, text: str) -> list[tuple[str, float]]:
        """
        Extracts and scores keywords from given text.
        Returns: list of (keyword, score) ordered by highest relevance.
        """
        if not text:
            return []

        text_lower = text.lower()
        scored: dict[str, float] = {}

        # 1. Multi-word phrase matches (highest weighting)
        for pattern, norm_term in self.PHRASE_PATTERNS:
            if re.search(pattern, text_lower):
                scored[norm_term] = scored.get(norm_term, 0.0) + 3.5

        # 2. Individual word tokens
        tokens = re.findall(r'\b[a-z_][a-z0-9_]*\b', text_lower)
        counts = Counter(tokens)

        for token, count in counts.items():
            if token in self.STOPWORDS or len(token) < 3:
                continue

            if token in self.HIGH_VALUE_TERMS:
                val = 2.5 * count
            elif len(token) >= 7:
                val = 1.4 * count
            else:
                val = 1.0 * count

            scored[token] = scored.get(token, 0.0) + val

        # Normalize 0.0 to 1.0
        if scored:
            max_val = max(scored.values())
            normalized = {k: round(v / max_val, 3) for k, v in scored.items()}
        else:
            normalized = {}

        return sorted(normalized.items(), key=lambda x: x[1], reverse=True)


class ChainQuestionSelector:
    """
    Recommendation Engine for Technical Interview Questions (Instagram-feed style).
    Chains next question from keywords of the candidate's previous answer while strictly
    adhering to the staged difficulty progression:
    - Turns 1 to 5: Stage 1 = Easy (Levels 1-2)
    - Turns 6 to 12: Stage 2 = Medium (Level 3)
    - Turns 13+: Stage 3 = Hard (Levels 4-5)
    """

    def __init__(self):
        self.extractor = KeywordExtractor()

    def get_target_stage(self, turn_index: int) -> tuple[str, list[int]]:
        """
        Determines the target stage and difficulty level range based on turn index.
        First 5 questions: Easy (Levels 1-2)
        Next turns (6-12): Medium (Level 3)
        Next turns (13+): Hard (Levels 4-5)
        """
        if turn_index <= 5:
            return "easy", [1, 2]
        elif turn_index <= 12:
            return "medium", [3]
        else:
            return "hard", [4, 5]

    def select_first_question(
        self,
        topic: str = "machine_learning",
        resume_context: str = ""
    ) -> dict:
        """Selects the opening Easy question, informed by candidate's resume/topic."""
        conn = get_db_connection()
        c = conn.cursor()

        # Extract resume keywords if available
        resume_keywords = [kw for kw, _ in self.extractor.extract(resume_context)[:6]] if resume_context else []

        # Find foundational Easy questions (difficulty 1 or 2)
        query = """
            SELECT id, question_text, model_answer, keywords, difficulty, stage, topic
            FROM questions
            WHERE stage = 'easy'
        """
        params = []
        if topic and topic.lower() != "software engineer":
            query += " AND topic = ?"
            params.append(topic.lower().replace(" ", "_"))

        c.execute(query, params)
        rows = c.fetchall()

        if not rows:
            # Fallback to any easy question
            c.execute("SELECT id, question_text, model_answer, keywords, difficulty, stage, topic FROM questions WHERE stage = 'easy' LIMIT 10")
            rows = c.fetchall()

        conn.close()

        if not rows:
            return {
                "id": "q_fallback_init",
                "question_text": "What is Linear Regression and how does it work?",
                "model_answer": "Linear Regression is a fundamental supervised algorithm predicting continuous targets using Y = mx + b.",
                "keywords": ["linear_regression", "regression", "y_equals_mx_plus_b"],
                "difficulty": 2,
                "chain_reason": "Introductory foundational question"
            }

        # Score by resume keyword overlap + freshness (penalty for times_used) + exploration randomness
        import random
        scored_rows = []
        for row in rows:
            q_keywords = set(json.loads(row["keywords"]))
            overlap = len(q_keywords.intersection(set(resume_keywords)))
            times_used = row["times_used"] if "times_used" in row.keys() else 0
            score = (overlap * 2.0) - (times_used * 0.7) + random.uniform(0.5, 2.5)
            scored_rows.append((score, row))

        scored_rows.sort(key=lambda x: x[0], reverse=True)
        top_candidates = [r for _, r in scored_rows[:max(1, min(4, len(scored_rows)))]]
        best_row = random.choice(top_candidates)

        return {
            "id": best_row["id"],
            "question_text": best_row["question_text"],
            "model_answer": best_row["model_answer"],
            "keywords": json.loads(best_row["keywords"]),
            "difficulty": best_row["difficulty"],
            "chain_reason": "Foundational opening question"
        }

    def select_next_question(
        self,
        previous_answer: str,
        current_turn: int,
        asked_ids: list[str],
        resume_context: str = ""
    ) -> dict:
        """
        Main recommendation method:
        1. Identifies the target difficulty stage (Easy for 1-5, Medium for 6-12, Hard for 13+).
        2. Extracts keywords from the candidate's previous answer.
        3. Queries the inverted index for connected questions.
        4. Scores candidates on: keyword overlap (45%), stage match (30%), resume bonus (15%), freshness (10%).
        5. Returns the highest-scoring question + chain rationale.
        """
        target_stage, target_levels = self.get_target_stage(current_turn)
        extracted_keywords = self.extractor.extract(previous_answer)
        top_kws = [kw for kw, _ in extracted_keywords[:6]]

        conn = get_db_connection()
        c = conn.cursor()

        candidates = {}

        if top_kws:
            placeholders_kw = ",".join("?" * len(top_kws))
            placeholders_asked = ",".join("?" * len(asked_ids)) if asked_ids else "'__none__'"

            # Query candidate questions that match these keywords
            query = f"""
                SELECT
                    q.id, q.question_text, q.model_answer, q.keywords,
                    q.difficulty, q.stage, q.topic, q.times_used,
                    ki.keyword AS matched_kw, ki.weight AS kw_weight
                FROM keyword_index ki
                JOIN questions q ON ki.question_id = q.id
                WHERE ki.keyword IN ({placeholders_kw})
                  AND q.id NOT IN ({placeholders_asked})
            """
            params = top_kws + (asked_ids if asked_ids else ["__none__"])
            rows = c.execute(query, params).fetchall()

            for r in rows:
                qid = r["id"]
                if qid not in candidates:
                    candidates[qid] = {
                        "id": qid,
                        "question_text": r["question_text"],
                        "model_answer": r["model_answer"],
                        "keywords": json.loads(r["keywords"]),
                        "difficulty": r["difficulty"],
                        "stage": r["stage"],
                        "topic": r["topic"],
                        "times_used": r["times_used"],
                        "matched_keywords": [],
                        "total_keyword_weight": 0.0
                    }
                candidates[qid]["matched_keywords"].append(r["matched_kw"])
                candidates[qid]["total_keyword_weight"] += r["kw_weight"]

        # Resume keywords for personalization bonus
        resume_keywords = set(kw for kw, _ in self.extractor.extract(resume_context)[:8]) if resume_context else set()

        scored_candidates = []
        for qid, cand in candidates.items():
            # 1. Keyword Signal (45%)
            keyword_score = min(1.0, cand["total_keyword_weight"] / 2.5)

            # 2. Stage Alignment (30%)
            if cand["stage"] == target_stage:
                stage_score = 1.0
            elif (target_stage == "easy" and cand["difficulty"] == 3) or (target_stage == "medium" and cand["difficulty"] in [2, 4]):
                stage_score = 0.5
            else:
                stage_score = 0.2

            # 3. Resume Alignment (15%)
            q_kws = set(cand["keywords"])
            resume_overlap = len(q_kws.intersection(resume_keywords))
            resume_score = min(1.0, resume_overlap / 2.0) if resume_keywords else 0.5

            # 4. Freshness / least used (10%)
            freshness_score = 1.0 / (1.0 + cand["times_used"] * 0.2)

            total_score = (
                keyword_score * 0.45 +
                stage_score * 0.30 +
                resume_score * 0.15 +
                freshness_score * 0.10
            )

            matched_str = ", ".join(cand["matched_keywords"][:3])
            cand["composite_score"] = total_score
            cand["chain_reason"] = f"Chained from concept(s): {matched_str} (Stage: {cand['stage'].title()})"
            scored_candidates.append(cand)

        scored_candidates.sort(key=lambda x: x["composite_score"], reverse=True)

        # Strictly prioritize candidates matching the turn's target stage
        stage_candidates = [c for c in scored_candidates if c["stage"] == target_stage]
        if stage_candidates:
            import random
            top_k = stage_candidates[:min(3, len(stage_candidates))]
            weights = [max(0.01, c["composite_score"] ** 2) for c in top_k]
            best = random.choices(top_k, weights=weights, k=1)[0]
            c.execute("UPDATE questions SET times_used = times_used + 1 WHERE id = ?", (best["id"],))
            conn.commit()
            conn.close()
            return best

        # Fallback: Pick an unasked question in the exact target stage
        import random
        placeholders_asked = ",".join("?" * len(asked_ids)) if asked_ids else "'__none__'"
        c.execute(f"""
            SELECT id, question_text, model_answer, keywords, difficulty, stage, topic, times_used
            FROM questions
            WHERE stage = ? AND id NOT IN ({placeholders_asked})
            ORDER BY times_used ASC, RANDOM()
            LIMIT 4
        """, [target_stage] + (asked_ids if asked_ids else ["__none__"]))
        fallback_rows = c.fetchall()
        fallback_row = random.choice(fallback_rows) if fallback_rows else None

        if not fallback_row:
            # Fallback across any stage if bank exhausted
            c.execute(f"""
                SELECT id, question_text, model_answer, keywords, difficulty, stage, topic, times_used
                FROM questions
                WHERE id NOT IN ({placeholders_asked})
                ORDER BY times_used ASC
                LIMIT 1
            """, (asked_ids if asked_ids else ["__none__"]))
            fallback_row = c.fetchone()

        if fallback_row:
            c.execute("UPDATE questions SET times_used = times_used + 1 WHERE id = ?", (fallback_row["id"],))
            conn.commit()
            conn.close()
            return {
                "id": fallback_row["id"],
                "question_text": fallback_row["question_text"],
                "model_answer": fallback_row["model_answer"],
                "keywords": json.loads(fallback_row["keywords"]),
                "difficulty": fallback_row["difficulty"],
                "stage": fallback_row["stage"],
                "chain_reason": f"Progressed to {target_stage.title()} Stage ({fallback_row['topic'].replace('_', ' ').title()})"
            }

        conn.close()
        return {
            "id": "q_final_exhaustion",
            "question_text": "Summarize a complex technical system you built or optimized recently.",
            "model_answer": "",
            "keywords": ["system_design", "optimization"],
            "difficulty": 3,
            "stage": target_stage,
            "chain_reason": "Wrap-up question"
        }


question_selector = ChainQuestionSelector()
