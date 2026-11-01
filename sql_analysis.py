import pandas as pd
import sqlite3

# Load data
customers = pd.read_csv("data/customer_data.csv")
campaigns = pd.read_csv("data/campaign_data.csv")
borough = pd.read_csv("data/borough_data.csv")

# Create database
conn = sqlite3.connect("revolut.db")

# Push tables into SQL
customers.to_sql("customers", conn, if_exists="replace", index=False)
campaigns.to_sql("campaigns", conn, if_exists="replace", index=False)
borough.to_sql("borough", conn, if_exists="replace", index=False)

print("✅ Data loaded into SQL database")
# =========================================
# SQL QUERY 1 — Avg LTV by Acquisition Channel
# =========================================

query1 = """
SELECT
    acquisition_channel,
    ROUND(AVG(monthly_spend_gbp * 0.02 * months_active), 2) AS avg_ltv,
    COUNT(*) AS total_customers
FROM customers
GROUP BY acquisition_channel
ORDER BY avg_ltv DESC;
"""

result1 = pd.read_sql(query1, conn)

print("\n📊 Avg LTV by Acquisition Channel:")
print(result1)
# =========================================
# SQL QUERY 2 — Total Estimated Revenue by Borough
# =========================================

query2 = """
SELECT
    c.borough,
    ROUND(SUM(c.monthly_spend_gbp * 0.02 * c.months_active), 2) AS total_estimated_revenue,
    COUNT(c.customer_id) AS total_customers
FROM customers c
JOIN borough b
    ON c.borough = b.borough
GROUP BY c.borough
ORDER BY total_estimated_revenue DESC
LIMIT 10;
"""

result2 = pd.read_sql(query2, conn)

print("\n🏙 Top 10 Boroughs by Total Estimated Revenue:")
print(result2)
# =========================================
# EXPORT RESULTS TO EXCEL
# =========================================

with pd.ExcelWriter("revolut_marketing_analysis.xlsx") as writer:
    result1.to_excel(writer, sheet_name="LTV_by_Channel", index=False)
    result2.to_excel(writer, sheet_name="Revenue_by_Borough", index=False)

print("\n✅ Results exported to Excel file") 