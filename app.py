import streamlit as st
import pandas as pd
import altair as alt

# 1. Page Configuration
st.set_page_config(
    page_title="97 Plough Drive | Tracker",
    page_icon="🏠",
    layout="wide"
)

# MODERN HIGH-CONTRAST CSS
st.markdown("""
    <style>
    /* Main container padding */
    .main .block-container { max-width: 1200px; padding-top: 2rem; }
    
    /* FIX FOR READABILITY: Bright Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        color: #3B82F6 !important; /* Bright Electric Blue */
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #94A3B8 !important; /* Muted Slate Label */
    }
    
    /* Header Styling */
    h1 { color: #F8FAFC; font-weight: 800; margin-bottom: 5px; }
    h3 { color: #CBD5E1; font-weight: 700; border-bottom: 1px solid #334155; padding-bottom: 10px; }
    
    /* Modernizing Tabs */
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 600;
        color: #94A3B8;
    }
    .stTabs [aria-selected="true"] {
        color: #3B82F6 !important;
        border-bottom-color: #3B82F6 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏠 97 Plough Drive")
st.markdown("##### Property Purchase & Room Budget Tracker")
st.markdown("---")

# 2. Data Initialization (New key 'v5' to prevent KeyErrors)
if "initialized_v5" not in st.session_state:
    # Admin Fees Data
    st.session_state.admin_df = pd.DataFrame([
        {"Description": "Solicitor / Legal Fees", "Budgeted": 0.0, "Actual": 0.0, "Status": "Pending"},
        {"Description": "Surveyor Fee", "Budgeted": 0.0, "Actual": 0.0, "Status": "Pending"},
        {"Description": "Stamp Duty", "Budgeted": 0.0, "Actual": 0.0, "Status": "Pending"},
        {"Description": "Mortgage Fee", "Budgeted": 0.0, "Actual": 0.0, "Status": "Pending"},
        {"Description": "Removal / Van Hire", "Budgeted": 0.0, "Actual": 0.0, "Status": "Pending"}
    ])
    
    # Room Items Template
    def create_room(items):
        return pd.DataFrame([
            {"Item": item, "Budgeted": 0.0, "Actual": 0.0, "Priority": "Medium", "Status": "Not Started", "Link": ""}
            for item in items
        ])
    
    st.session_state.rooms = {
        "Bedroom": create_room(["Bed Frame", "Mattress", "Wardrobe"]),
        "Living Room": create_room(["Sofa", "TV Stand", "Coffee Table"]),
        "Kitchen": create_room(["Fridge Freezer", "Microwave", "Kettle"]),
        "Bathroom": create_room(["Mirror", "Bath Mat", "Towel Rail"]),
        "Whole Apartment": create_room(["Light Bulbs", "Extension Leads", "Vacuum"])
    }
    st.session_state.initialized_v5 = True

# 3. Tab Layout
tabs = st.tabs(["📊 Dashboard", "⚖️ Admin Fees", "🛏️ Bedroom", "🛋️ Living Room", "🍳 Kitchen", "🛁 Bathroom", "📦 Whole Apt"])

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    summary_list = []
    
    for name, df in st.session_state.rooms.items():
        b = df["Budgeted"].sum()
        a = df["Actual"].sum()
        summary_list.append({"Category": name, "Budgeted": b, "Actual": a, "Variance": b - a})
    
    adm_b = st.session_state.admin_df["Budgeted"].sum()
    adm_a = st.session_state.admin_df["Actual"].sum()
    summary_list.append({"Category": "Admin Fees", "Budgeted": adm_b, "Actual": adm_a, "Variance": adm_b - adm_a})
    
    summary_df = pd.DataFrame(summary_list)
    total_b = summary_df["Budgeted"].sum()
    total_a = summary_df["Actual"].sum()
    total_v = total_b - total_a

    # HIGH VISIBILITY METRICS
    m1, m2, m3 = st.columns(3)
    m1.metric("TOTAL BUDGET", f"£{total_b:,.2f}")
    m2.metric("TOTAL SPENT", f"£{total_a:,.2f}", delta=f"£{total_v:,.2f} Left", delta_color="normal")
    m3.metric("REMAINING FUNDS", f"£{total_v:,.2f}")

    st.markdown("### Cost Distribution")
    chart_data = summary_df.melt(id_vars="Category", value_vars=["Budgeted", "Actual"], var_name="Type", value_name="Amount")
    chart = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X("Type:N", title=None),
        y=alt.Y("Amount:Q", title="Amount (£)"),
        color=alt.Color("Type:N", scale=alt.Scale(range=["#475569", "#3B82F6"]), legend=None),
        column=alt.Column("Category:N", title=None)
    ).properties(width=110, height=300)
    st.altair_chart(chart)

# --- TAB 2: ADMIN FEES ---
with tabs[1]:
    st.markdown("### Professional Fees")
    st.session_state.admin_df = st.data_editor(
        st.session_state.admin_df,
        column_config={
            "Budgeted": st.column_config.NumberColumn("Budget (£)", format="£%.2f"),
            "Actual": st.column_config.NumberColumn("Actual (£)", format="£%.2f"),
            "Status": st.column_config.SelectboxColumn(options=["Pending", "Paid"])
        },
        num_rows="dynamic", use_container_width=True, key="admin_edit_v5"
    )

# --- ROOM TABS ---
room_names = list(st.session_state.rooms.keys())
for i, name in enumerate(room_names, start=2):
    with tabs[i]:
        st.markdown(f"### {name} Purchasing List")
        st.session_state.rooms[name] = st.data_editor(
            st.session_state.rooms[name],
            column_config={
                "Budgeted": st.column_config.NumberColumn("Budget (£)", format="£%.2f"),
                "Actual": st.column_config.NumberColumn("Actual (£)", format="£%.2f"),
                "Priority": st.column_config.SelectboxColumn(options=["High", "Medium", "Low"]),
                "Status": st.column_config.SelectboxColumn(options=["Not Started", "Ordered", "Done"]),
                "Link": st.column_config.LinkColumn("Product Link")
            },
            num_rows="dynamic", use_container_width=True, key=f"edit_{name}_v5"
        )
