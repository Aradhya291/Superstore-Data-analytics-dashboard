import streamlit as st
import pandas as pd
import plotly.express as px

# Title
st.title("📊 Superstore Sales Dashboard")

# Load Data
df = pd.read_excel("C:/Users/HP/Desktop/data analytics mini project/Sample - Superstore.xlsx")

# Convert date column
df['Order Date'] = pd.to_datetime(df['Order Date'])

# Sidebar Filters
st.sidebar.header("🔍 Filters")

region = st.sidebar.multiselect(
    "Select Region",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

category = st.sidebar.multiselect(
    "Select Category",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['Order Date'].min(), df['Order Date'].max()]
)

# Filter Data
filtered_df = df[
    (df['Region'].isin(region)) &
    (df['Category'].isin(category)) &
    (df['Order Date'] >= pd.to_datetime(date_range[0])) &
    (df['Order Date'] <= pd.to_datetime(date_range[1]))
]

# KPIs
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
total_orders = filtered_df.shape[0]

st.metric("💰 Total Sales", f"${total_sales:,.2f}")
st.metric("📈 Total Profit", f"${total_profit:,.2f}")
st.metric("📦 Total Orders", total_orders)

# Sales Over Time
sales_time = filtered_df.groupby('Order Date')['Sales'].sum().reset_index()
fig1 = px.line(sales_time, x='Order Date', y='Sales', title="Sales Over Time")
st.plotly_chart(fig1)

# Sales by Category
fig2 = px.bar(filtered_df, x='Category', y='Sales', title="Sales by Category")
st.plotly_chart(fig2)

# Sales by Region
fig3 = px.pie(filtered_df, names='Region', values='Sales', title="Sales by Region")
st.plotly_chart(fig3)

# Profit vs Discount
fig4 = px.scatter(filtered_df, x='Discount', y='Profit',
                  title="Profit vs Discount",
                  color='Category')
st.plotly_chart(fig4)

# Top Products
top_products = filtered_df.groupby('Product Name')['Sales'].sum().nlargest(10).reset_index()
fig5 = px.bar(top_products, x='Sales', y='Product Name',
              orientation='h', title="Top 10 Products")
st.plotly_chart(fig5)