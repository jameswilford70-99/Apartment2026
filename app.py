import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="97 Plough Drive | Tracker",
    page_icon="🏠",
    layout="wide"
)

# ULTRA-HIGH CONTRAST CSS
st.markdown("""
    <style>
    .main .block-container { max-width: 1200px; padding-top: 2rem; }
    
    /* Metrics: Pure White/Bright Blue for Maximum Readability */
    [data-testid="stMetricValue"] {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important; /* Pure White */
        text-shadow: 0px 0px 10px rgba(59, 130, 246, 0.5);
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #60A5FA !important; /* Sky Blue */
    }
    
    /* Global Text Clarity */
    h1, h3 { color: #F8FAFC !important; font-weight: 800; }
    .stMarkdown p { font-size: 1.1rem; color: #CBD5E1; }
    
    /* Clean Tab Styling */
    .stTabs [data-baseweb="tab"] { font-size: 1.1rem; font-weight: 600; color: #94A3B8; }
    .stTabs [aria-selected="true"] { color: #FFFFFF !important; border-bottom-color: #3B82F6 !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🏠 97 Plough Drive")
st.markdown("##### Property Purchase & Room Budget Tracker")
st.markdown("---")

# 2. DATA INITIALIZATION (Wiping old keys to ensure a clean start)
if "v_stable_v10" not in st.session_state:
    # Admin Fees
    st.session_state.admin_df = pd.DataFrame([
        {"Item": "Solicitor Fees", "Budget": 1500.0, "Actual": 0.0, "Status": "Pending"},
        {"Item": "Surveyor Fee", "Budget": 500.0, "Actual": 0.0, "Status": "Pending"},
        {"Item": "Stamp Duty", "Budget": 0.0, "Actual": 0.0, "Status": "Pending"}
    ])
    
    # Room Data
    def init_room(items):
        return pd.DataFrame([{"Item": i, "Budget": 100.0, "Actual": 0.0, "Status": "Not Started"} for i in items])
    
    st.session_state.room_data = {
        "Bedroom": init_room(["Bed Frame", "Mattress", "Wardrobe"]),
        "Living Room": init_room(["Sofa", "TV Stand", "Coffee Table"]),
        "Kitchen": init_room(["Fridge Freezer", "Microwave", "Kettle"]),
        "Bathroom": init_room(["Mirror", "Bath Mat"]),
        "Whole Apt": init_room(["Light Bulbs", "Vacuum"])
    }
    st.session_state.v_stable_v10 = True

# 3. TAB NAVIGATION
tabs = st.tabs(["📊 Dashboard", "⚖️ Admin Fees", "🛏️ Bedroom", "🛋️ Living Room", "🍳 Kitchen", "🛁 Bathroom", "📦 Whole Apt"])

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    # Calculate totals
    summary = []
    for name, df in st.session_state.room_data.items():
        summary.append({"Category": name, "Budgeted": df["Budget"].sum(), "Actual": df["Actual"].sum()})
    
    adm_b, adm_a = st.session_state.admin_df["Budget"].sum(), st.session_state.admin_df["Actual"].sum()
    summary.append({"Category": "Admin Fees", "Budgeted": adm_b, "Actual": adm_a})
    
    summary_df = pd.DataFrame(summary).set_index("Category")
    total_b, total_a = summary_df["Budgeted"].sum(), summary_df["Actual"].sum()
    rem = total_b - total_a

    # HIGH-VISIBILITY KPI ROW
    c1, c2, c3 = st.columns(3)
    c1.metric("TOTAL BUDGET", f"£{total_b:,.2f}")
    c2.metric("TOTAL SPENT", f"£{total_a:,.2f}", delta=f"£{rem:,.2f} Left", delta_color="normal")
    c3.metric("FUNDS REMAINING", f"£{rem:,.2f}")

    st.markdown("### Expense Analysis")
    
    # NATIVE STREAMLIT CHART: 100% Reliable, no library conflicts
    if not summary_df.empty:
        st.bar_chart(summary_df[["Budgeted", "Actual"]], height=400, color=["#475569", "#3B82F6"])
    else:
        st.info("Start adding costs in the tabs to see your chart!")

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
        num_rows="dynamic", use_container_width=True, key="admin_edit_v10"
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
            num_rows="dynamic", use_container_width=True, key=f"room_{name}_v10"
        )
