import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
page_title="SalesPulse Analytics",
page_icon="📊",
layout="wide"
)

st.title("📊 SalesPulse")
st.subheader("Sales Analytics & Business Intelligence Dashboard")

st.markdown(
"Analyze sales performance, revenue trends, and product categories."
)

# Load sales data from CSV
@st.cache_data
def load_data():
    df = pd.read_csv("data/sales_data.csv")

    # Convert Date column to datetime
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Convert numeric columns
    numeric_columns = ["Quantity", "Sales", "Profit"]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Remove duplicate order IDs
    df = df.drop_duplicates(subset=["Order_ID"])

    # Remove records with missing required values
    df = df.dropna(
        subset=["Order_ID", "Date", "Category", "Sales", "Profit"]
    )

    # Remove invalid numeric records
    df = df[
        (df["Sales"] >= 0)
        & (df["Profit"] >= 0)
        & (df["Quantity"] > 0)
    ]

    return df


df = load_data() 

# Create Month column from Date
df["Month"] = df["Date"].dt.strftime("%B")

# Data Quality Summary
st.subheader("Data Quality Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Records", len(df))

with col2:
    st.metric(
        "Duplicate Orders",
        int(df["Order_ID"].duplicated().sum())
    )

with col3:
    st.metric(
        "Missing Values",
        int(df.isnull().sum().sum())
    )

# Sidebar filters

st.sidebar.header("Dashboard Filters")

selected_categories = st.sidebar.multiselect(
"Select Categories",
options=df["Category"].unique(),
default=df["Category"].unique()
)

filtered_df = df[df["Category"].isin(selected_categories)]

# Calculate KPIs

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_orders = filtered_df["Order_ID"].nunique()

# KPI cards

col1, col2, col3 = st.columns(3)

col1.metric("Total Revenue", f"₹{total_sales:,.0f}")
col2.metric("Total Profit", f"₹{total_profit:,.0f}")
col3.metric("Total Orders", total_orders)

st.divider()

# Monthly sales chart

monthly_sales = (
filtered_df.groupby("Month", as_index=False)["Sales"].sum()
)

month_order = [
"January", "February", "March", "April",
"May", "June", "July", "August",
"September", "October", "November", "December"
]

monthly_sales["Month"] = pd.Categorical(
monthly_sales["Month"],
categories=month_order,
ordered=True
)

monthly_sales = monthly_sales.sort_values("Month")

fig_sales = px.bar(
monthly_sales,
x="Month",
y="Sales",
title="Monthly Revenue",
labels={"Sales": "Revenue (₹)", "Month": "Month"},
text_auto=True
)

st.plotly_chart(fig_sales, width="stretch")

# Category performance chart

category_sales = (
filtered_df.groupby("Category", as_index=False)["Sales"].sum()
)

fig_category = px.pie(
category_sales,
names="Category",
values="Sales",
title="Revenue by Product Category",
hole=0.4
)

col4, col5 = st.columns(2)

with col4:
    st.plotly_chart(fig_category, width="stretch")

with col5:
    st.subheader("Sales Records")
    st.dataframe(filtered_df, width="stretch")

# Download filtered data
csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Sales Report (CSV)",
    data=csv_data,
    file_name="sales_report.csv",
    mime="text/csv"
)

st.caption("SalesPulse | Sales Analytics Dashboard")


