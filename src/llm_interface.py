"""
LLM Interface module for interacting with the master evaluation model.

This version exclusively targets OpenAI's GPT-4o mini (or any compatible
model exposed through the Chat Completions API). All text generation used
throughout the assignment routes through this module so the rest of the
codebase stays provider-agnostic.
"""

import logging
from typing import Optional, List, Dict, Any

from openai import OpenAI, OpenAIError

from src.config import (
    MASTER_MODEL_NAME,
    MASTER_MAX_NEW_TOKENS,
    MASTER_TEMPERATURE,
    OPENAI_API_KEY
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global client for lazy initialization
_openai_client: Optional[OpenAI] = None

# Default system prompts
EVALUATOR_SYSTEM_PROMPT = (
    "You are an expert machine learning instructor with deep expertise in ML theory, "
    "pedagogy, and assessment. Your role is to evaluate student answers with precision, "
    "fairness, and educational value. Apply the following principles:\n"
    "- **Semantic Understanding**: Focus on conceptual correctness, not just word matching\n"
    "- **Fair Assessment**: Recognize valid alternative phrasings and equivalent explanations\n"
    "- **Constructive Feedback**: Identify both strengths and areas for improvement\n"
    "- **Consistency**: Apply scoring criteria uniformly across all evaluations\n"
    "- **Pedagogical Value**: Provide explanations that help students learn and improve"
)

NOVICE_SYSTEM_PROMPT = (
    "You are a confused beginner who only partially understands machine learning. "
    "When answering questions you make small mistakes and omit key ideas."
)


def _get_openai_client() -> OpenAI:
    """Lazily create and cache the OpenAI client."""
    global _openai_client
    if _openai_client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError(
                "Missing OpenAI credentials. Please set the OPENAI_API_KEY "
                "environment variable before running the app."
            )
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("Initialized OpenAI client")
    return _openai_client


def _call_openai(
    messages: List[Dict[str, Any]],
    max_new_tokens: int,
    temperature: float,
) -> str:
    """Helper that wraps the Chat Completions API."""
    client = _get_openai_client()
    try:
        response = client.chat.completions.create(
            model=MASTER_MODEL_NAME,
            messages=messages,
            max_tokens=max_new_tokens,
            temperature=temperature,
        )
        content = response.choices[0].message.content or ""
        return content.strip()
    except OpenAIError as exc:
        error_msg = f"OpenAI API error: {exc}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from exc


def generate_completion(
    prompt: str,
    max_new_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
) -> str:
    """
    Generate text completion using the OpenAI Chat Completions API.

    Args:
        prompt: The input prompt text
        max_new_tokens: Maximum tokens to generate (defaults to config value)
        temperature: Sampling temperature (defaults to config value)

    Returns:
        Generated text string (only new tokens, prompt is excluded)

    Raises:
        RuntimeError: If the OpenAI API fails
    """
    if max_new_tokens is None:
        max_new_tokens = MASTER_MAX_NEW_TOKENS
    if temperature is None:
        temperature = MASTER_TEMPERATURE

    messages = [
        {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    return _call_openai(messages, max_new_tokens, temperature)


def generate_novice_answer(question: str) -> str:
    """
    Generate a simulated "novice" student answer using the OpenAI model.

    Args:
        question: The question text to answer

    Returns:
        A simulated novice student answer

    Raises:
        RuntimeError: If the OpenAI API fails
    """
    prompt = (
        "Provide a short answer to the following machine learning question. "
        "Demonstrate partial understanding but leave small gaps or mistakes.\n\n"
        f"Question: {question}\n\nNovice answer:"
    )

    messages = [
        {"role": "system", "content": NOVICE_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    return _call_openai(messages, max_new_tokens=200, temperature=0.7)

