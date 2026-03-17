import streamlit as st
import pandas as pd
import requests
import json
import os

API_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Project Risk Manager AI", layout="wide", page_icon="🛡️")

def load_local_data():
    """Load the mock JSON as the source of truth for the dashboard."""
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_data.json')
    with open(data_path, 'r') as f:
        return json.load(f)

data = load_local_data()
projects = data.get("projects", [])

st.title("🛡️ AI-Powered Project Risk Management System")
st.markdown("Monitor internal project constraints and external market risks using Multi-Agent AI.")

# --- Dashboard Tab ---
tab1, tab2, tab3 = st.tabs(["📊 Portfolio Dashboard", "🤖 CrewAI Agent Reports", "💬 Ask Risk Chatbot"])

with tab1:
    st.header("Project Portfolio Health")
    
    metrics_cols = st.columns(len(projects))
    
    # Calculate fast real-time risk scores via API
    for i, proj in enumerate(projects):
        try:
            res = requests.post(f"{API_URL}/risk/score", json=proj).json()
            score = res.get("score", 0)
            category = res.get("category", "Unknown")
            
            color = "green" if category == "Low" else "orange" if category == "Medium" else "red"
            
            with metrics_cols[i]:
                st.markdown(f"### {proj['name']}")
                st.markdown(f"**Status:** {proj['status']}")
                st.markdown(f"**Risk Score:** <span style='color:{color}; font-size: 24px'>{score:.1f}/100</span> ({category})", unsafe_allow_html=True)
                st.progress(proj['completed_tasks'] / proj['total_tasks'], text="Task Completion")
                st.caption(f"Budget Spent: ${proj['spent']} / ${proj['budget']}")
                if int(proj['payment_delays_days']) > 0:
                    st.error(f"⚠️ Payment delayed by {proj['payment_delays_days']} days")
                    
        except Exception as e:
            with metrics_cols[i]:
                st.error(f"API Offline. Start FastAPI server. {e}")

with tab2:
    st.header("Generate Deep Agentic Risk Reports")
    st.info("Triggers the CrewAI Multi-Agent pipeline to perform deep analysis on a project using VectorDB context and Market Sentiment.")
    
    selected_proj_name = st.selectbox("Select Project for Deep Analysis", [p["name"] for p in projects])
    selected_proj = next(p for p in projects if p["name"] == selected_proj_name)
    
    if st.button("🚀 Run CrewAI Analysis"):
        with st.spinner("Agents are analyzing logs, market news, and historical precedents... (This takes 15-30 seconds)"):
            try:
                # Add a timeout to avoid hangs
                res = requests.post(f"{API_URL}/agent/report", json=selected_proj, timeout=60).json()
                if res.get("status") == "success":
                    st.success(res.get("message", "Analysis Complete!"))
                    st.markdown("### 📄 Comprehensive Risk Report")
                    st.markdown(res.get("report", "No report content returned."))
                else:
                    st.error(res.get("detail", "An error occurred during agent execution."))
            except requests.exceptions.Timeout:
                st.error("The agent analysis timed out. The CrewAI process took longer than 60 seconds.")
            except Exception as e:
                st.error(f"Failed to trigger agent report. Verify API is running. Error: {e}")

with tab3:
    st.header("Conversational Risk Assistant")
    st.markdown("Ask natural language questions about project risks, historical mitigations, and current status.")
    
    # Simple Chat UI
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("E.g., What are the mitigation strategies for database migration latency?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # Provide contexts of all projects to Chatbot
                context = json.dumps(projects)
                payload = {"query": prompt, "context": context}
                res = requests.post(f"{API_URL}/chat", json=payload).json()
                reply = res.get("reply", "No response.")
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                error_msg = f"Failed to connect to Chatbot API: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
