# Power BI risk dashboard specification

Status: design only. No .pbix file was created, because Power BI Desktop is not available in this environment. charts/10_dashboard_preview_page1.png is a Python layout prototype of page 1. Build the report in Power BI Desktop (free, Windows) by following this file.

## 1. Import and model
1. Get Data > Text/CSV > data/processed/bank_clean.csv. Click Transform Data.
2. Set types: customer_id Whole number. age, balance, default_flag, housing_loan_flag, personal_loan_flag, negative_balance_flag, previously_contacted_flag Whole number. job, marital, education, personal_loan, housing_loan, age_band, balance_band Text. Delete marketing columns (contact, day, month, duration, campaign, pdays, previous, poutcome, y) so nobody uses them by mistake.
3. Close and Apply. One flat table, bank_clean, no relationships are needed. If you later add a segment dimension table, relate it one to many on the segment key.
4. Calculated columns (Modeling > New column):
   Risk Points = 2 * bank_clean[negative_balance_flag] + bank_clean[personal_loan_flag]
   Risk Tier = SWITCH(TRUE(), bank_clean[Risk Points] = 0, "Low", bank_clean[Risk Points] = 1, "Medium", "High")
   Sort Risk Tier by a helper column Tier Order = SWITCH(bank_clean[Risk Tier], "Low", 1, "Medium", 2, 3).
   The weights match Excel and SQL. They are illustrative, not validated.

## 2. Measures (field names checked against bank_clean)
Total Customers = COUNTROWS(bank_clean)
Defaults = SUM(bank_clean[default_flag])
Default Rate = DIVIDE([Defaults], [Total Customers])
Portfolio Default Rate = CALCULATE([Default Rate], ALL(bank_clean))
Share of Customers = DIVIDE([Total Customers], CALCULATE([Total Customers], ALL(bank_clean)))
Share of Defaults = DIVIDE([Defaults], CALCULATE([Defaults], ALL(bank_clean)))
Lift = DIVIDE([Default Rate], [Portfolio Default Rate])
CI Low = VAR n = [Total Customers] VAR p = [Default Rate] VAR z = 1.96 RETURN IF(n = 0, BLANK(), (p + z^2/(2*n) - z*SQRT(p*(1-p)/n + z^2/(4*n^2))) / (1 + z^2/n))
CI High = VAR n = [Total Customers] VAR p = [Default Rate] VAR z = 1.96 RETURN IF(n = 0, BLANK(), (p + z^2/(2*n) + z*SQRT(p*(1-p)/n + z^2/(4*n^2))) / (1 + z^2/n))
Neg Balance Customers = CALCULATE([Total Customers], bank_clean[negative_balance_flag] = 1)
Neg Balance Default Rate = CALCULATE([Default Rate], bank_clean[negative_balance_flag] = 1)
Watchlist Count = CALCULATE([Total Customers], bank_clean[default_flag] = 0, bank_clean[negative_balance_flag] = 1, bank_clean[personal_loan_flag] = 1)
Small Sample Flag = IF([Total Customers] < 100, "Small sample", "")
Median Balance = MEDIAN(bank_clean[balance])
Not buildable: exposure, defaulted exposure, ECL, delinquency, monthly trend, sector or geography. The data has no loan amount, days past due, dates, sector or region.

## 3. Page 1: Executive Risk Overview
Layout: top row of four cards, middle row two charts, bottom row two charts, slicers in a left rail. Keep one blue colour, red only for flagged segments.
Cards: Total Customers, Defaults, Default Rate, Neg Balance Default Rate. Fields: measures above.
Charts: clustered column, Default Rate by balance_band (axis: balance_band; tooltip: Total Customers, Defaults, CI Low, CI High). Column chart, Default Rate by Risk Tier. Clustered column, Share of Customers and Share of Defaults by Risk Tier. Bar chart, Default Rate by job with Small Sample Flag in tooltip.
Slicers: personal_loan, housing_loan, age_band, education. Loan purpose is not in the data. A trend line is not possible.
Interpretation: defaults concentrate in negative balance customers. Decisions supported: where to focus review capacity.
Validate: Total Customers 4,521, Defaults 76, Default Rate 1.68%, Neg Balance Default Rate 11.75%.

## 4. Page 2: Borrower Risk Analysis
Layout: two by two grid plus a table.
Visuals: Default Rate by balance_band (income is unavailable, balance is the proxy). Default Rate by personal_loan and negative_balance_flag as a matrix (rows personal_loan, columns negative_balance_flag, values Default Rate and Total Customers) to show overlap. Risk tier distribution as a 100% stacked bar of Total Customers. Segment contribution: bar of Share of Defaults by job, marital and education using a field parameter or three small bars. Default versus non default comparison: table with Median Balance and Total Customers by default_raw.
Not available: loan size bands, credit history, repayment behaviour.
Interpretation: separate high rate segments from high count segments. Decisions: review criteria, tier rules.
Validate: High tier 366 customers, 43 defaults, 11.75%. Medium 588, 10, 1.70%. Low 3,567, 23, 0.64%. Matrix cell negative balance with loan: 103 customers, 15 defaults, 14.56%.

## 5. Page 3: Portfolio Monitoring
Layout: KPI strip, concentration chart, watchlist table.
Visuals: Customers holding loan products by Risk Tier (a count, not exposure). Concentration chart: Share of Customers versus Share of Defaults by balance_band. Early warning table: customer_id, age, job, balance, personal_loan, filtered to default_flag = 0, negative_balance_flag = 1 and personal_loan_flag = 1, sorted by balance ascending. High risk segment monitor: Default Rate, Lift and Small Sample Flag by segment with conditional formatting (red when Lift is 2 or more).
Early warning indicators supported by the data: overdrawn account, overdrawn plus personal loan. Indicators that need data this file lacks: days past due, balance trend, utilisation change, limit breaches.
Validate: Watchlist Count should equal 88 (103 customers with both flags minus 15 flagged defaults).
Decisions supported: which customers to contact first, where to tighten monitoring.

## 6. Formatting and validation rules
Use one font, one blue, red only for exceptions. No gauges or maps. Add a text box on each page with the data caveat. Validate every card and chart against sql/03_verified_output_from_test_run.txt and the Risk_Analysis sheet in the Excel workbook. If a number differs, check slicer state first.
