WITH monthly_spending AS (
    SELECT 
        client_id,
        strftime('%Y-%m', date) AS month,
        SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS monthly_spending
    FROM transactions
    GROUP BY client_id, month
),
total_months AS (
    SELECT COUNT(DISTINCT strftime('%Y-%m', date)) AS num_months
    FROM transactions
),
fraud_per_user AS (
    SELECT 
        transactions.client_id,
        COUNT(*) AS total_transactions,
        SUM(CASE WHEN fraud_labels.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count
    FROM transactions
    LEFT JOIN fraud_labels ON transactions.id = fraud_labels.transaction_id
    GROUP BY transactions.client_id
)
SELECT 
    monthly_spending.client_id,
    COUNT(DISTINCT monthly_spending.month) AS active_months,
    total_months.num_months AS total_months,
    '$' || ROUND(SUM(monthly_spending.monthly_spending) / total_months.num_months, 2) AS avg_monthly_spending,
    '$' || ROUND(CAST(REPLACE(users.yearly_income, '$', '') AS REAL) / 12.0, 2) AS monthly_income,
    ROUND((SUM(monthly_spending.monthly_spending) / total_months.num_months) / (CAST(REPLACE(users.yearly_income, '$', '') AS REAL) / 12.0) * 100, 2) || '%' AS pct_income_spent,
    ROUND(fraud_per_user.fraud_count * 100.0 / fraud_per_user.total_transactions, 2) || '%' AS fraud_rate
FROM monthly_spending
LEFT JOIN users ON monthly_spending.client_id = users.id
LEFT JOIN fraud_per_user ON monthly_spending.client_id = fraud_per_user.client_id
CROSS JOIN total_months
GROUP BY monthly_spending.client_id
ORDER BY (SUM(monthly_spending.monthly_spending) / total_months.num_months) / (CAST(REPLACE(users.yearly_income, '$', '') AS REAL) / 12.0) DESC