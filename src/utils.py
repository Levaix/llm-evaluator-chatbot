"""
Utility functions for the LLM Evaluator Chatbot.

This module provides helper functions for logging, timestamps, and
other common operations used throughout the application.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from src.config import LOG_PATH


def get_timestamp() -> str:
    """
    Get current timestamp as ISO format string.
    
    Returns:
        ISO format timestamp string (e.g., "2024-01-15T14:30:45.123456")
    """
    return datetime.now().isoformat()


def append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    """
    Append a record to a JSONL (JSON Lines) file.
    
    JSONL format means each line is a separate JSON object.
    This is useful for append-only logging of evaluations.
    
    Args:
        path: Path to the JSONL file
        record: Dictionary to append as a JSON line
    
    Raises:
        IOError: If file cannot be written
    """
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert record to JSON string
    json_line = json.dumps(record, ensure_ascii=False)
    
    # Append to file
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(json_line + '\n')
    except Exception as e:
        error_msg = f"Failed to append to JSONL file {path}: {e}"
        raise IOError(error_msg) from e


def format_score_display(score: int) -> str:
    """
    Format a score (0-100) for display.
    
    Args:
        score: Integer score from 0 to 100
    
    Returns:
        Formatted string (e.g., "85/100")
    """
    return f"{score}/100"


def get_score_color(score: int) -> str:
    """
    Get a color name for a score (useful for UI).
    
    Args:
        score: Integer score from 0 to 100
    
    Returns:
        Color name: "red" (<50), "orange" (50-69), "yellow" (70-84), "green" (>=85)
    """
    if score < 50:
        return "red"
    elif score < 70:
        return "orange"
    elif score < 85:
        return "yellow"
    else:
        return "green"













