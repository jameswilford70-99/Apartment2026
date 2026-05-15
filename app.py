import streamlit as st
import pandas as pd
import altair as alt

# 1. Page Configuration for a Modern, Premium Feel
st.set_page_config(
    page_title="97 Plough Drive — Budget Terminal",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to inject a clean, modern aesthetic
st.markdown("""
    <style>
    .main .block-container { max-width: 1200px; padding-top: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; color: #1E293B; }
    div[data-testid="stMetricDelta"] { font-size: 1rem; }
    .stTabs [data-baseweb="tab"] { font-size: 1.1rem; font-weight: 600; padding: 0.5rem 1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("🏠 97 Plough Drive")
st.subtitle("Property Purchase & Room Budget Tracker")
st.markdown("---")

# 2. Initialize Session State Data (Pre-populated with your items)
if "initialized" not in st.session_state:
    # Admin Fees Data
    st.session_state.admin_df = pd.DataFrame([
        {"Fee Description": "Solicitor / Legal Fees", "Budgeted Cost": 0.0, "Actual Cost": 0.0, "Status": "Pending", "Notes": ""},
        {"Fee Description": "Surveyor Fee", "Budgeted Cost": 0.0, "Actual Cost": 0.0, "Status": "Pending", "Notes": ""},
        {"Fee Description": "Stamp Duty", "Budgeted Cost": 0.0, "Actual Cost": 0.0, "Status": "Pending", "Notes": ""},
        {"Fee Description": "Mortgage Arrangement Fee", "Budgeted Cost": 0.0, "Actual Cost": 0.0, "Status": "Pending", "Notes": ""},
        {"Fee Description": "Land Registry Fee", "Budgeted Cost": 0.0, "Actual Cost": 0.0, "Status": "Pending", "Notes": ""},
        {"Fee Description": "Removal / Van Hire", "Budgeted Cost": 0.0, "Actual Cost": 0.0, "Status": "Pending", "Notes": ""}
    ])
    
    # Room Items Common Columns Template
    room_template = lambda items: [
        {"Item Name": item, "Budgeted Amount": 0.0, "Actual Cost": 0.0, "Priority": "High" if i < 2 else "Medium", "Status": "Not Started", "Product Link": "", "Notes": ""}
        for i, item in enumerate(items)
    ]
    
    st.session_state.rooms = {
        "Bedroom": pd.DataFrame(room_template(["Bed Frame", "Mattress", "Wardrobe", "Bedside Tables"])),
        "Living Room": pd.DataFrame(room_template(["Sofa", "TV Stand", "Coffee Table", "Armchair"])),
        "Kitchen": pd.DataFrame(room_template(["Fridge Freezer", "Microwave", "Kettle & Toaster"])),
        "Bathroom": pd.DataFrame(room_template(["Mirror", "Bath Mat", "Towel Rail"])),
        "Whole Apartment": pd.DataFrame(room_template(["Light Bulbs", "Extension Leads", "Vacuum Cleaner"]))
    }
    st.session_state.initialized = True

# 3. Define Reusable Data Editor Column Schemes
room_config = {
    "Item Name": st.column_config.TextColumn("Item Name", width="medium", required=True),
    "Budgeted Amount": st.column_config.NumberColumn("Budgeted (£)", min_value=0.0, format="£%.2f"),
    "Actual Cost": st.column_config.NumberColumn("Actual Cost (£)", min_value=0.0, format="£%.2f"),
    "Priority": st.column_config.SelectboxColumn("Priority", options=["High", "Medium", "Low"], default="Medium"),
    "Status": st.column_config.SelectboxColumn("Status", options=["Not Started", "Ordered", "Done"], default="Not Started"),
    "Product Link": st.column_config.LinkColumn("Product Link", placeholder="https://..."),
    "Notes": st.column_config.TextColumn("Notes", width="large")
}

admin_config = {
    "Fee Description": st.column_config.TextColumn("Fee Description", width="medium", required=True),
    "Budgeted Cost": st.column_config.NumberColumn("Budgeted (£)", min_value=0.0, format="£%.2f"),
    "Actual Cost": st.column_config.NumberColumn("Actual Cost (£)", min_value=0.0, format="£%.2f"),
    "Status": st.column_config.SelectboxColumn("Status", options=["Pending", "Paid"], default="Pending"),
    "Notes": st.column_config.TextColumn("Notes", width="large")
}

# 4. App Navigation Tabs
tabs = st.tabs(["📊 Dashboard", "⚖️ Admin Fees", "🛏️ Bedroom", "🛋️ Living Room", "🍳 Kitchen", "🛁 Bathroom", "🏠 Whole Apartment"])

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    # Dynamic calculations aggregating edits across all components
    summary_data = []
    
    # Process Rooms
    for room_name, df in st.session_state.rooms.items():
        b_sum = df["Budgeted Amount"].sum()
        a_sum = df["Actual Cost"].sum()
        summary_data.append({"Category": room_name, "Budgeted": b_sum, "Actual": a_sum, "Variance": b_sum - a_sum})
        
    # Process Admin Fees
    adm_b = st.session_state.admin_df["Budgeted Cost"].sum()
    adm_a = st.session_state.admin_df["Actual Cost"].sum()
    summary_data.append({"Category": "Admin Fees", "Budgeted": adm_b, "Actual": adm_a, "Variance": adm_b - adm_a})
    
    summary_df = pd.DataFrame(summary_data)
    
    total_budget = summary_df["Budgeted"].sum()
    total_actual = summary_df["Actual"].sum()
    total_variance = total_budget - total_actual

    # Top Level High-Level KPIs
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Budget Allocated", f"£{total_budget:,.2f}")
    kpi2.metric("Total Actual Expenditure", f"£{total_actual:,.2f}", delta=f"£{total_variance:,.2f} remaining", delta_color="normal")
    kpi3.metric("Net Variance Portfolio", f"£{total_variance:,.2f}", help="Positive indicates under budget, negative indicates over budget.")
    
    st.markdown("### Cost Allocation Profile")
    
    # Generate Side-by-Side Modern Bar Chart using Altair
    chart_data = summary_df.melt(id_vars=["Category"], value_vars=["Budgeted", "Actual"], var_name="Type", value_name="Amount")
    
    chart = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X("Type:N", title=None, axis=alt.Axis(labels=True, ticks=False)),
        y=alt.Y("Amount:Q", title="Amount (£)", axis=alt.Axis(format="£~s")),
        color=alt.Color("Type:N", scale=alt.Scale(domain=["Budgeted", "Actual"], range=["#475569", "#3B82F6"]), legend=None),
        column=alt.Column("Category:N", title=None, header=alt.Header(labelOrient='bottom', labelPadding=10))
    ).properties(width=130, height=300).configure_view(stroke='transparent')
    
    st.altair_chart(chart, use_container_width=True)
    
    # Summary Breakdown Dataframe Table View
    st.markdown("### Detailed Summary Matrix")
    st.dataframe(
        summary_df,
        column_config={
            "Category": st.column_config.TextColumn("Category / Room"),
            "Budgeted": st.column_config.NumberColumn("Total Budgeted", format="£%.2f"),
            "Actual": st.column_config.NumberColumn("Total Actual", format="£%.2f"),
            "Variance": st.column_config.NumberColumn("Net Variance", format="£%.2f")
        },
        use_container_width=True,
        hide_index=True
    )

# --- TAB 2: ADMIN FEES ---
with tabs[1]:
    st.markdown("### Professional & Transaction Fees Log")
    edited_admin = st.data_editor(
        st.session_state.admin_df,
        column_config=admin_config,
        num_rows="dynamic",
        use_container_width=True,
        key="admin_editor"
    )
    # Calculate variances inline and save updates back to session state
    edited_admin["Variance"] = edited_admin["Budgeted Cost"] - edited_admin["Actual Cost"]
    st.session_state.admin_df = edited_admin

# --- TABS 3-7: ROOM PURSUITS ---
for idx, room_name in enumerate(st.session_state.rooms.keys(), start=2):
    with tabs[idx]:
        st.markdown(f"### {room_name} Procurement List")
        
        current_room_df = st.session_state.rooms[room_name]
        edited_room = st.data_editor(
            current_room_df,
            column_config=room_config,
            num_rows="dynamic",
            use_container_width=True,
            key=f"editor_{room_name}"
        )
        # Calculate individual item variances and save back
        edited_room["Variance"] = edited_room["Budgeted Amount"] - edited_room["Actual Cost"]
        st.session_state.rooms[room_name] = edited_room
