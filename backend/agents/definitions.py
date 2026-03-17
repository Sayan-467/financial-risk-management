import os
from crewai import Agent, LLM
from langchain_groq import ChatGroq

from .tools import (
    SemanticSearchTool,
    ProjectLogSearchTool,
    MarketNewsSearchTool,
    SentimentAnalysisTool,
    RiskPredictionTool
)

def get_langchain_llm():
    """Return a Groq LangChain LLM instance for the Chatbot."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. Please add it to your .env file."
        )
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=api_key,
        temperature=0.2,
    )

llm_chatbot = get_langchain_llm()

# CrewAI 1.x requires native LLM objects to pass custom keys robustly
crewai_llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.environ.get("GROQ_API_KEY")
)

# Initialize Tools
semantic_search = SemanticSearchTool()
project_log_search = ProjectLogSearchTool()
market_news_search = MarketNewsSearchTool()
sentiment_analysis = SentimentAnalysisTool()
risk_prediction = RiskPredictionTool()

# Agent 1: Project Status Tracking Agent
status_tracker = Agent(
    role="Project Status Tracking Agent",
    goal="Monitor internal project logs and context to identify delays, blockers, or resource shortages.",
    backstory="You are an internal auditor examining project logs to find subtle signs of project failure.",
    tools=[project_log_search],
    llm=crewai_llm,
    verbose=True
)

# Agent 2: Market Analysis Agent
market_analyst = Agent(
    role="Market Analysis Agent",
    goal="Analyze external market news and calculate negative sentiment to identify macroeconomic risks affecting the project.",
    backstory="You are a seasoned financial analyst. You read market news and calculate sentiment to assess external impacts on IT projects.",
    tools=[market_news_search, sentiment_analysis],
    llm=crewai_llm,
    verbose=True
)

# Agent 3: Risk Scoring Agent
risk_scorer = Agent(
    role="Risk Scoring Agent",
    goal="Combine internal constraints and external sentiment to output a final Risk Score and Category.",
    backstory="You are a data-driven risk assessor. You use machine learning models to synthesize multiple inputs into a single risk score.",
    tools=[risk_prediction],
    llm=crewai_llm,
    verbose=True
)

# Agent 4: Reporting Agent
reporting_agent = Agent(
    role="Reporting Agent",
    goal="Generate actionable mitigation insights and summarize the risks using historical precedents.",
    backstory="You are a senior PMO analyst. You correlate current risks with historical data to suggest actionable mitigations.",
    tools=[semantic_search],
    llm=crewai_llm,
    verbose=True
)

# Agent 5: Project Risk Manager (Coordinator)
coordinator_agent = Agent(
    role="Project Risk Manager",
    goal="Coordinate the efforts of tracking, analysis, scoring, and reporting to produce a comprehensive Risk Profile.",
    backstory="You are the lead Risk Executive orchestrating a team of specialist agents to secure project delivery.",
    tools=[], # The coordinator primarily delegates and synthesizes
    llm=crewai_llm,
    verbose=True,
    allow_delegation=True
)
