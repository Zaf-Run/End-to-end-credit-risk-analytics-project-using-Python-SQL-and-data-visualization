# Data dictionary

Generated from the Data_Dictionary sheet of excel/credit_risk_workbook.xlsx. Missing counts are for the raw file. "unknown" placeholders are listed under quality issues.

| Column | Description | Data type | Business meaning | Analytical relevance | Missing values | Potential quality issues |
|---|---|---|---|---|---|---|
| age | Customer age in years | Integer | Life stage proxy | Descriptive only. Excluded from scoring (fairness) | none | Range 19 to 87. 38 IQR outliers, plausible values |
| job | Occupation category | Text (12 levels) | Employment type proxy | Segment analysis. Employment status is not recorded directly | none | 38 'unknown'. Label 'admin.' cleaned to 'admin' |
| marital | Marital status | Text (3 levels) | Household context | Descriptive only. Excluded from scoring (fairness) | none | None found |
| education | Education level | Text (4 levels) | Human capital proxy | Descriptive only | none | 187 'unknown' kept as own category |
| default | Has credit in default (yes/no) | Text yes/no | Customer level default indicator. Contract definition not given | TARGET for risk analysis | none | Only 76 yes. Definition and observation window unknown |
| balance | Average yearly balance in the account | Integer | Deposit account position, not loan exposure | Strongest signal. May be a consequence of default, not a cause | none | Currency unit not stated. 366 negative. Max 71188, heavy right tail |
| housing | Has housing loan (yes/no) | Text yes/no | Mortgage product holder | Exposure proxy (holder count only) | none | No amount, tenor or rate |
| loan | Has personal loan (yes/no) | Text yes/no | Unsecured credit holder | Risk indicator and exposure proxy | none | No amount, tenor or rate |
| contact | Contact channel of last campaign call | Text | Marketing operations | Excluded: not a credit variable | none | 1324 'unknown' |
| day | Day of month of last contact | Integer | Marketing operations | Excluded | none | Not a default date |
| month | Month of last contact | Text | Marketing operations | Excluded. Cannot support a default trend | none | Not a default date |
| duration | Last call length in seconds | Integer | Marketing operations | Excluded: known only after the call (leakage for campaign target) | none | 330 IQR outliers |
| campaign | Contacts made in this campaign | Integer | Marketing operations | Excluded | none | Max 50 |
| pdays | Days since previous campaign contact (-1 = never) | Integer | Marketing operations | Excluded | none | -1 is a code, not a number of days |
| previous | Contacts before this campaign | Integer | Marketing operations | Excluded | none | Max 25 |
| poutcome | Outcome of previous campaign | Text | Marketing operations | Excluded: not repayment behaviour | none | 3705 'unknown' (81.9%) |
| y | Subscribed to term deposit (yes/no) | Text yes/no | Marketing outcome | Excluded: NOT a credit outcome | none | Do not confuse with default |
| default_flag | 1 if default = yes | Derived 0/1 | Target in numeric form | Used in all rates | 0 | Formula in Cleaned_Data |
| negative_balance_flag | 1 if balance below zero | Derived 0/1 | Overdrawn indicator | Risk indicator | 0 | May overlap with the default definition |
| balance_band / age_band | Banded versions | Derived text | Segments for monitoring | Segmentation | 0 | Band edges are analyst choices |
| risk_points / risk_tier | Illustrative score and Low/Medium/High tier | Derived | Transparent rule based tiering | Monitoring segmentation | 0 | Not validated on independent data |
