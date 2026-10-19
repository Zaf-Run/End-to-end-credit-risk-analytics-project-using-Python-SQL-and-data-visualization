# Data audit and cleaning log

Script: python/01_clean_and_audit.py. Output: data/processed/bank_clean.csv and audit.json.

## Audit results (all from the script)
Rows 4,521. Columns 17. Duplicate rows 0. Missing cells 0.
Placeholder category "unknown": job 38, education 187, contact 1,324, poutcome 3,705.
Target `default`: no 4,445, yes 76 (1.68%). Class imbalance is severe, about 58 to 1.
Balance: 366 negative, 357 zero, median 444, mean 1,422.66, 99th percentile 14,194.6, maximum 71,188.
IQR outlier screen: age 38, balance 506, duration 330, campaign 318, pdays 816, previous 816.
`pdays` equals -1 for 3,705 rows. This is a code for "never contacted", not a number.

## Decisions and reasons
1. Kept all rows. No duplicates and no invalid values were found, so deletion was not justified.
2. Did not remove or cap outliers. Large balances are plausible customers. Negative balances are the key risk signal, so trimming would destroy information. Capping is used only for chart display and is labelled.
3. Did not impute. There are no true missing values. "unknown" stays as its own category because dropping it would bias small groups, and the missingness may itself be informative.
4. Cleaned the label "admin." to "admin". Formatting only.
5. Created a synthetic `customer_id` (row number). The source has no identifier. It is excluded from any model.
6. Created flags and bands: default_flag, personal_loan_flag, housing_loan_flag, negative_balance_flag, age_band, balance_band. Band edges are analyst choices and are documented.
7. Renamed the age band "<30" to "Under 30" after a test showed Excel reads "<30" as an operator inside COUNTIFS. The Excel and Python numbers now agree exactly.
8. Excluded marketing fields from risk analysis and models: contact, day, month, duration, campaign, pdays, previous, poutcome, y. They describe a sales campaign. `duration` is known only after the call. `y` is a deposit subscription, not a credit outcome.
9. Excluded age and marital status from the scoring framework for fairness and responsible lending reasons. They are reported descriptively only.

## Leakage and circularity
Balance may be a consequence of being in default (an overdrawn account may trigger the flag). A negative balance then predicts default partly by construction. Treat the balance signal as a monitoring indicator, not as proof of cause. The source definition would settle this.
