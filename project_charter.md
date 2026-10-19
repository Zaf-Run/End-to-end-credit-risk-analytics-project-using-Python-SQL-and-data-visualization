# Project Charter: Credit Risk Analytics and Loan Default Risk Assessment

## Two projects, one dataset
Project 1, Credit Risk Analytics, looks at the whole portfolio. It covers segmentation, concentration, early warning indicators, SQL, Excel and a dashboard design.
Project 2, Loan Default Risk Assessment, looks at the individual customer. It covers default drivers, statistical validation and a baseline prediction model.
Both use the same file, so data work is shared. The folders keep the two storylines separate.

## Banking context
Banks lend against uncertain repayment. A Credit Risk Analytics team measures how much loss the portfolio may carry and where it sits. A Credit Portfolio Monitoring team watches the book after approval and raises early warnings.

## Business problem
Which customers show signs of credit distress, how concentrated are those signs, and what can a bank monitor early without rejecting good customers?

## Objectives
1. Measure the observed default rate and its uncertainty.
2. Identify customer characteristics associated with default.
3. Find where defaults concentrate, separating high rate segments from high count segments.
4. Build a transparent low, medium and high risk framework and test it.
5. Test a simple baseline model honestly, including its limits.
6. Package SQL, Excel, Python and a dashboard design for a bank risk audience.

## Key research questions
The eight questions in the brief are answered in the reports. Questions that need loan amounts, income, interest rates, debt to income ratio, loan purpose or dates are marked "not answerable with this data".

## Stakeholders
Head of Credit Risk, Credit Risk Analytics team, Credit Portfolio Monitoring team, Retail Credit Policy, Model Validation, Compliance and Internal Audit.

## Analytical scope
In scope: descriptive analysis of 4,521 customers, segment default rates, concentration, rule based tiers, baseline logistic regression and tree, SQL, Excel, dashboard design.
Out of scope: ECL under IFRS 9, regulatory provisioning, loan level exposure, time trends, causal claims.

## Dataset (important)
File: bank.csv from the UCI Bank Marketing data (a Portuguese bank telemarketing campaign), 4,521 rows, 17 columns, semicolon separated.
It is a marketing dataset. The only credit field is `default` (has credit in default, yes or no). It is a customer level flag. Its contract definition, observation window and currency are not documented.
It does not represent the Bangladeshi banking sector. All findings are about this sample only.
Citation: Moro, Cortez and Rita (2014), "A data driven approach to predict the success of bank telemarketing", Decision Support Systems. UCI lists the licence on the dataset page. Confirm it before republishing the data.
The attached scoring.jpg is a generic credit score gauge. It is not used in calculations.

## Expected deliverables
Cleaned data, data dictionary, cleaning log, Python scripts (run), SQL scripts (tested in SQLite), Excel workbook (72,680 formulas, zero errors), charts, dashboard prototype and Power BI specification, two reports, two case studies, README.

## Assumptions
1. `default = yes` is treated as the customer level default indicator as recorded by the source bank.
2. One row is one customer. No customer appears twice (no identifier exists, so this cannot be proven).
3. Every rate uses all customers in the segment as the denominator.
4. `unknown` is kept as its own category.

## Limitations
Only 76 defaults. Small segments have wide intervals. Balance may be a result of default, not a cause. No time dimension. No loan amounts. Marketing columns are not credit variables. Findings cannot be transferred to another bank or to Bangladesh without validation.

## Success criteria
Every number traces to a script or formula that was run. Excel, SQL and Python agree. Limitations are stated next to the findings. Nothing claims causation, savings or regulatory compliance.

## Concepts: definitions and what this data can support
Credit risk: the risk of loss when a borrower fails to meet obligations. Supported only as a descriptive view.
Probability of default (PD): the likelihood of default over a stated horizon. This data gives an observed default share, a crude PD proxy, with no known horizon. A model output here is a score, not a calibrated PD.
Loss given default (LGD): the share of exposure lost after default, after recoveries. Not calculable. No recoveries, collateral or exposure exist.
Exposure at default (EAD): the amount owed at default. Not calculable. Balance is a deposit balance, not a loan balance.
Expected credit loss (ECL): conceptually PD x LGD x EAD. Not calculable here because two of three inputs are missing. Even with all inputs, an IFRS 9 estimate needs staging, forward looking information, discounting and governance. The formula alone is not a regulatory estimate.
Delinquency: a missed or late payment. Not observable. There are no payment dates or days past due.
Loan default: a formal event defined by contract and regulation, such as a missed payment beyond a set number of days or unlikeliness to pay. The source definition is unknown, so this project says "default flag" and not "loan default" in strict terms.
Non performing loans (NPLs): loans classified as non performing under a regulator's rules, such as Bangladesh Bank's classification circulars. A default flag is not an NPL label. Not calculable.
Credit scoring: ranking customers by risk using data. A rule based tier is built here and tested, with caveats.
Credit portfolio concentration risk: risk from too much exposure to one borrower, sector or segment. Only customer count concentration is measurable. Exposure concentration is not.
