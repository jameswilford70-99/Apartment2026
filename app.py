import streamlit as st
import pandas as pd
import altair as alt

# 1. Page Configuration
st.set_page_config(
    page_title="97 Plough Drive | Terminal",
    page_icon="🏠",
    layout="wide"
)

# Modern UI Styling
st.markdown("""
    <style>
    .main .block-container { max-width: 1200px; padding-top: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 800; color: #1E293B; }
    /* Style headers */
    h1 { color: #0F172A; font-weight: 800; margin-bottom: 0px; }
    h3 { color: #334155; font-weight: 700; border-bottom: 2px solid #F1F5F9; padding-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏠 97 Plough Drive")
st.markdown("##### Property Purchase & Room Budget Tracker")
st.markdown("---")

# 2. Data Initialization (Using clean keys to avoid KeyErrors)
if "initialized_v4" not in st.session_state:
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
    st.session_state.initialized_v4 = True

# 3. UI Navigation
tabs = st.tabs(["📊 Dashboard", "⚖️ Admin Fees", "🛏️ Bedroom", "🛋️ Living Room", "🍳 Kitchen", "🛁 Bathroom", "📦 Whole Apt"])

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    summary_list = []
    
    # Calculate Room Totals
    for name, df in st.session_state.rooms.items():
        b = df["Budgeted"].sum()
        a = df["Actual"].sum()
        summary_list.append({"Category": name, "Budgeted": b, "Actual": a, "Variance": b - a})
    
    # Calculate Admin Totals
    adm_b = st.session_state.admin_df["Budgeted"].sum()
    adm_a = st.session_state.admin_df["Actual"].sum()
    summary_list.append({"Category": "Admin Fees", "Budgeted": adm_b, "Actual": adm_a, "Variance": adm_b - adm_a})
    
    summary_df = pd.DataFrame(summary_list)
    
    # Metrics
    m1, m2, m3 = st.columns(3)
    total_b = summary_df["Budgeted"].sum()
    total_a = summary_df["Actual"].sum()
    m1.metric("Total Budget", f"£{total_b:,.2f}")
    m2.metric("Total Spend", f"£{total_a:,.2f}", delta=f"£{total_b - total_a:,.2f} Left")
    m3.metric("Variance", f"£{total_b - total_a:,.2f}")

    # Bar Chart
    st.markdown("### Budget vs Actual by Room")
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
    st.markdown("### Legal & Transaction Fees")
    st.session_state.admin_df = st.data_editor(
        st.session_state.admin_df,
        column_config={
            "Budgeted": st.column_config.NumberColumn("Budget (£)", format="£%.2f"),
            "Actual": st.column_config.NumberColumn("Actual (£)", format="£%.2f"),
            "Status": st.column_config.SelectboxColumn(options=["Pending", "Paid"])
        },
        num_rows="dynamic", use_container_width=True, key="admin_edit"
    )

# --- ROOM TABS ---
room_names = list(st.session_state.rooms.keys())
for i, name in enumerate(room_names, start=2):
    with tabs[i]:
        st.markdown(f"### {name} Item Tracker")
        st.session_state.rooms[name] = st.data_editor(
            st.session_state.rooms[name],
            column_config={
                "Budgeted": st.column_config.NumberColumn("Budget (£)", format="£%.2f"),
                "Actual": st.column_config.NumberColumn("Actual (£)", format="£%.2f"),
                "Priority": st.column_config.SelectboxColumn(options=["High", "Medium", "Low"]),
                "Status": st.column_config.SelectboxColumn(options=["Not Started", "Ordered", "Done"]),
                "Link": st.column_config.LinkColumn("Product Link")
            },
            num_rows="dynamic", use_container_width=True, key=f"edit_{name}"
        )
