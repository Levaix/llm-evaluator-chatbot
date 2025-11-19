# LLM Evaluator Chatbot - Part 2

**Part 2 of DAI Assignment: LLM-based Answer Evaluation System**

This project implements a Streamlit chatbot that evaluates student answers to machine learning questions using a combination of LLM-based evaluation and automatic metrics (ROUGE).

> **📊 Documentation with Diagrams**: This project includes comprehensive documentation with visual diagrams:
> - `ARCHITECTURE.md` - System architecture with diagrams
> - `PROCESS_FLOWS.md` - Process flow diagrams
> - `DECISIONS.md` - Decision log
> - `DEPLOYMENT.md` - Deployment strategy
> - `TEST_RESULTS.md` - Test results and metrics
> 
> **How to View Diagrams**: See the [Viewing Diagrams](#-viewing-diagrams) section below.

## 📋 Project Description

The system provides an interactive web interface where:
1. Students are presented with ML theory questions
2. Students submit free-text answers
3. The system evaluates answers by comparing them to reference answers
4. Evaluation includes:
   - **LLM-generated explanation** (detailed feedback on correctness, gaps, misconceptions)
   - **Numerical score** (0-100) from the LLM
   - **ROUGE metrics** (ROUGE-1 and ROUGE-L) for lexical overlap
5. Users can provide feedback on evaluation quality
6. All interactions are logged for analysis

## 🏗️ Folder Structure

```
.
├── data/
│   ├── Q&A_db_practice.json      # Q&A database (included in repository)
│   └── evaluations_log.jsonl     # Log file (created automatically)
├── src/
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── data_loader.py            # Dataset loading functions
│   ├── llm_interface.py          # OpenAI model interface
│   ├── evaluator.py              # Core evaluation logic
│   ├── sentiment.py              # Sentiment analysis for feedback
│   └── utils.py                  # Utility functions
├── app/
│   ├── __init__.py
│   └── streamlit_app.py          # Main Streamlit application
├── notebooks/
│   ├── 01_explore_dataset.ipynb
│   ├── 02_evaluation_prototyping.ipynb
│   └── 03_batch_simulation.ipynb
├── tests/
│   ├── __init__.py
│   └── test_evaluator.py
├── requirements.txt
├── README.md
├── run_app.sh                    # Linux/macOS launcher
└── run_app.bat                   # Windows launcher
```

## 🚀 Installation

### 1. Create Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Prepare Dataset

The `Q&A_db_practice.json` file is already included in the repository in the `data/` directory. The file contains a JSON array of objects with this format:

```json
[
  {
    "question": "What is an activation function?",
    "answer": "An activation function introduces non-linearity into neural networks..."
  },
  {
    "question": "Explain backpropagation.",
    "answer": "Backpropagation is an algorithm for training neural networks..."
  }
]
```

> **Note**: If you want to use your own dataset, you can replace `data/Q&A_db_practice.json` with your own file following the same format.

## 🎯 Running the Application

> ⚠️ **IMPORTANT: Set up API Key First!**
> 
> **Before running the Streamlit application, you MUST set up your OpenAI API key:**
> 
> 1. Copy `.env.example` to `.env`:
>    - **Windows**: `copy .env.example .env`
>    - **Linux/macOS**: `cp .env.example .env`
> 
> 2. Open `.env` and replace `REPLACE_ME` with your actual OpenAI API key:
>    ```
>    OPENAI_API_KEY=sk-your-actual-api-key-here
>    ```
> 
> 3. Get your API key from: https://platform.openai.com/api-keys
> 
> **Without setting the API key, the application will show an error: "Missing OpenAI credentials"**
> 
> See the [Environment Variables](#-environment-variables) section for more details.

### Option 1: Using the Launcher Scripts

**Windows:**
```bash
run_app.bat # if it does not work, use below

.\run_app.bat
```

**Linux/macOS:**
```bash
chmod +x run_app.sh
./run_app.sh
```

### Option 2: Direct Streamlit Command

```bash
streamlit run app/streamlit_app.py
```

The app will open in your default web browser at `http://localhost:8501`.

> ⚠️ **Important:** Always run the command from the project root (the folder that
> contains `app/`, `src/`, `notebooks/`, etc.). If you launch Streamlit from
> somewhere else, Python won’t find the `src` package and you’ll see
> `ModuleNotFoundError: No module named 'src'`.  
> If you must run it from another directory, set `PYTHONPATH` first, e.g.:
> 
> **PowerShell**
> ```powershell
> $env:PYTHONPATH = "C:\Users\Levin\OneDrive\Desktop\DAI Assignment Part 2"
> streamlit run app/streamlit_app.py
> ```
> Replace the path with the location of the project on your machine.

### Working with the Notebooks

The project includes three Jupyter notebooks for exploration and testing:

#### Prerequisites

1. **Install Jupyter** (if not already installed):
   ```bash
   pip install jupyter notebook
   ```
   Or for JupyterLab:
   ```bash
   pip install jupyterlab
   ```

2. **Set up Environment Variables**:
   - Create a `.env` file in the project root (see Configuration section)
   - Or set `OPENAI_API_KEY` as an environment variable:
     - **Windows PowerShell**: `$env:OPENAI_API_KEY="sk-your-key"`
     - **Windows CMD**: `set OPENAI_API_KEY=sk-your-key`
     - **Linux/macOS**: `export OPENAI_API_KEY="sk-your-key"`

#### Running the Notebooks

**Option 1: Jupyter Notebook (Classic)**
```bash
# Navigate to project root
cd "C:\Users\Levin\OneDrive\Desktop\DAI Assignment Part 2" #student example.....professor folder after downloading

# Start Jupyter
jupyter notebook
```
Then navigate to the `notebooks/` folder in the browser and open any notebook.

**Option 2: JupyterLab**
```bash
jupyter lab
```

**Option 3: VS Code**
1. Install the "Jupyter" extension in VS Code
2. Open any `.ipynb` file
3. VS Code will automatically detect it as a notebook
4. Run cells individually or click "Run All"

#### Notebook Descriptions

**01_explore_dataset.ipynb**
- Explores the Q&A database
- Shows statistics and sample entries
- **No API key needed** - just loads data

**02_evaluation_prototyping.ipynb**
- Tests evaluation with good/mediocre/bad answers
- Demonstrates LLM evaluation quality
- **Requires API key** - makes 3 API calls (~$0.001)

**03_batch_simulation.ipynb**
- Runs batch evaluations (5 by default)
- Analyzes correlations between LLM scores and ROUGE
- Creates visualizations
- **Requires API key** - makes multiple API calls (~$0.005-0.01)

#### Troubleshooting

- **"ModuleNotFoundError: No module named 'src'"**: Start Jupyter from the project root directory
- **"Missing OpenAI credentials"**: Set `OPENAI_API_KEY` environment variable or create `.env` file
- **"FileNotFoundError: Q&A database file not found"**: The file should be included in the repository. If missing, ensure you've cloned/downloaded the complete repository.
- **Jupyter not found**: Install with `pip install jupyter notebook`

**Note**: All notebooks automatically load environment variables from `.env` file (if it exists) thanks to `python-dotenv` in the first cell.

## ⚙️ Configuration

### Environment Variables

You can customize the system using environment variables. The repo ships with a
`.env.example`—copy it to `.env`, paste your key, and everything (app + notebooks)
will pick it up automatically thanks to `python-dotenv`.

- `OPENAI_API_KEY`: **Required.** Your OpenAI API key (never commit it).
- `MASTER_MODEL_NAME`: OpenAI model ID (default: `gpt-4o-mini`).
- `MASTER_MAX_NEW_TOKENS`: Maximum tokens to generate (default: `512`).
- `MASTER_TEMPERATURE`: Generation temperature (default: `0.2`).
- `DATA_PATH`: Path to Q&A database (default: `data/Q&A_db_practice.json`).
- `LOG_PATH`: Path to evaluation log file (default: `data/evaluations_log.jsonl`).

**Setup Steps**

1. Duplicate the template: `cp .env.example .env` (or PowerShell: `copy .env.example .env`).
2. Edit `.env` and replace `REPLACE_ME` with your real OpenAI key.
3. (Optional) Override `MASTER_MODEL_NAME` or other settings in the same file.
4. Whenever you open a new shell:  
   - PowerShell: `Get-Content .env | foreach { if ($_ -match '=') { $name,$value = $_ -split '=',2; Set-Item -Path Env:$name -Value $value } }`  
   - macOS/Linux: `export $(grep -v '^#' .env | xargs)`

**Direct export (if you don’t want to use .env):**

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key"
$env:MASTER_MODEL_NAME="gpt-4o-mini"  # optional override
streamlit run app/streamlit_app.py

# Linux/macOS
export OPENAI_API_KEY="sk-your-key"
export MASTER_MODEL_NAME="gpt-4o-mini"
streamlit run app/streamlit_app.py
```

## 🤖 Model Choice and Rationale

### Default Model: gpt-4o-mini

**Why this model?**
- **Quality**: Solid reasoning and rubric-following for evaluation tasks.
- **Cost**: Lower per-token pricing than GPT-4 Turbo/Omni while retaining high accuracy.
- **Speed**: Optimized for latency, which keeps the Streamlit experience responsive.
- **Zero setup**: No local weights or GPUs required—only an API key.

### Other OpenAI Models
- `gpt-4o` – higher quality, higher cost.
- `gpt-4o-mini-transcribe` – useful if you want to expand into speech inputs.
- `o3-mini` – reasoning-focused but with higher latency.

Override the default by setting `MASTER_MODEL_NAME` before launching the app.

## 📊 Evaluation Strategy

### 1. LLM-based Evaluation

The master LLM is prompted to:
- Compare student answer to reference answer
- Identify correct points, missing concepts, and misconceptions
- Provide detailed explanation
- Assign a numerical score (0-100)

**Prompting Strategy:**
- Clear instructions with structured format
- Explicit scoring rubric (0-30: major errors, 31-50: partial, etc.)
- Language-aware (supports multiple languages)

### 2. Automatic Metrics (ROUGE)

- **ROUGE-1**: Unigram overlap (word-level matching)
- **ROUGE-L**: Longest common subsequence (sentence-level matching)

These provide objective, quantitative measures of lexical overlap.

### 3. Combined Approach

- **LLM**: Captures semantic correctness and understanding
- **ROUGE**: Provides objective lexical metrics
- **Together**: Comprehensive evaluation with both qualitative and quantitative aspects

## 🔄 Alternative Approaches

### 1. Pure Metric-based
- **Pros**: Fast, deterministic, no LLM needed
- **Cons**: Misses semantic understanding, can't identify misconceptions

### 2. Fine-tuned Evaluator
- **Pros**: Highly consistent, optimized for evaluation task
- **Cons**: Requires training data, more complex setup

### 3. RLHF (Reinforcement Learning from Human Feedback)
- **Pros**: Can improve over time with feedback
- **Cons**: Complex implementation, requires feedback loop

### 4. Judge LLM
- **Pros**: Specialized model for evaluation, potentially better quality
- **Cons**: Requires separate model, more resources

### 5. Multi-model Ensemble
- **Pros**: More robust, reduces bias
- **Cons**: Slower, more resource-intensive

## 🌐 Features

### Core Features
- ✅ Question selection from Q&A database
- ✅ Free-text answer input
- ✅ LLM-based evaluation with explanation
- ✅ Numerical scoring (0-100)
- ✅ ROUGE metrics (ROUGE-1, ROUGE-L)
- ✅ Reference answer display
- ✅ Evaluation logging (JSONL format)

### Optional Enhancements
- ✅ **Sentiment Analysis**: Analyzes user feedback sentiment
- ✅ **Multi-language Support**: Evaluation in multiple languages
- ✅ **Novice Answer Generation**: Auto-generate test answers
- ✅ **Feedback Collection**: Tags and free-text feedback
- ✅ **Interaction Logging**: All evaluations logged to JSONL

## 📓 Notebooks

### 01_explore_dataset.ipynb
- Loads and explores the Q&A database
- Shows basic statistics and sample entries
- Explains dataset structure

### 02_evaluation_prototyping.ipynb
- Tests evaluation with good/mediocre/bad answers
- Analyzes evaluation quality
- Discusses strengths and improvements

### 03_batch_simulation.ipynb
- Simulates multiple evaluations
- Analyzes correlations between LLM scores and ROUGE
- Generates summary statistics and visualizations

**To run notebooks:** See the [Working with the Notebooks](#working-with-the-notebooks) section above.

## 📊 Viewing Diagrams

The documentation files (`ARCHITECTURE.md` and `PROCESS_FLOWS.md`) contain **Mermaid diagrams** - a text-based diagram syntax that renders as visual flowcharts and architecture diagrams. Here are several ways to view them:

### Option 1: GitHub/GitLab (Easiest - Recommended)

If the files are uploaded to GitHub or GitLab, the diagrams will **automatically render** when viewing the `.md` files.

**Steps:**
1. Upload the project to GitHub/GitLab
2. Navigate to any `.md` file (e.g., `ARCHITECTURE.md`)
3. The diagrams will render automatically - no setup needed!

### Option 2: VS Code

VS Code has built-in Mermaid support with extensions.

**Steps:**
1. Install the **"Markdown Preview Mermaid Support"** extension
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Search: "Markdown Preview Mermaid Support"
   - Install by Matt Bierner
2. Open any `.md` file
3. Press `Ctrl+Shift+V` (or `Cmd+Shift+V` on Mac) to open preview
4. Diagrams will render automatically

**Alternative Extension**: "Mermaid Preview" by vstirbu

### Option 3: Online Mermaid Editor (No Installation)

Use the online Mermaid Live Editor - works in any browser.

**Steps:**
1. Go to: https://mermaid.live/ or https://mermaid-js.github.io/mermaid-live-editor/
2. Copy the Mermaid code from any diagram (between ```mermaid and ```)
3. Paste into the editor
4. Diagram renders instantly

**Example:**
- Open `ARCHITECTURE.md`
- Find a diagram block starting with ````mermaid`
- Copy everything between ```mermaid and ```
- Paste into https://mermaid.live/
- View the rendered diagram

### Option 4: Markdown Viewers with Mermaid Support

Several markdown viewers support Mermaid:

- **Typora** (Paid, but has free trial): https://typora.io/
- **Obsidian** (Free): https://obsidian.md/ (install "Mermaid" plugin)
- **Mark Text** (Free, Open Source): https://marktext.app/

### Option 5: Convert to Images (For Presentations)

If you need static images for presentations:

1. Go to https://mermaid.live/
2. Paste Mermaid code
3. Click "Download PNG" or "Download SVG"
4. Save as image file

### Quick Reference: Which Files Have Diagrams?

| File | Number of Diagrams | Types |
|------|-------------------|-------|
| `ARCHITECTURE.md` | 4 | System architecture, data flow, dependencies |
| `PROCESS_FLOWS.md` | 6+ | Flowcharts for all major processes |
| `DECISIONS.md` | 0 | Text-based (no diagrams) |
| `DEPLOYMENT.md` | 0 | Text-based (no diagrams) |
| `TEST_RESULTS.md` | 0 | Text-based (no diagrams) |

### Recommended Approach

**Best Option**: Upload to GitHub and share the repository link
- ✅ No installation needed
- ✅ Diagrams render automatically
- ✅ Easy to navigate
- ✅ Professional presentation

**Alternative**: Use Option 3 (Online Editor) to view individual diagrams quickly.

## 🧪 Testing

Run tests with pytest:

```bash
pytest tests/test_evaluator.py -v
```

Tests use mocking to avoid loading the actual LLM model, making them fast and reliable.

## 📝 Logging

All evaluations are logged to `data/evaluations_log.jsonl` in JSONL format. Each record contains:

- Timestamp
- Question ID and text
- Reference and student answers
- LLM score and explanation
- ROUGE metrics
- User feedback (tags, text, sentiment)

**Example log entry:**
```json
{
  "timestamp": "2024-01-15T14:30:45.123456",
  "question_id": 0,
  "question_text": "What is an activation function?",
  "reference_answer": "...",
  "student_answer": "...",
  "llm_score": 75,
  "rouge_1": 0.45,
  "rouge_l": 0.42,
  "llm_explanation": "...",
  "user_feedback_tags": ["useful", "clear"],
  "user_feedback_text": "Good evaluation!",
  "feedback_sentiment_label": "POSITIVE",
  "feedback_sentiment_score": 0.92
}
```

## 🐛 Troubleshooting

### OpenAI API Issues
- **401 Unauthorized**: Ensure `OPENAI_API_KEY` is set in the environment and has not expired.
- **429 Rate Limit**: Back off for a few seconds or reduce batch size in notebooks.
- **Service Unavailable**: Automatic retries are not built-in—rerun the evaluation or add retry logic around `generate_completion`.

### Dataset Issues
- **File not found**: The `Q&A_db_practice.json` file is included in the repository. If missing, ensure you've cloned/downloaded the complete repository.
- **Invalid JSON**: Validate JSON format
- **Empty dataset**: Ensure at least one question-answer pair exists

### Performance / Cost
- **Slow evaluation**: GPT-4o mini usually answers in ~1-2s; if slower, check network latency.
- **Unexpected spend**: Lower `MASTER_MAX_NEW_TOKENS` or switch to a cheaper model (e.g., `gpt-4o-mini` → `gpt-4o-mini-low`).

## 📚 Code Documentation

All modules include:
- **Docstrings**: Function and class documentation
- **Comments**: Explanatory comments for complex logic
- **Type hints**: Type annotations for clarity
- **Error handling**: Graceful error messages

## 🔒 Privacy and Security

- **API key management**: Store `OPENAI_API_KEY` in environment variables or `.env` files that stay out of version control.
- **Data handling**: Prompts and student answers are sent to OpenAI for grading; scrub PII before running evaluations if needed.
- **Logging**: Evaluation logs are stored locally in `data/evaluations_log.jsonl`. Remove sensitive entries before sharing.

## 📄 License

This project is part of an academic assignment. Use responsibly.

## 👤 Author

Part 2 of DAI Assignment - LLM Evaluator Chatbot

## 🙏 Acknowledgments

- OpenAI for GPT-4o mini access
- HuggingFace for the transformers library used in sentiment analysis
- Streamlit for the web framework

## ℹ️ Disclaimer

Portions of this README (including setup instructions and troubleshooting tips)
were generated with the assistance of AI tooling to ensure clarity and
completeness. All guidance has been reviewed and verified within this project.

---

**Ready to submit!** This project is self-contained, well-documented, and ready to zip and submit.

