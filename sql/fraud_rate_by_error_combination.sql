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