-- Total spent per user, ordered by highest
-- Note: amount is stored as text with a '$' prefix, so we strip the symbol and cast to REAL to get correct numeric totals
SELECT 
    transactions.client_id,
    SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS total_spent
FROM transactions
LEFT JOIN users ON transactions.client_id = users.id
GROUP BY transactions.client_id
ORDER BY total_spent DESC