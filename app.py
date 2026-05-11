import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Home Purchase Tracker", layout="wide")

st.title("🏠 New Apartment Budget Tracker")
st.write("Keep track of your spending and upcoming costs in one place.")

# Initialize session state for data storage
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['Item', 'Category', 'Priority', 'Cost'])

# --- Sidebar: Data Entry ---
st.sidebar.header("Add New Expense")
with st.sidebar.form("expense_form", clear_on_submit=True):
    item = st.text_input("Item Name (e.g., Solicitor Fees, Sofa)")
    category = st.selectbox("Category", ["Purchase Costs", "Renovations", "Furniture", "Utilities/Admin", "Other"])
    priority = st.select_slider("Priority", options=["Wishlist", "Medium", "Essential"])
    cost = st.number_input("Estimated/Actual Cost (£)", min_value=0.0, step=10.0)
    
    submit = st.form_submit_button("Add to Tracker")

if submit and item:
    new_data = pd.DataFrame([[item, category, priority, cost]], columns=['Item', 'Category', 'Priority', 'Cost'])
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_data], ignore_index=True)

# --- Main Dashboard ---
if not st.session_state.expenses.empty:
    # Key Metrics
    total_spend = st.session_state.expenses['Cost'].sum()
    st.metric(label="Total Running Cost", value=f"£{total_spend:,.2f}")

    # Layout: Table and Charts
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Expense Log")
        st.dataframe(st.session_state.expenses, use_container_width=True)
        
        if st.button("Clear All Data"):
            st.session_state.expenses = pd.DataFrame(columns=['Item', 'Category', 'Priority', 'Cost'])
            st.rerun()

    with col2:
        st.subheader("Costs by Category")
        cat_totals = st.session_state.expenses.groupby('Category')['Cost'].sum()
        st.bar_chart(cat_totals)

        st.subheader("Priority Breakdown")
        priority_totals = st.session_state.expenses.groupby('Priority')['Cost'].sum()
        st.pie_chart(priority_totals)
else:
    st.info("Your tracker is empty. Use the sidebar to add your first expense!")
