"""
First regression baseline on the FAIR-MAST level 2 shot table.

Target : W_MHD at the time of peak plasma current (generic_energy_current_max), fitted as log W.
Inputs : quantities at the same time slice (peak Ip):
         |Ip|, |B_T|, line-integrated density, P_heat = P_ohm + P_NBI, R_geo, a, kappa
Models : mean-only reference, log-linear OLS (power-law scaling form), log-quadratic ridge,
         random forest, histogram gradient boosting (all scikit-learn)
CV     : random 5-fold vs. leave-one-campaign-out (M5..M9)

Run from the repo root after the shot table has been downloaded (eda.ipynb cell 3):
    python baseline.py
Outputs: results/*.csv, figures/baseline_*.png
"""
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import KFold, LeaveOneGroupOut, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

SEED = 0
N_JOBS = int(os.environ.get("N_JOBS", -1))   # set N_JOBS=1 where multiprocessing is unavailable
Path("results").mkdir(exist_ok=True)
Path("figures").mkdir(exist_ok=True)

# ----------------------------------------------------------------------------- data
shots = pd.read_parquet("fairmast/shots_level2.parquet")


def nbi_power_at_peak_ip(df):
    """Total NBI power (MW) at peak Ip.

    The published column `nbi_power_max_current` is a name collision (see column_classification.md 10.1).
    Checked on the real table: it equals the SS-beam power exactly on SS-only shots (i.e. it is the total there)
    and is ~44% of peak power on two-beam shots (i.e. SW power only). So: total = SS + SW, unless the column
    already equals SS. Missing beam power means no beam -> 0.
    """
    col, ss = df["nbi_power_max_current"], df["nbi_power_ss_max_current"]
    same = col.notna() & ss.notna() & np.isclose(col, ss, rtol=1e-3)
    return pd.Series(np.where(same, col, ss.fillna(0) + col.fillna(0)), index=df.index)


d = pd.DataFrame({
    "shot_id": shots["shot_id"],
    "campaign": shots["campaign"],
    "W_kJ": shots["generic_energy_current_max"] / 1e3,           # J -> kJ
    "Ip_MA": shots["plasma_max_current"].abs() / 1e3,            # kA -> MA (sign = direction)
    "Bt_T": shots["generic_toroidal_max_current"].abs(),         # sign = field direction
    "nL_1e20m2": shots["thomson_density_line_max_current"] / 1e20,  # CO2 interferometer line integral
    "P_ohm_MW": shots["ohmnic_heating_max_current"],
    "P_nbi_MW": nbi_power_at_peak_ip(shots),
    "R_m": shots["generic_geo_radius_max_current"],
    "a_m": shots["generic_minor_radius_max_current"],
    "kappa": shots["generic_plasma_elongation_max_current"],
})
d["P_heat_MW"] = d["P_ohm_MW"] + d["P_nbi_MW"]

n0 = len(d)
keep = (shots["shot_useful"] == 1) & (shots["shot_abort"] != 1)
keep &= d["campaign"].isin(["M5", "M6", "M7", "M8", "M9"])
keep &= d["W_kJ"] >= 1                                            # drop failed / near-zero EFIT energies
for c in ["Ip_MA", "Bt_T", "nL_1e20m2", "P_ohm_MW", "R_m", "a_m", "kappa"]:
    keep &= d[c] > 0                                              # logs need positive values; P_ohm<0 = transient
d = d[keep].dropna().reset_index(drop=True)

FEATURES = ["Ip_MA", "Bt_T", "nL_1e20m2", "P_heat_MW", "R_m", "a_m", "kappa"]
X = np.log(d[FEATURES])
X.columns = [f"log_{c}" for c in FEATURES]
y = np.log(d["W_kJ"])
groups = d["campaign"]
print(f"shots: {n0} in table -> {len(d)} after filters")
print(d.groupby("campaign").size().to_dict())

# ----------------------------------------------------------------------------- models
MODELS = {
    "Mean only": DummyRegressor(),
    "Log-linear (scaling law)": LinearRegression(),
    "Log-quadratic ridge": make_pipeline(PolynomialFeatures(2, include_bias=False), StandardScaler(),
                                         RidgeCV(alphas=np.logspace(-3, 3, 13))),
    "Random forest": RandomForestRegressor(n_estimators=400, min_samples_leaf=5, n_jobs=N_JOBS, random_state=SEED),
    "Gradient boosting": HistGradientBoostingRegressor(max_iter=500, learning_rate=0.05, random_state=SEED),
}
SCHEMES = {
    "Random 5-fold": (KFold(5, shuffle=True, random_state=SEED), None),
    "Leave one campaign out": (LeaveOneGroupOut(), groups),
}


def scores(y_true, y_pred):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    return dict(r2=r2_score(y_true, y_pred), rmse_log=rmse,
                typical_error_pct=100 * (np.exp(rmse) - 1),
                median_abs_error_pct=100 * np.median(np.abs(np.exp(y_pred - y_true) - 1)))


rows, oof = [], {}
for scheme, (cv, g) in SCHEMES.items():
    for name, model in MODELS.items():
        pred = cross_val_predict(model, X, y, cv=cv, groups=g, n_jobs=1)
        oof[(scheme, name)] = pred
        rows.append(dict(scheme=scheme, model=name, fold="all", n=len(y), **scores(y, pred)))
        if scheme == "Leave one campaign out":
            for camp in sorted(groups.unique()):
                m = (groups == camp).values
                rows.append(dict(scheme=scheme, model=name, fold=camp, n=int(m.sum()), **scores(y[m], pred[m])))
metrics = pd.DataFrame(rows)
metrics.to_csv("results/baseline_metrics.csv", index=False)
print("\n", metrics[metrics.fold == "all"].pivot(index="model", columns="scheme", values="r2").round(3))

# ----------------------------------------------------------------------------- scaling-law exponents
ols = LinearRegression().fit(X, y)
rng = np.random.default_rng(SEED)
boot = np.array([LinearRegression().fit(X.iloc[i], y.iloc[i]).coef_
                 for i in (rng.integers(0, len(y), len(y)) for _ in range(500))])
# IPB98(y,2) tau_E ~ Ip^0.93 B^0.15 n^0.41 P^-0.69 R^1.97 kappa^0.78 eps^0.58 (eps = a/R);  W = tau_E * P
ipb98_W = {"Ip_MA": 0.93, "Bt_T": 0.15, "nL_1e20m2": 0.41, "P_heat_MW": 1 - 0.69,
           "R_m": 1.97 - 0.58, "a_m": 0.58, "kappa": 0.78}
expo = pd.DataFrame({
    "feature": FEATURES,
    "exponent": ols.coef_,
    "ci95_low": np.percentile(boot, 2.5, axis=0),
    "ci95_high": np.percentile(boot, 97.5, axis=0),
    "IPB98y2_implied_for_W": [ipb98_W[f] for f in FEATURES],
})
expo.to_csv("results/scaling_exponents.csv", index=False)
print("\n", expo.round(2).to_string(index=False))

# per-campaign exponent stability
per_camp = pd.DataFrame({c: LinearRegression().fit(X[groups == c], y[groups == c]).coef_
                         for c in sorted(groups.unique())}, index=FEATURES).T
per_camp.to_csv("results/scaling_exponents_by_campaign.csv")

# ----------------------------------------------------------------------------- permutation importance (held-out campaigns)
imp = []
for tr, te in LeaveOneGroupOut().split(X, y, groups):
    m = clone(MODELS["Gradient boosting"]).fit(X.iloc[tr], y.iloc[tr])
    r = permutation_importance(m, X.iloc[te], y.iloc[te], n_repeats=10, random_state=SEED, scoring="r2")
    imp.append(r.importances_mean)
importance = pd.Series(np.mean(imp, axis=0), index=FEATURES).sort_values(ascending=False)
importance.to_csv("results/gb_permutation_importance.csv", header=["mean_drop_in_r2"])
print("\nGB permutation importance (mean drop in held-out R2):\n", importance.round(3).to_string())

# ----------------------------------------------------------------------------- figures
plt.rcParams.update({"font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9, "legend.fontsize": 8,
                     "xtick.labelsize": 8, "ytick.labelsize": 8, "axes.spines.top": False,
                     "axes.spines.right": False, "savefig.dpi": 300})
CAMP_COLORS = dict(zip(sorted(groups.unique()), plt.cm.viridis(np.linspace(0, 0.9, groups.nunique()))))
order = list(MODELS)

# (1) model comparison: R2 under random K-fold vs. per held-out campaign
fig, ax = plt.subplots(figsize=(6.5, 3.4))
for i, name in enumerate(order):
    camp = metrics[(metrics.model == name) & (metrics.scheme == "Leave one campaign out") & (metrics.fold != "all")]
    for _, r in camp.iterrows():
        ax.scatter(r.r2, i + 0.12, color=CAMP_COLORS[r.fold], s=22, zorder=3)
    lo = metrics[(metrics.model == name) & (metrics.scheme == "Leave one campaign out") & (metrics.fold == "all")].r2.iloc[0]
    kf = metrics[(metrics.model == name) & (metrics.scheme == "Random 5-fold") & (metrics.fold == "all")].r2.iloc[0]
    ax.scatter(kf, i - 0.12, marker="D", color="0.2", s=26, zorder=3)
    ax.scatter(lo, i + 0.12, marker="|", color="k", s=160, zorder=4)
ax.set_yticks(range(len(order)), order)
ax.invert_yaxis()
ax.axvline(0, color="0.7", lw=0.8)
ax.set_xlim(-0.15, 1.0)
ax.set_xlabel("R² on log W_MHD (higher = better)")
ax.set_title("Held-out campaigns score below random folds for every model", loc="left")
handles = [plt.Line2D([], [], marker="D", ls="", color="0.2", label="random 5-fold"),
           plt.Line2D([], [], marker="|", ls="", color="k", markersize=10, label="leave-one-campaign-out, pooled")]
handles += [plt.Line2D([], [], marker="o", ls="", color=c, label=f"held-out {k}") for k, c in CAMP_COLORS.items()]
ax.legend(handles=handles, frameon=False, loc="lower left", bbox_to_anchor=(1.0, 0.0))
fig.tight_layout()
fig.savefig("figures/baseline_model_comparison.png", bbox_inches="tight")

# (2) predicted vs measured, leave-one-campaign-out, scaling law vs gradient boosting
fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.5), sharex=True, sharey=True)
W = d["W_kJ"].values
lim = (W.min() * 0.8, W.max() * 1.25)
for ax, name in zip(axes, ["Log-linear (scaling law)", "Gradient boosting"]):
    pred = np.exp(oof[("Leave one campaign out", name)])
    for camp, c in CAMP_COLORS.items():
        m = (groups == camp).values
        ax.scatter(W[m], pred[m], s=4, alpha=0.35, color=c, lw=0, label=camp)
    ax.plot(lim, lim, color="k", lw=0.8)
    s = metrics[(metrics.model == name) & (metrics.scheme == "Leave one campaign out") & (metrics.fold == "all")].iloc[0]
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_title(f"{name}: R² = {s.r2:.2f}", loc="left")
    ax.set_xlabel("Measured W_MHD at peak Ip (kJ)")
axes[0].set_ylabel("Predicted, campaign held out (kJ)")
axes[1].legend(frameon=False, markerscale=3, loc="lower right", title="campaign", title_fontsize=8)
fig.tight_layout()
fig.savefig("figures/baseline_pred_vs_true.png", bbox_inches="tight")

# (3) fitted exponents vs IPB98(y,2)-implied
fig, ax = plt.subplots(figsize=(6.0, 3.4))
yy = np.arange(len(FEATURES))
for camp, c in CAMP_COLORS.items():                       # each campaign fitted on its own
    ax.scatter(per_camp.loc[camp, FEATURES], yy + 0.22, s=12, color=c, alpha=0.8, label=f"{camp} only")
ax.errorbar(expo.exponent, yy, xerr=[expo.exponent - expo.ci95_low, expo.ci95_high - expo.exponent],
            fmt="o", color="k", ms=5, capsize=2, label="all campaigns (95% bootstrap CI)")
ax.scatter(expo.IPB98y2_implied_for_W, yy, marker="x", color="C3", s=30, zorder=3, label="IPB98(y,2), W = τ·P")
ax.axvline(0, color="0.7", lw=0.8)
ax.set_yticks(yy, ["Ip", "B_T", "n_e line integral", "P_heat", "R_geo", "a", "κ"])
ax.invert_yaxis()
ax.set_xlabel("Exponent in W ∝ Π xᵢ^αᵢ")
ax.set_title("Only the P_heat exponent is stable across campaigns", loc="left")
ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0))
fig.tight_layout()
fig.savefig("figures/baseline_scaling_exponents.png", bbox_inches="tight")
print("\nsaved results/*.csv and figures/baseline_*.png")
