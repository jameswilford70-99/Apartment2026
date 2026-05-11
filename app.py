import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURATION ---
st.set_page_config(page_title="Apartment Tracker", layout="wide")

# Google Sheets Auth setup
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("secrets.json", scopes=scopes)
client = gspread.authorize(creds)

# Open the Google Sheet
SHEET_NAME = "Apartment_Budget"
sheet = client.open(SHEET_NAME).sheet1

# --- HELPER FUNCTIONS ---
def load_data():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    if df.empty:
        # Create empty dataframe with columns if sheet is totally blank below headers
        df = pd.DataFrame(columns=["Item", "Category", "Priority", "Status", "Planned_Cost", "Actual_Cost"])
    else:
        # Ensure costs are numeric
        df['Planned_Cost'] = pd.to_numeric(df['Planned_Cost'], errors='coerce').fillna(0)
        df['Actual_Cost'] = pd.to_numeric(df['Actual_Cost'], errors='coerce').fillna(0)
    return df

def add_item_to_sheet(item_data):
    # Append a new row to the Google Sheet
    sheet.append_row(item_data)

# --- MAIN APP ---
st.title("🏗️ New Apartment Budget & Prep Tracker")

df = load_data()

# --- TOP LEVEL METRICS ---
st.markdown("### Budget Overview")
col1, col2, col3, col4 = st.columns(4)

total_planned = df['Planned_Cost'].sum()
total_actual = df['Actual_Cost'].sum()
variance = total_planned - total_actual

# Calculate how much is allocated to the Sofa specifically
sofa_data = df[df['Item'].str.contains('Sofa', case=False, na=False)]
sofa_planned = sofa_data['Planned_Cost'].sum() if not sofa_data.empty else 0

col1.metric("Total Planned Cost", f"£{total_planned:,.2f}")
col2.metric("Actual Spend So Far", f"£{total_actual:,.2f}")
col3.metric("Current Variance", f"£{variance:,.2f}", delta=f"£{variance:,.2f}", delta_color="normal")
col4.metric("Sofa Allocation", f"£{sofa_planned:,.2f}")

st.divider()

# --- INPUT FORM ---
st.sidebar.header("Add New Item / Expense")
with st.sidebar.form("add_item_form", clear_on_submit=True):
    item_name = st.text_input("Item / Expense Name", placeholder="e.g., Solicitor Fees, Corner Sofa...")
    
    category = st.selectbox("Category", [
        "Buying Costs (Solicitor, Stamp Duty, Survey)", 
        "Living Room", 
        "Kitchen", 
        "Bedroom", 
        "Bathroom",
        "Luna's Corner",
        "Misc / Decor"
    ])
    
    priority = st.selectbox("Priority", ["Must-Have", "High", "Medium", "Low (Maybe Later)"])
    
    status = st.selectbox("Status", ["Researching", "Budgeted", "Ordered", "Paid & Delivered"])
    
    planned_cost = st.number_input("Planned Cost (£)", min_value=0.0, step=10.0)
    actual_cost = st.number_input("Actual Cost (£) - Leave 0 if not paid yet", min_value=0.0, step=10.0)
    
    submit_button = st.form_submit_button("Add to Tracker")
    
    if submit_button and item_name:
        new_row = [item_name, category, priority, status, planned_cost, actual_cost]
        add_item_to_sheet(new_row)
        st.success(f"Added {item_name} to the tracker!")
        st.rerun()

# --- DATA VIEW & FILTERS ---
st.markdown("### Expense Breakdown")

# Filter controls
f_col1, f_col2 = st.columns(2)
cat_filter = f_col1.multiselect("Filter by Category", options=df['Category'].unique(), default=df['Category'].unique())
stat_filter = f_col2.multiselect("Filter by Status", options=df['Status'].unique(), default=df['Status'].unique())

filtered_df = df[(df['Category'].isin(cat_filter)) & (df['Status'].isin(stat_filter))]

# Calculate difference column for display
filtered_df['Difference'] = filtered_df['Planned_Cost'] - filtered_df['Actual_Cost']

# Display the styled dataframe
st.dataframe(
    filtered_df.style.format({
        'Planned_Cost': '£{:,.2f}'.format,
        'Actual_Cost': '£{:,.2f}'.format,
        'Difference': '£{:,.2f}'.format
    }),
    use_container_width=True,
    hide_index=True
)
