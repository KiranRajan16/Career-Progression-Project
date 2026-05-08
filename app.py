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

st.set_page_config(layout="wide")

# -----------------------------
# Load Data
# -----------------------------
df = pd.read_csv("data/Palo_Alto_Networks.csv")

# -----------------------------
# FEATURE ENGINEERING (REQUIRED)
# -----------------------------
df['TrainingIntensity'] = df['TrainingTimesLastYear'] / (df['YearsAtCompany'] + 1)
df['PromotionGapRatio'] = df['YearsSinceLastPromotion'] / (df['YearsAtCompany'] + 1)
df['RoleStagnationIndex'] = df['YearsInCurrentRole'] / (df['YearsAtCompany'] + 1)
df['ManagerStability'] = df['YearsWithCurrManager'] / (df['YearsAtCompany'] + 1)

# -----------------------------
# RISK LEVEL
# -----------------------------
def assign_risk(row):
    if row['PromotionGapRatio'] > 0.6 and row['RoleStagnationIndex'] > 0.6:
        return "High Risk"
    elif row['PromotionGapRatio'] > 0.3:
        return "Medium Risk"
    else:
        return "Low Risk"

df['RiskLevel'] = df.apply(assign_risk, axis=1)

# -----------------------------
# Derived Columns (safety)
# -----------------------------
if 'TrainingNeed' not in df.columns:
    df['TrainingNeed'] = df['TrainingIntensity'].apply(
        lambda x: "High Need" if x < 0.2 else "Moderate" if x < 0.5 else "Low Need"
    )

if 'CareerStage' not in df.columns:
    df['CareerStage'] = df['YearsAtCompany'].apply(
        lambda x: "Early" if x < 3 else "Mid" if x < 7 else "Late"
    )

if 'Action' not in df.columns:
    df['Action'] = df.apply(
        lambda row: "Promotion Review" if row['RiskLevel']=="High Risk"
        else "Training Needed" if row['TrainingNeed']=="High Need"
        else "Monitor",
        axis=1
    )

# -----------------------------
# CREATE CAREER CLUSTER
# -----------------------------
def cluster_label(row):
    if row['PromotionGapRatio'] < 0.3:
        return "Fast Growth"
    elif row['RoleStagnationIndex'] > 0.6:
        return "High Risk Cluster"
    else:
        return "Stable"

df['CareerCluster'] = df.apply(cluster_label, axis=1)

# -----------------------------
# RETENTION OPPORTUNITY
# -----------------------------
df['RetentionOpportunity'] = (
    (df['RiskLevel'].isin(["High Risk", "Medium Risk"])) |
    (df['YearsSinceLastPromotion'] > 3) |
    (df['JobSatisfaction'] <= 2)
)
# -----------------------------
# TITLE
# -----------------------------
st.markdown('<p class="title">Career Progression and Promotion Gap Analysis for Retention Optimization at Palo Alto Networks</p>', unsafe_allow_html=True)

# -----------------------------
# SIDEBAR (FINAL VERSION)
# -----------------------------
st.sidebar.markdown(
    "<h2 class='sidebar-title'>🔍 Filters</h2>",
    unsafe_allow_html=True
)

# -----------------------------
# Department (TEXT VALUES)
# -----------------------------
dept = st.sidebar.multiselect(
    "Department",
    sorted(df['Department'].dropna().unique()),
    default=sorted(df['Department'].dropna().unique())
)

# -----------------------------
# Job Role (TEXT VALUES)
# -----------------------------
role = st.sidebar.multiselect(
    "Job Role",
    sorted(df['JobRole'].dropna().unique()),
    default=sorted(df['JobRole'].dropna().unique())
)

# -----------------------------
# Risk Level (COLORED TEXT STYLE)
# -----------------------------
risk_options = {
    "🔴 High Risk": "High Risk",
    "🟡 Medium Risk": "Medium Risk",
    "🟢 Low Risk": "Low Risk"
}

selected_risk_display = st.sidebar.multiselect(
    "Risk Level",
    list(risk_options.keys()),
    default=list(risk_options.keys())
)

risk = [risk_options[r] for r in selected_risk_display]

# -----------------------------
# Career Cluster (COLORED)
# -----------------------------
cluster_options = {
    "🔵 Fast Growth": "Fast Growth",
    "🟣 Stable": "Stable",
    "🔴 High Risk Cluster": "High Risk Cluster"
}

selected_cluster_display = st.sidebar.multiselect(
    "Career Cluster",
    list(cluster_options.keys()),
    default=list(cluster_options.keys())
)

cluster = [cluster_options[c] for c in selected_cluster_display]

# -----------------------------
# Promotion Gap Slider
# -----------------------------
gap = st.sidebar.slider(
    "Promotion Gap",
    0.0, 1.0, (0.0, 1.0)
)

# -----------------------------
# FILTERED DATA
# -----------------------------
filtered_df = df[
    (df['Department'].isin(dept)) &
    (df['JobRole'].isin(role)) &
    (df['CareerCluster'].isin(cluster)) &
    (df['RiskLevel'].isin(risk)) &
    (df['PromotionGapRatio'] >= gap[0]) &
    (df['PromotionGapRatio'] <= gap[1])
]

# -----------------------------
# KPI SECTION
# -----------------------------
st.markdown("<h3 class='section-title'>📊 Key Metrics</h3>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"""
<div class="kpi-card kpi-blue">
    <div class="kpi-title">Total Employees</div>
    <div class="kpi-value">{len(filtered_df)}</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="kpi-card kpi-red">
    <div class="kpi-title">High Risk</div>
    <div class="kpi-value">{len(filtered_df[filtered_df['RiskLevel']=='High Risk'])}</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="kpi-card kpi-green">
    <div class="kpi-title">Retention Opportunities</div>
    <div class="kpi-value">{len(filtered_df[filtered_df['RetentionOpportunity']])}</div>
</div>
""", unsafe_allow_html=True)

col4.markdown(f"""
<div class="kpi-card kpi-purple">
    <div class="kpi-title">Training Need</div>
    <div class="kpi-value">{len(filtered_df[filtered_df['TrainingNeed']=='High Need'])}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

# -----------------------------
# TABS (MAIN IMPROVEMENT)
# -----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Career Clusters",
    "📊 Promotion Gap",
    "🎯 Retention",
    "👨‍💼 Manager Insights",
    "🔍 Cluster Explorer"
])

# -----------------------------
# TAB 1: CLUSTER DASHBOARD
# -----------------------------
with tab1:
    st.markdown("<h3 class='tab-title'>Career Pattern Insights", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    fig1 = px.pie(filtered_df, names="CareerCluster",
                  title="Cluster Distribution",
                  color_discrete_sequence=["#636EFA", "#EF553B", "#00CC96"])
    col1.plotly_chart(fig1, use_container_width=True)

    fig2 = px.histogram(filtered_df, x="CareerCluster",
                        color="RiskLevel",
                        title="Cluster vs Risk",
                        color_discrete_map={
        "High Risk": "#FF4B4B",    
        "Medium Risk": "#FFC300",   
        "Low Risk": "#28A745"      
    })
    col2.plotly_chart(fig2, use_container_width=True)

    st.markdown(
        "<div class = 'info-cluster'>Clusters group employees, based on career growth patterns like promotion speed and role changes.</div>",
        unsafe_allow_html= True
    )

# -----------------------------
# TAB 2: PROMOTION GAP
# -----------------------------
with tab2:
    st.markdown("<h3 class='tab-title'>Promotion Gap Monitor", unsafe_allow_html=True)

    fig3 = px.histogram(filtered_df, x="PromotionGapRatio",
                        title="Promotion Gap Distribution", color_discrete_sequence=["#AB63FA"] )
    st.plotly_chart(fig3, use_container_width=True)

    role_stagnation = filtered_df.groupby("JobRole")["RoleStagnationIndex"].mean().reset_index()

    fig4 = px.bar(role_stagnation,
                  x="JobRole", y="RoleStagnationIndex",
                  title="Role-level Stagnation", color_discrete_sequence=["#FFA15A"] ) 
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown(
        "<div class = 'info-promotion'>High promotion gap indicates employees are stuck without growth.</div>",
        unsafe_allow_html= True
    )

# -----------------------------
# TAB 3: RETENTION PANEL
# -----------------------------
with tab3:
    st.markdown("<h3 class='tab-title'>Retention Opportunities", unsafe_allow_html=True)

    retention_df = filtered_df[filtered_df['RetentionOpportunity']==True]
    if retention_df.empty:
        st.warning("⚠️ No matching employees. Adjust filters.")
    else:
        st.dataframe(retention_df[['JobRole','RiskLevel','TrainingNeed','Action']])

    # Action summary
    action_counts = retention_df['Action'].value_counts().reset_index()
    action_counts.columns = ['Action', 'Count']
    fig5 = px.pie(action_counts, names='Action', values='Count',
              title="Recommended Actions", color_discrete_sequence=["#19D3F3", "#FF6692", "#B6E880"])
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown(
        "<div class = 'info-retention'>Focus on these employees for proactive retention strategies.</div>",
        unsafe_allow_html= True
    )

# -----------------------------
# TAB 4: MANAGER INSIGHTS
# -----------------------------
with tab4:
    st.markdown("<h3 class='tab-title'>Manager Impact Analysis", unsafe_allow_html=True)

    fig6 = px.scatter(
        filtered_df,
        x="ManagerStability",
        y="PromotionGapRatio",
        color="RiskLevel",
        title="Manager Stability vs Promotion Gap",
        color_discrete_map={
        "High Risk": "#D62728",
        "Medium Risk": "#FFBF00",
        "Low Risk": "#2CA02C"
    }
    )
    st.plotly_chart(fig6, use_container_width=True)

    team = filtered_df.groupby("YearsWithCurrManager")["RoleStagnationIndex"].mean().reset_index()

    fig7 = px.line(team,
                   x="YearsWithCurrManager",
                   y="RoleStagnationIndex",
                   title="Team Stagnation Trend")
    st.plotly_chart(fig7, use_container_width=True)

    st.markdown(
        "<div class = 'info-manager'>Managers with longer tenure influence employee growth patterns.</div>",
        unsafe_allow_html= True
    )

# -----------------------------
# TAB 5: CLUSTER EXPLORER
# -----------------------------
with tab5:
    st.markdown("<h3 class='tab-title'>🔍 Cluster Explorer", unsafe_allow_html=True)

    selected_cluster = st.selectbox(
        "Select Career Cluster",
        filtered_df['CareerCluster'].unique()
    )

    cluster_df = filtered_df[
        filtered_df['CareerCluster'] == selected_cluster
    ]

    st.dataframe(cluster_df.head(), use_container_width=True)

    # Summary stats
    st.markdown("### 📊 Cluster Summary")
    st.write(cluster_df.describe())

    # Extra insight (VERY GOOD ADDITION)
    st.markdown("### 📈 Key Patterns")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Avg Promotion Gap", round(cluster_df['PromotionGapRatio'].mean(),2))

    with col2:
        st.metric("Avg Stagnation", round(cluster_df['RoleStagnationIndex'].mean(),2))

    st.markdown(
        "<div class = 'info-explorer'>This section is used to deeply analyze each cluster and understand employee career patterns.</div>",
        unsafe_allow_html= True
    )