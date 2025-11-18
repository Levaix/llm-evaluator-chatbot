"""
Streamlit Chatbot Application for LLM-based Answer Evaluation

This is the main Streamlit web application that provides a chatbot-like
interface for evaluating student answers to ML questions. It integrates
all the core modules (data loading, LLM evaluation, sentiment analysis)
into a user-friendly web interface.
"""

import sys
from pathlib import Path
import os

# Add project root to Python path so we can import src modules
# This ensures the app works regardless of where it's run from
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Change to project root directory so relative paths work correctly
os.chdir(project_root)

# Load environment variables from .env file (if it exists)
# This must be done before importing src.config which reads these variables
try:
    from dotenv import load_dotenv
    load_dotenv()  # Loads variables from .env file in project root
except ImportError:
    # python-dotenv not installed, will use system environment variables only
    pass
except Exception as e:
    # If .env file doesn't exist or other error, continue with system env vars
    pass

import streamlit as st
import pandas as pd
import logging

from src.config import DATA_PATH, LOG_PATH, print_config
from src.data_loader import load_qa_dataset, get_random_question
from src.evaluator import evaluate_answer, EvaluationResult
from src.sentiment import analyze_feedback_sentiment
from src.utils import (
    append_jsonl,
    get_timestamp,
    format_score_display,
    get_score_color
)
from src.llm_interface import generate_novice_answer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="LLM Evaluator Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "last_evaluation" not in st.session_state:
    st.session_state.last_evaluation = None
if "dataset" not in st.session_state:
    st.session_state.dataset = None
if "show_reference" not in st.session_state:
    st.session_state.show_reference = False
if "language" not in st.session_state:
    st.session_state.language = "English"


def load_dataset():
    """Load the Q&A dataset and store in session state."""
    try:
        if st.session_state.dataset is None:
            with st.spinner("Loading Q&A dataset..."):
                st.session_state.dataset = load_qa_dataset()
            st.success(f"Loaded {len(st.session_state.dataset)} questions")
        return st.session_state.dataset
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        st.info(f"Please ensure the file exists at: {DATA_PATH}")
        return None


def get_new_question():
    """Get a new random question and update session state."""
    dataset = load_dataset()
    if dataset is None:
        return
    
    try:
        question_data = get_random_question(dataset)
        st.session_state.current_question = question_data
        st.session_state.last_evaluation = None
        st.rerun()
    except Exception as e:
        st.error(f"Failed to get question: {e}")


def log_evaluation(eval_result: EvaluationResult, feedback_tags=None, feedback_text="", sentiment_result=None):
    """Log an evaluation to the JSONL file."""
    record = {
        "timestamp": get_timestamp(),
        "question_id": eval_result.question_id,
        "question_text": eval_result.question,
        "reference_answer": eval_result.reference_answer,
        "student_answer": eval_result.student_answer,
        "llm_score": eval_result.llm_score,
        "rouge_1": eval_result.rouge_1,
        "rouge_l": eval_result.rouge_l,
        "llm_explanation": eval_result.llm_explanation,
        "user_feedback_tags": feedback_tags or [],
        "user_feedback_text": feedback_text,
        "feedback_sentiment_label": sentiment_result.get("label", "NEUTRAL") if sentiment_result else "NEUTRAL",
        "feedback_sentiment_score": sentiment_result.get("score", 0.5) if sentiment_result else 0.5,
    }
    
    try:
        append_jsonl(LOG_PATH, record)
        logger.info("Evaluation logged successfully")
    except Exception as e:
        logger.error(f"Failed to log evaluation: {e}")
        st.warning(f"Failed to log evaluation: {e}")


# Main UI
st.title("🤖 LLM Evaluator Chatbot")
st.markdown("**Part 2: LLM-based Answer Evaluation System**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Print config info
    with st.expander("System Configuration", expanded=False):
        from src.config import MASTER_MODEL_NAME
        st.code(f"""
Model: {MASTER_MODEL_NAME}
Data Path: {DATA_PATH}
Log Path: {LOG_PATH}
        """.strip())
    
    # Load dataset info
    dataset = load_dataset()
    if dataset is not None:
        st.success(f"✅ Dataset loaded: {len(dataset)} questions")
    else:
        st.error("❌ Dataset not loaded")
    
    st.divider()
    
    # Language selection
    st.subheader("🌐 Language")
    language_options = ["English", "Spanish", "French", "German", "Italian", "Portuguese"]
    selected_language = st.selectbox(
        "Evaluation Language",
        language_options,
        index=language_options.index(st.session_state.language) if st.session_state.language in language_options else 0
    )
    st.session_state.language = selected_language
    
    st.divider()
    
    # Display options
    st.subheader("📋 Display Options")
    st.session_state.show_reference = st.checkbox(
        "Show reference answer by default",
        value=st.session_state.show_reference
    )
    
    st.divider()
    
    # Navigation
    st.subheader("🧭 Navigation")
    if st.button("🔄 New Question", use_container_width=True):
        get_new_question()
    
    st.divider()
    
    # Info
    st.info("""
    **Instructions:**
    1. Answer the question shown
    2. Click "Evaluate Answer"
    3. Review the evaluation
    4. Provide feedback (optional)
    5. Click "New Question" to continue
    """)


# Main content area
if dataset is None:
    st.error("⚠️ Cannot proceed without dataset. Please ensure the Q&A database file exists.")
    st.stop()

# Get or initialize current question
if st.session_state.current_question is None:
    get_new_question()

if st.session_state.current_question is None:
    st.warning("No question available. Please check the dataset.")
    st.stop()

current_q = st.session_state.current_question

# Display current question
st.header("📝 Current Question")
st.info(f"**Question ID:** {current_q['id']}")
st.markdown(f"### {current_q['question']}")

# Reference answer (expandable)
with st.expander("📚 Reference Answer", expanded=st.session_state.show_reference):
    st.markdown(current_q['answer'])

st.divider()

# Answer input section
st.header("✍️ Your Answer")

# Initialize answer input state
if "student_answer_input" not in st.session_state:
    st.session_state.student_answer_input = ""

# Apply any pending updates (e.g., generated novice answer) before rendering widget
if "pending_student_answer" in st.session_state:
    st.session_state.student_answer_input = st.session_state.pending_student_answer
    del st.session_state.pending_student_answer

# Text area for student answer
student_answer = st.text_area(
    "Type your answer here:",
    height=200,
    placeholder="Enter your answer to the question above...",
    key="student_answer_input"
)

# Buttons row
col1, col2 = st.columns(2)

with col1:
    if st.button("🎲 Generate Novice Answer", use_container_width=True):
        with st.spinner("Generating novice answer..."):
            try:
                novice_answer = generate_novice_answer(current_q['question'])
                st.session_state.pending_student_answer = novice_answer
                st.rerun()
            except Exception as e:
                st.error(f"Failed to generate novice answer: {e}")

with col2:
    evaluate_clicked = st.button("✅ Evaluate Answer", use_container_width=True, type="primary")

# Evaluation section
if evaluate_clicked and student_answer.strip():
    with st.spinner("Evaluating your answer... This may take a moment."):
        try:
            # Perform evaluation
            eval_result = evaluate_answer(
                question_id=current_q['id'],
                question=current_q['question'],
                reference_answer=current_q['answer'],
                student_answer=student_answer,
                language=st.session_state.language
            )
            
            # Store in session state
            st.session_state.last_evaluation = eval_result
            
            # Display results
            st.divider()
            st.header("📊 Evaluation Results")
            
            # Score display
            score_color = get_score_color(eval_result.llm_score)
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.metric("LLM Score", format_score_display(eval_result.llm_score))
                st.progress(eval_result.llm_score / 100.0)
            
            with col2:
                st.metric("ROUGE-1", f"{eval_result.rouge_1:.3f}")
            
            with col3:
                st.metric("ROUGE-L", f"{eval_result.rouge_l:.3f}")
            
            # LLM Explanation
            st.subheader("💬 Detailed Explanation")
            st.markdown(eval_result.llm_explanation)
            
            # Show student answer for reference
            with st.expander("📝 Your Answer (for reference)"):
                st.markdown(student_answer)
            
        except Exception as e:
            st.error(f"Evaluation failed: {e}")
            logger.error(f"Evaluation error: {e}", exc_info=True)

# Display previous evaluation if exists
elif st.session_state.last_evaluation is not None:
    eval_result = st.session_state.last_evaluation
    st.divider()
    st.header("📊 Previous Evaluation Results")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.metric("LLM Score", format_score_display(eval_result.llm_score))
        st.progress(eval_result.llm_score / 100.0)
    with col2:
        st.metric("ROUGE-1", f"{eval_result.rouge_1:.3f}")
    with col3:
        st.metric("ROUGE-L", f"{eval_result.rouge_l:.3f}")
    
    st.subheader("💬 Detailed Explanation")
    st.markdown(eval_result.llm_explanation)

# Feedback section (only show if evaluation exists)
if st.session_state.last_evaluation is not None:
    st.divider()
    st.header("💭 Feedback on Evaluation")
    
    feedback_tags = st.multiselect(
        "Select applicable tags:",
        options=["useful", "rigorous", "clear", "relevant", "instructive", "unrelated"],
        help="Select tags that describe your experience with this evaluation"
    )
    
    feedback_text = st.text_area(
        "Additional comments (optional):",
        height=100,
        placeholder="Share your thoughts about the evaluation quality..."
    )
    
    if st.button("📤 Submit Feedback", type="primary"):
        if feedback_tags or feedback_text.strip():
            # Analyze sentiment if feedback text provided
            sentiment_result = None
            if feedback_text.strip():
                with st.spinner("Analyzing sentiment..."):
                    sentiment_result = analyze_feedback_sentiment(feedback_text)
            
            # Log evaluation with feedback
            log_evaluation(
                st.session_state.last_evaluation,
                feedback_tags=feedback_tags,
                feedback_text=feedback_text,
                sentiment_result=sentiment_result
            )
            
            # Show sentiment result if available
            if sentiment_result:
                sentiment_label = sentiment_result["label"]
                sentiment_score = sentiment_result["score"]
                st.success(f"✅ Feedback submitted! Sentiment: {sentiment_label} (confidence: {sentiment_score:.2f})")
            else:
                st.success("✅ Feedback submitted!")
            
            # Clear feedback inputs
            st.rerun()
        else:
            st.warning("Please provide at least one tag or comment before submitting.")

# Footer
st.divider()
st.caption("LLM Evaluator Chatbot - Part 2 of DAI Assignment | All evaluations are logged to the JSONL file")

