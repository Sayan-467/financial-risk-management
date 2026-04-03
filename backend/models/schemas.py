from pydantic import BaseModel
from typing import Optional, List

class Project(BaseModel):
    id: str
    name: str
    status: str
    budget: float
    spent: float
    timeline_days: int
    days_elapsed: int
    completed_tasks: int
    total_tasks: int
    resource_utilization: float
    payment_delays_days: int
    recent_logs: Optional[List[str]] = None
    market_context: Optional[str] = None
    description: Optional[str] = None
    employees: Optional[int] = None
    tech_stack: Optional[str] = None

class RiskScore(BaseModel):
    score: float
    category: str
    explanation: Optional[str] = None

class AlertRequest(BaseModel):
    project_id: int
    message: str
    severity: str

class ChatQuery(BaseModel):
    query: str
    context: Optional[str] = None

class HistoricalRisk(BaseModel):
    id: str
    project_type: str
    description: str
    mitigation: str
    severity: str

class MarketNews(BaseModel):
    title: str
    content: str
    sentiment: str

class IngestionPayload(BaseModel):
    historical_risks: List[HistoricalRisk]
    market_news: List[MarketNews]
    projects: List[Project]
