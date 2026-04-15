import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans

# -----------------------------
# Step 1: Load Data
# -----------------------------
df = pd.read_csv("data/Palo Dataset.csv")

# -----------------------------
# Step 2: Handle Missing Values
# -----------------------------
# Fill numerical columns with median
num_cols = df.select_dtypes(include=np.number).columns
df[num_cols] = df[num_cols].fillna(df[num_cols].median())

# Fill categorical columns with mode
cat_cols = df.select_dtypes(include='object').columns
for col in cat_cols:
    df[col].fillna(df[col].mode()[0], inplace=True)

# -----------------------------
# Step 3: Encode Categorical Columns
# -----------------------------
le = LabelEncoder()

for col in cat_cols:
    df[col] = le.fit_transform(df[col])

# -----------------------------
# Step 4: Feature Engineering
# -----------------------------
# Avoid division by zero
df['YearsAtCompany'] = df['YearsAtCompany'].replace(0, 1)

df['PromotionGapRatio'] = df['YearsSinceLastPromotion'] / df['YearsAtCompany']
df['RoleStagnationIndex'] = df['YearsInCurrentRole'] / df['YearsAtCompany']
df['TrainingIntensity'] = df['TrainingTimesLastYear'] / df['YearsAtCompany']
df['ManagerStability'] = df['YearsWithCurrManager'] / df['YearsAtCompany']

# -----------------------------
# Step 5: Select Features for Clustering
# -----------------------------
features = [
    'PromotionGapRatio',
    'RoleStagnationIndex',
    'TrainingIntensity',
    'ManagerStability',
    'YearsAtCompany',
    'YearsInCurrentRole'
]

X = df[features]

# -----------------------------
# Step 6: Feature Scaling
# -----------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# -----------------------------
# Step 7: Apply K-Means Clustering
# -----------------------------
kmeans = KMeans(n_clusters=4, random_state=42)
df['Cluster'] = kmeans.fit_predict(X_scaled)

# Preview
print(df.head())

# -----------------------------
# Step 1: Analyze clusters (mean values)
# -----------------------------
cluster_summary = df.groupby('Cluster').mean()

print("Cluster Summary:")
print(cluster_summary)

# Create mapping based on your observation
cluster_labels = {
    0: "Fast Growth",
    1: "Stagnant Employees",
    2: "Stable Employees",
    3: "High Risk"
}

# Apply labels
df['CareerCluster'] = df['Cluster'].map(cluster_labels)

print(df[['Cluster', 'CareerCluster']].head())
print(df['CareerCluster'].value_counts())

# -----------------------------
# Step 1: Create Risk Score Function
# -----------------------------
def assign_risk(row):
    if (row['PromotionGapRatio'] > 0.6 and 
        row['RoleStagnationIndex'] > 0.6 and 
        row['TrainingIntensity'] < 0.2):
        return "High Risk"
    
    elif (row['PromotionGapRatio'] > 0.3 and 
          row['RoleStagnationIndex'] > 0.3):
        return "Medium Risk"
    
    else:
        return "Low Risk"

df['RiskLevel'] = df.apply(assign_risk, axis=1)
print(df[['PromotionGapRatio', 'RoleStagnationIndex', 'TrainingIntensity']].head())

# -----------------------------
# Step 2: Apply function
# -----------------------------
df['RiskLevel'] = df.apply(assign_risk, axis=1)

print(df[['CareerCluster', 'RiskLevel']].head())
print(df['RiskLevel'].value_counts())
df['RetentionOpportunity'] = (
    (df['RiskLevel'] == "Medium Risk") & 
    (df['Attrition'] == 0)
)

# -----------------------------
# Step 8: Save Output
# -----------------------------
df.to_csv("final_clustered_data.csv", index=False)