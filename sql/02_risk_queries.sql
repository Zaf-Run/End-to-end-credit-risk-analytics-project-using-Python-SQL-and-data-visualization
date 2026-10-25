-- Credit risk queries on bank_clean. Standard SQL unless a comment says otherwise.
-- Denominator for every rate: all customers in the segment (one row per customer).

-- Q1 Overall default rate
SELECT COUNT(*) AS customers, SUM(default_flag) AS defaults,
       ROUND(100.0 * SUM(default_flag) / COUNT(*), 2) AS default_rate_pct
FROM bank_clean;

-- Q2 Default rate by borrower segment (change the column to job, marital, education, age_band, personal_loan)
SELECT job AS segment, COUNT(*) AS customers, SUM(default_flag) AS defaults,
       ROUND(100.0 * SUM(default_flag) / COUNT(*), 2) AS default_rate_pct
FROM bank_clean GROUP BY job ORDER BY default_rate_pct DESC;

-- Q3 Average and total balance by default status (balance is a deposit account balance, not loan exposure)
SELECT default_raw AS default_status, COUNT(*) AS customers, ROUND(AVG(balance), 0) AS avg_balance,
       MIN(balance) AS min_balance, MAX(balance) AS max_balance
FROM bank_clean GROUP BY default_raw;

-- Q4 Default rate across balance bands (income is not in the data; balance is the closest financial capacity field)
SELECT balance_band, COUNT(*) AS customers, SUM(default_flag) AS defaults,
       ROUND(100.0 * SUM(default_flag) / COUNT(*), 2) AS default_rate_pct
FROM bank_clean GROUP BY balance_band ORDER BY balance_band;

-- Q5 Exposure by segment. Loan amounts do not exist, so the honest exposure proxy is the NUMBER of customers holding a loan product.
SELECT job, SUM(personal_loan_flag) AS personal_loan_holders, SUM(housing_loan_flag) AS housing_loan_holders,
       SUM(CASE WHEN personal_loan_flag = 1 OR housing_loan_flag = 1 THEN 1 ELSE 0 END) AS any_loan_holders
FROM bank_clean GROUP BY job ORDER BY any_loan_holders DESC;

-- Q6 Risk concentration: share of customers versus share of defaults, with lift.
-- A window function (SUM() OVER ()) gives the portfolio totals. Supported by SQLite 3.25+, PostgreSQL, MySQL 8, SQL Server.
SELECT balance_band,
       COUNT(*) AS customers,
       SUM(default_flag) AS defaults,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_of_customers_pct,
       ROUND(100.0 * SUM(default_flag) / SUM(SUM(default_flag)) OVER (), 1) AS share_of_defaults_pct,
       ROUND((1.0 * SUM(default_flag) / COUNT(*)) / (1.0 * SUM(SUM(default_flag)) OVER () / SUM(COUNT(*)) OVER ()), 2) AS lift
FROM bank_clean GROUP BY balance_band ORDER BY balance_band;

-- Q7 Missing or invalid records. Missing values are absent in this file, so we test explicit rules.
SELECT 'null_key_fields' AS check_name,
       SUM(CASE WHEN age IS NULL OR balance IS NULL OR default_raw IS NULL THEN 1 ELSE 0 END) AS records FROM bank_clean
UNION ALL SELECT 'age_outside_18_100', SUM(CASE WHEN age < 18 OR age > 100 THEN 1 ELSE 0 END) FROM bank_clean
UNION ALL SELECT 'default_not_yes_no', SUM(CASE WHEN default_raw NOT IN ('yes','no') THEN 1 ELSE 0 END) FROM bank_clean
UNION ALL SELECT 'unknown_job', SUM(CASE WHEN job = 'unknown' THEN 1 ELSE 0 END) FROM bank_clean
UNION ALL SELECT 'unknown_education', SUM(CASE WHEN education = 'unknown' THEN 1 ELSE 0 END) FROM bank_clean
UNION ALL SELECT 'negative_balance', SUM(CASE WHEN balance < 0 THEN 1 ELSE 0 END) FROM bank_clean
UNION ALL SELECT 'duplicate_customer_id', COUNT(*) - COUNT(DISTINCT customer_id) FROM bank_clean;

-- Q8 Ranking of high risk segments. Requires at least 100 customers so tiny groups do not dominate the ranking.
SELECT segment_type, segment, customers, defaults, ROUND(100.0 * defaults / customers, 2) AS default_rate_pct,
       RANK() OVER (ORDER BY 1.0 * defaults / customers DESC) AS risk_rank
FROM (
  SELECT 'job' AS segment_type, job AS segment, COUNT(*) AS customers, SUM(default_flag) AS defaults FROM bank_clean GROUP BY job
  UNION ALL SELECT 'marital', marital, COUNT(*), SUM(default_flag) FROM bank_clean GROUP BY marital
  UNION ALL SELECT 'balance_band', balance_band, COUNT(*), SUM(default_flag) FROM bank_clean GROUP BY balance_band
  UNION ALL SELECT 'personal_loan', personal_loan, COUNT(*), SUM(default_flag) FROM bank_clean GROUP BY personal_loan
  UNION ALL SELECT 'education', education, COUNT(*), SUM(default_flag) FROM bank_clean GROUP BY education
) t WHERE customers >= 100 ORDER BY risk_rank LIMIT 10;

-- Q9 Monthly default trend: NOT POSSIBLE. The column "month" is the month of the marketing contact, not the date a
-- default occurred. This query is deliberately omitted so no misleading time trend is produced.

-- Q10 Dashboard summary: tier level KPIs (the same rule as the Python and Excel files: negative balance = 2 points, personal loan = 1 point)
WITH scored AS (
  SELECT *, 2 * negative_balance_flag + personal_loan_flag AS risk_points,
         CASE WHEN 2 * negative_balance_flag + personal_loan_flag = 0 THEN 'Low'
              WHEN 2 * negative_balance_flag + personal_loan_flag = 1 THEN 'Medium' ELSE 'High' END AS risk_tier
  FROM bank_clean)
SELECT risk_tier, COUNT(*) AS customers, SUM(default_flag) AS defaults,
       ROUND(100.0 * SUM(default_flag) / COUNT(*), 2) AS default_rate_pct,
       ROUND(100.0 * SUM(default_flag) / (SELECT SUM(default_flag) FROM bank_clean), 1) AS share_of_defaults_pct
FROM scored GROUP BY risk_tier ORDER BY CASE risk_tier WHEN 'Low' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END;

-- Q11 Early warning watchlist: customers with a non defaulted flag but already showing the High tier signals
-- (negative balance AND personal loan). Output is a review list, not a decision.
SELECT customer_id, age, job, balance, personal_loan
FROM bank_clean WHERE default_flag = 0 AND negative_balance_flag = 1 AND personal_loan_flag = 1
ORDER BY balance ASC LIMIT 20;
