import streamlit as st
import pandas as pd
import os

# --- CONFIG ---
FILE_PATH = "sales dashboard.csv"

st.set_page_config(layout="wide")
st.title("📊 Sales Dashboard")

# --- CALCULATION FUNCTION ---
def recalculate_missing(df):
    df = df.copy()

    # Clean column names
    df.columns = df.columns.str.strip()

    # Ensure numeric columns are numeric
    numeric_cols = [
        "Bought For", "Sold For", "Fees",
        "Profit", "Profit Margin", "ROI", "Net Profit"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Profit
    df.loc[df["Profit"].isna(), "Profit"] = (
        df["Sold For"] - df["Bought For"]
    )

    # Net Profit
    df.loc[df["Net Profit"].isna(), "Net Profit"] = (
        df["Profit"] - df["Fees"]
    )

    # Profit Margin (%)
    df.loc[df["Profit Margin"].isna(), "Profit Margin"] = (
        (df["Profit"] / df["Sold For"]) * 100
    )

    # ROI (%)
    df.loc[df["ROI"].isna(), "ROI"] = (
        (df["Profit"] / df["Bought For"]) * 100
    )

    return df


# --- LOAD DATA ---
def load_data():
    if os.path.exists(FILE_PATH):
        df = pd.read_csv(FILE_PATH)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = recalculate_missing(df)
    else:
        df = pd.DataFrame(columns=[
            "Date", "Name", "Category", "Bought For", "Sold For",
            "Profit", "Profit Margin", "ROI", "Fees", "Net Profit"
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
st.subheader("📋 Sales Data")

edited_df = st.data_editor(
    filtered_df,
    use_container_width=True,
    num_rows="dynamic",
    disabled=["Profit", "Profit Margin", "ROI", "Net Profit"]
)

# Recalculate after edits
edited_df = recalculate_missing(edited_df)

# --- SAVE BUTTON ---
if st.button("💾 Save Changes"):
    edited_df.to_csv(FILE_PATH, index=False)
    st.success("Changes saved!")

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

        st.success("New entry added!")

# --- METRICS ---
st.subheader("📈 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Revenue", f"£{filtered_df['Sold For'].sum():,.2f}")
col2.metric("Profit", f"£{filtered_df['Profit'].sum():,.2f}")
col3.metric("Avg ROI", f"{filtered_df['ROI'].mean():.1f}%")
col4.metric("Items", len(filtered_df))

# --- CHARTS ---
st.subheader("📊 Insights")

st.write("Profit by Category")
st.bar_chart(filtered_df.groupby("Category")["Profit"].sum())

st.write("Profit Over Time")
st.line_chart(filtered_df.groupby("Date")["Profit"].sum())
