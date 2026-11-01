import pandas as pd

# Load datasets
borough = pd.read_csv("data/borough_data.csv")
customers = pd.read_csv("data/customer_data.csv")
campaigns = pd.read_csv("data/campaign_data.csv")
trends = pd.read_csv("data/monthly_trends.csv")

print("✅ DATA LOADED\n")

# -------------------------
# 1. Check shape
# -------------------------
print("Borough shape:", borough.shape)
print("Customers shape:", customers.shape)
print("Campaigns shape:", campaigns.shape)
print("Trends shape:", trends.shape)

print("\n-------------------------")

# -------------------------
# 2. Check missing values
# -------------------------
print("\nMissing values:\n")
print("Borough:\n", borough.isnull().sum())
print("\nCustomers:\n", customers.isnull().sum())
print("\nCampaigns:\n", campaigns.isnull().sum())
print("\nTrends:\n", trends.isnull().sum())

print("\n-------------------------")

# -------------------------
# 3. Basic sanity check
# -------------------------
print("\nCampaign Funnel Check:")
print("Any clicks > impressions:",
      (campaigns["clicks"] > campaigns["impressions"]).sum())

print("Any signups > clicks:",
      (campaigns["signups"] > campaigns["clicks"]).sum())

print("Any paid > signups:",
      (campaigns["conversions_to_paid"] > campaigns["signups"]).sum())
# =====================================
# BOROUGH PENETRATION ANALYSIS
# =====================================

# Create penetration %
borough["revolut_penetration_pct"] = (
    borough["current_revolut_users_est"] /
    borough["population"] * 100
).round(2)

print("\nTop 5 Boroughs by Revolut Penetration:")
print(
    borough.sort_values("revolut_penetration_pct", ascending=False)
    [["borough", "revolut_penetration_pct"]]
    .head()
)

print("\nBottom 5 Boroughs by Revolut Penetration:")
print(
    borough.sort_values("revolut_penetration_pct")
    [["borough", "revolut_penetration_pct"]]
    .head()
)
from sklearn.preprocessing import MinMaxScaler

# Select features
features = borough[[
    "median_income_gbp",
    "young_professional_pct",
    "fintech_awareness_pct",
    "commuter_footfall_daily",
    "revolut_penetration_pct"
]]

# Normalize
scaler = MinMaxScaler()
scaled = scaler.fit_transform(features)

scaled_df = pd.DataFrame(scaled, columns=features.columns)

# Build weighted opportunity score
borough["opportunity_score"] = (
    scaled_df["median_income_gbp"] * 0.25 +
    scaled_df["young_professional_pct"] * 0.25 +
    scaled_df["fintech_awareness_pct"] * 0.20 +
    scaled_df["commuter_footfall_daily"] * 0.15 -
    scaled_df["revolut_penetration_pct"] * 0.15
)

print("\nTop 5 Boroughs by Opportunity Score:")
print(
    borough.sort_values("opportunity_score", ascending=False)
    [["borough", "opportunity_score"]]
    .head()
)
# =====================================
# CUSTOMER LIFETIME VALUE
# =====================================

# Estimate monthly revenue (assume 2% interchange revenue)
customers["monthly_revenue_est"] = customers["monthly_spend_gbp"] * 0.02

# Estimate lifetime value
customers["estimated_ltv"] = (
    customers["monthly_revenue_est"] *
    customers["months_active"]
)

print("\nAverage LTV:", round(customers["estimated_ltv"].mean(), 2))

# Top 25% customers
high_value_threshold = customers["estimated_ltv"].quantile(0.75)

high_value_customers = customers[
    customers["estimated_ltv"] >= high_value_threshold
]

print("\nHigh Value Customer Count:", high_value_customers.shape[0])
print("\nTop Acquisition Channels (High Value Customers):")
print(high_value_customers["acquisition_channel"].value_counts())

print("\nTop Boroughs (High Value Customers):")
print(high_value_customers["borough"].value_counts().head())

print("\nTop Occupations (High Value Customers):")
print(high_value_customers["occupation"].value_counts().head())
# =====================================
# CHURN ANALYSIS
# =====================================

print("\nOverall Churn Rate:")
print(round(customers["churned"].mean() * 100, 2), "%")

# Churn by acquisition channel
print("\nChurn Rate by Acquisition Channel:")
print(
    customers.groupby("acquisition_channel")["churned"]
    .mean()
    .sort_values(ascending=False) * 100
)

# Churn by occupation
print("\nChurn Rate by Occupation:")
print(
    customers.groupby("occupation")["churned"]
    .mean()
    .sort_values(ascending=False) * 100
)

# Churn by app engagement
print("\nAverage App Opens Per Week:")
print("Churned Users:",
      round(customers[customers["churned"] == 1]["app_opens_per_week"].mean(), 2))
print("Active Users:",
      round(customers[customers["churned"] == 0]["app_opens_per_week"].mean(), 2))
# =====================================
# CHURN PREDICTION MODEL
# =====================================

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Select numeric features
X = customers[[
    "age",
    "annual_income_gbp",
    "monthly_transactions",
    "international_transfers",
    "months_active",
    "estimated_ltv"
]]

y = customers["churned"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Accuracy
accuracy = model.score(X_test, y_test)
print("\nModel Accuracy:", round(accuracy * 100, 2), "%")

# Feature importance
importance = pd.Series(
    model.feature_importances_,
    index=X.columns
).sort_values(ascending=False)

print("\nFeature Importance:")
print(importance)