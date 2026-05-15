import streamlit as st
import pandas as pd
import altair as alt

# 1. Page Configuration
st.set_page_config(
    page_title="97 Plough Drive | Terminal",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a modern, high-contrast look
st.markdown("""
    <style>
    .main .block-container { max-width: 1200px; padding-top: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 2.2rem; font-weight: 800; color: #1E293B; }
    div[data-testid="stMetricDelta"] { font-size: 1rem; }
    .stTabs [data-baseweb="tab"] { font-size: 1rem; font-weight: 600; padding: 0.5rem 1rem; }
    /* Style headers */
    h1 { color: #0F172A; font-weight: 800; }
    h3 { color: #334155; font-weight: 700; border-bottom: 2px solid #F1F5F9; padding-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏠 97 Plough Drive")
st.markdown("##### Property Purchase & Room Budget Tracker")
st.markdown("---")

# 2. Data Initialization (Session State)
if "initialized" not in st.session_state:
    # Template for admin fees
    st.session_state.admin_df = pd.DataFrame([
        {"Fee Description": "Solicitor / Legal Fees", "Budgeted (£)": 0.0, "Actual (£)": 0.0, "Status": "Pending", "Notes": ""},
        {"Fee Description": "Surveyor Fee", "Budgeted (£)": 0.0, "Actual (£)": 0.0, "Status": "Pending", "Notes": ""},
        {"Fee Description": "Stamp Duty", "Budgeted (£)": 0.0, "Actual (£)": 0.0, "Status": "Pending", "Notes": ""},
        {"Fee Description": "Mortgage Arrangement Fee", "Budgeted (£)": 0.0, "Actual (£)": 0.0, "Status": "Pending", "Notes": ""},
        {"Fee Description": "Land Registry Fee", "Budgeted (£)": 0.0, "Actual (£)": 0.0, "Status": "Pending", "Notes": ""},
        {"Fee Description": "Removal / Van Hire", "Budgeted (£)": 0.0, "Actual (£)": 0.0, "Status": "Pending", "Notes": ""}
    ])
    
    # Template for room items
    room_template = lambda items: [
        {"Item Name": item, "Budgeted (£)": 0.0, "Actual (£)": 0.0, "Priority": "High" if i < 2 else "Medium", "Status": "Not Started", "Product Link": "", "Notes": ""}
        for i, item in enumerate(items)
    ]
    
    st.session_state.rooms = {
        "Bedroom": pd.DataFrame(room_template(["Bed Frame", "Mattress", "Wardrobe"])),
        "Living Room": pd.DataFrame(room_template(["Sofa", "TV Stand", "Coffee Table"])),
        "Kitchen": pd.DataFrame(room_template(["Fridge Freezer", "Microwave", "Kettle"])),
        "Bathroom": pd.DataFrame(room_template(["Mirror", "Bath Mat", "Towel Rail"])),
        "Whole Apartment": pd.DataFrame(room_template(["Light Bulbs", "Extension Leads", "Vacuum Cleaner"]))
    }
    st.session_state.initialized = True

# 3. UI Tabs Configuration
tabs = st.tabs(["📊 Dashboard", "⚖️ Admin Fees", "🛏️ Bedroom", "🛋️ Living Room", "🍳 Kitchen", "🛁 Bathroom", "📦 Whole Apartment"])

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    # Aggregate data from all sessions
    summary_data = []
    
    for room_name, df in st.session_state.rooms.items():
        b_sum = df["Budgeted (£)"].sum()
        a_sum = df["Actual (£)"].sum()
        summary_data.append({"Category": room_name, "Budgeted": b_sum, "Actual": a_sum, "Variance": b_sum - a_sum})
        
    adm_b = st.session_state.admin_df["Budgeted (£)"].sum()
    adm_a = st.session_state.admin_df["Actual (£)"].sum()
    summary_data.append({"Category": "Admin Fees", "Budgeted": adm_b, "Actual": adm_a, "Variance": adm_b - adm_a})
    
    summary_df = pd.DataFrame(summary_data)
    total_budget = summary_df["Budgeted"].sum()
    total_actual = summary_df["Actual"].sum()
    total_variance = total_budget - total_actual

    # KPI Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Budget", f"£{total_budget:,.2f}")
    m2.metric("Total Spend", f"£{total_actual:,.2f}", delta=f"£{total_variance:,.2f} Left", delta_color="normal")
    m3.metric("Net Variance", f"£{total_variance:,.2f}", help="Remaining funds based on budget estimates.")
    
    st.markdown("### Expense Comparison")
    
    # Modern Bar Chart
    chart_data = summary_df.melt(id_vars=["Category"], value_vars=["Budgeted", "Actual"], var_name="Type", value_name="Amount")
    chart = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X("Type:N", title=None, axis=alt.Axis(labels=True, ticks=False)),
        y=alt.Y("Amount:Q", title="Amount (£)", axis=alt.Axis(format="£~s")),
        color=alt.Color("Type:N", scale=alt.Scale(domain=["Budgeted", "Actual"], range=["#475569", "#3B82F6"]), legend=None),
        column=alt.Column("Category:N", title=None, header=alt.Header(labelOrient='bottom', labelPadding=10))
    ).properties(width=120, height=300).configure_view(stroke='transparent')
    
    st.altair_chart(chart, use_container_width=False)
    
    st.markdown("### Detailed Summary Matrix")
    st.dataframe(summary_df, use_container_width=True, hide_index=True, column_config={
        "Budgeted": st.column_config.NumberColumn(format="£%.2f"),
        "Actual": st.column_config.NumberColumn(format="£%.2f"),
        "Variance": st.column_config.NumberColumn(format="£%.2f")
    })

# --- TAB 2: ADMIN FEES ---
with tabs[1]:
    st.markdown("### ⚖️ Legal & Admin Fee Log")
    edited_admin = st.data_editor(
        st.session_state.admin_df,
        column_config={
            "Budgeted (£)": st.column_config.NumberColumn(format="£%.2f"),
            "Actual (£)": st.column_config.NumberColumn(format="£%.2f"),
            "Status": st.column_config.SelectboxColumn(options=["Pending", "Paid"])
        },
        num_rows="dynamic",
        use_container_width=True,
        key="admin_editor"
    )
    st.session_state.admin_df = edited_admin

# --- TABS 3-7: ROOM TABLES ---
room_keys = list(st.session_state.rooms.keys())
for idx, room_name in enumerate(room_keys, start=2):
    with tabs[idx]:
        st.markdown(f"### 📦 {room_name} Purchasing List")
        
        edited_room = st.data_editor(
            st.session_state.rooms[room_name],
            column_config={
                "Budgeted (£)": st.column_config.NumberColumn(format="£%.2f", min_value=0),
                "Actual (£)": st.column_config.NumberColumn(format="£%.2f", min_value=0),
                "Priority": st.column_config.SelectboxColumn(options=["High", "Medium", "Low"]),
                "Status": st.column_config.SelectboxColumn(options=["Not Started", "Ordered", "Done"]),
                "Product Link": st.column_config.LinkColumn("Product Link") # Fixed: No placeholder
            },
            num_rows="dynamic",
            use_container_width=True,
            key=f"editor_{room_name}"
        )
        st.session_state.rooms[room_name] = edited_room
