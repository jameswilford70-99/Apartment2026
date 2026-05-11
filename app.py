import streamlit as st
import pandas as pd
import os

# Page Configuration
st.set_page_config(page_title="Apartment Purchase Tracker", layout="wide")

# File to store data
DATA_FILE = "apartment_budget.csv"

# Load data function
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=['Item', 'Room', 'Category', 'Priority', 'Cost'])

# Initialize session state
if 'expenses' not in st.session_state:
    st.session_state.expenses = load_data()

st.title("🏠 Apartment Purchase & Moving Tracker")

# --- Sidebar: Data Entry ---
st.sidebar.header("Add New Expense")
with st.sidebar.form("expense_form", clear_on_submit=True):
    item = st.text_input("Item Name (e.g., Removal Van, King Bed)")
    
    room = st.selectbox("Room/Area", [
        "N/A (General)", "Kitchen", "Living Room", "Master Bedroom", 
        "Bathroom", "Hallway/Storage", "Balcony/Outdoor"
    ])
    
    category = st.selectbox("Category", [
        "Acquisition & Logistics", # Moving, Surveys, Fees
        "Furniture", 
        "Appliances", 
        "Renovations", 
        "Utilities & Admin"
    ])
    
    priority = st.select_slider("Priority", options=["Wishlist", "Medium", "Essential"])
    cost = st.number_input("Cost (£)", min_value=0.0, step=10.0)
    
    submit = st.form_submit_button("Add to Tracker")

if submit and item:
    new_row = pd.DataFrame([[item, room, category, priority, cost]], 
                           columns=['Item', 'Room', 'Category', 'Priority', 'Cost'])
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
    # Save to CSV immediately
    st.session_state.expenses.to_csv(DATA_FILE, index=False)
    st.rerun()

# --- Main Dashboard ---
if not st.session_state.expenses.empty:
    # Key Metrics
    total_spend = st.session_state.expenses['Cost'].sum()
    st.metric(label="Total Running Cost", value=f"£{total_spend:,.2f}")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Expense Breakdown")
        # Display the dataframe
        st.dataframe(st.session_state.expenses, use_container_width=True)
        
        if st.button("Delete Last Entry"):
            st.session_state.expenses = st.session_state.expenses[:-1]
            st.session_state.expenses.to_csv(DATA_FILE, index=False)
            st.rerun()

    with col2:
        st.subheader("Spending by Room")
        room_totals = st.session_state.expenses.groupby('Room')['Cost'].sum()
        st.bar_chart(room_totals)

        st.subheader("Spending by Category")
        cat_totals = st.session_state.expenses.groupby('Category')['Cost'].sum()
        st.bar_chart(cat_totals)
else:
    st.info("Your tracker is empty. Use the sidebar to add your first expense (e.g., your moving van or deposit)!")
