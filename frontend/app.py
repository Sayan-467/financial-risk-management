import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import json
import os

API_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Project Risk Manager AI", layout="wide", page_icon="🛡️")

# Inject Custom CSS
css_path = os.path.join(os.path.dirname(__file__), 'style.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Inject Subtle Crosshair Cursor
import streamlit.components.v1 as components
components.html(
    """
    <script>
        const parentDoc = window.parent.document;
        let cursor = parentDoc.getElementById('glow-cursor');
        // Remove old cursor elements from previous themes
        if (cursor) cursor.remove();
        let trail = parentDoc.getElementById('cursor-trail');
        if (trail) trail.remove();

        if (!parentDoc.getElementById('cross-cursor')) {
            const style = parentDoc.createElement('style');
            style.innerHTML = `
                .cross-cursor {
                    position: fixed;
                    top: 0; left: 0;
                    width: 24px; height: 24px;
                    pointer-events: none;
                    z-index: 9999999;
                    transform: translate(-50%, -50%);
                    opacity: 0.7;
                    transition: opacity 0.2s;
                }
                .cross-cursor::before, .cross-cursor::after {
                    content: '';
                    position: absolute;
                    background: #1e293b;
                }
                .cross-cursor::before {
                    top: 0; left: 50%;
                    width: 1.5px; height: 100%;
                    transform: translateX(-50%);
                }
                .cross-cursor::after {
                    top: 50%; left: 0;
                    width: 100%; height: 1.5px;
                    transform: translateY(-50%);
                }
                * { cursor: none !important; }
            `;
            parentDoc.head.appendChild(style);

            const cur = parentDoc.createElement('div');
            cur.id = 'cross-cursor';
            cur.className = 'cross-cursor';
            parentDoc.body.appendChild(cur);

            parentDoc.addEventListener('mousemove', e => {
                window.requestAnimationFrame(() => {
                    cur.style.left = e.clientX + 'px';
                    cur.style.top = e.clientY + 'px';
                });
            });
        }
    </script>
    """,
    height=0,
    width=0
)

def load_local_data():
    """Load the mock JSON as the source of truth for the dashboard."""
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_data.json')
    with open(data_path, 'r') as f:
        return json.load(f)

def save_local_data(new_data):
    """Save updated data back to the JSON file."""
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_data.json')
    with open(data_path, 'w') as f:
        json.dump(new_data, f, indent=2)

data = load_local_data()
projects = data.get("projects", [])

# --- Branded Header ---
import base64

banner_path = os.path.join(os.path.dirname(__file__), 'assets', 'hero_banner.png')
if os.path.exists(banner_path):
    with open(banner_path, 'rb') as img_file:
        banner_b64 = base64.b64encode(img_file.read()).decode()
    st.markdown(f"""
    <div style="text-align:center; margin-bottom: 8px;">
        <img src="data:image/png;base64,{banner_b64}" style="width:100%; max-height:180px; object-fit:cover; border-radius: 12px; opacity:0.85;" />
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; margin-bottom: 24px;">
    <h1 style="font-family: 'Playfair Display', serif; font-size: 2.4rem; font-weight: 700; color: #0f172a; margin: 0; padding: 0;">AI-Powered Project Risk Management</h1>
    <p style="font-family: 'Inter', sans-serif; font-size: 1rem; color: #64748b !important; margin-top: 8px;">Enterprise-grade risk intelligence for portfolio decision-makers.</p>
    <hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, #b8860b, transparent); margin: 20px auto; width: 200px;" />
</div>
""", unsafe_allow_html=True)

# --- Session state for real-time projects submitted via Agent Reports ---
if "rt_projects" not in st.session_state:
    st.session_state.rt_projects = []

# --- Dashboard Tabs (3 tabs now) ---
tab1, tab2, tab3 = st.tabs(["📊 Portfolio Dashboard", "🧠 Agent Reports", "💬 Risk Assistant"])

with tab1:
    st.markdown("""
    <div style="margin-bottom:12px;">
        <h2 style="font-family:'Playfair Display',serif; color:#0f172a; font-size:1.8rem; margin:0;"
        >📊 Portfolio Dashboard</h2>
        <p style="color:#64748b; font-size:0.9rem; margin-top:4px;">
            Live overview of all IT projects — including any you've submitted in the Agent Reports tab.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Merge static sample projects with real-time submitted projects
    all_projects = projects + st.session_state.rt_projects

    with st.expander("ℹ️ How to read this dashboard"):
        st.markdown('''
        * **Risk Score:** 0-100 from the ML model — budget burn, schedule delay, payment issues.
        * 🟢 **Low (<40):** Healthy  |  🟠 **Medium (40-70):** Warning  |  🔴 **High (>70):** Critical
        * Projects you analyse in the **Agent Reports** tab appear here automatically.
        ''')

    st.divider()

    # ── Top-level KPIs ──────────────────────────────────────────────────────
    total_budget = sum(p["budget"] for p in all_projects)
    total_spent  = sum(p["spent"]  for p in all_projects)
    at_risk      = sum(1 for p in all_projects if p.get("status") in ["At Risk", "Blocked"])

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Projects", len(all_projects))
    k2.metric("Portfolio Budget", f"${total_budget:,.0f}")
    k3.metric("Total Spent", f"${total_spent:,.0f}",
              delta=f"${total_budget - total_spent:,.0f} remaining", delta_color="normal")
    k4.metric("⚠️ At Risk / Blocked", at_risk)

    if st.session_state.rt_projects:
        if st.button("🗑️ Clear Live Projects", use_container_width=True):
            st.session_state.rt_projects = []
            st.rerun()

    st.divider()

    # ── Status filter ────────────────────────────────────────────────────────
    all_statuses = sorted(set(p["status"] for p in all_projects))
    selected_statuses = st.multiselect("Filter by Status", all_statuses, default=all_statuses)
    filtered = [p for p in all_projects if p["status"] in selected_statuses]

    if not filtered:
        st.warning("No projects match the selected filters.")
    else:
        # ── Budget Burn Rate chart ───────────────────────────────────────────
        st.subheader("💸 Budget Burn Rate")
        df_budget = pd.DataFrame({
            "Project": [p["name"] for p in filtered],
            "Budget":  [p["budget"] for p in filtered],
            "Spent":   [p["spent"]  for p in filtered],
        })
        fig_budget = px.bar(
            df_budget, x="Project", y=["Budget", "Spent"], barmode="group",
            color_discrete_map={"Budget": "#1e293b", "Spent": "#b8860b"},
            title="Budget vs. Spent per Project"
        )
        fig_budget.update_layout(
            plot_bgcolor="#fafafa", paper_bgcolor="#ffffff",
            font={"family": "Inter, sans-serif", "color": "#334155"},
            title_font={"family": "Playfair Display, serif", "size": 18, "color": "#0f172a"},
            xaxis={"gridcolor": "#edebe7", "color": "#64748b"},
            yaxis={"gridcolor": "#edebe7", "color": "#64748b"},
            legend={"font": {"color": "#64748b"}},
            margin={"l": 20, "r": 20, "t": 50, "b": 20}
        )
        st.plotly_chart(fig_budget, use_container_width=True)

        # ── Timeline Progress chart ──────────────────────────────────────────
        st.subheader("📅 Schedule Progress")
        df_timeline = pd.DataFrame({
            "Project": [p["name"] for p in filtered],
            "% Complete (Days)": [
                round(p["days_elapsed"] / max(p["timeline_days"], 1) * 100, 1)
                for p in filtered
            ],
            "% Complete (Tasks)": [
                round(p["completed_tasks"] / max(p["total_tasks"], 1) * 100, 1)
                for p in filtered
            ],
        })
        fig_timeline = px.bar(
            df_timeline, x="Project",
            y=["% Complete (Days)", "% Complete (Tasks)"],
            barmode="group",
            color_discrete_map={"% Complete (Days)": "#6366f1", "% Complete (Tasks)": "#22c55e"},
            title="Timeline vs. Task Completion (%)"
        )
        fig_timeline.update_layout(
            plot_bgcolor="#fafafa", paper_bgcolor="#ffffff",
            font={"family": "Inter, sans-serif", "color": "#334155"},
            yaxis={"range": [0, 110], "gridcolor": "#edebe7"},
            margin={"l": 20, "r": 20, "t": 50, "b": 20}
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

        st.divider()

        # ── Per-project cards with inline edit ──────────────────────────────
        st.subheader("🗂️ Project Cards")
        for proj in filtered:
            try:
                res = requests.post(f"{API_URL}/risk/score", json=proj, timeout=8).json()
                score    = res.get("score", 0)
                category = res.get("category", "Unknown")
            except Exception:
                score, category = 0, "Unknown"

            badge_color = "#22c55e" if category == "Low" else "#f97316" if category == "Medium" else "#ef4444"
            is_rt = proj in st.session_state.rt_projects  # label real-time entries

            with st.expander(
                f"{'🔴' if category=='High' else '🟠' if category=='Medium' else '🟢'}  "
                f"{proj['name']}  —  {score:.0f}/100 ({category})"
                + ("  *(live)*" if is_rt else "")
            ):
                c1, c2, c3 = st.columns(3)
                c1.metric("Risk Score", f"{score:.1f} / 100")
                c2.metric("Budget Spent", f"${proj['spent']:,.0f} / ${proj['budget']:,.0f}")
                c3.metric("Tasks Done", f"{proj['completed_tasks']} / {proj['total_tasks']}")

                st.progress(
                    min(proj["completed_tasks"] / max(proj["total_tasks"], 1), 1.0),
                    text="Task Completion"
                )
                if proj.get("payment_delays_days", 0) > 0:
                    st.error(f"⚠️ Payment delayed by {proj['payment_delays_days']} days")
                if proj.get("description"):
                    st.caption(f"📝 {proj['description']}")
                if proj.get("tech_stack"):
                    st.caption(f"🛠️ Tech Stack: {proj['tech_stack']}")
                if proj.get("employees"):
                    st.caption(f"👥 Team size: {proj['employees']} employees")

                # Inline edit form for non-RT projects (RT ones are read-only snapshots)
                if not is_rt:
                    with st.form(f"edit_{proj['id']}"):
                        st.markdown("**✏️ Quick Edit**")
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            new_status   = st.selectbox("Status",
                                ["On Track", "In Progress", "At Risk", "Blocked", "Completed"],
                                index=["On Track", "In Progress", "At Risk", "Blocked", "Completed"].index(
                                    proj["status"]) if proj["status"] in
                                    ["On Track", "In Progress", "At Risk", "Blocked", "Completed"] else 0
                            )
                            new_spent    = st.number_input("Budget Spent ($)", min_value=0, value=int(proj["spent"]))
                            new_done     = st.number_input("Completed Tasks",  min_value=0, value=int(proj["completed_tasks"]))
                        with ec2:
                            new_util     = st.slider("Resource Utilization", 0.0, 2.0, float(proj["resource_utilization"]), 0.05)
                            new_delay    = st.number_input("Payment Delay (days)", min_value=0, value=int(proj["payment_delays_days"]))
                        save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True)
                        if save_btn:
                            for p in data["projects"]:
                                if p["id"] == proj["id"]:
                                    p["status"] = new_status
                                    p["spent"]  = new_spent
                                    p["completed_tasks"] = new_done
                                    p["resource_utilization"] = new_util
                                    p["payment_delays_days"] = new_delay
                                    break
                            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_data.json')
                            with open(data_path, 'w') as f:
                                json.dump(data, f, indent=2)
                            st.success("✅ Saved! Dashboard will refresh.")
                            st.rerun()


with tab2:
    st.markdown("""
    <div style="margin-bottom:8px;">
        <h2 style="font-family:'Playfair Display',serif; color:#0f172a; font-size:1.8rem; margin:0;">
            🧠 Real-Time IT Project Risk Assessment
        </h2>
        <p style="color:#64748b; font-size:0.95rem; margin-top:4px;">
            Enter your IT project details below. The AI agents will identify, assess, and suggest mitigations for risks in real time.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("realtime_risk_form", clear_on_submit=False):
        # ── Section 1: Project Identity ───────────────────────────────────────
        st.markdown("### 📋 Project Identity")
        col_a, col_b = st.columns(2)
        with col_a:
            rt_name = st.text_input("Project Name *", placeholder="e.g. Cloud ERP Migration")
            rt_tech = st.text_input("Tech Stack", placeholder="e.g. AWS, Kubernetes, Python, PostgreSQL")
        with col_b:
            rt_status = st.selectbox("Project Status", ["In Progress", "On Track", "At Risk", "Blocked", "Completed"])
            rt_employees = st.number_input("Number of Employees / Team Size", min_value=1, max_value=10000, value=10, step=1)

        rt_description = st.text_area(
            "Project Description *",
            placeholder="Briefly describe the IT project scope, objectives, and key deliverables...",
            height=110
        )

        # ── Section 2: Financial Health ────────────────────────────────────────
        st.markdown("### 💰 Financial Health")
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            rt_budget = st.number_input("Total Budget ($)", min_value=1000, value=500000, step=10000)
        with col_f2:
            rt_spent = st.number_input("Budget Spent ($)", min_value=0, value=150000, step=5000)
        with col_f3:
            rt_delay = st.number_input("Payment Delay (days)", min_value=0, value=0, step=1)

        # ── Section 3: Schedule & Progress ─────────────────────────────────────
        st.markdown("### 📅 Schedule & Progress")
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            rt_timeline = st.number_input("Total Timeline (days)", min_value=1, value=180, step=1)
        with col_s2:
            rt_elapsed = st.number_input("Days Elapsed", min_value=0, value=60, step=1)
        with col_s3:
            rt_comp_tasks = st.number_input("Completed Tasks", min_value=0, value=30, step=1)
        with col_s4:
            rt_total_tasks = st.number_input("Total Tasks", min_value=1, value=100, step=1)

        rt_resource_util = st.slider(
            "Resource Utilization (0 = idle, 1.0 = fully allocated, >1.0 = overloaded)",
            min_value=0.0, max_value=2.0, value=0.85, step=0.05,
            format="%.2f"
        )

        # ── Section 4: Market Context ──────────────────────────────────────────
        st.markdown("### 🌐 Market & External Context")
        rt_market = st.text_area(
            "Market / Regulatory Context",
            placeholder="Describe external risks: e.g. 'New GDPR compliance mandate', 'Cloud vendor pricing changes', 'Talent shortage in DevOps'...",
            height=90
        )

        st.divider()
        submitted = st.form_submit_button("🚀 Run Full AI Risk Analysis", use_container_width=True)

    # ── After form submission ─────────────────────────────────────────────────
    if submitted:
        if not rt_name.strip():
            st.error("⚠️ Please enter a Project Name before running the analysis.")
        elif not rt_description.strip():
            st.error("⚠️ Please enter a Project Description before running the analysis.")
        else:
            # Build project payload
            import uuid
            project_payload = {
                "id": f"RT-{uuid.uuid4().hex[:6].upper()}",
                "name": rt_name.strip(),
                "description": rt_description.strip(),
                "tech_stack": rt_tech.strip() or "Not specified",
                "employees": int(rt_employees),
                "status": rt_status,
                "budget": float(rt_budget),
                "spent": float(rt_spent),
                "payment_delays_days": int(rt_delay),
                "timeline_days": int(rt_timeline),
                "days_elapsed": int(rt_elapsed),
                "completed_tasks": int(rt_comp_tasks),
                "total_tasks": int(rt_total_tasks),
                "resource_utilization": float(rt_resource_util),
                "market_context": rt_market.strip() or "General IT Market"
            }

            # --- Save to session state so it appears in Portfolio Dashboard ---
            # Check if project with same ID already exists to avoid duplicates on re-runs
            if not any(p["id"] == project_payload["id"] for p in st.session_state.rt_projects):
                st.session_state.rt_projects.append(project_payload)

            # ── Step 1: Instant ML Risk Preview ──────────────────────────────
            st.markdown("---")
            st.markdown("### ⚡ Instant ML Risk Preview")
            try:
                ml_res = requests.post(f"{API_URL}/risk/score", json=project_payload, timeout=10).json()
                ml_score = ml_res.get("score", 0)
                ml_cat = ml_res.get("category", "Unknown")
                color = "#22c55e" if ml_cat == "Low" else "#f97316" if ml_cat == "Medium" else "#ef4444"
                budget_pct = (rt_spent / rt_budget * 100) if rt_budget > 0 else 0
                task_pct = (rt_comp_tasks / rt_total_tasks * 100) if rt_total_tasks > 0 else 0
                
                mc1, mc2, mc3, mc4 = st.columns(4)
                mc1.metric("🎯 Risk Score", f"{ml_score:.1f} / 100")
                mc2.metric("🏷️ Risk Category", ml_cat)
                mc3.metric("💸 Budget Consumed", f"{budget_pct:.1f}%")
                mc4.metric("✅ Tasks Completed", f"{task_pct:.1f}%")
                st.markdown(
                    f"<div style='padding:10px 16px; border-radius:8px; background:{color}22; border-left:4px solid {color}; color:{color}; font-weight:600; font-size:1rem;'>"
                    f"Risk Level: {ml_cat}</div>",
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.warning(f"Could not fetch ML preview (API may be offline): {e}")

            # ── Step 2: Full CrewAI Agent Report ─────────────────────────────
            st.markdown("---")
            st.markdown("### 📄 Full AI Agent Report")
            st.info(
                "🤖 The AI agents are now analyzing your project — examining internal health, market sentiment, "
                "computing an ML risk score, and searching historical precedents. This takes 1–3 minutes on a free API tier."
            )
            with st.spinner(f"Agents analyzing **{rt_name}**... Please wait (up to 3 minutes)"):
                try:
                    res = requests.post(
                        f"{API_URL}/agent/report",
                        json=project_payload,
                        timeout=180
                    ).json()

                    if res.get("status") == "success":
                        st.success("✅ Analysis complete!")
                        st.markdown(res.get("report", "No report content returned."))
                        
                        # Download button for the report
                        report_md = res.get("report", "")
                        st.download_button(
                            label="⬇️ Download Report as Markdown",
                            data=report_md,
                            file_name=f"risk_report_{rt_name.replace(' ', '_')}.md",
                            mime="text/markdown"
                        )
                    else:
                        st.error(res.get("detail", "An error occurred during agent execution."))
                except requests.exceptions.Timeout:
                    st.error("⏱️ The agent analysis timed out after 3 minutes. Please try again.")
                except Exception as e:
                    st.error(f"❌ Failed to reach the agent API. Ensure FastAPI is running.\n\nError: {e}")


with tab3:
    st.header("💬 Conversational Risk Assistant")
    st.markdown("Ask natural language questions about project risks, historical mitigations, and current status.")

    all_projects_ctx = projects + st.session_state.rt_projects
    
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
                context = json.dumps(all_projects_ctx)
                payload = {"query": prompt, "context": context}
                res = requests.post(f"{API_URL}/chat", json=payload).json()
                reply = res.get("reply", "No response.")
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                error_msg = f"Failed to connect to Chatbot API: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

