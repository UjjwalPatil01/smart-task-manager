"""Modern, interactive Streamlit dashboard for Smart Task Manager."""
import json
import os
import sys
from datetime import date, datetime
import pandas as pd
import altair as alt
import requests
import streamlit as st

# Add project root to sys.path so app imports work seamlessly
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.config import settings
from app.core.database import SessionLocal, Base, engine
from app.services.task_service import TaskService
from app.services.ai_service import AIService
from app.schemas.task import TaskCreate, TaskUpdate, SubTask

# Initialize DB tables
Base.metadata.create_all(bind=engine)

# ==========================================
# PAGE CONFIG & MODERN CUSTOM STYLING
# ==========================================
st.set_page_config(
    page_title="Smart Task Manager 🚀",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics, glassmorphism & responsive badges
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #090d16 0%, #0f172a 100%);
    }
    
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.4);
    }
    
    .task-card {
        background: rgba(30, 41, 59, 0.6);
        border-left: 4px solid #38bdf8;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        transition: all 0.2s ease;
    }
    .task-card:hover {
        background: rgba(30, 41, 59, 0.85);
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.15);
    }
    .task-card.priority-urgent { border-left-color: #ef4444; }
    .task-card.priority-high { border-left-color: #f97316; }
    .task-card.priority-medium { border-left-color: #38bdf8; }
    .task-card.priority-low { border-left-color: #10b981; }
    
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-urgent { background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.4); }
    .badge-high { background: rgba(249, 115, 22, 0.2); color: #fdba74; border: 1px solid rgba(249, 115, 22, 0.4); }
    .badge-medium { background: rgba(56, 189, 248, 0.2); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.4); }
    .badge-low { background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4); }
    .badge-category { background: rgba(147, 51, 234, 0.2); color: #d8b4fe; border: 1px solid rgba(147, 51, 234, 0.4); }
    .badge-ai { background: rgba(236, 72, 153, 0.2); color: #f472b6; border: 1px solid rgba(236, 72, 153, 0.4); }
    .badge-overdue { background: rgba(220, 38, 38, 0.3); color: #fecaca; border: 1px solid #ef4444; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATA ACCESS LAYER (API with Service Fallback)
# ==========================================
API_URL = f"http://{settings.API_HOST}:{settings.API_PORT}{settings.API_V1_STR}"

def check_api_live() -> bool:
    try:
        r = requests.get(f"http://{settings.API_HOST}:{settings.API_PORT}/", timeout=0.8)
        return r.status_code == 200
    except Exception:
        return False

API_ONLINE = check_api_live()

def get_db_session():
    return SessionLocal()

def fetch_stats():
    if API_ONLINE:
        try:
            r = requests.get(f"{API_URL}/analytics/stats", timeout=1.5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
    db = get_db_session()
    try:
        stats = TaskService.get_stats(db)
        return stats.model_dump()
    finally:
        db.close()

def fetch_tasks(search=None, status_filter=None, priority=None, category=None, sort_by=None, order="asc", is_archived=False):
    if API_ONLINE:
        try:
            params = {
                "search": search or None,
                "status": status_filter if status_filter not in ["all", None] else None,
                "priority": priority if priority not in ["all", None] else None,
                "category": category if category not in ["all", None] else None,
                "sort_by": sort_by or None,
                "order": order,
                "is_archived": is_archived
            }
            r = requests.get(f"{API_URL}/tasks/", params={k: v for k, v in params.items() if v is not None}, timeout=2.0)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
    db = get_db_session()
    try:
        tasks, _ = TaskService.list_tasks(
            db=db,
            search=search,
            status=status_filter if status_filter not in ["all", None] else None,
            priority=priority if priority not in ["all", None] else None,
            category=category if category not in ["all", None] else None,
            is_archived=is_archived,
            sort_by=sort_by,
            order=order
        )
        return [t.to_dict() for t in tasks]
    finally:
        db.close()

def create_task_action(title, description, priority, category, due, recurrence, is_ai=False, ai_reason=""):
    task_in = TaskCreate(
        title=title,
        description=description or None,
        priority=priority,
        category=category,
        due=due or None,
        recurrence=recurrence,
        is_ai_generated=is_ai,
        ai_reasoning=ai_reason or None,
        subtasks=[]
    )
    if API_ONLINE:
        try:
            r = requests.post(f"{API_URL}/tasks/", json=task_in.model_dump(), timeout=2.0)
            if r.status_code in [200, 201]:
                return True
        except Exception:
            pass
    db = get_db_session()
    try:
        TaskService.create_task(db, task_in)
        return True
    finally:
        db.close()

def toggle_task_action(task_id: int):
    if API_ONLINE:
        try:
            r = requests.patch(f"{API_URL}/tasks/{task_id}/toggle", timeout=2.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
    db = get_db_session()
    try:
        TaskService.toggle_done(db, task_id)
        return True
    finally:
        db.close()

def delete_task_action(task_id: int, permanent: bool = False):
    if API_ONLINE:
        try:
            r = requests.delete(f"{API_URL}/tasks/{task_id}?permanent={str(permanent).lower()}", timeout=2.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
    db = get_db_session()
    try:
        TaskService.delete_task(db, task_id, permanent=permanent)
        return True
    finally:
        db.close()

def update_subtasks_action(task_id: int, subtasks_list):
    db = get_db_session()
    try:
        task_in = TaskUpdate(subtasks=[SubTask(**st) for st in subtasks_list])
        TaskService.update_task(db, task_id, task_in)
        return True
    finally:
        db.close()

# Auto-seed legacy data non-destructively on first run
db = get_db_session()
try:
    TaskService.seed_from_legacy_json(db)
finally:
    db.close()

# ==========================================
# SIDEBAR: SYSTEM STATUS & QUICK ACTIONS
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/tasklist.png", width=64)
    st.title("Smart Task Manager")
    st.caption("AI-Powered Productivity & Task Management")
    st.divider()

    # System Status Badges
    ai_online = AIService.is_configured()
    st.subheader("System Health")
    c1, c2 = st.columns(2)
    with c1:
        if API_ONLINE:
            st.success("API: Online")
        else:
            st.info("Direct Engine")
    with c2:
        if ai_online:
            st.success("Gemini: Active")
        else:
            st.warning("AI: Offline Mode")

    if not ai_online:
        st.caption("💡 Add `GOOGLE_API_KEY` to `.env` to unlock live Gemini reasoning. Resilient keyword heuristics are active.")

    st.divider()
    st.subheader("Task Navigation")
    view_mode = st.radio("Select View", ["📋 Task Board", "📊 Productivity Analytics", "💾 Backup & Data"], label_visibility="collapsed")

# ==========================================
# VIEW 1: TASK BOARD
# ==========================================
if view_mode == "📋 Task Board":
    # Header & Metric Bar
    stats = fetch_stats()
    
    st.title("Workspace Dashboard 🚀")
    
    # KPI Row
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Total Tasks", stats.get("total", 0))
    with k2:
        st.metric("Completed", stats.get("completed", 0), f"{stats.get('completion_rate', 0)}%")
    with k3:
        st.metric("Pending", stats.get("pending", 0))
    with k4:
        st.metric("Overdue", stats.get("overdue", 0), delta=f"-{stats.get('overdue', 0)}" if stats.get("overdue", 0) > 0 else "0", delta_color="inverse")
    with k5:
        st.metric("High Priority", stats.get("high_priority", 0))

    st.progress(stats.get("completion_rate", 0) / 100.0)

    # Add Task Expander
    with st.expander("✨ Add New Task", expanded=False):
        with st.form("new_task_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns([2, 1])
            with f_col1:
                t_title = st.text_input("Task Title *", placeholder="e.g. Finish final research paper for exam", key="nt_title")
                t_desc = st.text_area("Notes / Description", placeholder="Additional context, sub-goals, or links...", height=80, key="nt_desc")
            with f_col2:
                t_due = st.date_input("Due Date", value=None, min_value=date(2026, 1, 1), key="nt_due")
                t_category = st.selectbox("Category", ["personal", "study", "work", "health", "finance", "other"], index=0, key="nt_cat")
                t_priority_choice = st.selectbox("Priority", ["Auto (AI Classify)", "low", "medium", "high", "urgent"], index=0, key="nt_prio")
                t_recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly", "monthly"], index=0, key="nt_rec")
            
            t_breakdown = st.checkbox("🪄 Automatically decompose into actionable subtasks with AI", value=False)
            submitted = st.form_submit_button("Add Task 🚀", use_container_width=True)

            if submitted:
                if not t_title.strip():
                    st.error("Please provide a task title.")
                else:
                    due_str = t_due.isoformat() if t_due else None
                    is_ai = False
                    ai_reason = ""
                    assigned_prio = t_priority_choice
                    assigned_cat = t_category

                    if t_priority_choice == "Auto (AI Classify)":
                        ai_res = AIService.suggest_priority(t_title, t_desc)
                        assigned_prio = ai_res.get("priority", "medium")
                        assigned_cat = ai_res.get("suggested_category", t_category)
                        ai_reason = ai_res.get("reasoning", "")
                        is_ai = True

                    subtasks_list = []
                    if t_breakdown:
                        decomp = AIService.decompose_task(t_title, t_desc)
                        for idx, st_title in enumerate(decomp.get("subtasks", [])):
                            subtasks_list.append({"id": f"st_{idx}", "title": st_title, "done": False})

                    # Create task
                    task_in = TaskCreate(
                        title=t_title,
                        description=t_desc,
                        priority=assigned_prio,
                        category=assigned_cat,
                        due=due_str,
                        recurrence=t_recurrence,
                        is_ai_generated=is_ai,
                        ai_reasoning=ai_reason,
                        subtasks=[SubTask(**s) for s in subtasks_list]
                    )
                    db = get_db_session()
                    try:
                        TaskService.create_task(db, task_in)
                        st.success(f"Task created: '{t_title}' (Priority: {assigned_prio.upper()})")
                        st.rerun()
                    finally:
                        db.close()

    # Search & Filter Controls Bar
    st.markdown("### Tasks")
    c_search, c_status, c_cat, c_prio, c_sort = st.columns([3, 2, 2, 2, 2])
    with c_search:
        search_query = st.text_input("Search", placeholder="Search tasks...", label_visibility="collapsed")
    with c_status:
        status_filter = st.selectbox("Status", ["all", "pending", "completed", "archived"], label_visibility="collapsed")
    with c_cat:
        cat_filter = st.selectbox("Category", ["all", "personal", "study", "work", "health", "finance"], label_visibility="collapsed")
    with c_prio:
        prio_filter = st.selectbox("Priority", ["all", "urgent", "high", "medium", "low"], label_visibility="collapsed")
    with c_sort:
        sort_choice = st.selectbox("Sort", ["Default", "Due Date (asc)", "Due Date (desc)", "Priority", "Created Date"], label_visibility="collapsed")

    sort_field = None
    sort_order = "asc"
    if sort_choice == "Due Date (asc)":
        sort_field = "due"; sort_order = "asc"
    elif sort_choice == "Due Date (desc)":
        sort_field = "due"; sort_order = "desc"
    elif sort_choice == "Priority":
        sort_field = "priority"; sort_order = "desc"
    elif sort_choice == "Created Date":
        sort_field = "created_at"; sort_order = "desc"

    tasks = fetch_tasks(
        search=search_query,
        status_filter=status_filter if status_filter != "all" else None,
        priority=prio_filter if prio_filter != "all" else None,
        category=cat_filter if cat_filter != "all" else None,
        sort_by=sort_field,
        order=sort_order,
        is_archived=(status_filter == "archived")
    )

    if not tasks:
        st.info("No matching tasks found. Relax your filters or add a new task!")
    else:
        today_str = date.today().isoformat()
        for t in tasks:
            t_id = t["id"]
            prio = t.get("priority", "medium")
            cat = t.get("category", "personal")
            is_done = t.get("done", False)
            due = t.get("due")
            is_overdue = (not is_done and due and due < today_str)

            card_border_class = f"priority-{prio}"
            prio_badge_class = f"badge-{prio}"

            with st.container():
                st.markdown(f"""
                <div class="task-card {card_border_class}">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span class="badge {prio_badge_class}">{prio.upper()}</span>
                            <span class="badge badge-category">{cat.upper()}</span>
                            {'<span class="badge badge-ai">🤖 AI</span>' if t.get('is_ai_generated') else ''}
                            {'<span class="badge badge-overdue">⚠️ OVERDUE</span>' if is_overdue else ''}
                            <span style="font-size:1.05rem; font-weight:600; text-decoration:{'line-through' if is_done else 'none'}; opacity:{0.6 if is_done else 1.0}; margin-left:8px;">
                                {t['title']}
                            </span>
                        </div>
                        <div style="color:#94a3b8; font-size:0.85rem;">
                            📅 {due or 'No deadline'}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if t.get("ai_reasoning"):
                    st.caption(f"🧠 *AI Reasoning:* {t['ai_reasoning']}")

                # Subtasks checklist
                subtasks_raw = t.get("subtasks", "[]")
                try:
                    subtasks = json.loads(subtasks_raw) if isinstance(subtasks_raw, str) else (subtasks_raw or [])
                except Exception:
                    subtasks = []

                if subtasks:
                    with st.expander(f"Checklist ({sum(1 for s in subtasks if s.get('done'))}/{len(subtasks)})", expanded=False):
                        modified_subtasks = False
                        for s in subtasks:
                            checked = st.checkbox(s.get("title", ""), value=s.get("done", False), key=f"st_{t_id}_{s.get('id')}")
                            if checked != s.get("done", False):
                                s["done"] = checked
                                modified_subtasks = True
                        if modified_subtasks:
                            update_subtasks_action(t_id, subtasks)
                            st.rerun()

                # Action Buttons Row
                b_c1, b_c2, b_c3, b_c4 = st.columns([1.5, 1.5, 1.5, 6])
                with b_c1:
                    toggle_label = "↩️ Undo" if is_done else "✅ Complete"
                    if st.button(toggle_label, key=f"btn_toggle_{t_id}", use_container_width=True):
                        toggle_task_action(t_id)
                        st.rerun()
                with b_c2:
                    if not subtasks:
                        if st.button("🪄 Subtasks", key=f"btn_decomp_{t_id}", use_container_width=True):
                            decomp = AIService.decompose_task(t["title"], t.get("description"))
                            new_st = [{"id": f"st_{i}", "title": s, "done": False} for i, s in enumerate(decomp.get("subtasks", []))]
                            update_subtasks_action(t_id, new_st)
                            st.success("Subtasks generated!")
                            st.rerun()
                with b_c3:
                    if st.button("🗑️ Delete", key=f"btn_del_{t_id}", use_container_width=True):
                        delete_task_action(t_id, permanent=False)
                        st.rerun()

                st.write("")  # Spacer

# ==========================================
# VIEW 2: PRODUCTIVITY ANALYTICS
# ==========================================
elif view_mode == "📊 Productivity Analytics":
    st.title("Productivity & Task Intelligence 📊")
    stats = fetch_stats()

    # AI Productivity Coach Card
    st.subheader("🤖 AI Productivity Coach")
    coach_insights = AIService.generate_productivity_insights(stats)

    with st.container():
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid #a855f7;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h4 style="margin:0; color:#d8b4fe;">Weekly Assessment</h4>
                <div style="font-size:1.5rem; font-weight:700; color:#38bdf8;">Score: {coach_insights.get('productivity_score', 80)}/100</div>
            </div>
            <p style="margin-top:10px; color:#e2e8f0; font-size:1rem;">{coach_insights.get('summary')}</p>
            <h5 style="color:#7dd3fc; margin-top:14px; margin-bottom:8px;">Actionable Recommendations:</h5>
            <ul style="color:#cbd5e1;">
                {''.join(f'<li>{r}</li>' for r in coach_insights.get('actionable_recommendations', []))}
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Visualizations Grid
    c_chart1, c_chart2 = st.columns(2)

    with c_chart1:
        st.subheader("Category Distribution")
        cat_data = stats.get("categories", {})
        if cat_data:
            df_cat = pd.DataFrame(list(cat_data.items()), columns=["Category", "Count"])
            chart_cat = alt.Chart(df_cat).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Category", type="nominal", scale=alt.Scale(scheme="category10")),
                tooltip=["Category", "Count"]
            ).properties(height=300)
            st.altair_chart(chart_cat, use_container_width=True)
        else:
            st.info("No category data available yet.")

    with c_chart2:
        st.subheader("Priority Allocation")
        prio_data = stats.get("priorities", {})
        if prio_data:
            df_prio = pd.DataFrame(list(prio_data.items()), columns=["Priority", "Count"])
            chart_prio = alt.Chart(df_prio).mark_bar(cornerRadius=6).encode(
                x=alt.X("Priority", sort=["urgent", "high", "medium", "low"]),
                y=alt.Y("Count", type="quantitative"),
                color=alt.Color("Priority", scale=alt.Scale(domain=["urgent", "high", "medium", "low"], range=["#ef4444", "#f97316", "#38bdf8", "#10b981"])),
                tooltip=["Priority", "Count"]
            ).properties(height=300)
            st.altair_chart(chart_prio, use_container_width=True)
        else:
            st.info("No priority data available yet.")

# ==========================================
# VIEW 3: BACKUP & DATA MANAGEMENT
# ==========================================
elif view_mode == "💾 Backup & Data":
    st.title("Data Safety, Backup & Portability 💾")
    st.markdown("""
    This section guarantees complete data portability and protection. You can export all current tasks, download backups, or inspect legacy records.
    """)

    all_tasks = fetch_tasks(status_filter="all", is_archived=True)
    df_export = pd.DataFrame(all_tasks)

    b1, b2 = st.columns(2)
    with b1:
        st.subheader("Export Tasks")
        if not df_export.empty:
            csv_data = df_export.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download CSV Export",
                data=csv_data,
                file_name=f"tasks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

            json_data = json.dumps(all_tasks, indent=2).encode("utf-8")
            st.download_button(
                "📥 Download JSON Export",
                data=json_data,
                file_name=f"tasks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        else:
            st.info("No tasks to export.")

    with b2:
        st.subheader("Recovered Legacy Data Inspection")
        legacy_path = os.path.join(ROOT_DIR, "data", "tasks_legacy.json")
        if os.path.exists(legacy_path):
            with open(legacy_path, "r", encoding="utf-8") as f:
                legacy_tasks = json.load(f)
            st.success(f"Preserved original tasks archive: {len(legacy_tasks)} tasks intact.")
            with st.expander("View Preserved Legacy JSON", expanded=False):
                st.json(legacy_tasks)
        else:
            st.warning("Legacy tasks file not found.")

    st.divider()
    st.subheader("Active Database Diagnostics")
    st.code(f"Database URL: {settings.DATABASE_URL}\nStorage Engine: SQLite with WAL (Write-Ahead Logging)\nTotal Records: {len(all_tasks)}")
