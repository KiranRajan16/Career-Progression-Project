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
# Derived Columns (if missing)
# -----------------------------
if 'TrainingNeed' not in df.columns:
    df['TrainingNeed'] = df['TrainingIntensity'].apply(
        lambda x: "High Need" if x < 0.2 else "Moderate" if x < 0.5 else "Low Need"
    )

if 'CareerStage' not in df.columns:
    def career_stage(y):
        if y < 3:
            return "Early Career"
        elif y < 7:
            return "Mid Career"
        else:
            return "Late Career"
    df['CareerStage'] = df['YearsAtCompany'].apply(career_stage)

if 'Action' not in df.columns:
    def suggest_action(row):
        if row['RiskLevel'] == "High Risk":
            return "Immediate Promotion Review"
        elif row['TrainingNeed'] == "High Need":
            return "Assign Training Program"
        else:
            return "Monitor"
    df['Action'] = df.apply(suggest_action, axis=1)

# -----------------------------
# Title
# -----------------------------
st.markdown('<p class="title">Career Progression and Promotion Gap Analysis for Retention Optimization ' \
                'at Palo Alto Networks</p>', unsafe_allow_html=True)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.markdown("<h2>🔍 User Capabilities</h2>", unsafe_allow_html=True)

department = st.sidebar.multiselect("Department", df['Department'].unique(), df['Department'].unique())
role = st.sidebar.multiselect("Job Role", df['JobRole'].unique(), df['JobRole'].unique())
risk = st.sidebar.multiselect("Risk Level", df['RiskLevel'].unique(), df['RiskLevel'].unique())
cluster = st.sidebar.multiselect("Career Cluster", df['CareerCluster'].unique(), df['CareerCluster'].unique())
career_stage = st.sidebar.multiselect("Career Stage", df['CareerStage'].unique(), df['CareerStage'].unique())

gap_range = st.sidebar.slider("Promotion Gap", 0.0, 1.0, (0.0, 1.0))

# -----------------------------
# Filtering Logic
# -----------------------------
filtered_df = df[
    (df['Department'].isin(department)) &
    (df['JobRole'].isin(role)) &
    (df['RiskLevel'].isin(risk)) &
    (df['CareerCluster'].isin(cluster)) &
    (df['CareerStage'].isin(career_stage)) &
    (df['PromotionGapRatio'] >= gap_range[0]) &
    (df['PromotionGapRatio'] <= gap_range[1])
]

# -----------------------------
# KPI Cards
# -----------------------------
st.markdown('<p class="section">📊 Key Metrics</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

total = len(filtered_df)
high_risk = len(filtered_df[filtered_df['RiskLevel'] == "High Risk"])
retention = len(filtered_df[filtered_df['RetentionOpportunity'] == True])
training_need = len(filtered_df[filtered_df['TrainingNeed'] == "High Need"])

with col1:
    st.markdown(f'<div class="kpi-card kpi-blue"><div class="kpi-value">{total}</div><div>Total Employees</div></div>', unsafe_allow_html=True)

with col2:
    st.markdown(f'<div class="kpi-card kpi-red"><div class="kpi-value">{high_risk}</div><div>High Risk</div></div>', unsafe_allow_html=True)

with col3:
    st.markdown(f'<div class="kpi-card kpi-green"><div class="kpi-value">{retention}</div><div>Retention Opportunities</div></div>', unsafe_allow_html=True)

with col4:
    st.markdown(f'<div class="kpi-card kpi-orange"><div class="kpi-value">{training_need}</div><div>Training Needed</div></div>', unsafe_allow_html=True)

# -----------------------------
# Career Clustering Dashboard
# -----------------------------
st.markdown('<p class="section">📈 Career Clustering</p>', unsafe_allow_html=True)

col5, col6 = st.columns(2)

with col5:
    fig1 = px.pie(filtered_df, names='CareerCluster', title='Cluster Distribution')
    st.plotly_chart(fig1, use_container_width=True)

with col6:
    fig2 = px.bar(filtered_df, x='CareerCluster', title='Career Pattern Summary')
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# Promotion Gap Monitor
# -----------------------------
st.markdown('<p class="section">📊 Promotion Gap Monitor</p>', unsafe_allow_html=True)

high_gap = filtered_df[filtered_df['PromotionGapRatio'] > 0.6]
st.write("High Promotion Gap Employees")
st.dataframe(high_gap)

role_stagnation = filtered_df.groupby('JobRole')['RoleStagnationIndex'].mean().reset_index()
fig_role = px.bar(role_stagnation, x='JobRole', y='RoleStagnationIndex')
st.plotly_chart(fig_role, use_container_width=True)

# -----------------------------
# Retention Panel
# -----------------------------
st.markdown('<p class="section">🎯 Retention Opportunities</p>', unsafe_allow_html=True)

retention_df = filtered_df[filtered_df['RetentionOpportunity'] == True]
st.dataframe(retention_df[['JobRole','RiskLevel','TrainingNeed','Action']], use_container_width=True)

# -----------------------------
# Manager Insights
# -----------------------------
st.markdown('<p class="section">👨‍💼 Manager Insights</p>', unsafe_allow_html=True)

fig_manager = px.scatter(
    filtered_df,
    x="ManagerStability",
    y="PromotionGapRatio",
    color="RiskLevel"
)
st.plotly_chart(fig_manager, use_container_width=True)

team_stagnation = filtered_df.groupby('YearsWithCurrManager')['RoleStagnationIndex'].mean().reset_index()
fig_team = px.line(team_stagnation, x='YearsWithCurrManager', y='RoleStagnationIndex')
st.plotly_chart(fig_team, use_container_width=True)

# -----------------------------
# Cluster Explorer
# -----------------------------
st.markdown('<p class="section">🔍 Cluster Explorer</p>', unsafe_allow_html=True)

selected_cluster = st.selectbox("Select Cluster", filtered_df['CareerCluster'].unique())
cluster_df = filtered_df[filtered_df['CareerCluster'] == selected_cluster]

st.write(cluster_df.describe())

# -----------------------------
# Final Data Table
# -----------------------------
st.markdown('<p class="section">📋 Filtered Data</p>', unsafe_allow_html=True)
st.dataframe(filtered_df, use_container_width=True)