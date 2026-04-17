import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Superstore Advanced Dashboard", layout="wide")

# ------------------ CUSTOM UI ------------------
st.markdown("""
    <style>
    body {background-color: #0E1117;}
    .main {background-color: #0E1117;}
    h1 {color: #00BFFF;}
    </style>
""", unsafe_allow_html=True)

# ------------------ TITLE ------------------
st.title("📊 Superstore Advanced Analytics Dashboard with Maps")

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

filtered_df = filtered_df.copy()

# ------------------ KPIs ------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Sales", f"${filtered_df['Sales'].sum():,.0f}")
col2.metric("📈 Profit", f"${filtered_df['Profit'].sum():,.0f}")
col3.metric("📦 Orders", filtered_df.shape[0])
col4.metric("📊 Avg Discount", f"{filtered_df['Discount'].mean():.2f}")

# ------------------ DOWNLOAD ------------------
st.download_button(
    "📥 Download Filtered Data",
    filtered_df.to_csv(index=False),
    file_name="filtered_data.csv",
    mime="text/csv"
)

# ------------------ CHARTS ------------------

# Row 1
col5, col6 = st.columns(2)

sales_time = filtered_df.groupby('Order Date')['Sales'].sum().reset_index()
fig1 = px.line(sales_time, x='Order Date', y='Sales',
               title="📈 Sales Over Time", markers=True)
col5.plotly_chart(fig1, use_container_width=True)

fig2 = px.bar(filtered_df, x='Category', y='Sales',
              color='Category', title="📊 Sales by Category")
col6.plotly_chart(fig2, use_container_width=True)

# Row 2
col7, col8 = st.columns(2)

fig3 = px.pie(filtered_df, names='Region', values='Sales',
              title="🌍 Sales by Region", hole=0.4)
col7.plotly_chart(fig3, use_container_width=True)

fig4 = px.scatter(filtered_df, x='Discount', y='Profit',
                  color='Category', size='Sales',
                  title="📉 Profit vs Discount")
col8.plotly_chart(fig4, use_container_width=True)

# Row 3 (ONLY Top Products now)
st.subheader("🏆 Top Products")

top_products = filtered_df.groupby('Product Name')['Sales'].sum().nlargest(10).reset_index()
fig5 = px.bar(top_products, x='Sales', y='Product Name',
              orientation='h', title="Top 10 Products")

st.plotly_chart(fig5, use_container_width=True)

# ------------------ MAP SECTION ------------------

st.subheader("🗺️ Sales Map Analysis")

state_coords = {
    "California": (36.7783, -119.4179),
    "Texas": (31.9686, -99.9018),
    "New York": (40.7128, -74.0060),
    "Washington": (47.7511, -120.7401),
    "Florida": (27.6648, -81.5158),
    "Illinois": (40.6331, -89.3985),
    "Pennsylvania": (41.2033, -77.1945),
    "Ohio": (40.4173, -82.9071),
    "Michigan": (44.3148, -85.6024),
    "Georgia": (32.1656, -82.9001)
}

filtered_df['Latitude'] = filtered_df['State'].map(lambda x: state_coords.get(x, (None, None))[0])
filtered_df['Longitude'] = filtered_df['State'].map(lambda x: state_coords.get(x, (None, None))[1])

map_df = filtered_df.dropna(subset=['Latitude', 'Longitude'])

map_type = st.radio("Select Map Type", ["Scatter Map", "Heatmap"], horizontal=True)

if map_type == "Scatter Map":
    fig_map = px.scatter_mapbox(
        map_df,
        lat="Latitude",
        lon="Longitude",
        size="Sales",
        color="Profit",
        hover_name="City",
        hover_data=["State", "Sales", "Profit"],
        zoom=3,
        height=500
    )
else:
    fig_map = px.density_mapbox(
        map_df,
        lat="Latitude",
        lon="Longitude",
        z="Sales",
        radius=20,
        center=dict(lat=37, lon=-95),
        zoom=3,
        height=500
    )

fig_map.update_layout(mapbox_style="open-street-map")

st.plotly_chart(fig_map, use_container_width=True)

# ------------------ DATA TABLE ------------------
st.subheader("📄 Filtered Data Preview")
st.dataframe(filtered_df)