#!/bin/bash
# Linux/macOS launcher script for Streamlit app

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run Streamlit app
streamlit run app/streamlit_app.py









