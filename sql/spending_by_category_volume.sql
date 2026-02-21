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