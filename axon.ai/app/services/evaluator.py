import re
import math
from collections import Counter
from typing import Optional

from app.models.interview import TurnEvaluation


class AnswerEvaluator:
    """
    Evaluates student technical answers purely algorithmically (zero LLM / zero API key).
    Combines:
    1. Keyword coverage against expected technical concepts (35%)
    2. TF-IDF Cosine Similarity against verified model answer (35%)
    3. Depth & length relative to difficulty stage (15%)
    4. Technical structure & causality markers (15%)
    """

    STOPWORDS = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "can", "shall", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "about", "between",
        "through", "after", "before", "above", "below", "and", "but", "or",
        "not", "no", "nor", "so", "if", "then", "than", "that", "this",
        "these", "those", "it", "its", "we", "they", "them", "their", "our",
        "you", "your", "he", "she", "his", "her", "my", "i", "me", "also"
    }

    def tokenize(self, text: str) -> list[str]:
        """Tokenizes text into lowercase words excluding stopwords."""
        words = re.findall(r'\b[a-z_][a-z0-9_]*\b', text.lower())
        return [w for w in words if w not in self.STOPWORDS and len(w) > 2]

    def compute_cosine_similarity(self, text_a: str, text_b: str) -> float:
        """Calculates TF-IDF vector cosine similarity between candidate and model answer."""
        if not text_a or not text_b:
            return 0.0

        tokens_a = self.tokenize(text_a)
        tokens_b = self.tokenize(text_b)

        if not tokens_a or not tokens_b:
            return 0.0

        freq_a = Counter(tokens_a)
        freq_b = Counter(tokens_b)

        vocab = set(freq_a.keys()).union(set(freq_b.keys()))
        dot_product = sum(freq_a.get(term, 0) * freq_b.get(term, 0) for term in vocab)
        norm_a = math.sqrt(sum(v ** 2 for v in freq_a.values()))
        norm_b = math.sqrt(sum(v ** 2 for v in freq_b.values()))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def evaluate(
        self,
        question: str,
        student_answer: str,
        model_answer: str,
        expected_keywords: list[str],
        difficulty_level: int = 2
    ) -> TurnEvaluation:
        """
        Evaluates the answer and generates a validated TurnEvaluation object.
        """
        clean_answer = (student_answer or "").strip()

        # Handle trivial / empty response
        if len(clean_answer) < 5 or clean_answer.lower() in ["idk", "i don't know", "skip", "no idea"]:
            return TurnEvaluation(
                score=1.0,
                technical_accuracy="No substantive technical response was provided.",
                areas_for_improvement="Provide an explanation covering fundamental principles and terminology.",
                feedback="Try attempting the question by explaining any relevant concept or keyword you remember.",
                difficulty_level=difficulty_level
            )

        answer_lower = clean_answer.lower()

        from app.services.keyword_engine import KeywordExtractor
        extracted_answer_kws = set(kw for kw, _ in KeywordExtractor().extract(clean_answer))

        # 1. Keyword coverage score (0.0 - 1.0)
        matched_keywords = []
        missing_keywords = []
        for kw in expected_keywords:
            kw_clean = kw.replace("_", " ").lower()
            if (
                kw.lower() in extracted_answer_kws
                or kw_clean in answer_lower
                or kw.lower() in answer_lower
                or any(tok in extracted_answer_kws for tok in kw.split("_") if len(tok) > 3)
            ):
                matched_keywords.append(kw.replace("_", " "))
            else:
                missing_keywords.append(kw.replace("_", " "))

        if expected_keywords:
            keyword_score = min(1.0, len(matched_keywords) / max(2, min(3, len(expected_keywords))))
        else:
            keyword_score = 0.5

        # 2. Cosine similarity score (0.0 - 1.0)
        similarity = self.compute_cosine_similarity(clean_answer, model_answer)

        # 3. Word count & depth score (0.0 - 1.0)
        word_count = len(clean_answer.split())
        target_words = {1: 15, 2: 25, 3: 45, 4: 65, 5: 85}.get(difficulty_level, 35)

        if word_count >= target_words:
            depth_score = 1.0
        elif word_count >= target_words * 0.6:
            depth_score = 0.75
        else:
            depth_score = max(0.3, word_count / target_words)

        # 4. Structure & Causality indicators (0.0 - 1.0)
        structure_score = 0.3
        # Has mathematical notation, equations, or code syntax
        if re.search(r'[=+\-*/^><_()\[\]{}]|\bdef\b|\bclass\b|y\s*=', clean_answer):
            structure_score += 0.25
        # Has reasoning conjunctions
        if re.search(r'\b(because|therefore|since|resulting in|minimizes|proportional|whereas|due to|tradeoff)\b', clean_answer, re.I):
            structure_score += 0.25
        # Multi-sentence punctuation
        sentences = [s for s in re.split(r'[.!?]+', clean_answer) if s.strip()]
        if len(sentences) >= 2:
            structure_score += 0.20
        structure_score = min(1.0, structure_score)

        # Composite weighted score (1.0 to 10.0 scale)
        composite = (
            keyword_score * 0.35 +
            similarity * 0.35 +
            depth_score * 0.15 +
            structure_score * 0.15
        )

        # Non-linear boost for strong answers
        final_score = round(max(1.0, min(10.0, 1.0 + composite * 9.0)), 1)

        # Formulate technical accuracy text
        if matched_keywords:
            tech_acc = f"Accurately addressed core concepts including: {', '.join(matched_keywords[:4])}."
        elif similarity > 0.4:
            tech_acc = "General conceptual understanding demonstrated, though specific terminology was sparse."
        else:
            tech_acc = "Partial understanding shown; key formal technical mechanisms were missing."

        # Formulate areas for improvement
        if missing_keywords:
            improvement = f"Could be strengthened by discussing: {', '.join(missing_keywords[:3])}."
        elif word_count < target_words:
            improvement = "Expand on the underlying mechanics and edge-case implications."
        else:
            improvement = "Good depth; consider exploring performance tradeoffs or alternative implementations."

        # Formulate constructive feedback
        if final_score >= 8.0:
            feedback = "Excellent response! Precise terminology and clear technical explanation."
        elif final_score >= 6.0:
            feedback = "Strong attempt. Solid understanding shown; integrate more formal equations or edge cases to reach top marks."
        elif final_score >= 4.0:
            feedback = "Fair attempt. Focus on articulating the exact mathematical or operational definitions."
        else:
            feedback = "Review the fundamental concepts for this topic and practice structuring your explanation."

        return TurnEvaluation(
            score=final_score,
            technical_accuracy=tech_acc,
            areas_for_improvement=improvement,
            feedback=feedback,
            difficulty_level=difficulty_level
        )


answer_evaluator = AnswerEvaluator()
