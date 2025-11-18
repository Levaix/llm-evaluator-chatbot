# Decision Log

This document records the key architectural, design, and implementation decisions made during the development of the LLM Evaluator Chatbot, along with the rationale and trade-offs considered.

## Table of Contents
1. [Model Selection](#model-selection)
2. [Evaluation Strategy](#evaluation-strategy)
3. [Prompt Design](#prompt-design)
4. [Technology Stack](#technology-stack)
5. [Architecture Decisions](#architecture-decisions)
6. [Data Storage](#data-storage)
7. [User Interface](#user-interface)
8. [Error Handling](#error-handling)

---

## Model Selection

### Decision: Use GPT-4o-mini as the Master Evaluation Model

**Date**: Initial implementation  
**Status**: Accepted  
**Context**: Need for a cost-effective, high-quality LLM for answer evaluation.

**Decision**:
- Primary model: `gpt-4o-mini` (OpenAI)
- Temperature: 0.2 (low for consistency)
- Max tokens: 512 (configurable)

**Rationale**:
1. **Cost Efficiency**: Significantly cheaper than GPT-4 Turbo/Omni while maintaining quality
2. **Performance**: Fast response times (~1-2s) suitable for interactive use
3. **Quality**: Strong reasoning and rubric-following capabilities
4. **Zero Setup**: No local infrastructure needed, only API key
5. **Reliability**: Stable API with good uptime

**Alternatives Considered**:
- **GPT-4o**: Higher quality but 3-5x more expensive
- **GPT-3.5-turbo**: Cheaper but lower quality for evaluation tasks
- **Local Models (Llama, Mistral)**: No API costs but requires GPU infrastructure
- **o3-mini**: Better reasoning but higher latency and cost

**Trade-offs**:
- ✅ Low cost, fast, good quality
- ❌ Dependent on external API
- ❌ Potential rate limits at scale

**Future Considerations**:
- Support for multiple models (fallback options)
- Model comparison capabilities
- Fine-tuned evaluator model for better consistency

---

## Evaluation Strategy

### Decision: Hybrid LLM + ROUGE Approach

**Date**: Initial design  
**Status**: Accepted  
**Context**: Need comprehensive evaluation combining semantic understanding and objective metrics.

**Decision**:
- Combine LLM-based evaluation (semantic) with ROUGE metrics (lexical)
- LLM provides explanation and score (0-100)
- ROUGE provides ROUGE-1 and ROUGE-L scores

**Rationale**:
1. **Semantic Understanding**: LLM captures meaning, not just word matching
2. **Objective Metrics**: ROUGE provides quantitative lexical overlap
3. **Comprehensive**: Both qualitative and quantitative assessment
4. **Explainability**: LLM provides detailed feedback for learning
5. **Flexibility**: Can handle various answer styles and phrasings

**Alternatives Considered**:
1. **Pure Metric-based (ROUGE only)**
   - ✅ Fast, deterministic, no API costs
   - ❌ Misses semantic understanding, can't identify misconceptions
   - **Rejected**: Insufficient for educational evaluation

2. **LLM-only**
   - ✅ Best semantic understanding
   - ❌ No objective metrics, higher cost
   - **Rejected**: Missing quantitative component

3. **Fine-tuned Evaluator**
   - ✅ Highly consistent, optimized for task
   - ❌ Requires training data, complex setup
   - **Future Consideration**: Could improve consistency

4. **Multi-model Ensemble**
   - ✅ More robust, reduces bias
   - ❌ Slower, more resource-intensive
   - **Future Consideration**: For production deployment

**Trade-offs**:
- ✅ Comprehensive evaluation
- ✅ Educational value (explanations)
- ❌ Higher computational cost than pure metrics
- ❌ LLM scores may vary slightly between runs

---

## Prompt Design

### Decision: Structured Multi-Step Evaluation Prompt

**Date**: Recent enhancement  
**Status**: Accepted  
**Context**: Need for consistent, high-quality evaluations with clear reasoning.

**Decision**:
- 6-step structured evaluation process
- Explicit scoring rubric with detailed ranges
- Semantic equivalence evaluation
- Chain-of-thought reasoning structure

**Rationale**:
1. **Consistency**: Structured approach reduces variability
2. **Fairness**: Semantic equivalence prevents penalizing valid phrasings
3. **Transparency**: Step-by-step reasoning is auditable
4. **Quality**: Detailed rubric leads to more accurate scoring
5. **Educational Value**: Better feedback for students

**Prompt Structure**:
1. Content Analysis
2. Correctness Assessment
3. Semantic Equivalence Evaluation
4. Completeness Assessment
5. Scoring Rubric Application
6. Constructive Explanation

**Alternatives Considered**:
1. **Simple Prompt**: "Evaluate this answer and give a score"
   - ❌ Too vague, inconsistent results
   - **Rejected**: Insufficient guidance

2. **Few-shot Prompting**: Include examples
   - ✅ Can improve consistency
   - ❌ Increases token usage and cost
   - **Future Consideration**: For specific use cases

3. **Structured Output (JSON)**: Request JSON format
   - ✅ Easier parsing, more reliable
   - ❌ Some models struggle with strict JSON
   - **Future Consideration**: With newer models

**Trade-offs**:
- ✅ More sophisticated and consistent
- ✅ Better educational value
- ❌ Longer prompts (higher token cost)
- ❌ More complex parsing required

---

## Technology Stack

### Decision: Python + Streamlit + OpenAI

**Date**: Initial design  
**Status**: Accepted  
**Context**: Need for rapid development with good user experience.

**Decision**:
- **Language**: Python 3.8+
- **Web Framework**: Streamlit
- **LLM Provider**: OpenAI API
- **Data Processing**: pandas
- **Metrics**: HuggingFace evaluate library

**Rationale**:
1. **Rapid Development**: Streamlit enables fast UI development
2. **Python Ecosystem**: Rich libraries for ML/NLP tasks
3. **Accessibility**: Easy to run locally, no complex setup
4. **Integration**: Seamless OpenAI API integration
5. **Community**: Strong support and documentation

**Alternatives Considered**:
1. **Flask/FastAPI + React**
   - ✅ More flexible, better for production
   - ❌ More complex, longer development time
   - **Rejected**: Overkill for assignment scope

2. **Django**
   - ✅ Full-featured framework
   - ❌ Heavier, more complex than needed
   - **Rejected**: Unnecessary complexity

3. **Jupyter Notebooks Only**
   - ✅ Great for prototyping
   - ❌ Poor user experience, not interactive
   - **Rejected**: Need proper web interface

**Trade-offs**:
- ✅ Fast development, easy to use
- ✅ Good for prototyping and demos
- ❌ Streamlit has limitations for complex UIs
- ❌ Not optimized for high-traffic production

---

## Architecture Decisions

### Decision: Modular Monolithic Architecture

**Date**: Initial design  
**Status**: Accepted  
**Context**: Balance between simplicity and maintainability.

**Decision**:
- Single application with clear module boundaries
- Separation of concerns (data, evaluation, UI, config)
- No microservices or distributed components

**Rationale**:
1. **Simplicity**: Easier to understand and maintain
2. **Development Speed**: Faster iteration
3. **Deployment**: Single application to deploy
4. **Testing**: Easier to test integrated system
5. **Suitable Scale**: Appropriate for assignment scope

**Alternatives Considered**:
1. **Microservices Architecture**
   - ✅ Better scalability, independent deployment
   - ❌ More complex, overkill for current needs
   - **Future Consideration**: If scaling to production

2. **Serverless (AWS Lambda, etc.)**
   - ✅ Cost-effective, auto-scaling
   - ❌ Cold starts, vendor lock-in
   - **Future Consideration**: For production deployment

**Trade-offs**:
- ✅ Simple, maintainable
- ✅ Fast development
- ❌ Less scalable than microservices
- ❌ Single point of failure

---

## Data Storage

### Decision: File-based Storage (JSON/JSONL)

**Date**: Initial design  
**Status**: Accepted  
**Context**: Need for simple, portable data storage.

**Decision**:
- Q&A Database: JSON file
- Evaluation Logs: JSONL (JSON Lines) file
- No database system

**Rationale**:
1. **Simplicity**: No database setup required
2. **Portability**: Easy to share and backup
3. **Human-readable**: Easy to inspect and debug
4. **Version Control**: Can track changes in git
5. **Sufficient**: Meets current data volume needs

**Alternatives Considered**:
1. **SQLite Database**
   - ✅ Better querying, ACID properties
   - ❌ Additional dependency, more complex
   - **Future Consideration**: If querying needs grow

2. **PostgreSQL/MySQL**
   - ✅ Production-ready, scalable
   - ❌ Requires database server, overkill
   - **Rejected**: Unnecessary for current scope

3. **NoSQL (MongoDB)**
   - ✅ Flexible schema
   - ❌ Additional infrastructure
   - **Rejected**: Not needed for structured data

**Trade-offs**:
- ✅ Simple, no dependencies
- ✅ Easy to work with
- ❌ Limited querying capabilities
- ❌ Not suitable for high-volume production

---

## User Interface

### Decision: Streamlit with Sidebar Configuration

**Date**: Initial design  
**Status**: Accepted  
**Context**: Need for intuitive, responsive web interface.

**Decision**:
- Single-page application
- Sidebar for configuration and navigation
- Main area for questions and results
- Real-time feedback and updates

**Rationale**:
1. **User Experience**: Clean, intuitive interface
2. **Responsiveness**: Real-time updates
3. **Accessibility**: Easy to use without training
4. **Development Speed**: Streamlit enables rapid UI development
5. **Mobile-friendly**: Responsive design

**UI Features**:
- Question display with reference answer toggle
- Text area for student answers
- Evaluation results with visualizations
- Feedback collection
- Language selection
- Configuration display

**Alternatives Considered**:
1. **Multi-page Application**
   - ✅ Better organization for complex features
   - ❌ More navigation, current scope doesn't need it
   - **Future Consideration**: If features expand

2. **Custom HTML/CSS/JS**
   - ✅ Full control, better performance
   - ❌ Much longer development time
   - **Rejected**: Not worth the effort for assignment

**Trade-offs**:
- ✅ Fast development, good UX
- ✅ Easy to modify
- ❌ Limited customization options
- ❌ Performance limitations for complex interactions

---

## Error Handling

### Decision: Graceful Degradation with User Feedback

**Date**: Initial design  
**Status**: Accepted  
**Context**: Need for robust error handling without breaking user experience.

**Decision**:
- Multiple levels of error handling
- User-friendly error messages
- Fallback values for critical operations
- Comprehensive logging for debugging

**Strategies**:
1. **Input Validation**: Validate at multiple layers
2. **Default Values**: Fallback scores (50) if parsing fails
3. **Error Messages**: Clear, actionable feedback
4. **Logging**: Detailed error logs for debugging
5. **Graceful Degradation**: Continue operation when possible

**Rationale**:
1. **User Experience**: Don't break the flow
2. **Debugging**: Comprehensive logs help identify issues
3. **Reliability**: System continues operating despite errors
4. **Transparency**: Users understand what went wrong

**Examples**:
- Score parsing failure → Default to 50 with warning
- API failure → Show error message, allow retry
- Dataset loading failure → Clear error with file path
- ROUGE computation failure → Use 0.0, log warning

**Alternatives Considered**:
1. **Fail Fast**: Stop on any error
   - ✅ Clear failure points
   - ❌ Poor user experience
   - **Rejected**: Too disruptive

2. **Silent Failures**: Hide errors
   - ✅ No user confusion
   - ❌ Hard to debug, unreliable
   - **Rejected**: Unacceptable for evaluation system

**Trade-offs**:
- ✅ Good user experience
- ✅ Robust operation
- ❌ May hide some issues
- ❌ Requires careful fallback design

---

## Additional Decisions

### Sentiment Analysis Model

**Decision**: Use DistilBERT-based sentiment model  
**Rationale**: Fast, accurate, runs locally (no API costs)  
**Trade-off**: Local model loading vs. API service

### Configuration Management

**Decision**: Environment variables with `.env` support  
**Rationale**: Secure, flexible, standard practice  
**Trade-off**: Requires setup vs. hardcoded values

### Logging Format

**Decision**: JSONL (JSON Lines) for evaluation logs  
**Rationale**: Easy to parse, append-only, human-readable  
**Trade-off**: Simple file format vs. structured database

### Testing Strategy

**Decision**: Unit tests with mocking  
**Rationale**: Fast, reliable, no API costs  
**Trade-off**: Mocked tests vs. integration tests

---

## Decision Review Process

This decision log should be reviewed and updated when:
- Major architectural changes are made
- New technologies are adopted
- Significant trade-offs are reconsidered
- Performance or cost issues arise
- User feedback indicates problems

## Future Decision Points

1. **Production Deployment**: Choose hosting platform and architecture
2. **Database Migration**: When to move from files to database
3. **Model Upgrades**: When to adopt newer LLM models
4. **Caching Strategy**: If and how to implement caching
5. **Authentication**: User management and security
6. **API Development**: REST API for programmatic access


