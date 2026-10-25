# SQL setup from scratch (SQLite Free)

Option A: browser only. Open sqlime.org (or any online SQLite playground). Upload data/processed/bank_clean.csv. It creates a table from the file. Name the table bank_clean. Paste a query from 02_risk_queries.sql and run it one at a time.
Option B: local, simple. Install DB Browser for SQLite (free). File > New Database. File > Import > Table from CSV file, choose bank_clean.csv, tick "Column names in first line", name the table bank_clean. Open the Execute SQL tab, paste a query, press the play button.
Option C: command line. Install SQLite, then run: sqlite3 risk.db   then   .mode csv   then   .import --skip 1 data/processed/bank_clean.csv bank_clean   then   .mode column   .headers on. The CSV import creates all columns as text, so run 01_create_table.sql first to get proper types.
Standard SQL is used throughout. Window functions (SUM() OVER, RANK() OVER) need SQLite 3.25 or later, which every current install has.
Verify: compare your results with 03_verified_output_from_test_run.txt, which is the real output of these queries on this data. Spot checks: Q1 must return 4,521 customers, 76 defaults, 1.68%.
Expected shapes: Q1 one row (customers, defaults, default_rate_pct). Q2 twelve rows by job. Q4 and Q6 five rows by balance band. Q8 ten rows with risk_rank. Q10 three rows Low, Medium, High.
Calculations split: use SQL for aggregation and checks on large data. Use Excel for the lightweight summary workbook and sharing. Dashboards read the same cleaned table.
