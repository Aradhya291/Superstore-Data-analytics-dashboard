import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Superstore Dashboard", layout="wide")

# ------------------ CUSTOM UI ------------------
st.markdown("""
    <style>
    body {background-color: #0E1117;}
    .main {background-color: #0E1117;}
    h1 {color: #00BFFF;}
    .css-1d391kg {background-color: #111;}
    </style>
""", unsafe_allow_html=True)

# ------------------ TITLE ------------------
st.title("📊 Superstore Advanced Analytics Dashboard")

# ------------------ LOAD DATA ------------------
df = pd.read_excel("Sample - Superstore.xlsx")
df['Order Date'] = pd.to_datetime(df['Order Date'])

# ------------------ SIDEBAR ------------------
st.sidebar.header("🔍 Advanced Filters")

region = st.sidebar.multiselect("Region", df['Region'].unique(), default=df['Region'].unique())
category = st.sidebar.multiselect("Category", df['Category'].unique(), default=df['Category'].unique())
segment = st.sidebar.multiselect("Segment", df['Segment'].unique(), default=df['Segment'].unique())

date_range = st.sidebar.date_input(
    "Date Range",
    [df['Order Date'].min(), df['Order Date'].max()]
)

discount_range = st.sidebar.slider(
    "Discount Range",
    float(df['Discount'].min()),
    float(df['Discount'].max()),
    (float(df['Discount'].min()), float(df['Discount'].max()))
)

# Search box
search_product = st.sidebar.text_input("🔎 Search Product")

# ------------------ FILTER DATA ------------------
filtered_df = df[
    (df['Region'].isin(region)) &
    (df['Category'].isin(category)) &
    (df['Segment'].isin(segment)) &
    (df['Discount'].between(discount_range[0], discount_range[1])) &
    (df['Order Date'] >= pd.to_datetime(date_range[0])) &
    (df['Order Date'] <= pd.to_datetime(date_range[1]))
]

if search_product:
    filtered_df = filtered_df[
        filtered_df['Product Name'].str.contains(search_product, case=False)
    ]

# ------------------ KPIs ------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Sales", f"${filtered_df['Sales'].sum():,.0f}")
col2.metric("📈 Profit", f"${filtered_df['Profit'].sum():,.0f}")
col3.metric("📦 Orders", filtered_df.shape[0])
col4.metric("📊 Avg Discount", f"{filtered_df['Discount'].mean():.2f}")

# ------------------ DOWNLOAD BUTTON ------------------
st.download_button(
    "📥 Download Filtered Data",
    filtered_df.to_csv(index=False),
    file_name="filtered_data.csv",
    mime="text/csv"
)

# ------------------ CHARTS ------------------

# Row 1
col5, col6 = st.columns(2)

# Sales Over Time
sales_time = filtered_df.groupby('Order Date')['Sales'].sum().reset_index()
fig1 = px.line(sales_time, x='Order Date', y='Sales',
               title="📈 Sales Over Time", markers=True)
col5.plotly_chart(fig1, use_container_width=True)

# Sales by Category
fig2 = px.bar(filtered_df, x='Category', y='Sales',
              color='Category', title="📊 Sales by Category")
col6.plotly_chart(fig2, use_container_width=True)

# Row 2
col7, col8 = st.columns(2)

# Region Pie
fig3 = px.pie(filtered_df, names='Region', values='Sales',
              title="🌍 Sales by Region", hole=0.4)
col7.plotly_chart(fig3, use_container_width=True)

# Profit vs Discount
fig4 = px.scatter(filtered_df, x='Discount', y='Profit',
                  color='Category', size='Sales',
                  title="📉 Profit vs Discount")
col8.plotly_chart(fig4, use_container_width=True)

# Row 3
col9, col10 = st.columns(2)

# Top Products
top_products = filtered_df.groupby('Product Name')['Sales'].sum().nlargest(10).reset_index()
fig5 = px.bar(top_products, x='Sales', y='Product Name',
              orientation='h', title="🏆 Top 10 Products")
col9.plotly_chart(fig5, use_container_width=True)

# Sub-Category Analysis
fig6 = px.sunburst(filtered_df,
                   path=['Category', 'Sub-Category'],
                   values='Sales',
                   title="📦 Category → Sub-Category")
col10.plotly_chart(fig6, use_container_width=True)

# ------------------ DATA PREVIEW ------------------
st.subheader("📄 Filtered Data Preview")
st.dataframe(filtered_df)