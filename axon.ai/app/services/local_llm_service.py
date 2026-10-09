"""
Local LLM Service for AXON Interview Phase.
Uses Ollama (or any OpenAI-compatible local server) — NO API keys required.

This module mirrors the interface of llm_service.py so it can be swapped in
via a single config toggle (settings.use_local_llm).
"""
import json
from typing import Optional

from openai import OpenAI

from app.core.config import settings
from app.services.difficulty import LEVEL_PROMPTS

# ---------- Reuse prompts and helpers from the cloud service ----------
from app.services.llm_service import (
    QUESTION_SYSTEM_PROMPT,
    EVALUATION_SYSTEM_PROMPT,
    SYNTHESIS_SYSTEM_PROMPT,
    _extract_json,
)

# ---------- Local LLM Client ----------
# Connects to Ollama running locally — no API key needed.
# The openai library requires *some* value for api_key; Ollama ignores it.
_client = OpenAI(
    base_url=settings.local_llm_base_url,
    api_key="ollama",
)

_MODEL = settings.local_llm_model


def generate_grounded_question(
    resume_context: str,
    role_topic: str,
    difficulty_level: int = 2,
    turn_index: int = 1,
    target_skill: Optional[str] = None,
    previous_questions: Optional[list[str]] = None,
) -> str:
    """
    Generates a resume-grounded, difficulty-calibrated interview question
    using the local LLM (Ollama).
    """
    level_instruction = LEVEL_PROMPTS.get(difficulty_level, LEVEL_PROMPTS[2])

    prev_q_str = ""
    if previous_questions:
        formatted_prev = "\n".join(f"- {q}" for q in previous_questions)
        prev_q_str = (
            f"\n<previously_asked_questions>\n{formatted_prev}\n"
            f"</previously_asked_questions>\n"
        )

    target_skill_str = ""
    if target_skill:
        target_skill_str = f"\nTarget Remediation Skill to Assess: {target_skill}\n"

    prompt = f"""
<resume_context>
{resume_context}
</resume_context>

Role Track: {role_topic}
{target_skill_str}
Question Number: {turn_index}
Difficulty Setting: {level_instruction}
{prev_q_str}
Task: Generate one technical interview question tailored to the candidate's background and the difficulty setting.
"""

    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": QUESTION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()


def evaluate_answer(
    question: str,
    answer: str,
    difficulty_level: int = 2,
) -> dict:
    """
    Evaluates a candidate's answer independently from question generation.
    Returns structured evaluation with score (1.0 – 10.0).
    """
    level_instruction = LEVEL_PROMPTS.get(difficulty_level, LEVEL_PROMPTS[2])

    prompt = f"""
Difficulty Level of Question: {level_instruction}

Question Asked:
{question}

Candidate's Answer:
{answer}

Evaluate the candidate's answer and produce the required JSON format.
"""

    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": EVALUATION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    return _extract_json(response.choices[0].message.content)


def synthesize_interview_performance(
    qa_logs: list[dict],
    mode: str = "practice",
) -> dict:
    """
    Synthesizes overall interview performance from the complete QA log.
    Produces radar scores, strengths/weaknesses, and remediation roadmap.
    """
    transcript_text = json.dumps(qa_logs, indent=2)

    prompt = f"""
Interview Mode: {mode}

Transcript of Interview Turns:
{transcript_text}

Perform full technical synthesis and return the structured JSON assessment.
"""

    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    return _extract_json(response.choices[0].message.content)


# Backward compatibility wrapper for legacy endpoint
def generate_interview_question(context: str, topic: str) -> str:
    return generate_grounded_question(
        resume_context=context,
        role_topic=topic,
        difficulty_level=2,
        turn_index=1,
    )
