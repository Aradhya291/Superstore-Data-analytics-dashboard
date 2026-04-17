import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Dynamic Analytics Dashboard", layout="wide")

# ------------------ CUSTOM UI ------------------
st.markdown("""
    <style>
    body {background-color: #0E1117;}
    .main {background-color: #0E1117;}
    h1 {color: #00BFFF;}
    </style>
""", unsafe_allow_html=True)

# ------------------ TITLE ------------------
st.title("📊 Dynamic Data Analytics Dashboard")

# ------------------ FILE UPLOAD ------------------
st.sidebar.subheader("📤 Upload Dataset")

uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.sidebar.success("✅ Custom dataset loaded!")
else:
    df = pd.read_excel("Sample - Superstore.xlsx")

# ------------------ BASIC INFO ------------------
st.subheader("📌 Dataset Overview")

colA, colB = st.columns(2)
colA.metric("Rows", df.shape[0])
colB.metric("Columns", df.shape[1])

# ------------------ DATA TYPES ------------------
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

# ------------------ SIDEBAR FILTERS ------------------
st.sidebar.subheader("🔍 Filters")

# Categorical filters
for col in categorical_cols[:3]:  # limit to 3 filters to avoid clutter
    selected = st.sidebar.multiselect(f"{col}", df[col].dropna().unique())
    if selected:
        df = df[df[col].isin(selected)]

# ------------------ SEARCH ------------------
search = st.sidebar.text_input("🔎 Search Any Value")

if search:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

# ------------------ DOWNLOAD ------------------
st.download_button(
    "📥 Download Data",
    df.to_csv(index=False),
    file_name="data.csv",
    mime="text/csv"
)

# ------------------ KPIs ------------------
st.subheader("📊 Quick KPIs")

if numeric_cols:
    col1, col2, col3 = st.columns(3)
    col1.metric("Sum", f"{df[numeric_cols[0]].sum():,.0f}")
    col2.metric("Average", f"{df[numeric_cols[0]].mean():,.2f}")
    col3.metric("Max", f"{df[numeric_cols[0]].max():,.0f}")

# ------------------ DYNAMIC CHART ------------------
st.subheader("📈 Custom Chart Builder")

x_axis = st.selectbox("Select X-axis", df.columns)
y_axis = st.selectbox("Select Y-axis", numeric_cols if numeric_cols else df.columns)

chart_type = st.selectbox(
    "Chart Type",
    ["Bar", "Line", "Scatter", "Histogram"]
)

if chart_type == "Bar":
    fig = px.bar(df, x=x_axis, y=y_axis)
elif chart_type == "Line":
    fig = px.line(df, x=x_axis, y=y_axis)
elif chart_type == "Scatter":
    fig = px.scatter(df, x=x_axis, y=y_axis)
elif chart_type == "Histogram":
    fig = px.histogram(df, x=x_axis)

st.plotly_chart(fig, use_container_width=True)

# ------------------ PREDEFINED CHARTS (IF SUPERSTORE) ------------------
if all(col in df.columns for col in ['Sales', 'Profit', 'Category']):
    st.subheader("📊 Superstore Insights")

    col4, col5 = st.columns(2)

    fig1 = px.bar(df, x='Category', y='Sales', color='Category',
                  title="Sales by Category")
    col4.plotly_chart(fig1, use_container_width=True)

    fig2 = px.scatter(df, x='Sales', y='Profit',
                      color='Category', title="Sales vs Profit")
    col5.plotly_chart(fig2, use_container_width=True)

# ------------------ MAP SECTION ------------------
if all(col in df.columns for col in ['State', 'Sales']):
    st.subheader("🗺️ Map Visualization")

    state_coords = {
        "California": (36.7783, -119.4179),
        "Texas": (31.9686, -99.9018),
        "New York": (40.7128, -74.0060),
        "Washington": (47.7511, -120.7401),
        "Florida": (27.6648, -81.5158)
    }

    df['Latitude'] = df['State'].map(lambda x: state_coords.get(x, (None, None))[0])
    df['Longitude'] = df['State'].map(lambda x: state_coords.get(x, (None, None))[1])

    map_df = df.dropna(subset=['Latitude', 'Longitude'])

    fig_map = px.scatter_mapbox(
        map_df,
        lat="Latitude",
        lon="Longitude",
        size="Sales",
        color="Sales",
        zoom=3
    )

    fig_map.update_layout(mapbox_style="open-street-map")

    st.plotly_chart(fig_map, use_container_width=True)

# ------------------ DATA PREVIEW ------------------
st.subheader("📄 Data Preview")
st.dataframe(df)