from crewai import Task, Crew, Process
from .definitions import (
    status_tracker, market_analyst, risk_scorer, reporting_agent, coordinator_agent
)

def create_risk_assessment_crew(project_id: str, project_details: dict) -> Crew:
    """
    Creates and wires a CrewAI crew specifically for evaluating the risk of a single project.
    """
    
    # Task 1: Analyze internal project logs
    description = project_details.get('description', 'No description provided.')
    employees = project_details.get('employees', 'Unknown')
    tech_stack = project_details.get('tech_stack', 'Not specified')
    status = project_details.get('status', 'Unknown')
    
    task_track_status = Task(
        description=(
            f"Analyze the internal health of the following IT project and produce a structured risk summary. "
            f"Do NOT call any tools — use ONLY the information provided below.\n\n"
            f"Project ID: {project_id}\n"
            f"Project Name: {project_details['name']}\n"
            f"Description: {description}\n"
            f"Tech Stack: {tech_stack}\n"
            f"Employees: {employees}\n"
            f"Status: {status}\n"
            f"Budget: ${project_details.get('budget', 0):,.0f} | Spent: ${project_details.get('spent', 0):,.0f}\n"
            f"Timeline: {project_details.get('days_elapsed', 0)} / {project_details.get('timeline_days', 0)} days elapsed\n"
            f"Tasks: {project_details.get('completed_tasks', 0)} / {project_details.get('total_tasks', 1)} completed\n"
            f"Resource Utilization: {project_details.get('resource_utilization', 1.0)} (>1.0 means overloaded)\n"
            f"Payment Delays: {project_details.get('payment_delays_days', 0)} days\n\n"
            f"Identify internal blockers, risks, resource constraints, budget issues, and schedule risks from these details."
        ),
        expected_output="A concise bullet-point summary of internal project health: key blockers, resource constraints, budget concerns, and schedule risks.",
        agent=status_tracker,
    )
    
    # Task 2: Analyze external market conditions
    market_context = project_details.get('market_context', 'General IT Market')
    task_market_analysis = Task(
        description=(
            f"You must follow these EXACT steps and NO others:\n"
            f"STEP 1: Call 'search_market_news' with query: '{market_context}'\n"
            f"STEP 2: Call 'analyze_sentiment' on the text returned from step 1\n"
            f"STEP 3: Write your final answer immediately. DO NOT call any more tools.\n\n"
            f"FORBIDDEN tools (never call these): brave_search, web_search, google_search, duckduckgo_search, or any tool not listed above.\n"
            f"You are analyzing an IT project using {tech_stack}. After exactly 2 tool calls, stop and finalize."
        ),
        expected_output="A negative sentiment score (0.0-1.0) and a 2-3 sentence summary of external market pressures.",
        agent=market_analyst,
    )
    
    # Task 3: Calculate ML Risk Score
    res_util = project_details.get('resource_utilization', 1.0)
    pay_delay = project_details.get('payment_delays_days', 0)
    comp_tasks = project_details.get('completed_tasks', 0)
    tot_tasks = project_details.get('total_tasks', 1)
    budget = project_details.get('budget', 0)
    spent = project_details.get('spent', 0)
    
    task_score_risk = Task(
        description=(
            f"Using the 'predict_risk_score' tool, calculate the risk score for the IT project '{project_details['name']}'. "
            f"Use: resource_utilization={res_util}, payment_delay={pay_delay}, completed_tasks={comp_tasks}, total_tasks={tot_tasks}. "
            f"Budget: ${budget:,.0f}, Spent: ${spent:,.0f}. "
            f"Team size: {employees} employees. "
            f"Use the negative sentiment found by the Market Analyst as the negative_sentiment parameter."
        ),
        expected_output="A JSON object containing the `score` (0-100) and `category` (Low/Medium/High).",
        agent=risk_scorer,
        context=[task_track_status, task_market_analysis]
    )
    
    # Task 4: Generate Report and Mitigations
    task_generate_report = Task(
        description=(
            f"Use only the 'search_historical_risks' tool to find historical precedents matching the issues found for project '{project_id}' ({project_details['name']}). "
            f"This is an IT project with tech stack: {tech_stack}, team size: {employees}. "
            f"Do NOT attempt to use any other tools. "
            f"Provide a final executive summary as a Markdown report including: risk score and category, key internal and external risk factors, "
            f"and specific actionable mitigation steps relevant to an IT organization. Include timeline recommendations."
        ),
        expected_output="A comprehensive Markdown report with risk score, category, internal/external factors, and prioritized action plan tailored for the IT organization.",
        agent=reporting_agent,
        context=[task_track_status, task_market_analysis, task_score_risk]
    )
    
    # Assembly
    crew = Crew(
        agents=[status_tracker, market_analyst, risk_scorer, reporting_agent, coordinator_agent],
        tasks=[task_track_status, task_market_analysis, task_score_risk, task_generate_report],
        process=Process.sequential,
        verbose=True,
        max_rpm=3 # Enforce slow rate limit for cumulative Free-tier LLMs
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
