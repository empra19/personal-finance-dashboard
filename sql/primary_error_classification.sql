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