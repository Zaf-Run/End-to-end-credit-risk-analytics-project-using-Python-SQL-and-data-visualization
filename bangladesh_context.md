# Banking context and Bangladesh relevance

Read this first: the dataset is a Portuguese bank telemarketing sample. It does not describe Bangladeshi borrowers. This note links the analytical method to the work of a risk team in Bangladesh. It does not transfer the findings.

## Verification status of sources
I searched on 19 October 2026. I could open the official Bangladesh Bank (BB) text of one document directly. Other items were confirmed through news reports or copies hosted elsewhere. Each is labelled. Before citing any of them in a CV or interview, open the circular on bb.org.bd and check the current wording, because BB revises these rules often.

## Sources
1. BRPD Circular Letter No. 22, 13 October 2025, "Loan Classification and Provisioning". Official BB site: https://www.bb.org.bd/mediaroom/circulars/brpd/oct132025brpdl22e.pdf . Status: opened the BB text. Paragraph 2 states that banks keep provisions of 1% for standard loans and 5% for Special Mention Accounts (SMA) under BRPD Circular No. 15 of 27 November 2024 and BRPD Circular No. 05 of 25 June 2025. It sets 1% for all unclassified short term agricultural credit and cottage, micro and small enterprise credit. It says all other instructions of Circular 15/2024 and later changes remain.
2. BRPD Circular No. 15, 27 November 2024, "Loan Classification and Provisioning". Status: date and title confirmed through Circular Letter 22 and through a bank training deck, not through the original PDF. Open the original on bb.org.bd.
3. BRPD Circular No. 05, 25 June 2025, on forms for loan classification and provisioning reporting (CL forms). Status: seen in a copy hosted on a third party site (crislbd.com), not on bb.org.bd.
4. BRPD Circular No. 05, 3 March 2026, on starting continuous loan renewal at least two months before expiry. Status: reported by BSS on 3 March 2026, https://www.bssnews.net/business/365549 . Original not opened.
5. Overdue timeline change for term loans (three months to become overdue, phased from 30 September 2024 and 31 March 2025). Status: The Business Standard report, https://www.tbsnews.net/node/826041 . Secondary source. Confirm against the circular.
6. A news report says BB later set 0.50% provisioning for unclassified short term agriculture and CMSME loans until 31 December 2026, superseding Circular Letter 22. Status: one trade publication, no date shown, https://apparelresources.com/business-news/manufacturing/bangladesh-bank-cuts-provisioning-norms-spur-lending/ . Not confirmed on the BB site. Treat as unverified. Check which rate is current.
7. Guidelines on Internal Credit Risk Rating (ICRR) System for Banks, October 2018. Status: reported by The Financial Express, 4 November 2018, https://thefinancialexpress.com.bd/economy/bb-issues-new-guidelines-for-credit-risk-management-1540914597 . It is described as having sector specific models. Original and any later revision not opened.
8. Single borrower and large loan exposure limits. Status: news reports describe a 2022 tightening (Financial Express, https://thefinancialexpress.com.bd/economy/bangladesh/no-bank-can-lend-more-than-25pc-of-its-capital-to-any-company-or-group-1642433055 ) and a later relaxation linked to a bank's NPL ratio (The Business Standard, https://www.tbsnews.net/node/1439296 , date not confirmed). The limits have changed more than once. Do not quote percentages without reading the current guideline.

## What matters for a risk team
Credit risk assessment: BB expects banks to grade borrowers (ICRR). Our rule tiers and logistic baseline are the analytical cousin of a grading model. They would need local data and validation.
Loan classification and provisioning: classification depends on days past due, loan type and qualitative judgement. It needs payment dates and amounts. This dataset has neither, so it cannot produce a classification or an NPL ratio. A default flag is not an NPL.
Concentration: BB limits exposure to single borrowers and groups. This dataset has no exposure, so it can show only customer count concentration, such as 8.1% of customers holding 56.6% of flagged defaults.
Portfolio monitoring and early warning: monthly reporting to BB (CL forms) means a bank needs clean monthly data. The Power BI design in this repo shows what a monitoring page could contain once dates and amounts exist.
Responsible lending: the framework deliberately leaves out age and marital status, and recommends human review before any adverse decision.
Model governance: a model built on another country's data must be validated locally, tested for stability and calibration, documented, and monitored. See the limitations in Project 2.

## What is a requirement and what is a recommendation
Requirements: the BB circulars above, once their current text is confirmed.
Recommendations: everything else in this repo, including early warning indicators, tiers and monitoring KPIs. They are analytical suggestions, not regulatory text.
