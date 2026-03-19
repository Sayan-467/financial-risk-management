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
        max_retries=5,
        max_tokens=600,
    )

llm_chatbot = get_langchain_llm()

# CrewAI 1.x requires native LLM objects to pass custom keys robustly
crewai_llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.environ.get("GROQ_API_KEY"),
    max_retries=5,
    max_tokens=1024,
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
    goal="Analyze project details provided in the task description to identify delays, blockers, or resource shortages.",
    backstory="You are an internal auditor examining project metrics and context to find subtle signs of project failure. Analyze the information given to you directly in the task — you do NOT need to call any tools. Simply produce a structured risk summary from the provided project details.",
    tools=[],
    llm=crewai_llm,
    verbose=True
)

# Agent 2: Market Analysis Agent
market_analyst = Agent(
    role="Market Analysis Agent",
    goal="Use exactly two tools in sequence: first 'search_market_news', then 'analyze_sentiment'. Then immediately write your final answer. Do not call any other tools.",
    backstory=(
        "You are a financial analyst. You have access to EXACTLY two tools: 'search_market_news' and 'analyze_sentiment'. "
        "Your workflow is strict: Step 1 — call 'search_market_news' once. Step 2 — call 'analyze_sentiment' once on the results. Step 3 — write your final answer immediately. "
        "You MUST STOP after step 3. You are STRICTLY FORBIDDEN from calling ANY other tool including 'brave_search', 'web_search', 'google_search', 'duckduckgo_search', or any tool not explicitly listed above. "
        "If you feel the urge to do more research, resist it and write your final answer with what you have."
    ),
    tools=[market_news_search, sentiment_analysis],
    llm=crewai_llm,
    verbose=True
)

# Agent 3: Risk Scoring Agent
risk_scorer = Agent(
    role="Risk Scoring Agent",
    goal="Combine internal constraints and external sentiment to output a final Risk Score and Category.",
    backstory="You are a data-driven risk assessor. You MUST ONLY use the 'predict_risk_score' tool. Do NOT attempt to use any other tools.",
    tools=[risk_prediction],
    llm=crewai_llm,
    verbose=True
)

# Agent 4: Reporting Agent
reporting_agent = Agent(
    role="Reporting Agent",
    goal="Generate actionable mitigation insights and summarize the risks using historical precedents.",
    backstory="You are a senior PMO analyst. You MUST ONLY use the 'search_historical_risks' tool to find historical precedents. Do NOT attempt to use any other tools.",
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
