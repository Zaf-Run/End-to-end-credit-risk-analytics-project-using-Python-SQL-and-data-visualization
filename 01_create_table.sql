-- Run once in SQLite. Loads nothing by itself: import data/processed/bank_clean.csv into a table named bank_clean
-- (DB Browser for SQLite: File > Import > Table from CSV file; tick "Column names in first line").
-- Or use the SQLite command line:  .mode csv   then   .import --skip 1 data/processed/bank_clean.csv bank_clean
CREATE TABLE IF NOT EXISTS bank_clean (
  customer_id INTEGER, age INTEGER, job TEXT, marital TEXT, education TEXT, default_raw TEXT,
  balance INTEGER, housing_loan TEXT, personal_loan TEXT, contact TEXT, day INTEGER, month TEXT,
  duration INTEGER, campaign INTEGER, pdays INTEGER, previous INTEGER, poutcome TEXT, y TEXT,
  default_flag INTEGER, housing_loan_flag INTEGER, personal_loan_flag INTEGER, negative_balance_flag INTEGER,
  age_band TEXT, balance_band TEXT, previously_contacted_flag INTEGER
);
