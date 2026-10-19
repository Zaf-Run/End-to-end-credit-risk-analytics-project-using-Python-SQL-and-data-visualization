"""Step 2: descriptive risk analysis, statistical tests, rule based tiers, baseline models. All outputs are written to disk."""
import pandas as pd, numpy as np, json, os, warnings
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(f"{ROOT}/data/processed/bank_clean.csv")
N, K = len(df), int(df.default_flag.sum()); BASE = K / N
R = {"N": N, "K": K, "base_rate": BASE}
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 130})
BLUE, RED, GREY = "#1F4E79", "#C0392B", "#9AA5B1"

def wilson(k, n, z=1.96):
    if n == 0: return (np.nan, np.nan)
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n))/d; h = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return c - h, c + h

def seg(col, order=None):
    g = df.groupby(col, observed=True).default_flag.agg(["sum", "count"]).rename(columns={"sum": "defaults", "count": "customers"})
    g["default_rate"] = g.defaults / g.customers
    ci = [wilson(a, b) for a, b in zip(g.defaults, g.customers)]
    g["ci_low"] = [c[0] for c in ci]; g["ci_high"] = [c[1] for c in ci]
    g["share_of_customers"] = g.customers / N; g["share_of_defaults"] = g.defaults / K
    g["lift_vs_portfolio"] = g.default_rate / BASE
    g = g.reset_index().rename(columns={col: "segment"}); g.insert(0, "dimension", col)
    return g

dims = ["balance_band", "personal_loan", "housing_loan", "age_band", "job", "marital", "education"]
seg_all = pd.concat([seg(d) for d in dims]); seg_all["segment"] = seg_all["segment"].astype(str)
seg_all.round(4).to_csv(f"{ROOT}/data/processed/segment_summary.csv", index=False)

# ---- statistical tests
tests = []
for d in dims:
    t = pd.crosstab(df[d], df.default_flag); chi2, p, dof, exp = stats.chi2_contingency(t)
    v = np.sqrt(chi2 / (N * (min(t.shape) - 1)))
    row = dict(variable=d, test="chi-square", p_value=p, cramers_v=v, cells_expected_below_5=int((exp < 5).sum()), cells=int(exp.size))
    if t.shape == (2, 2):
        row["test"] = "Fisher exact"; row["p_value"] = stats.fisher_exact(t)[1]
    tests.append(row)
mw = stats.mannwhitneyu(df[df.default_flag == 1].balance, df[df.default_flag == 0].balance)
tests.append(dict(variable="balance (numeric)", test="Mann-Whitney U", p_value=mw.pvalue, cramers_v=np.nan, cells_expected_below_5=np.nan, cells=np.nan))
mwa = stats.mannwhitneyu(df[df.default_flag == 1].age, df[df.default_flag == 0].age)
tests.append(dict(variable="age (numeric)", test="Mann-Whitney U", p_value=mwa.pvalue, cramers_v=np.nan, cells_expected_below_5=np.nan, cells=np.nan))
T = pd.DataFrame(tests)
order = T.p_value.rank(method="first").astype(int); m = len(T)
srt = T.sort_values("p_value").reset_index(drop=True); adj = []; prev = 0
for i, p in enumerate(srt.p_value):
    a = min(1, (m - i) * p); prev = max(prev, a); adj.append(prev)
srt["p_holm_adjusted"] = adj
srt.to_csv(f"{ROOT}/data/processed/statistical_tests.csv", index=False)
R["tests"] = srt.round(6).to_dict("records")
R["median_balance_default"] = float(df[df.default_flag == 1].balance.median()); R["median_balance_nondefault"] = float(df[df.default_flag == 0].balance.median())
R["mean_balance_default"] = float(df[df.default_flag == 1].balance.mean()); R["mean_balance_nondefault"] = float(df[df.default_flag == 0].balance.mean())
R["overall_ci"] = wilson(K, N)
R["balance_total_customers"] = {"mean": float(df.balance.mean()), "median": float(df.balance.median())}
R["age_mean"] = float(df.age.mean()); R["age_median"] = float(df.age.median())
R["pct_loan"] = float(df.personal_loan_flag.mean()); R["pct_housing"] = float(df.housing_loan_flag.mean())
# two-proportion difference CI for the two headline contrasts
def diff_ci(a, b):
    k1, n1 = a; k2, n2 = b; p1, p2 = k1/n1, k2/n2; se = np.sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2); d = p1 - p2
    return d, d - 1.96*se, d + 1.96*se
neg = df.negative_balance_flag == 1
R["diff_neg_vs_nonneg"] = diff_ci((df[neg].default_flag.sum(), neg.sum()), (df[~neg].default_flag.sum(), (~neg).sum()))
ln = df.personal_loan_flag == 1
R["diff_loan_vs_noloan"] = diff_ci((df[ln].default_flag.sum(), ln.sum()), (df[~ln].default_flag.sum(), (~ln).sum()))
# overlap of the two flags
cross = df.groupby(["negative_balance_flag", "personal_loan_flag"]).default_flag.agg(["sum", "count"]).reset_index()
cross["rate"] = cross["sum"] / cross["count"]; R["cross_neg_loan"] = cross.round(4).to_dict("records")

# ---- rule based tiers (a priori logic: overdrawn = 2 points, personal loan = 1 point)
df["risk_points"] = 2 * df.negative_balance_flag + df.personal_loan_flag
df["risk_tier"] = pd.cut(df.risk_points, [-1, 0, 1, 3], labels=["Low", "Medium", "High"])
tier = seg("risk_tier"); R["tiers"] = tier.round(4).to_dict("records")
df[["customer_id", "risk_points", "risk_tier"]].to_csv(f"{ROOT}/data/processed/risk_tiers.csv", index=False)
pts = seg("risk_points"); R["points"] = pts.round(4).to_dict("records")
from sklearn.metrics import roc_auc_score
R["tier_points_auc_insample"] = float(roc_auc_score(df.default_flag, df.risk_points))

# ---- models
from sklearn.model_selection import RepeatedStratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import average_precision_score, brier_score_loss, confusion_matrix, roc_curve, precision_recall_curve
X = pd.DataFrame({"neg": df.negative_balance_flag, "logpos": np.log1p(df.balance.clip(lower=0)), "loan": df.personal_loan_flag,
                  "housing": df.housing_loan_flag, "age": df.age, "job": df.job, "marital": df.marital, "education": df.education})
y = df.default_flag.values
def pipe(model, cats, nums):
    pre = ColumnTransformer([("n", StandardScaler(), nums), ("c", OneHotEncoder(handle_unknown="ignore"), cats)])
    return Pipeline([("pre", pre), ("m", model)])
specs = {
 "Rule tiers (points)": None,
 "Logistic, 2 flags": (pipe(LogisticRegression(C=1.0, max_iter=1000), [], ["neg", "loan"]), ["neg", "loan"]),
 "Logistic, full": (pipe(LogisticRegression(C=0.3, max_iter=2000), ["job", "marital", "education"], ["neg", "logpos", "loan", "housing", "age"]),
                    ["neg", "logpos", "loan", "housing", "age", "job", "marital", "education"]),
 "Decision tree (depth 3)": (pipe(DecisionTreeClassifier(max_depth=3, min_samples_leaf=40, random_state=0), [], ["neg", "logpos", "loan", "housing", "age"]),
                             ["neg", "logpos", "loan", "housing", "age"]),
}
cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=42)
res = {k: dict(auc=[], ap=[], brier=[]) for k in specs}; oof = {k: np.zeros(N) for k in specs}; cnt = np.zeros(N)
for tr, te in cv.split(X, y):
    cnt[te] += 1
    for name, spec in specs.items():
        if spec is None:
            s = df.risk_points.values[te] / 3.0
            # map points to the training default rate for that points value (a simple frequency model, fit on train only)
            tr_rate = pd.Series(y[tr]).groupby(df.risk_points.values[tr]).mean()
            s = pd.Series(df.risk_points.values[te]).map(tr_rate).fillna(BASE).values
        else:
            p, cols = spec; p.fit(X.iloc[tr][cols], y[tr]); s = p.predict_proba(X.iloc[te][cols])[:, 1]
        res[name]["auc"].append(roc_auc_score(y[te], s)); res[name]["ap"].append(average_precision_score(y[te], s))
        res[name]["brier"].append(brier_score_loss(y[te], s)); oof[name][te] += s
for k in oof: oof[k] /= cnt
R["cv_metrics"] = {k: {m: [float(np.mean(v)), float(np.std(v))] for m, v in d.items()} for k, d in res.items()}
R["brier_baseline_constant"] = float(brier_score_loss(y, np.full(N, BASE)))
R["pr_baseline"] = BASE
# out of fold diagnostics for the full logistic model
best = "Logistic, full"; s = oof[best]
R["oof_auc_full"] = float(roc_auc_score(y, s)); R["oof_ap_full"] = float(average_precision_score(y, s))
# review capacity threshold: top 10% highest scores
thr10 = np.quantile(s, 0.90); pred = (s >= thr10).astype(int); tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
R["top10"] = dict(threshold=float(thr10), tp=int(tp), fp=int(fp), fn=int(fn), tn=int(tn), precision=tp/(tp+fp), recall=tp/(tp+fn),
                  f1=2*tp/(2*tp+fp+fn))
# cost based threshold, ILLUSTRATIVE ratio: missing a default costs 10x reviewing a good customer
rows = []
for ratio in [5, 10, 20]:
    ths = np.unique(np.round(np.quantile(s, np.linspace(0.5, 0.999, 300)), 5)); best_c = None
    for t in ths:
        pr = (s >= t).astype(int); tn_, fp_, fn_, tp_ = confusion_matrix(y, pr).ravel(); c = fp_ * 1 + fn_ * ratio
        if best_c is None or c < best_c[0]: best_c = (c, t, tp_, fp_, fn_, tn_)
    allc = ratio * K  # cost of flagging nobody
    rows.append(dict(fn_to_fp_cost_ratio=ratio, threshold=float(best_c[1]), tp=int(best_c[2]), fp=int(best_c[3]), fn=int(best_c[4]), tn=int(best_c[5]),
                     cost=float(best_c[0]), cost_flag_nobody=float(allc), cost_flag_everybody=float(N - K)))
R["cost_thresholds"] = rows
# calibration table (deciles of out of fold score)
q = pd.qcut(pd.Series(s).rank(method="first"), 10, labels=False)
cal = pd.DataFrame({"bin": q, "pred": s, "obs": y}).groupby("bin").agg(mean_pred=("pred", "mean"), obs_rate=("obs", "mean"), n=("obs", "size"), defaults=("obs", "sum")).reset_index()
cal.round(4).to_csv(f"{ROOT}/data/processed/calibration_table.csv", index=False); R["calibration"] = cal.round(4).to_dict("records")
# bootstrap CI for out of fold AUC
rng = np.random.default_rng(1); b = []
for _ in range(1000):
    i = rng.integers(0, N, N)
    if y[i].sum() > 0: b.append(roc_auc_score(y[i], s[i]))
R["oof_auc_ci"] = [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]
# holdout split demonstration (stratified 70/30) for the full model, preprocessing fit on train only
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=7)
p, cols = specs[best]; p.fit(Xtr[cols], ytr); ph = p.predict_proba(Xte[cols])[:, 1]
R["holdout"] = dict(n_test=int(len(yte)), defaults_test=int(yte.sum()), auc=float(roc_auc_score(yte, ph)), ap=float(average_precision_score(yte, ph)), brier=float(brier_score_loss(yte, ph)))
# coefficients (standardised numeric inputs) and unadjusted vs adjusted odds ratios
import statsmodels.api as sm
Z = pd.DataFrame({"negative_balance": X.neg, "personal_loan": X.loan, "housing_loan": X.housing, "age_per_10yrs": X.age / 10.0, "log_positive_balance": X.logpos})
m = sm.Logit(y, sm.add_constant(Z)).fit(disp=0); ci = m.conf_int()
orr = pd.DataFrame({"odds_ratio": np.exp(m.params), "ci_low": np.exp(ci[0]), "ci_high": np.exp(ci[1]), "p_value": m.pvalues}).drop("const")
R["odds_ratios"] = orr.round(4).reset_index().rename(columns={"index": "variable"}).to_dict("records"); orr.round(4).to_csv(f"{ROOT}/data/processed/odds_ratios.csv")
# ---- charts
CH = f"{ROOT}/charts"
def bar_ci(g, title, fname, xlabel, horizontal=False, labels=None):
    g = g.copy(); lab = labels or g.segment.astype(str)
    fig, ax = plt.subplots(figsize=(7.5, 4.2)); x = np.arange(len(g)); r = g.default_rate * 100
    err = [r - g.ci_low * 100, g.ci_high * 100 - r]
    cols = [RED if v > BASE * 100 * 1.5 else BLUE for v in r]
    ax.bar(x, r, color=cols, yerr=err, capsize=3, ecolor="#444", width=.65)
    ax.axhline(BASE * 100, color=GREY, ls="--", lw=1); ax.text(len(g) - .5, BASE * 100 + .2, f"Portfolio {BASE*100:.2f}%", ha="right", color="#555", fontsize=8)
    for xi, (v, n, d) in enumerate(zip(r, g.customers, g.defaults)): ax.text(xi, v + err[1].iloc[xi] + .25, f"{v:.1f}%\n(n={n}, d={d})", ha="center", fontsize=7)
    ax.set_xticks(x); ax.set_xticklabels(lab, rotation=0 if len(g) < 7 else 40, ha="center" if len(g) < 7 else "right", fontsize=8)
    ax.set_ylabel("Default rate (%)"); ax.set_xlabel(xlabel); ax.set_title(title, loc="left", fontsize=11, fontweight="bold"); ax.set_ylim(0, max(r + err[1]) * 1.35)
    fig.tight_layout(); fig.savefig(f"{CH}/{fname}"); plt.close(fig)
S = lambda d: seg_all[seg_all.dimension == d].copy()
bar_ci(S("balance_band"), "Default rate by account balance band", "01_default_by_balance_band.png", "Balance band (currency units as recorded)", labels=["Negative", "Zero", "1 to 500", "501 to 2000", "Above 2000"])
bar_ci(S("personal_loan"), "Default rate by personal loan status", "02_default_by_personal_loan.png", "Has personal loan", labels=["No", "Yes"])
g = S("job").sort_values("default_rate", ascending=False); bar_ci(g, "Default rate by job (small groups, wide intervals)", "03_default_by_job.png", "Job category")
bar_ci(S("age_band"), "Default rate by age band", "04_default_by_age_band.png", "Age band")
bar_ci(S("marital"), "Default rate by marital status", "05_default_by_marital.png", "Marital status")
bar_ci(tier.assign(segment=tier.segment.astype(str)), "Default rate by rule based risk tier", "06_default_by_risk_tier.png", "Risk tier (illustrative rules)")
# concentration chart: share of customers vs share of defaults
fig, ax = plt.subplots(figsize=(7.5, 4.2)); b = S("balance_band"); x = np.arange(len(b)); w = .38
ax.bar(x - w/2, b.share_of_customers * 100, w, color=GREY, label="Share of customers"); ax.bar(x + w/2, b.share_of_defaults * 100, w, color=RED, label="Share of defaults")
ax.set_xticks(x); ax.set_xticklabels(["Negative", "Zero", "1 to 500", "501 to 2000", "Above 2000"], fontsize=8); ax.set_ylabel("%"); ax.legend(frameon=False, fontsize=8)
ax.set_title("Concentration: customers versus defaults by balance band", loc="left", fontsize=11, fontweight="bold"); fig.tight_layout(); fig.savefig(f"{CH}/07_concentration_balance.png"); plt.close(fig)
# balance distribution
fig, ax = plt.subplots(figsize=(7.5, 4.2)); clipv = df.balance.clip(-3500, 8000)
ax.hist(clipv[df.default_flag == 0], bins=60, density=True, alpha=.6, color=BLUE, label="Non default"); ax.hist(clipv[df.default_flag == 1], bins=30, density=True, alpha=.6, color=RED, label="Default")
ax.axvline(0, color="#333", lw=.8); ax.set_xlabel("Balance (clipped to -3,500 and 8,000 for display only)"); ax.set_ylabel("Density"); ax.legend(frameon=False)
ax.set_title("Balance distribution by default status", loc="left", fontsize=11, fontweight="bold"); fig.tight_layout(); fig.savefig(f"{CH}/08_balance_distribution.png"); plt.close(fig)
# ROC and PR and calibration
fig, axs = plt.subplots(1, 3, figsize=(13, 4))
for name in ["Logistic, full", "Logistic, 2 flags", "Decision tree (depth 3)", "Rule tiers (points)"]:
    f, t, _ = roc_curve(y, oof[name]); axs[0].plot(f, t, label=f"{name} ({roc_auc_score(y, oof[name]):.2f})")
    pr, rc, _ = precision_recall_curve(y, oof[name]); axs[1].plot(rc, pr, label=name)
axs[0].plot([0, 1], [0, 1], color=GREY, ls="--"); axs[0].set_title("ROC (pooled out of fold scores)", fontsize=10, fontweight="bold"); axs[0].set_xlabel("False positive rate"); axs[0].set_ylabel("True positive rate"); axs[0].legend(frameon=False, fontsize=7)
axs[1].axhline(BASE, color=GREY, ls="--"); axs[1].set_title("Precision recall (pooled out of fold)", fontsize=10, fontweight="bold"); axs[1].set_xlabel("Recall"); axs[1].set_ylabel("Precision")
axs[2].plot(cal.mean_pred * 100, cal.obs_rate * 100, "o-", color=BLUE); mx = max(cal.mean_pred.max(), cal.obs_rate.max()) * 100; axs[2].plot([0, mx], [0, mx], color=GREY, ls="--")
axs[2].set_title("Calibration by decile (full logistic)", fontsize=10, fontweight="bold"); axs[2].set_xlabel("Mean predicted (%)"); axs[2].set_ylabel("Observed default rate (%)")
fig.tight_layout(); fig.savefig(f"{CH}/09_model_diagnostics.png"); plt.close(fig)
json.dump(R, open(f"{ROOT}/data/processed/results.json", "w"), indent=1, default=str)
print(json.dumps({k: R[k] for k in ["N", "K", "base_rate", "overall_ci", "diff_neg_vs_nonneg", "diff_loan_vs_noloan", "cross_neg_loan", "tiers", "cv_metrics", "oof_auc_full", "oof_auc_ci", "oof_ap_full", "top10", "cost_thresholds", "holdout", "odds_ratios", "brier_baseline_constant", "tests"]}, indent=1, default=str))
