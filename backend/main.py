from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from dotenv import load_dotenv

import os

# Load environment variables (like GEMINI_API_KEY) from .env file
load_dotenv()

from models.schemas import Project, RiskScore, AlertRequest, ChatQuery, IngestionPayload
from database.ingest import load_initial_data

app = FastAPI(
    title="AI-Powered Project Risk Management API",
    description="Backend API for managing IT project risks via multi-agent architecture.",
    version="1.0.0"
)

# Enable CORS for the Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("Starting API and ingesting initial mock data into ChromaDB...")
    load_initial_data()


@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Project Risk Management API is running."}

# We will populate these endpoints later after setting up ML and Agents

from agents.crew import create_risk_assessment_crew
from ml.model import risk_predictor
from chatbot.engine import chatbot_engine
from database.chroma_db import db

@app.post("/api/v1/risk/score", response_model=RiskScore)
async def get_risk_score(project: Project):
    """Calculate the risk score of a given project using the fast ML pipeline."""
    # We use the fast ML pipeline here for immediate dashboard feedback.
    # A background task could use the full CrewAI agent ensemble.
    score, category = risk_predictor.predict_risk(
        resource_utilization=project.resource_utilization,
        payment_delays_days=project.payment_delays_days,
        completed_tasks=project.completed_tasks,
        total_tasks=project.total_tasks,
        negative_sentiment=0.5 # Default unless analyzed by Agent
    )
    
    explanation = f"Calculated using ML model. Resource Utilization: {project.resource_utilization}. Payment Delay: {project.payment_delays_days} days."
    return RiskScore(score=score, category=category, explanation=explanation)

@app.post("/api/v1/chat", response_model=Dict[str, str])
async def chat_with_agent(query: ChatQuery):
    """Interact with the Conversational AI for risk querying."""
    response = chatbot_engine.generate_response(query.query, query.context)
    return {"reply": response}

@app.post("/api/v1/ingest", response_model=Dict[str, str])
async def ingest_new_data(payload: IngestionPayload):
    """Ingest new projects, logs, and news dynamically into the Vector Database."""
    # Process historical risks
    for r in payload.historical_risks:
        db.add_historical_risk(r.id, r.description, r.mitigation, {"severity": r.severity, "project_type": r.project_type})
        
    for n in payload.market_news:
        db.add_market_news(n.title, n.title, n.content, {"sentiment": n.sentiment})
        
    return {"status": "success", "message": f"Ingested data into Vector DB successfully."}

@app.post("/api/v1/agent/report")
async def generate_agent_report(project: Project):
    """Triggers the full CrewAI orchestration to generate a comprehensive report for ONE project."""
    try:
        crew = create_risk_assessment_crew(project.id, project.dict())
        result = crew.kickoff()
        # CrewAI 1.x returns a CrewOutput object. The markdown text is available in .raw
        report_text = result.raw if hasattr(result, 'raw') else str(result)
        # Remove tool call tags like <brunswick_market_research>...</brunswick_market_research>
        import re
        cleaned_report = re.sub(r'<[^>]+>', '', report_text)
        return {"status": "success", "message": "Report generated successfully.", "report": cleaned_report.strip()}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
