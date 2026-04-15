import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Load Data
# -----------------------------
df = pd.read_csv("final_clustered_data.csv")

st.title("Employee Career Progression Dashboard")

# -----------------------------
# Sidebar Filters
# -----------------------------
department = st.sidebar.selectbox("Select Department", df['Department'].unique())
risk_level = st.sidebar.selectbox("Select Risk Level", df['RiskLevel'].unique())

filtered_df = df[
    (df['Department'] == department) &
    (df['RiskLevel'] == risk_level)
]

# -----------------------------
# Show Data
# -----------------------------
st.subheader("Filtered Employee Data")
st.dataframe(filtered_df)

# -----------------------------
# Cluster Distribution
# -----------------------------
st.subheader("Career Cluster Distribution")

cluster_counts = df['CareerCluster'].value_counts()

fig1, ax1 = plt.subplots()
cluster_counts.plot(kind='bar', ax=ax1)
st.pyplot(fig1)

# -----------------------------
# Risk Level Distribution
# -----------------------------
st.subheader("Risk Level Distribution")

risk_counts = df['RiskLevel'].value_counts()

fig2, ax2 = plt.subplots()
risk_counts.plot(kind='bar', ax=ax2)
st.pyplot(fig2)

# -----------------------------
# Retention Opportunities
# -----------------------------
st.subheader("Retention Opportunities")

retention_df = df[df['RetentionOpportunity'] == True]
st.dataframe(retention_df)

# -----------------------------
# Key Metrics
# -----------------------------
st.subheader("Key Metrics")

st.write("Total Employees:", len(df))
st.write("High Risk Employees:", len(df[df['RiskLevel'] == "High Risk"]))
st.write("Retention Opportunities:", len(retention_df))