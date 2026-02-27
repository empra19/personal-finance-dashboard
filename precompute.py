import sqlite3
import pandas as pd

conn = sqlite3.connect('data/finance.db')

# # Fraud rate by error type
# df_fraud_error = pd.read_sql_query("""
#     SELECT 
#         t.errors,
#         COUNT(*) AS total_transactions,
#         SUM(CASE WHEN f.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
#         ROUND(100.0 * SUM(CASE WHEN f.is_fraud = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS fraud_rate
#     FROM transactions t
#     LEFT JOIN fraud_labels f ON t.id = f.transaction_idpytho
#     GROUP BY t.errors
#     HAVING COUNT(*) >= 1000
#     ORDER BY fraud_rate DESC
# """, conn)
# df_fraud_error.to_csv('data/fraud_by_error.csv', index=False)
# print('Done - fraud_by_error.csv saved')


# # Fraud rate over time
# df_fraud_time = pd.read_sql_query("""
#     SELECT 
#         strftime('%Y-%m', t.date) AS month,
#         COUNT(*) AS total_transactions,
#         SUM(CASE WHEN f.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
#         ROUND(100.0 * SUM(CASE WHEN f.is_fraud = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS fraud_rate
#     FROM transactions t
#     LEFT JOIN fraud_labels f ON t.id = f.transaction_id
#     GROUP BY month
#     ORDER BY month ASC
# """, conn)
# df_fraud_time.to_csv('data/fraud_over_time.csv', index=False)
# print('Done - fraud_over_time.csv saved')

# # Fraud vs non-fraud amounts
# df_fraud_amounts = pd.read_sql_query("""
#     SELECT 
#         f.is_fraud,
#         ROUND(AVG(CAST(REPLACE(t.amount, '$', '') AS REAL)), 2) AS avg_amount,
#         ROUND(MIN(CAST(REPLACE(t.amount, '$', '') AS REAL)), 2) AS min_amount,
#         ROUND(MAX(CAST(REPLACE(t.amount, '$', '') AS REAL)), 2) AS max_amount
#     FROM transactions t
#     LEFT JOIN fraud_labels f ON t.id = f.transaction_id
#     WHERE f.is_fraud IS NOT NULL
#     GROUP BY f.is_fraud
# """, conn)
# df_fraud_amounts.to_csv('data/fraud_amounts.csv', index=False)
# print('Done - fraud_amounts.csv saved')


# Fraud rate by merchant category
df_fraud_category = pd.read_sql_query("""
    SELECT 
        mcc_codes.description,
        COUNT(*) AS total_transactions,
        SUM(CASE WHEN f.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
        ROUND(100.0 * SUM(CASE WHEN f.is_fraud = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS fraud_rate
    FROM transactions t
    LEFT JOIN fraud_labels f ON t.id = f.transaction_id
    LEFT JOIN mcc_codes ON t.mcc = mcc_codes.mcc
    WHERE mcc_codes.description IS NOT NULL
    GROUP BY mcc_codes.description
    HAVING COUNT(*) >= 1000
    ORDER BY fraud_rate DESC
""", conn)
df_fraud_category.to_csv('data/fraud_by_category.csv', index=False)
print('Done - fraud_by_category.csv saved')

conn.close()