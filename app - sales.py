import streamlit as st
import pandas as pd
import os

FILE_PATH = "sales_data.csv"

st.set_page_config(layout="wide")
st.title("📊 Sales Dashboard")

# --- LOAD DATA ---
def load_data():
    if os.path.exists(FILE_PATH):
        df = pd.read_csv(FILE_PATH)
        df["Date"] = pd.to_datetime(df["Date"])
    else:
        df = pd.DataFrame(columns=[
            "Date","Name","Category","Bought For","Sold For",
            "Profit","Profit Margin","ROI","Fees","Net Profit"
        ])
    return df

df = load_data()

# --- FILTERS ---
st.sidebar.header("Filters")

category_filter = st.sidebar.multiselect(
    "Category",
    options=df["Category"].dropna().unique(),
    default=df["Category"].dropna().unique()
)

name_filter = st.sidebar.multiselect(
    "Name",
    options=df["Name"].dropna().unique(),
    default=df["Name"].dropna().unique()
)

filtered_df = df[
    (df["Category"].isin(category_filter)) &
    (df["Name"].isin(name_filter))
]

# --- EDITABLE TABLE ---
st.subheader("📋 Sales Data (Editable)")

edited_df = st.data_editor(
    filtered_df,
    num_rows="dynamic",
    use_container_width=True
)

# SAVE BUTTON FOR EDITS
if st.button("💾 Save Changes"):
    edited_df.to_csv(FILE_PATH, index=False)
    st.success("Changes saved locally!")

# --- ADD NEW ENTRY ---
st.subheader("➕ Add New Entry")

with st.form("new_entry_form"):
    col1, col2, col3 = st.columns(3)
    
    date = col1.date_input("Date")
    name = col2.text_input("Name")
    category = col3.text_input("Category")

    col4, col5, col6 = st.columns(3)

    bought_for = col4.number_input("Bought For", min_value=0.0)
    sold_for = col5.number_input("Sold For", min_value=0.0)
    fees = col6.number_input("Fees", min_value=0.0)

    submitted = st.form_submit_button("Add Entry")

    if submitted:
        profit = sold_for - bought_for
        net_profit = profit - fees
        profit_margin = (profit / sold_for) * 100 if sold_for != 0 else 0
        roi = (profit / bought_for) * 100 if bought_for != 0 else 0

        new_row = pd.DataFrame([{
            "Date": date,
            "Name": name,
            "Category": category,
            "Bought For": bought_for,
            "Sold For": sold_for,
            "Profit": profit,
            "Profit Margin": profit_margin,
            "ROI": roi,
            "Fees": fees,
            "Net Profit": net_profit
        }])

        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(FILE_PATH, index=False)

        st.success("Entry added!")

# --- KPI DASHBOARD ---
st.subheader("📈 Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Revenue", f"£{filtered_df['Sold For'].sum():,.2f}")
col2.metric("Profit", f"£{filtered_df['Profit'].sum():,.2f}")
col3.metric("Avg ROI", f"{filtered_df['ROI'].mean():.1f}%")
col4.metric("Items", len(filtered_df))
