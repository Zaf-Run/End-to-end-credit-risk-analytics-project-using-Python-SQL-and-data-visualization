"""Step 1: data audit and cleaning for bank.csv (UCI Bank Marketing sample, semicolon separated)."""
import pandas as pd, numpy as np, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw = pd.read_csv(f"{ROOT}/data/raw/bank.csv", sep=";")
audit = {"rows": int(raw.shape[0]), "cols": int(raw.shape[1]),
         "duplicates": int(raw.duplicated().sum()),
         "missing_cells": int(raw.isna().sum().sum()),
         "unknown_counts": {c: int((raw[c] == "unknown").sum()) for c in raw.select_dtypes("object")
                            if (raw[c] == "unknown").any()},
         "negative_balance": int((raw.balance < 0).sum()),
         "zero_balance": int((raw.balance == 0).sum()),
         "pdays_minus1": int((raw.pdays == -1).sum()),
         "default_counts": raw["default"].value_counts().to_dict()}
out = {}
for c in ["age", "balance", "duration", "campaign", "pdays", "previous"]:
    q1, q3 = raw[c].quantile([.25, .75]); i = q3 - q1
    out[c] = int(((raw[c] < q1 - 1.5 * i) | (raw[c] > q3 + 1.5 * i)).sum())
audit["iqr_outliers"] = out
audit["balance_p99"] = float(raw.balance.quantile(.99)); audit["balance_max"] = int(raw.balance.max())

df = raw.copy()
df.insert(0, "customer_id", np.arange(1, len(df) + 1))
df["default_flag"] = (df["default"] == "yes").astype(int)
df["housing_loan_flag"] = (df["housing"] == "yes").astype(int)
df["personal_loan_flag"] = (df["loan"] == "yes").astype(int)
df["negative_balance_flag"] = (df["balance"] < 0).astype(int)
df["age_band"] = pd.cut(df.age, [0, 29, 39, 49, 59, 120], labels=["Under 30", "30-39", "40-49", "50-59", "60+"])
df["balance_band"] = pd.cut(df.balance, [-1e9, -1, 0, 500, 2000, 1e9],
                            labels=["1 Negative", "2 Zero", "3 1-500", "4 501-2000", "5 Above 2000"])
df["previously_contacted_flag"] = (df.pdays != -1).astype(int)
df["job"] = df["job"].str.replace(".", "", regex=False)
df = df.rename(columns={"default": "default_raw", "loan": "personal_loan", "housing": "housing_loan"})
df.to_csv(f"{ROOT}/data/processed/bank_clean.csv", index=False)
audit["clean_cols"] = list(df.columns)
json.dump(audit, open(f"{ROOT}/data/processed/audit.json", "w"), indent=1, default=str)
print(json.dumps(audit, indent=1, default=str))
