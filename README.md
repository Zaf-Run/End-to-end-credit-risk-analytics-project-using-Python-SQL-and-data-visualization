# Credit Risk Analytics and Loan Default Risk Assessment

Two portfolio projects built on one dataset, with SQL, Excel, Python and a Power BI design.
Project 1: portfolio level credit risk analytics and monitoring. Project 2: customer level default risk assessment with a baseline model.

## Read this first
The data supplied is the UCI Bank Marketing sample (4,521 customers of a Portuguese bank telemarketing campaign). It is not a loan portfolio. The only credit field is a customer level `default` flag with an undocumented definition. There are no loan amounts, income, interest rates, dates or payment history. So exposure, LGD, EAD, ECL, NPL classification and time trends are not calculated. Findings describe this sample only and do not represent Bangladeshi banking.

## Business problem
Where do credit defaults concentrate, which indicators could support early warning, and how can a bank act without rejecting good customers?

## Objectives
Measure default rates with uncertainty. Find associated factors without claiming causes. Separate high rate from high count segments. Build and test a transparent tier framework. Test a baseline model honestly. Show the SQL, Excel and dashboard skills a bank risk team uses.

## Dataset source
UCI Machine Learning Repository, Bank Marketing data. Moro, Cortez and Rita (2014), "A data driven approach to predict the success of bank telemarketing", Decision Support Systems. File used: bank.csv (semicolon separated). Check the licence on the UCI page before republishing the data.

## Tools
Python (pandas, scipy, scikit learn, statsmodels, matplotlib), SQLite, Excel (openpyxl generated, 72,680 formulas), Power BI (design only).

## Methodology
Audit and clean with a decision log. Segment analysis with Wilson intervals and Holm adjusted tests. Rule based tiers. Repeated stratified cross validation for logistic regression, a shallow tree and the rule tiers. Excel, SQL and Python results reconciled.

## Key findings (all from the scripts in this repo)
Default flag rate 1.68% (76 of 4,521; 95% interval 1.35% to 2.10%).
Negative balance customers: 8.1% of customers, 56.6% of defaults, default rate 11.75% versus 0.79% for others.
Tiers: High 11.75%, Medium 1.70%, Low 0.64%. About 30% of defaults still fall in Low.
Adjusted odds ratios: negative balance 3.13, personal loan 1.80. Housing loan, age, job and education show no reliable effect.
Logistic regression, repeated cross validation: ROC AUC 0.87, average precision 0.15 (reference 0.017). Reviewing the top 10% of scores catches 59% of defaults with 408 false alarms.
All results are associations. No causal claim is made.

## Dashboard preview
[Dashboard preview](charts/10_dashboard_preview_page1.png)
Python layout prototype, not a Power BI export. Full design: powerbi/powerbi_spec.md.
Screenshots of the finished Power BI report: add here after you build it. Dashboard link: add here after publishing.

## Project structure
```
data/raw/bank.csv                 original file
data/processed/                   bank_clean.csv, audit.json, segment_summary.csv, statistical_tests.csv,
                                  odds_ratios.csv, calibration_table.csv, risk_tiers.csv, results.json
docs/                             project_charter.md, data_dictionary.md/.csv, cleaning_log.md, bangladesh_context.md
python/                           01_clean_and_audit.py, 02_analysis.py, 03_build_excel.py, 04_dashboard_preview.py
sql/                              01_create_table.sql, 02_risk_queries.sql, 03_verified_output_from_test_run.txt, README_sql_setup.md
excel/credit_risk_workbook.xlsx   Raw_Data, Cleaned_Data, Data_Dictionary, Lookups, Risk_Analysis, Summary, Dashboard, Pivot_Guide
charts/                           PNG charts and dashboard prototype
powerbi/powerbi_spec.md           three page design, DAX, validation values
project1_credit_risk_analytics/   report.md, case_study.md
project2_loan_default_assessment/ report.md, case_study.md
```

## Reproduce
1. pip install -r requirements.txt
2. python python/01_clean_and_audit.py
3. python python/02_analysis.py
4. python python/03_build_excel.py (then open in Excel and let it calculate, or recalculate with LibreOffice)
5. python python/04_dashboard_preview.py
6. Load data/processed/bank_clean.csv into SQLite and run sql/02_risk_queries.sql (see sql/README_sql_setup.md)
Pivot tables must be added in Excel by hand (steps in the Pivot_Guide sheet). Power BI must be built in Power BI Desktop.

## What was and was not done
Done and run: cleaning, analysis, models, charts, SQL (tested in SQLite 3.45), Excel (recalculated, zero formula errors, reconciled to Python).
Not done: pivot tables, a Power BI file, any Bangladesh data analysis, ECL, LGD, EAD, NPL classification.

## Limitations
Customer level flag with unknown definition. Only 76 defaults. Balance may follow default. No exposure, dates or payment history. Different country and a marketing context. See the reports for detail.

## References
Moro, Cortez and Rita (2014). Bangladesh Bank sources and their verification status: docs/bangladesh_context.md.
