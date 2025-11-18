"""
Core evaluation module for comparing student answers to reference answers.

This module implements the main evaluation logic, combining:
1. LLM-based evaluation (explanation + score)
2. Automatic metrics (ROUGE-1, ROUGE-L)

The evaluation prompt is carefully designed to get consistent, useful
feedback from the LLM, and the score is parsed from the LLM's response.
"""

import logging
import re
from dataclasses import dataclass
from typing import Optional

from evaluate import load as load_metric

from src.config import ROUGE_METRIC_NAME
from src.llm_interface import generate_completion

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache the ROUGE metric to avoid reloading
_rouge_metric = None


def _get_rouge_metric():
    """Lazy load and cache the ROUGE metric."""
    global _rouge_metric
    if _rouge_metric is None:
        logger.info("Loading ROUGE metric...")
        _rouge_metric = load_metric(ROUGE_METRIC_NAME)
        logger.info("ROUGE metric loaded")
    return _rouge_metric


@dataclass
class EvaluationResult:
    """
    Container for evaluation results.
    
    Attributes:
        question_id: ID of the question (or None if not from dataset)
        question: The question text
        reference_answer: The standard/reference answer
        student_answer: The student's answer being evaluated
        llm_explanation: Detailed explanation from the LLM evaluator
        llm_score: Numerical score (0-100) from LLM
        rouge_1: ROUGE-1 F1 score (0-1)
        rouge_l: ROUGE-L F1 score (0-1)
    """
    question_id: Optional[int]
    question: str
    reference_answer: str
    student_answer: str
    llm_explanation: str
    llm_score: int
    rouge_1: float
    rouge_l: float


def build_evaluation_prompt(
    question: str,
    reference_answer: str,
    student_answer: str,
    language: str = "English"
) -> str:
    """
    Build a prompt for the LLM to evaluate a student's answer.
    
    The prompt instructs the LLM to:
    1. Compare the student answer to the reference answer
    2. Identify correctness, missing points, misconceptions
    3. Provide a detailed explanation
    4. Output a numerical score (0-100)
    
    Args:
        question: The question text
        reference_answer: The ideal/reference answer
        student_answer: The student's answer to evaluate
        language: Language for the response (e.g., "English", "Spanish")
    
    Returns:
        Formatted prompt string
    """
    prompt = f"""You are an expert machine learning instructor grading a student's answer to a theory question.

## Task
Evaluate the student's answer against the reference answer using a structured, step-by-step approach.

## Question
{question}

## Reference Answer (Ideal Answer)
{reference_answer}

## Student's Answer
{student_answer}

## Evaluation Process
Follow these steps systematically:

### Step 1: Content Analysis
- Identify all key concepts, principles, and facts present in the reference answer
- Check which of these concepts appear in the student's answer (even if phrased differently)
- Note any additional valid points the student may have included

### Step 2: Correctness Assessment
- **Correct Elements**: List what the student got right, including:
  * Accurate definitions or explanations
  * Correct conceptual understanding (even with different wording)
  * Valid examples or applications
- **Missing Elements**: Identify important concepts from the reference that are absent
- **Errors/Misconceptions**: Note any incorrect statements, misunderstandings, or conceptual errors

### Step 3: Semantic Equivalence Evaluation
- Consider whether the student's phrasing, while different, conveys the same meaning
- Recognize that correct answers can be expressed in multiple valid ways
- Do not penalize for stylistic differences if the core understanding is correct

### Step 4: Completeness Assessment
- Evaluate how comprehensively the student addressed the question
- Consider the depth of explanation relative to the reference answer
- Assess whether critical components are present, even if not all details are included

### Step 5: Scoring Rubric
Assign a score from 0 to 100 based on this detailed rubric:

**0-30 (Failing)**: 
- Major misconceptions or fundamental errors
- Completely incorrect understanding
- No valid concepts identified

**31-50 (Insufficient)**:
- Partially correct but missing most key concepts
- Some understanding but significant gaps
- Contains notable errors alongside correct elements

**51-70 (Adequate)**:
- Mostly correct with some important gaps
- Demonstrates basic understanding of core concepts
- Minor errors or omissions that don't fundamentally undermine the answer

**71-85 (Good)**:
- Strong understanding with minor gaps or omissions
- Covers most key concepts accurately
- May lack some depth or detail compared to reference

**86-100 (Excellent)**:
- Comprehensive and accurate answer
- Demonstrates deep understanding
- Covers all or nearly all key concepts
- May include additional valid insights

### Step 6: Constructive Explanation
Provide a detailed explanation that:
- Summarizes what the student understood correctly
- Clearly identifies what was missing or incorrect
- Explains the reasoning behind the assigned score
- Offers pedagogical insights for improvement

## Response Format
Please respond in {language}. Use this exact format:

**Step 1 - Content Analysis:**
[Your analysis here]

**Step 2 - Correctness Assessment:**
- Correct Elements: [list]
- Missing Elements: [list]
- Errors/Misconceptions: [list]

**Step 3 - Semantic Equivalence:**
[Your assessment of whether different phrasings convey equivalent meaning]

**Step 4 - Completeness:**
[Your evaluation of how comprehensively the question was addressed]

**Step 5 - Score Justification:**
[Explain why this specific score was assigned based on the rubric]

**Explanation:**
[Your comprehensive, pedagogical explanation suitable for student feedback]

**Score:** [A single integer from 0 to 100]

Begin your evaluation now:"""
    
    return prompt


def parse_score_from_text(text: str) -> int:
    """
    Parse the numerical score from the LLM's response text.
    
    Looks for patterns like:
    - "Score: 73"
    - "score = 73"
    - "73" (if preceded by "score" or similar)
    
    Args:
        text: The LLM response text containing the score
    
    Returns:
        Integer score between 0 and 100
        Defaults to 50 if parsing fails (conservative middle ground)
    
    Note:
        This is a simple regex-based parser. For production, consider
        more robust parsing or structured output formats.
    """
    # Try multiple patterns (including optional negative sign)
    patterns = [
        r"Score:\s*(-?\d+)",  # Match optional negative sign
        r"score:\s*(-?\d+)",
        r"Score\s*=\s*(-?\d+)",
        r"score\s*=\s*(-?\d+)",
        r"(-?\d+)\s*out\s*of\s*100",
        r"score\s+of\s+(-?\d+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                score = int(match.group(1))
                # Clamp to valid range (negative values become 0)
                score = max(0, min(100, score))
                return score
            except (ValueError, IndexError):
                continue
    
    # If no pattern matches, try to find any number between 0-100
    # that appears near the word "score"
    score_context = re.search(r"score.*?(\d{1,3})", text, re.IGNORECASE)
    if score_context:
        try:
            score = int(score_context.group(1))
            if 0 <= score <= 100:
                return score
        except (ValueError, IndexError):
            pass
    
    # Fallback: look for any number 0-100 in the last few lines
    lines = text.split('\n')[-5:]
    for line in reversed(lines):
        numbers = re.findall(r'\b(\d{1,3})\b', line)
        for num_str in numbers:
            try:
                score = int(num_str)
                if 0 <= score <= 100:
                    return score
            except ValueError:
                continue
    
    # Default fallback
    logger.warning(f"Could not parse score from text. Using default score of 50.")
    logger.debug(f"Text was: {text[:200]}...")
    return 50


def evaluate_answer(
    question_id: Optional[int],
    question: str,
    reference_answer: str,
    student_answer: str,
    language: str = "English",
) -> EvaluationResult:
    """
    Evaluate a student's answer against a reference answer.
    
    This is the main evaluation function that:
    1. Builds an evaluation prompt
    2. Calls the LLM to generate an explanation and score
    3. Parses the score from the LLM response
    4. Computes ROUGE metrics (ROUGE-1 and ROUGE-L)
    5. Returns a complete EvaluationResult
    
    Args:
        question_id: ID of the question (or None)
        question: The question text
        reference_answer: The standard/reference answer
        student_answer: The student's answer to evaluate
        language: Language for evaluation response (default: "English")
    
    Returns:
        EvaluationResult with all evaluation metrics
    
    Raises:
        RuntimeError: If LLM generation fails
        Exception: If ROUGE computation fails
    """
    logger.info(f"Evaluating answer for question ID: {question_id}")
    
    # Step 1: Build evaluation prompt
    prompt = build_evaluation_prompt(
        question=question,
        reference_answer=reference_answer,
        student_answer=student_answer,
        language=language
    )
    
    # Step 2: Call LLM for evaluation
    try:
        llm_response = generate_completion(prompt)
        logger.debug(f"LLM response length: {len(llm_response)} characters")
    except Exception as e:
        error_msg = f"Failed to generate LLM evaluation: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
    # Step 3: Parse score from LLM response
    llm_score = parse_score_from_text(llm_response)
    logger.info(f"Parsed LLM score: {llm_score}/100")
    
    # Step 4: Compute ROUGE metrics
    try:
        rouge_metric = _get_rouge_metric()
        
        # ROUGE expects lists of strings
        results = rouge_metric.compute(
            predictions=[student_answer],
            references=[reference_answer]
        )
        
        # Extract ROUGE-1 and ROUGE-L F1 scores
        rouge_1 = float(results.get("rouge1", 0.0))
        rouge_l = float(results.get("rougeL", 0.0))
        
        logger.info(f"ROUGE-1: {rouge_1:.3f}, ROUGE-L: {rouge_l:.3f}")
        
    except Exception as e:
        logger.warning(f"Failed to compute ROUGE metrics: {e}. Using 0.0 as fallback.")
        rouge_1 = 0.0
        rouge_l = 0.0
    
    # Step 5: Create and return result
    result = EvaluationResult(
        question_id=question_id,
        question=question,
        reference_answer=reference_answer,
        student_answer=student_answer,
        llm_explanation=llm_response,
        llm_score=llm_score,
        rouge_1=rouge_1,
        rouge_l=rouge_l
    )
    
    return result

