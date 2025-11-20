@echo off
REM Windows launcher script for Streamlit app

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Run Streamlit app
streamlit run app/streamlit_app.py

pause













