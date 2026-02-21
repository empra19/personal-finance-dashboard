-- Total spent and transaction count across all users by month
-- strftime('%Y-%m', date) extracts year and month from the date column
SELECT strftime('%Y-%m', date) AS month,
    COUNT(*) AS number_transactions,
    SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS monthly_total
FROM transactions
GROUP BY month
ORDER BY month ASC