"""
Configuration module for the LLM Evaluator Chatbot.

This module centralizes all configuration settings, allowing easy customization
via environment variables. It ensures required directories exist and provides
a function to print the current configuration for debugging.
"""

import os
from pathlib import Path


# Model Configuration
# The master LLM model used for evaluation (served via OpenAI)
# Default: gpt-4o-mini (fast, cost-efficient, strong reasoning ability)
MASTER_MODEL_NAME = os.getenv("MASTER_MODEL_NAME", "gpt-4o-mini")

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Maximum number of new tokens to generate during evaluation
# Lower values are faster but may truncate explanations
MASTER_MAX_NEW_TOKENS = int(os.getenv("MASTER_MAX_NEW_TOKENS", "512"))

# Temperature for generation (0.0 = deterministic, higher = more creative)
# Low temperature (0.2) is preferred for consistent evaluation
MASTER_TEMPERATURE = float(os.getenv("MASTER_TEMPERATURE", "0.2"))

# Data Paths
# Path to the Q&A database JSON file
DATA_PATH = Path(os.getenv("DATA_PATH", "data/Q&A_db_practice.json"))

# Path to the evaluation log file (JSONL format, append-only)
LOG_PATH = Path(os.getenv("LOG_PATH", "data/evaluations_log.jsonl"))

# Sentiment Analysis Model
# Small, fast model for analyzing user feedback sentiment
SENTIMENT_MODEL_NAME = os.getenv("SENTIMENT_MODEL_NAME", "distilbert-base-uncased-finetuned-sst-2-english")

# ROUGE Metric Configuration
# Cache the ROUGE metric object to avoid repeated loading
ROUGE_METRIC_NAME = "rouge"


def ensure_directories():
    """
    Ensure that all required directories exist.
    Creates directories if they don't exist, with error handling.
    """
    directories = [
        DATA_PATH.parent,  # data/
        LOG_PATH.parent,   # data/ (same as above, but safe to call twice)
    ]
    
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create directory {directory}: {e}")


def print_config():
    """
    Print the current configuration settings for debugging.
    Useful for verifying environment variables are being read correctly.
    """
    print("=" * 60)
    print("LLM Evaluator Chatbot - Configuration")
    print("=" * 60)
    print(f"Master Model Name:     {MASTER_MODEL_NAME}")
    print(f"OpenAI API Key:        {'Set' if OPENAI_API_KEY else 'Not set'}")
    print(f"Max New Tokens:         {MASTER_MAX_NEW_TOKENS}")
    print(f"Temperature:            {MASTER_TEMPERATURE}")
    print(f"Data Path:              {DATA_PATH}")
    print(f"Log Path:               {LOG_PATH}")
    print(f"Sentiment Model:        {SENTIMENT_MODEL_NAME}")
    print("=" * 60)


# Ensure directories exist when module is imported
ensure_directories()

