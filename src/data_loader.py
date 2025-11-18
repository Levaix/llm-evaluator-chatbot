"""
Data loading module for Q&A dataset.

This module handles loading and accessing the Q&A database JSON file.
It provides functions to load the dataset, get random questions, and
retrieve questions by ID with proper error handling.
"""

import json
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Optional
import random

from src.config import DATA_PATH

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_qa_dataset(path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load the Q&A dataset from a JSON file.
    
    The JSON file should contain a list of objects, each with:
    - "question": string (the question text)
    - "answer": string (the reference/standard answer)
    
    Args:
        path: Optional path to the JSON file. If None, uses DATA_PATH from config.
    
    Returns:
        pd.DataFrame with columns: ['id', 'question', 'answer']
        - id: integer index (0-based)
        - question: the question text
        - answer: the reference answer
    
    Raises:
        FileNotFoundError: If the JSON file doesn't exist
        ValueError: If the JSON structure is invalid or missing required fields
        json.JSONDecodeError: If the file is not valid JSON
    """
    if path is None:
        path = DATA_PATH
    
    # Resolve relative paths to absolute paths
    if not path.is_absolute():
        # Try to resolve relative to current working directory
        path = Path(path).resolve()
    
    # Check if file exists
    if not path.exists():
        error_msg = (
            f"Q&A database file not found at: {path}\n"
            f"Please ensure the file exists. Expected format:\n"
            f'[{{"question": "...", "answer": "..."}}, ...]'
        )
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    try:
        # Read JSON file
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate that data is a list
        if not isinstance(data, list):
            raise ValueError(f"Expected JSON file to contain a list, got {type(data)}")
        
        if len(data) == 0:
            raise ValueError("Q&A database is empty. Please add at least one question-answer pair.")
        
        # Validate structure and build DataFrame
        records = []
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"Item at index {idx} is not a dictionary")
            
            if "question" not in item or "answer" not in item:
                raise ValueError(
                    f"Item at index {idx} is missing 'question' or 'answer' field. "
                    f"Found keys: {list(item.keys())}"
                )
            
            # Ensure both fields are strings
            question = str(item["question"]).strip()
            answer = str(item["answer"]).strip()
            
            if not question or not answer:
                logger.warning(f"Item at index {idx} has empty question or answer, skipping")
                continue
            
            records.append({
                "id": idx,
                "question": question,
                "answer": answer
            })
        
        if len(records) == 0:
            raise ValueError("No valid question-answer pairs found in the dataset")
        
        df = pd.DataFrame(records)
        logger.info(f"Successfully loaded {len(df)} question-answer pairs from {path}")
        
        return df
    
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format in {path}: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    except Exception as e:
        error_msg = f"Error loading Q&A dataset from {path}: {e}"
        logger.error(error_msg)
        raise


def get_random_question(df: pd.DataFrame) -> Dict[str, any]:
    """
    Get a random question from the dataset.
    
    Args:
        df: DataFrame from load_qa_dataset()
    
    Returns:
        Dictionary with keys: {"id": int, "question": str, "answer": str}
    
    Raises:
        ValueError: If DataFrame is empty
    """
    if df.empty:
        raise ValueError("Cannot get random question from empty dataset")
    
    # Select a random row
    random_row = df.sample(n=1).iloc[0]
    
    return {
        "id": int(random_row["id"]),
        "question": str(random_row["question"]),
        "answer": str(random_row["answer"])
    }


def get_question_by_id(df: pd.DataFrame, qid: int) -> Dict[str, any]:
    """
    Get a question by its ID.
    
    Args:
        df: DataFrame from load_qa_dataset()
        qid: Integer question ID
    
    Returns:
        Dictionary with keys: {"id": int, "question": str, "answer": str}
    
    Raises:
        ValueError: If question ID doesn't exist
    """
    if df.empty:
        raise ValueError("Dataset is empty")
    
    # Filter by ID
    matches = df[df["id"] == qid]
    
    if matches.empty:
        available_ids = df["id"].tolist()
        raise ValueError(
            f"Question ID {qid} not found. Available IDs: {available_ids}"
        )
    
    row = matches.iloc[0]
    
    return {
        "id": int(row["id"]),
        "question": str(row["question"]),
        "answer": str(row["answer"])
    }









