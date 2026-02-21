-- Total spent per user, ordered by highest
-- Note: amount is stored as text with a '$' prefix, so we strip the symbol and cast to REAL to get correct numeric totals
SELECT 
    transactions.client_id,
    SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS total_spent
FROM transactions
LEFT JOIN users ON transactions.client_id = users.id
GROUP BY transactions.client_id
ORDER BY total_spent DESC

-- Total spent and transaction count across all users by month
-- strftime('%Y-%m', date) extracts year and month from the date column
SELECT 
    trftime('%Y-%m', date) AS month,
    COUNT(*) AS number_transactions,
    SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS monthly_total
FROM transactions
GROUP BY month
ORDER BY month ASC

-- Top 10 merchant categories by number of transactions
SELECT 
    mcc_codes.description,
    COUNT(*) AS number_transactions,
    SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS total_spent,
	ROUND(AVG(CAST(REPLACE(amount, '$', '') AS REAL)), 2) AS avg_transaction
FROM transactions
LEFT JOIN mcc_codes ON transactions.mcc = mcc_codes.mcc
GROUP BY mcc_codes.description
ORDER BY number_transactions DESC
LIMIT 10

-- Top 10 merchant categories by average transaction size
SELECT 
    mcc_codes.description,
    COUNT(*) AS number_transactions,
    SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS total_spent,
	ROUND(AVG(CAST(REPLACE(amount, '$', '') AS REAL)), 2) AS avg_transaction
FROM transactions
LEFT JOIN mcc_codes ON transactions.mcc = mcc_codes.mcc
GROUP BY mcc_codes.description
ORDER BY avg_transaction DESC
LIMIT 10

-- Simplifies errors to a single primary label for easier analysis.
-- Priority is ordered by business impact and fraud risk
-- Bad CVV is prioritised after analysis showed it has the highest fraud rate of any individual error type at 2.28%.
SELECT
    CASE 
        WHEN errors IS NULL THEN 'Clean'
        WHEN errors LIKE '%Insufficient Balance%' THEN 'Insufficient Balance'
        WHEN errors LIKE '%Bad CVV%' THEN 'Bad CVV'
        WHEN errors LIKE '%Bad PIN%' THEN 'Bad PIN'
        WHEN errors LIKE '%Technical Glitch%' THEN 'Technical Glitch'
        WHEN errors LIKE '%Bad Card Number%' THEN 'Bad Card Number'
        WHEN errors LIKE '%Bad Expiration%' THEN 'Bad Expiration'
        WHEN errors LIKE '%Bad Zipcode%' THEN 'Bad Zipcode'
        ELSE 'Other'
    END AS primary_error,
    COUNT(*) AS count
FROM transactions
GROUP BY primary_error
ORDER BY count DESC

-- Analyses fraud rate across different error combinations
-- Joins fraud_labels to transactions to calculate the percentage of confirmed fraud cases per error type
-- Findings: CVV errors show the highest fraud rate suggesting CVV failures are the strongest error indicator of fraudulent activity

SELECT 
    transactions.errors,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN fraud_labels.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(CASE WHEN fraud_labels.is_fraud = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS fraud_rate
FROM transactions
LEFT JOIN fraud_labels ON transactions.id = fraud_labels.transaction_id
GROUP BY transactions.errors
ORDER BY fraud_rate DESC

-- Introduces CTEs to calculate average monthly spending per user and compare 
-- against monthly income. Average is calculated only across Active Months

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

-- Extends the single CTE approach by adding a second CTE for total months
-- and a third for fraud rate per user. 
-- Dividing by total months rather than active months treats inactive months as zero spend, giving a
-- more complete picture of financial behaviour.

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