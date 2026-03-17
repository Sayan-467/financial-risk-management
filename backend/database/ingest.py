import json
import os
from .chroma_db import db

# Path to mock data
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sample_data.json')

def load_initial_data():
    """Load mock data from JSON and put into vector DB for initial setup"""
    
    if not os.path.exists(DATA_FILE):
        print(f"File {DATA_FILE} not found. Skipping initial data ingestion.")
        return

    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            
        print("Ingesting historical risks...")
        for risk in data.get("historical_risks", []):
            db.add_historical_risk(
                risk_id=risk["id"],
                description=risk["description"],
                mitigation=risk["mitigation"],
                metadata={"severity": risk["severity"], "project_type": risk["project_type"]}
            )

        print("Ingesting market news...")
        for i, news in enumerate(data.get("market_news", [])):
            db.add_market_news(
                news_id=f"news_{i}",
                title=news["title"],
                content=news["content"],
                metadata={"sentiment": news.get("sentiment", "Neutral")}
            )
            
        print("Ingesting initial project logs...")
        for project in data.get("projects", []):
            proj_id = project["id"]
            for j, log in enumerate(project.get("recent_logs", [])):
                db.add_project_logs(
                    log_id=f"log_{proj_id}_{j}",
                    project_id=proj_id,
                    log_text=log
                )
                
        print("Initial data ingestion complete.")
            
    except Exception as e:
        print(f"Error reading {DATA_FILE}: {str(e)}")

if __name__ == "__main__":
    load_initial_data()
