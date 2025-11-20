"""
Test module for the evaluator functionality.

This module contains pytest-style tests for the evaluation system.
It uses mocking to avoid loading the heavy LLM model during testing.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.evaluator import (
    build_evaluation_prompt,
    parse_score_from_text,
    evaluate_answer,
    EvaluationResult
)


def test_build_evaluation_prompt():
    """Test that build_evaluation_prompt returns a non-empty string."""
    question = "What is an activation function?"
    reference = "An activation function introduces non-linearity into neural networks."
    student = "It's a function used in neural networks."
    language = "English"
    
    prompt = build_evaluation_prompt(question, reference, student, language)
    
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert question in prompt
    assert reference in prompt
    assert student in prompt
    assert language in prompt


def test_parse_score_from_text():
    """Test parsing scores from various text formats."""
    # Test case 1: "Score: 73"
    text1 = "Explanation: The answer is mostly correct. Score: 73"
    assert parse_score_from_text(text1) == 73
    
    # Test case 2: "score = 85"
    text2 = "The student's answer is excellent. score = 85"
    assert parse_score_from_text(text2) == 85
    
    # Test case 3: "Score: 100"
    text3 = "Perfect answer. Score: 100"
    assert parse_score_from_text(text3) == 100
    
    # Test case 4: No score found (should default to 50)
    text4 = "This is an explanation without a score."
    result = parse_score_from_text(text4)
    assert isinstance(result, int)
    assert 0 <= result <= 100
    
    # Test case 5: Score out of range (should be clamped)
    text5 = "Score: 150"  # Invalid, should clamp to 100
    assert parse_score_from_text(text5) == 100
    
    text6 = "Score: -10"  # Invalid, should clamp to 0
    assert parse_score_from_text(text6) == 0


@patch('src.evaluator.generate_completion')
@patch('src.evaluator._get_rouge_metric')
def test_evaluate_answer_end_to_end(mock_rouge, mock_generate):
    """
    Test evaluate_answer function end-to-end with mocked LLM.
    
    This test mocks the LLM generation and ROUGE computation to avoid
    loading the actual model during testing.
    """
    # Mock LLM response
    mock_llm_response = """
    Explanation: The student's answer is partially correct but misses some key points.
    The answer shows understanding of the basic concept but lacks detail.
    
    Score: 65
    """
    mock_generate.return_value = mock_llm_response
    
    # Mock ROUGE metric
    mock_rouge_instance = MagicMock()
    mock_rouge_instance.compute.return_value = {
        "rouge1": 0.45,
        "rougeL": 0.42
    }
    mock_rouge.return_value = mock_rouge_instance
    
    # Test data
    question = "What is backpropagation?"
    reference = "Backpropagation is an algorithm for training neural networks by propagating errors backward."
    student = "Backpropagation is used to train neural networks."
    
    # Call evaluate_answer
    result = evaluate_answer(
        question_id=1,
        question=question,
        reference_answer=reference,
        student_answer=student,
        language="English"
    )
    
    # Verify result structure
    assert isinstance(result, EvaluationResult)
    assert result.question_id == 1
    assert result.question == question
    assert result.reference_answer == reference
    assert result.student_answer == student
    assert result.llm_explanation == mock_llm_response
    assert result.llm_score == 65  # Parsed from mock response
    assert result.rouge_1 == 0.45
    assert result.rouge_l == 0.42
    
    # Verify mocks were called
    mock_generate.assert_called_once()
    mock_rouge_instance.compute.assert_called_once()


def test_evaluate_answer_with_different_languages():
    """Test that evaluate_answer works with different languages."""
    # This is a simple test that just verifies the language parameter is passed through
    # We don't need to actually call the LLM, just check the prompt building
    
    question = "What is machine learning?"
    reference = "Machine learning is a subset of AI."
    student = "ML is AI."
    
    prompt_english = build_evaluation_prompt(question, reference, student, "English")
    prompt_spanish = build_evaluation_prompt(question, reference, student, "Spanish")
    
    assert "English" in prompt_english
    assert "Spanish" in prompt_spanish
    assert prompt_english != prompt_spanish


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])













