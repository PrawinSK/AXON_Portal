import json
import re
from typing import Optional, Any
from google import genai
from google.genai import types
from app.core.config import settings
from app.services.key_pool import key_pool
from app.services.difficulty import LEVEL_PROMPTS

QUESTION_SYSTEM_PROMPT = """
You are Axon, an elite AI Technical Recruiter conducting an adaptive interview for a university student.

Core Rules:
1. Ground the question strictly in the candidate's resume context, role requirements, and current difficulty level.
2. Ask EXACTLY ONE clear, probing technical question. Do not bundle multiple questions into one.
3. NEVER repeat questions previously asked in the interview.
4. If a target remediation skill is specified, prioritize probing that area while honoring the resume context.
5. Do not include conversational filler like "Great answer" or "Let's move on". State the question directly.
"""

EVALUATION_SYSTEM_PROMPT = """
You are an expert technical interviewer evaluating a student's answer to a technical question.
Evaluate the answer rigorously and return ONLY a valid JSON object with the following schema:
{
  "score": <float between 1.0 and 10.0>,
  "technical_accuracy": "<factual correctness of candidate answer>",
  "areas_for_improvement": "<specific knowledge gaps, edge cases missed, or imprecise phrasing>",
  "feedback": "<constructive, actionable guidance for the student>"
}

Scoring Rubric:
- 9.0 - 10.0: Flawless, deep explanation covering internal mechanisms, trade-offs, and best practices.
- 7.5 - 8.9: Strong answer with clear understanding; minor edge cases or optimizations omitted.
- 5.0 - 7.4: Partially correct; understands general concept but lacks depth or misses key implementation details.
- 3.0 - 4.9: Weak or vague answer; misconceptions present; misses core mechanics.
- 1.0 - 2.9: Incorrect, completely off-topic, or empty response.
"""

SYNTHESIS_SYSTEM_PROMPT = """
You are the Chief Assessment Officer at Axon. You synthesize a candidate's complete technical interview transcript.
Analyze the provided transcript of questions, candidate answers, and turn evaluations.
Return ONLY a valid JSON object with the following schema:
{
  "overall_score": <float between 1.0 and 10.0>,
  "technical_depth": <float between 1.0 and 10.0>,
  "logical_reasoning": <float between 1.0 and 10.0>,
  "communication_clarity": <float between 1.0 and 10.0>,
  "domain_scores": {
    "<skill_name>": <float between 1.0 and 10.0>
  },
  "strengths": ["<top strength 1>", "<top strength 2>", "<top strength 3>"],
  "weaknesses": ["<critical gap 1>", "<critical gap 2>"],
  "roadmap": [
    {
      "week": 1,
      "focus": "<core topic>",
      "action_items": ["<resource/exercise 1>", "<project practice 2>"]
    },
    {
      "week": 2,
      "focus": "<advanced topic>",
      "action_items": ["<resource/exercise 1>", "<project practice 2>"]
    }
  ]
}
"""


def _extract_json(text: str) -> dict:
    """Robustly parse JSON output from LLM, handling markdown code fences."""
    cleaned = text.strip()
    if "```" in cleaned:
        # Match ```json ... ``` or ``` ... ```
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
        if match:
            cleaned = match.group(1).strip()

    try:
        return json.loads(cleaned)
    except Exception as e:
        # Fallback regex search for { ... }
        match = re.search(r"(\{[\s\S]*\})", cleaned)
        if match:
            return json.loads(match.group(1))
        raise ValueError(f"Could not parse valid JSON from response: {text[:200]}") from e


def generate_grounded_question(
    resume_context: str,
    role_topic: str,
    difficulty_level: int = 2,
    turn_index: int = 1,
    target_skill: Optional[str] = None,
    previous_questions: Optional[list[str]] = None
) -> str:
    """
    Generates a resume-grounded, difficulty-calibrated interview question using Gemini 3.6 Flash.
    """
    level_instruction = LEVEL_PROMPTS.get(difficulty_level, LEVEL_PROMPTS[2])
    
    prev_q_str = ""
    if previous_questions:
        formatted_prev = "\n".join(f"- {q}" for q in previous_questions)
        prev_q_str = f"\n<previously_asked_questions>\n{formatted_prev}\n</previously_asked_questions>\n"

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

    def call_gemini(client: genai.Client, model_name: str) -> str:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=QUESTION_SYSTEM_PROMPT,
                temperature=0.4,
            )
        )
        return response.text.strip()

    return key_pool.execute(call_gemini)


def evaluate_answer(
    question: str,
    answer: str,
    difficulty_level: int = 2
) -> dict:
    """
    Evaluates candidate's answer independently from question generation.
    Returns structured evaluation with score (1.0 - 10.0).
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

    def call_gemini(client: genai.Client, model_name: str) -> dict:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=EVALUATION_SYSTEM_PROMPT,
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
        return _extract_json(response.text)

    return key_pool.execute(call_gemini)


def synthesize_interview_performance(
    qa_logs: list[dict],
    mode: str = "practice"
) -> dict:
    """
    Synthesizes overall interview performance from complete QA log.
    Produces radar scores, strengths/weaknesses, and remediation roadmap.
    """
    transcript_text = json.dumps(qa_logs, indent=2)
    prompt = f"""
Interview Mode: {mode}

Transcript of Interview Turns:
{transcript_text}

Perform full technical synthesis and return the structured JSON assessment.
"""

    def call_gemini(client: genai.Client, model_name: str) -> dict:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYNTHESIS_SYSTEM_PROMPT,
                temperature=0.3,
                response_mime_type="application/json"
            )
        )
        return _extract_json(response.text)

    return key_pool.execute(call_gemini)


# Backward compatibility wrapper for legacy endpoint
def generate_interview_question(context: str, topic: str) -> str:
    return generate_grounded_question(
        resume_context=context,
        role_topic=topic,
        difficulty_level=2,
        turn_index=1
    )