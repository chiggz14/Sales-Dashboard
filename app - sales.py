
import streamlit as st
import pandas as pd

# --- CONFIG ---
CSV_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/your_file.csv"

st.set_page_config(layout="wide")
st.title("📊 Sales Dashboard")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# --- FILTERS ---
st.sidebar.header("Filters")

category_filter = st.sidebar.multiselect(
    "Category",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

name_filter = st.sidebar.multiselect(
    "Name",
    options=df["Name"].unique(),
    default=df["Name"].unique()
)

filtered_df = df[
    (df["Category"].isin(category_filter)) &
    (df["Name"].isin(name_filter))
]

# --- DISPLAY TABLE ---
st.subheader("📋 Sales Data")
edited_df = st.data_editor(filtered_df, num_rows="dynamic")

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

        new_row = {
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
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        st.success("Entry added! (Reminder: push changes back to GitHub manually or automate)")

# --- EDITING NOTE ---
st.subheader("✏️ Edit Existing Data")
st.info("You can edit data directly in the table above.")

# --- KPIs ---
st.subheader("📈 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue", f"£{filtered_df['Sold For'].sum():,.2f}")
col2.metric("Total Profit", f"£{filtered_df['Profit'].sum():,.2f}")
col3.metric("Avg ROI", f"{filtered_df['ROI'].mean():.2f}%")
col4.metric("Items Sold", len(filtered_df))
