import streamlit as st
import pandas as pd
import os

# Page Configuration
st.set_page_config(page_title="Apartment Budget Tracker", layout="wide")

DATA_FILE = "apartment_budget.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except:
            return pd.DataFrame(columns=['Item', 'Room', 'Category', 'Priority', 'Cost'])
    return pd.DataFrame(columns=['Item', 'Room', 'Category', 'Priority', 'Cost'])

if 'expenses' not in st.session_state:
    st.session_state.expenses = load_data()

st.title("🏠 Apartment Purchase & Moving Tracker")

# --- Sidebar: Data Entry ---
st.sidebar.header("Add New Expense")
room_options = ["N/A (General)", "Kitchen", "Living Room", "Master Bedroom", "Bathroom", "Hallway/Storage", "Balcony/Outdoor"]
category_options = ["Acquisition & Logistics", "Furniture", "Appliances", "Renovations", "Utilities & Admin"]

with st.sidebar.form("expense_form", clear_on_submit=True):
    item = st.text_input("Item Name")
    room = st.selectbox("Room/Area", room_options)
    category = st.selectbox("Category", category_options)
    priority = st.select_slider("Priority", options=["Wishlist", "Medium", "Essential"])
    cost = st.number_input("Cost (£)", min_value=0.0, step=10.0)
    submit = st.form_submit_button("Add to Tracker")

if submit and item:
    new_row = pd.DataFrame([[item, room, category, priority, cost]], columns=['Item', 'Room', 'Category', 'Priority', 'Cost'])
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
    st.session_state.expenses.to_csv(DATA_FILE, index=False)
    st.rerun()

# --- Main Dashboard ---
if not st.session_state.expenses.empty:
    # 1. Total Metric
    total_spend = st.session_state.expenses['Cost'].sum()
    st.metric(label="Total Project Cost", value=f"£{total_spend:,.2f}")
    
    st.write("---")
    
    # 2. Room Breakdown Section
    st.subheader("Room-by-Room Totals")
    room_data = st.session_state.expenses.groupby('Room')['Cost'].sum()
    
    # Display room metrics in a grid
    r_cols = st.columns(4) 
    for i, (r_name, r_total) in enumerate(room_data.items()):
        r_cols[i % 4].metric(label=r_name, value=f"£{r_total:,.0f}")
    
    st.write("---")

    # 3. Filtering and Detailed View
    col_table, col_viz = st.columns([2, 1])
    
    with col_table:
        st.subheader("Detailed Expense Log")
        filter_room = st.selectbox("Filter view by Room:", ["All"] + room_options)
        
        display_df = st.session_state.expenses
        if filter_room != "All":
            display_df = display_df[display_df['Room'] == filter_room]
            
        st.dataframe(display_df, use_container_width=True)
        
        if st.button("Delete Last Entry"):
            if len(st.session_state.expenses) > 0:
                st.session_state.expenses = st.session_state.expenses[:-1]
                st.session_state.expenses.to_csv(DATA_FILE, index=False)
                st.rerun()

    with col_viz:
        st.subheader("Spending by Category")
        cat_data = st.session_state.expenses.groupby('Category')['Cost'].sum()
        st.bar_chart(cat_data)
        
        st.subheader("Spending by Priority")
        prio_data = st.session_state.expenses.groupby('Priority')['Cost'].sum()
        st.bar_chart(prio_data) # Swapped from pie_chart to bar_chart to fix the error
else:
    st.info("Your tracker is empty. Use the sidebar to add your first expense!")
