from crewai import Task, Crew, Process
from .definitions import (
    status_tracker, market_analyst, risk_scorer, reporting_agent, coordinator_agent
)

def create_risk_assessment_crew(project_id: str, project_details: dict) -> Crew:
    """
    Creates and wires a CrewAI crew specifically for evaluating the risk of a single project.
    """
    
    # Task 1: Analyze internal project logs
    task_track_status = Task(
        description=f"Analyze the internal logs for project '{project_id}' ({project_details['name']}) to identify internal blockers, delays, and resource constraints.",
        expected_output="A summary of internal project health, noting any major blockers or resource issues.",
        agent=status_tracker,
    )
    
    # Task 2: Analyze external market conditions
    market_context = project_details.get('market_context', 'General Tech Market')
    task_market_analysis = Task(
        description=f"Use the 'Search Market News' tool with query '{market_context}' to find relevant market news. Then use the 'Analyze Sentiment' tool on the results to compute a negative sentiment score. Do NOT use any tool other than 'Search Market News' and 'Analyze Sentiment'.",
        expected_output="A negative sentiment score and a summary of external market pressures.",
        agent=market_analyst,
    )
    
    # Task 3: Calculate ML Risk Score
    res_util = project_details.get('resource_utilization', 1.0)
    pay_delay = project_details.get('payment_delays_days', 0)
    comp_tasks = project_details.get('completed_tasks', 0)
    tot_tasks = project_details.get('total_tasks', 1)
    
    task_score_risk = Task(
        description=f"Using the ML Prediction tool, calculate the risk score using resource_utilization={res_util}, payment_delay={pay_delay}, completed_tasks={comp_tasks}, total_tasks={tot_tasks}. Use the negative sentiment found by the Market Analyst.",
        expected_output="A JSON object containing the `score` (0-100) and `category` (Low/Medium/High).",
        agent=risk_scorer,
        context=[task_track_status, task_market_analysis] # Depends on previous tasks
    )
    
    # Task 4: Generate Report and Mitigations
    task_generate_report = Task(
        description=f"Search historical risks that match the issues found in project '{project_id}'. Provide a final executive summary including the computed risk score, category, the internal and external factors, and suggested mitigations based on history.",
        expected_output="A comprehensive Markdown report detailing the risk profile and action plan for the project.",
        agent=reporting_agent,
        context=[task_track_status, task_market_analysis, task_score_risk]
    )
    
    # Assembly
    crew = Crew(
        agents=[status_tracker, market_analyst, risk_scorer, reporting_agent, coordinator_agent],
        tasks=[task_track_status, task_market_analysis, task_score_risk, task_generate_report],
        process=Process.sequential,
        verbose=True,
        max_rpm=15 # Enforce rate limit for Free-tier LLMs
    )
    
    return crew

def run_portfolio_risk_assessment(projects: list) -> dict:
    """Runs the agent crew on multiple projects and returns reports."""
    results = {}
    for proj in projects:
        crew = create_risk_assessment_crew(proj.id, proj.dict())
        result = crew.kickoff()
        results[proj.id] = result
        
    return results
