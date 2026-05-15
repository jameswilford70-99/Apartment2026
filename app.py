import streamlit as st
import pandas as pd
import altair as alt

# 1. Page Configuration
st.set_page_config(
    page_title="97 Plough Drive | Budget Terminal",
    page_icon="🏠",
    layout="wide"
)

# MODERN HIGH-CONTRAST CSS
st.markdown("""
    <style>
    .main .block-container { max-width: 1200px; padding-top: 2rem; }
    
    /* Metrics: Electric Blue for High Visibility */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        color: #60A5FA !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #94A3B8 !important;
    }
    
    /* Headers */
    h1 { font-weight: 800; color: #F8FAFC; }
    h3 { font-weight: 700; color: #E2E8F0; border-bottom: 2px solid #334155; padding-bottom: 8px; margin-top: 2rem; }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab"] { font-size: 1rem; font-weight: 600; color: #94A3B8; }
    .stTabs [aria-selected="true"] { color: #60A5FA !important; border-bottom-color: #60A5FA !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🏠 97 Plough Drive")
st.markdown("##### Property Purchase & Room Budget Tracker")
st.markdown("---")

# 2. DATA INITIALIZATION
if "v_production_ready" not in st.session_state:
    # Template for admin fees
    st.session_state.admin_df = pd.DataFrame([
        {"Item": "Solicitor / Legal Fees", "Budget": 0.0, "Actual": 0.0, "Status": "Pending"},
        {"Item": "Surveyor Fee", "Budget": 0.0, "Actual": 0.0, "Status": "Pending"},
        {"Item": "Stamp Duty", "Budget": 0.0, "Actual": 0.0, "Status": "Pending"},
        {"Item": "Mortgage Fee", "Budget": 0.0, "Actual": 0.0, "Status": "Pending"}
    ])
    
    # Template for rooms
    def create_room_df(items):
        return pd.DataFrame([
            {"Item": i, "Budget": 0.0, "Actual": 0.0, "Status": "Not Started"}
            for i in items
        ])
    
    st.session_state.room_data = {
        "Bedroom": create_room_df(["Bed Frame", "Mattress", "Wardrobe"]),
        "Living Room": create_room_df(["Sofa", "TV Stand", "Coffee Table"]),
        "Kitchen": create_room_df(["Fridge Freezer", "Microwave", "Kettle"]),
        "Bathroom": create_room_df(["Mirror", "Bath Mat", "Towel Rail"]),
        "Whole Apt": create_room_df(["Light Bulbs", "Extension Leads", "Vacuum"])
    }
    st.session_state.v_production_ready = True

# 3. APP TABS
tabs = st.tabs(["📊 Dashboard", "⚖️ Admin Fees", "🛏️ Bedroom", "🛋️ Living Room", "🍳 Kitchen", "🛁 Bathroom", "📦 Whole Apt"])

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    summary = []
    
    for name, df in st.session_state.room_data.items():
        summary.append({"Category": name, "Budgeted": df["Budget"].sum(), "Actual": df["Actual"].sum()})
        
    ab, aa = st.session_state.admin_df["Budget"].sum(), st.session_state.admin_df["Actual"].sum()
    summary.append({"Category": "Admin Fees", "Budgeted": ab, "Actual": aa})
    
    summary_df = pd.DataFrame(summary)
    total_b, total_a = summary_df["Budgeted"].sum(), summary_df["Actual"].sum()
    remaining = total_b - total_a

    # KPI Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("TOTAL BUDGET", f"£{total_b:,.2f}")
    col2.metric("TOTAL SPENT", f"£{total_a:,.2f}", delta=f"£{remaining:,.2f} Left", delta_color="normal")
    col3.metric("REMAINING", f"£{remaining:,.2f}")

    st.markdown("### Expense Analysis")
    
    # NEW GROUPED BAR CHART LOGIC (More stable than Facets)
    chart_data = summary_df.melt(id_vars="Category", value_vars=["Budgeted", "Actual"], var_name="Type", value_name="Amount")
    
    # Modern Grouped Bar Chart
    chart = alt.Chart(chart_data).mark_bar(
        cornerRadiusTopLeft=4,
        cornerRadiusTopRight=4
    ).encode(
        x=alt.X("Category:N", title=None, axis=alt.Axis(labelAngle=0, labelFontSize=12, labelPadding=10)),
        y=alt.Y("Amount:Q", title="Amount (£)", axis=alt.Axis(format="£~s", grid=True)),
        # xOffset creates the side-by-side bars for Budgeted/Actual
        xOffset="Type:N",
        color=alt.Color("Type:N", scale=alt.Scale(domain=["Budgeted", "Actual"], range=["#475569", "#3B82F6"]), 
                        legend=alt.Legend(title=None, orient='top-right')),
        tooltip=["Category", "Type", "Amount"]
    ).properties(
        height=400
    )

    # use_container_width=True will now correctly stretch this single chart
    st.altair_chart(chart, use_container_width=True)

# --- TAB 2: ADMIN FEES ---
with tabs[1]:
    st.markdown("### ⚖️ Professional & Admin Fees")
    st.session_state.admin_df = st.data_editor(
        st.session_state.admin_df,
        column_config={
            "Budget": st.column_config.NumberColumn("Budget (£)", format="£%.2f"),
            "Actual": st.column_config.NumberColumn("Actual (£)", format="£%.2f"),
            "Status": st.column_config.SelectboxColumn(options=["Pending", "Paid"])
        },
        num_rows="dynamic", use_container_width=True, key="admin_editor_final"
    )

# --- ROOM TABS ---
room_keys = list(st.session_state.room_data.keys())
for i, name in enumerate(room_keys, start=2):
    with tabs[i]:
        st.markdown(f"### 📦 {name} Items")
        st.session_state.room_data[name] = st.data_editor(
            st.session_state.room_data[name],
            column_config={
                "Budget": st.column_config.NumberColumn("Budget (£)", format="£%.2f"),
                "Actual": st.column_config.NumberColumn("Actual (£)", format="£%.2f"),
                "Status": st.column_config.SelectboxColumn(options=["Not Started", "Ordered", "Done"]),
                "Link": st.column_config.LinkColumn("Product Link")
            },
            num_rows="dynamic", use_container_width=True, key=f"room_editor_{name}_final"
        )
