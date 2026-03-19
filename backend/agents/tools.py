from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import json

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.chroma_db import db
from ml.model import nlp_processor, risk_predictor

class SemanticSearchInput(BaseModel):
    query: str = Field(..., description="The query to search the vector database for historical risks.")

class SemanticSearchTool(BaseTool):
    name: str = "search_historical_risks"
    description: str = "Searches the vector database for historical project risks and their mitigations."
    args_schema: Type[BaseModel] = SemanticSearchInput

    def _run(self, query: str) -> str:
        results = db.search_similar_risks(query)
        if not results['documents'][0]:
            return "No relevant historical risks found."
        text = json.dumps(results['documents'][0])
        return text[:400] + "..." if len(text) > 400 else text

class ProjectLogSearchInput(BaseModel):
    project_id: str = Field(..., description="The ID of the project to retrieve logs for.")

class ProjectLogSearchTool(BaseTool):
    name: str = "retrieve_project_logs"
    description: str = "Retrieves recent logs and context for a specific project from the database."
    args_schema: Type[BaseModel] = ProjectLogSearchInput

    def _run(self, project_id: str) -> str:
        results = db.get_project_context(project_id)
        if not results['documents']:
            return f"No logs found for project {project_id}."
        text = "\n".join(results['documents'])
        return text[:400] + "..." if len(text) > 400 else text

class MarketNewsSearchInput(BaseModel):
    query: str = Field(..., description="The market topic or project context to search news for.")

class MarketNewsSearchTool(BaseTool):
    name: str = "search_market_news"
    description: str = "Retrieves recent market news from the vector database based on context."
    args_schema: Type[BaseModel] = MarketNewsSearchInput

    def _run(self, query: str) -> str:
        results = db.search_market_news(query)
        if not results['documents'][0]:
            return "No relevant market news found."
        text = json.dumps(results['documents'][0])
        return text[:400] + "..." if len(text) > 400 else text

class SentimentAnalysisInput(BaseModel):
    text: str = Field(..., description="The text to analyze for sentiment.")

class SentimentAnalysisTool(BaseTool):
    name: str = "analyze_sentiment"
    description: str = "Analyzes the text and returns a negative sentiment score between 0 and 1."
    args_schema: Type[BaseModel] = SentimentAnalysisInput

    def _run(self, text: str) -> str:
        score = nlp_processor.analyze_sentiment([text])
        return f"Negative Sentiment Score: {score:.2f} (0 is completely positive, 1 is completely negative)"

class RiskPredictionInput(BaseModel):
    resource_utilization: float = Field(..., description="Resource utilization ratio (e.g., 0.95).")
    payment_delays_days: int = Field(..., description="Days payment is delayed.")
    completed_tasks: int = Field(..., description="Number of tasks completed.")
    total_tasks: int = Field(..., description="Total tasks in project.")
    negative_sentiment: float = Field(..., description="Negative sentiment score of market/logs (0-1).")

class RiskPredictionTool(BaseTool):
    name: str = "predict_risk_score"
    description: str = "Uses an ML model to predict a risk score (0-100) based on project metrics."
    args_schema: Type[BaseModel] = RiskPredictionInput

    def _run(self, resource_utilization: float, payment_delays_days: int, completed_tasks: int, total_tasks: int, negative_sentiment: float) -> str:
        score, category = risk_predictor.predict_risk(
            resource_utilization, payment_delays_days, completed_tasks, total_tasks, negative_sentiment
        )
        return json.dumps({"score": score, "category": category})
