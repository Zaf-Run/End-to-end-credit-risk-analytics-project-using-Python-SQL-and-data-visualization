"""Static dashboard PREVIEW built in matplotlib. It is a layout prototype of the proposed Power BI page 1, NOT a Power BI export."""
import pandas as pd, numpy as np, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = pd.read_csv(f"{ROOT}/data/processed/segment_summary.csv"); df = pd.read_csv(f"{ROOT}/data/processed/bank_clean.csv")
t = pd.read_csv(f"{ROOT}/data/processed/risk_tiers.csv")
N, K = len(df), df.default_flag.sum(); BASE = K / N
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
fig = plt.figure(figsize=(13, 7.4), facecolor="white"); gs = fig.add_gridspec(3, 4, height_ratios=[.55, 2, 2], hspace=.55, wspace=.35)
fig.suptitle("Executive Risk Overview (prototype, not a Power BI export)", x=.02, ha="left", fontsize=14, fontweight="bold", color="#1F4E79")
tiles = [("Customers", f"{N:,}"), ("Defaulted customers", f"{K}"), ("Default rate", f"{BASE*100:.2f}%"), ("Negative balance share of defaults", f"{df[df.negative_balance_flag==1].default_flag.sum()/K*100:.1f}%")]
for i, (a, b) in enumerate(tiles):
    ax = fig.add_subplot(gs[0, i]); ax.axis("off"); ax.text(0, .75, a, fontsize=9, color="#595959"); ax.text(0, .15, b, fontsize=20, fontweight="bold", color="#1F4E79")
def barpanel(pos, d, title, labels=None, hl=1.5):
    ax = fig.add_subplot(pos); g = s[s.dimension == d].reset_index(drop=True); r = g.default_rate * 100
    ax.bar(range(len(g)), r, color=["#C0392B" if v > BASE*100*hl else "#1F4E79" for v in r]); ax.axhline(BASE*100, color="#9AA5B1", ls="--", lw=1)
    ax.set_xticks(range(len(g))); ax.set_xticklabels(labels or g.segment, fontsize=7, rotation=0 if len(g) < 6 else 35, ha="center" if len(g) < 6 else "right")
    for i, v in enumerate(r): ax.text(i, v + .2, f"{v:.1f}%", ha="center", fontsize=7)
    ax.set_title(title, fontsize=9, fontweight="bold", loc="left"); ax.set_ylabel("Default rate %", fontsize=8); return ax
barpanel(gs[1, 0:2], "balance_band", "Default rate by balance band", ["Negative", "Zero", "1 to 500", "501 to 2000", "Above 2000"])
import json; g = pd.DataFrame(json.load(open(f"{ROOT}/data/processed/results.json"))["tiers"]); ax = fig.add_subplot(gs[1, 2])
ax.bar(g.segment, g.default_rate * 100, color=["#2E8B57", "#E0A526", "#C0392B"]); ax.set_title("Default rate by risk tier", fontsize=9, fontweight="bold", loc="left")
for i, v in enumerate(g.default_rate * 100): ax.text(i, v + .2, f"{v:.1f}%", ha="center", fontsize=7)
ax.set_ylabel("Default rate %", fontsize=8)
ax = fig.add_subplot(gs[1, 3]); ax.bar(g.segment, g.share_of_customers * 100, color="#9AA5B1", width=.4, label="Customers", align="edge"); ax.bar(g.segment, g.share_of_defaults * 100, color="#C0392B", width=-.4, label="Defaults", align="edge")
ax.set_title("Share of customers vs defaults", fontsize=9, fontweight="bold", loc="left"); ax.legend(frameon=False, fontsize=7); ax.set_ylabel("%", fontsize=8)
barpanel(gs[2, 0:2], "job", "Default rate by job (n varies, read with intervals)")
barpanel(gs[2, 2], "personal_loan", "By personal loan", ["No", "Yes"]); barpanel(gs[2, 3], "marital", "By marital status")
fig.text(.02, .01, "Data: UCI Bank Marketing sample (4,521 customers). 'default' is a customer level flag. No loan amounts, dates or income exist, so exposure and time trend visuals are not available.", fontsize=7, color="#595959")
fig.savefig(f"{ROOT}/charts/10_dashboard_preview_page1.png", dpi=140, bbox_inches="tight")
