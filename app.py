import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Load CSS
# -----------------------------
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Career Dashboard", layout="wide")

# -----------------------------
# Load Data
# -----------------------------
df = pd.read_csv("final_clustered_data.csv")

# -----------------------------
# Title
# -----------------------------
st.markdown('<p class="title">Career Progression and Promotion Gap Analysis for Retention Optimization at Palo Alto Networks</p>', unsafe_allow_html=True)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔍 User Capabilites")

department = st.sidebar.multiselect("Department", df['Department'].unique(), default=df['Department'].unique())
risk = st.sidebar.multiselect("Risk Level", df['RiskLevel'].unique(), default=df['RiskLevel'].unique())
cluster = st.sidebar.multiselect("Career Cluster", df['CareerCluster'].unique(), default=df['CareerCluster'].unique())

filtered_df = df[
    (df['Department'].isin(department)) &
    (df['RiskLevel'].isin(risk)) &
    (df['CareerCluster'].isin(cluster))
]

# -----------------------------
# KPI Cards
# -----------------------------
st.markdown('<p class="section">📊 Key Metrics</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

total = len(filtered_df)
high_risk = len(filtered_df[filtered_df['RiskLevel'] == "High Risk"])
retention = len(filtered_df[filtered_df['RetentionOpportunity'] == True])

with col1:
    st.markdown(f"""
    <div class="kpi-card kpi-blue">
        <div class="kpi-value">{total}</div>
        <div class="kpi-label">Total Employees</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card kpi-red">
        <div class="kpi-value">{high_risk}</div>
        <div class="kpi-label">High Risk</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card kpi-green">
        <div class="kpi-value">{retention}</div>
        <div class="kpi-label">Retention Opportunities</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# Charts Row
# -----------------------------
st.markdown('<p class="section">📈 Insights</p>', unsafe_allow_html=True)

col4, col5 = st.columns(2)

with col4:
    fig1 = px.pie(filtered_df, names='CareerCluster', title='Career Cluster Distribution')
    st.plotly_chart(fig1, use_container_width=True)

with col5:
    fig2 = px.bar(filtered_df, x='RiskLevel', color='RiskLevel', title='Risk Level Distribution',
                  color_discrete_map={
                      "High Risk": "red",
                      "Medium Risk": "orange",
                      "Low Risk": "green"
                  })
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# Manager Insight
# -----------------------------
st.markdown('<p class="section">👨‍💼 Manager Insight</p>', unsafe_allow_html=True)

fig3 = px.scatter(
    filtered_df,
    x="ManagerStability",
    y="PromotionGapRatio",
    color="RiskLevel",
    title="Manager Stability vs Promotion Gap",
    color_discrete_map={
        "High Risk": "red",
        "Medium Risk": "orange",
        "Low Risk": "green"
    }
)

st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# Retention Panel
# -----------------------------
st.markdown('<p class="section">🎯 Retention Opportunity Panel</p>', unsafe_allow_html=True)

retention_df = filtered_df[filtered_df['RetentionOpportunity'] == True]
st.dataframe(retention_df, use_container_width=True)

# -----------------------------
# Filtered Data
# -----------------------------
st.markdown('<p class="section">📋 Filtered Data</p>', unsafe_allow_html=True)

st.dataframe(filtered_df, use_container_width=True)