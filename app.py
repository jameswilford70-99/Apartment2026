import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="97 Plough Drive | Budget Terminal",
    page_icon="🏠",
    layout="wide"
)

# 2. ULTRA-MODERN HIGH-CONTRAST CSS
st.markdown("""
    <style>
    .main .block-container { max-width: 1200px; padding-top: 2rem; }
    
    /* Metrics: Bright Electric Blue & High Visibility */
    [data-testid="stMetricValue"] {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        color: #3B82F6 !important; 
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #94A3B8 !important;
    }
    
    /* Headers & Text */
    h1, h3 { color: #F8FAFC !important; font-weight: 800; }
    .stMarkdown p { font-size: 1.1rem; color: #CBD5E1; }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] { background-color: #0F172A; }
    </style>
""", unsafe_allow_html=True)

# 3. DATA INITIALIZATION & HARD RESET
if st.sidebar.button("🔄 Hard Reset App Data"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

if "v_pro_stable_v1" not in st.session_state:
    # Initialize Admin Fees
    st.session_state.admin_df = pd.DataFrame([
        {"Item": "Solicitor Fees", "Budget": 1500.0, "Actual": 0.0, "Status": "Pending"},
        {"Item": "Surveyor Fee", "Budget": 500.0, "Actual": 0.0, "Status": "Pending"},
        {"Item": "Stamp Duty", "Budget": 0.0, "Actual": 0.0, "Status": "Pending"}
    ])
    
    # Initialize Room Data
    def init_room(items):
        return pd.DataFrame([{"Item": i, "Budget": 200.0, "Actual": 0.0, "Status": "Not Started"} for i in items])
    
    st.session_state.room_data = {
        "Bedroom": init_room(["Bed Frame", "Mattress", "Wardrobe"]),
        "Living Room": init_room(["Sofa", "TV Stand", "Coffee Table"]),
        "Kitchen": init_room(["Fridge Freezer", "Microwave", "Kettle"]),
        "Bathroom": init_room(["Mirror", "Bath Mat"]),
        "Whole Apt": init_room(["Light Bulbs", "Vacuum"])
    }
    st.session_state.v_pro_stable_v1 = True

st.title("🏠 97 Plough Drive")
st.markdown("##### Property Purchase & Room Budget Tracker")
st.markdown("---")

# 4. TAB NAVIGATION
tabs = st.tabs(["📊 Dashboard", "⚖️ Admin Fees", "🛏️ Bedroom", "🛋️ Living Room", "🍳 Kitchen", "🛁 Bathroom", "📦 Whole Apt"])

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    # Aggregate Totals
    summary = []
    for name, df in st.session_state.room_data.items():
        summary.append({"Category": name, "Budgeted": df["Budget"].sum(), "Actual": df["Actual"].sum()})
    
    adm_b, adm_a = st.session_state.admin_df["Budget"].sum(), st.session_state.admin_df["Actual"].sum()
    summary.append({"Category": "Admin Fees", "Budgeted": adm_b, "Actual": adm_a})
    
    summary_df = pd.DataFrame(summary)
    total_b, total_a = summary_df["Budgeted"].sum(), summary_df["Actual"].sum()
    rem = total_b - total_a

    # KPI METRICS
    c1, c2, c3 = st.columns(3)
    c1.metric("TOTAL BUDGET", f"£{total_b:,.2f}")
    c2.metric("TOTAL SPENT", f"£{total_a:,.2f}", delta=f"£{rem:,.2f} Left", delta_color="normal")
    c3.metric("FUNDS REMAINING", f"£{rem:,.2f}")

    st.markdown("### Expense Analysis")
    
    # PLOTLY CHART: Extremely stable and visually superior
    if not summary_df.empty:
        fig = px.bar(
            summary_df, 
            x="Category", 
            y=["Budgeted", "Actual"],
            barmode="group",
            color_discrete_map={"Budgeted": "#475569", "Actual": "#3B82F6"},
            template="plotly_dark"
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis_title="Amount (£)",
            xaxis_title=None,
            font=dict(size=14)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Fill in your budgets in the tabs to generate the analysis chart.")

# --- TAB 2: ADMIN FEES ---
with tabs[1]:
    st.markdown("### ⚖️ Legal & Admin Costs")
    st.session_state.admin_df = st.data_editor(
        st.session_state.admin_df,
        column_config={
            "Budget": st.column_config.NumberColumn("Budget (£)", format="£%.2f"),
            "Actual": st.column_config.NumberColumn("Actual (£)", format="£%.2f"),
            "Status": st.column_config.SelectboxColumn(options=["Pending", "Paid"])
        },
        num_rows="dynamic", use_container_width=True, key="admin_edit_v1"
    )

# --- ROOM TABS ---
room_keys = list(st.session_state.room_data.keys())
for i, name in enumerate(room_keys, start=2):
    with tabs[i]:
        st.markdown(f"### 📦 {name} Requirements")
        st.session_state.room_data[name] = st.data_editor(
            st.session_state.room_data[name],
            column_config={
                "Budget": st.column_config.NumberColumn("Budget (£)", format="£%.2f"),
                "Actual": st.column_config.NumberColumn("Actual (£)", format="£%.2f"),
                "Status": st.column_config.SelectboxColumn(options=["Not Started", "Ordered", "Done"])
            },
            num_rows="dynamic", use_container_width=True, key=f"room_{name}_v1"
        )
