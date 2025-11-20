"""
Sentiment analysis module for user feedback.

This module provides a simple sentiment analysis function using a
lightweight transformer model. It's used to analyze user feedback
on the evaluation quality.
"""

import logging
from transformers import pipeline
from typing import Dict

from src.config import SENTIMENT_MODEL_NAME

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache the sentiment pipeline
_sentiment_pipeline = None


def _get_sentiment_pipeline():
    """Lazy load and cache the sentiment analysis pipeline."""
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        logger.info(f"Loading sentiment analysis model: {SENTIMENT_MODEL_NAME}")
        try:
            _sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=SENTIMENT_MODEL_NAME,
                device=-1  # Use CPU by default (model is small)
            )
            logger.info("Sentiment analysis model loaded")
        except Exception as e:
            logger.warning(f"Failed to load sentiment model: {e}. Sentiment analysis will be disabled.")
            _sentiment_pipeline = None
    return _sentiment_pipeline


def analyze_feedback_sentiment(text: str) -> Dict[str, any]:
    """
    Analyze the sentiment of user feedback text.
    
    This function uses a pre-trained sentiment analysis model to classify
    the feedback as POSITIVE, NEGATIVE, or NEUTRAL, along with a confidence score.
    
    Args:
        text: The feedback text to analyze
    
    Returns:
        Dictionary with keys:
        - "label": "POSITIVE", "NEGATIVE", or "NEUTRAL"
        - "score": float confidence score (0-1)
        
        If sentiment analysis fails, returns:
        - "label": "NEUTRAL"
        - "score": 0.5
    """
    if not text or not text.strip():
        return {"label": "NEUTRAL", "score": 0.5}
    
    pipeline_obj = _get_sentiment_pipeline()
    
    if pipeline_obj is None:
        # Fallback if model failed to load
        return {"label": "NEUTRAL", "score": 0.5}
    
    try:
        # Run sentiment analysis
        results = pipeline_obj(text, truncation=True, max_length=512)
        
        # Handle both single result and list of results
        if isinstance(results, list) and len(results) > 0:
            result = results[0]
        else:
            result = results
        
        # Extract label and score
        label = result.get("label", "NEUTRAL").upper()
        score = float(result.get("score", 0.5))
        
        # Map to our standard labels
        # The model typically returns "POSITIVE" or "NEGATIVE"
        # We consider scores near 0.5 as NEUTRAL
        if 0.4 <= score <= 0.6:
            label = "NEUTRAL"
        elif label not in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
            # Normalize label
            if "POS" in label or "positive" in label.lower():
                label = "POSITIVE"
            elif "NEG" in label or "negative" in label.lower():
                label = "NEGATIVE"
            else:
                label = "NEUTRAL"
        
        return {
            "label": label,
            "score": score
        }
    
    except Exception as e:
        logger.warning(f"Sentiment analysis failed for text '{text[:50]}...': {e}")
        return {"label": "NEUTRAL", "score": 0.5}













