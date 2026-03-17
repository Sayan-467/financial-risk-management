# AI-Powered Project Risk Management System

A complete end-to-end production-ready system that continuously identifies, assesses, and mitigates risks in IT projects using internal project logs and external market analysis via a Multi-Agent architecture (CrewAI).

## Features
- **FastAPI Backend**: REST API for data ingestion, risk scoring, and chatbot interactions.
- **Streamlit Frontend**: Dashboard visualizing project health, risks, and alerts.
- **CrewAI Orchestration**: 5 specialized agents working together.
- **ChromaDB**: Semantic search for historical risk mapping.
- **Local AI/ML**: Local scikit-learn models for predicting risk scores, and HuggingFace pipelines for NLP sentiment analysis.

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
