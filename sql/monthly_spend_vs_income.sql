WITH monthly_spending AS (
    SELECT 
        client_id,
        strftime('%Y-%m', date) AS month,
        SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS monthly_spending
    FROM transactions
    GROUP BY client_id, month
)
SELECT 
    monthly_spending.client_id,
    COUNT(DISTINCT monthly_spending.month) AS active_months,
    '$' || ROUND(AVG(monthly_spending.monthly_spending), 2) AS avg_monthly_spending,
    '$' || ROUND(CAST(REPLACE(users.yearly_income, '$', '') AS REAL) / 12.0, 2) AS monthly_income
FROM monthly_spending
LEFT JOIN users ON monthly_spending.client_id = users.id
GROUP BY monthly_spending.client_id
ORDER BY AVG(monthly_spending.monthly_spending) DESC