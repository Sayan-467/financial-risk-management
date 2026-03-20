# AI-Powered Project Risk Management System

A complete end-to-end production-ready system that continuously identifies, assesses, and mitigates risks in IT projects using internal project logs and external market analysis via a Multi-Agent architecture (CrewAI).

## Features
- **FastAPI Backend**: REST API for data ingestion, risk scoring, and chatbot interactions.
- **Streamlit Frontend**: Dashboard visualizing project health, risks, and alerts.
- **CrewAI Orchestration**: 5 specialized agents working together.
- **ChromaDB**: Semantic search for historical risk mapping.
- **Local AI/ML**: Local scikit-learn models for predicting risk scores, and HuggingFace pipelines for NLP sentiment analysis.

## System Architecture

The AI-Powered Project Risk Management system employs a modular, microservice-like structure:

1. **Frontend (Streamlit)**
   - **Portfolio Dashboard**: High-level view of all projects with real-time ML-predicted risk scores and an interactive budget-vs-spent chart.
   - **Agent Reports**: Allows users to input project metrics. The ML pipeline categorizes the risk automatically, and the CrewAI agent orchestrates a full risk mitigation report.
   - **Risk Assistant**: A conversational interface enabling users to query historical risks and project data.
2. **Backend (FastAPI)**
   - Serves as the central API gateway managing risk calculations, ML inferences, and data processing.
   - Houses the Pydantic models/schemas enforcing strict data validation.
3. **AI & ML Layer**
   - **CrewAI**: Orchestrates multi-agent workflows (Risk Analyst, Technical Auditor, Financial Advisor, etc.) to perform deep-dive risk analysis on selected projects.
   - **Machine Learning**: Uses a local model to predict instant project status ("On Track", "In Progress", "At Risk") and calculates real-time risk scores (0-100).
4. **Data Layer (ChromaDB & JSON)**
   - Uses ChromaDB to provide semantic search over historical project risks and market context.
   - Persists real-time project metrics dynamically into a local datastore (`sample_data.json`).

## Folder Structure
```
ai-project-risk-manager/
├── backend/
│   ├── main.py (FastAPI application)
│   ├── models/ (Pydantic schemas)
│   ├── database/ (ChromaDB logic)
│   ├── ml/ (Scikit-learn model and HuggingFace NLP pipeline)
│   ├── agents/ (CrewAI definitions and tools)
│   └── chatbot/ (LLM chatbot logic)
├── frontend/
│   ├── app.py (Main Streamlit app)
│   └── components/ (UI submodules)
├── data/
│   └── sample_data.json (Mock data dataset)
├── requirements.txt
└── README.md
```

## Deployment Guide

### Local Setup
1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables (create a `.env` file):
   ```
   OPENAI_API_KEY="" # Optional if using local HuggingFace/Scikit-learn
   # Any other API keys for actual financial news APIs
   ```

4. Run the Backend API:
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

5. Run the Frontend Dashboard (in a new terminal):
   ```bash
   cd frontend
   streamlit run app.py
   ```

### Docker (Recommended for Production)
*A Dockerfile would typically be placed here.*
1. Build the image: `docker build -t ai-risk-manager .`
2. Run the container: `docker run -p 8000:8000 -p 8501:8501 ai-risk-manager`

### Cloud Deployment
- **AWS**: Deploy the FastAPI backend on AWS App Runner or ECS. Deploy the Streamlit app on EC2 or Streamlit Community Cloud. Use managed PostgreSQL/Pinecone if migrating from local ChromaDB.
- **GCP**: Use Google Cloud Run for both FastAPI and Streamlit containers.

## Recent Updates
- **Automated Risk Categorization**: The manual "Project Status" dropdown was removed. The application now relies entirely on the built-in Machine Learning prediction module to intelligently classify incoming projects.
- **Real-Time Dashboard Integration**: The Agent Reports are fully hooked into the rest of the application. Projects run through the AI analysis now instantly reflect on the `Portfolio Dashboard` graph. Furthermore, generated markdown reports are pinned and visible directly inside the dashboard's "Project Details" expander.
- **Frontend UI Polish**: Corrected CSS regressions (like dark mode styling bugs causing invisible text) and improved contrast ratios in the custom navigation menus and dropdowns.
- **Missing Module Bugfixes**: Safely initialized `models/schemas.py` in the backend so Pydantic classes load perfectly via uvicorn.
