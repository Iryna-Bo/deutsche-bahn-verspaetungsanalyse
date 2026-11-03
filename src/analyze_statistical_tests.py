from pathlib import Path
import duckdb
import pandas as pd
import numpy as np

from scipy import stats
from scipy.stats import kruskal, chi2_contingency
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.proportion import proportion_confint

import matplotlib.pyplot as plt


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

RESULTS_DIR = BASE_DIR / "results" / "statistical_analysis"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

PLOTS_DIR = RESULTS_DIR / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

DATA_URL = (
    "https://huggingface.co/datasets/"
    "piebro/deutsche-bahn-data/resolve/main/"
    "monthly_processed_data/"
    "data-2025-03.parquet"
)

TRAIN_TYPES = [
    "S",
    "RB",
    "RE",
    "IC",
    "ICE"
]


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("STATISTICAL ANALYSIS – MARCH 2025")
print("=" * 70)

query = f"""
SELECT
    train_type,
    delay_in_min
FROM read_parquet('{DATA_URL}')
WHERE train_type IN ({",".join("'" + x + "'" for x in TRAIN_TYPES)})
  AND delay_in_min IS NOT NULL
"""

print("\nLoading historical data...")

con = duckdb.connect()

df = con.execute(query).df()

con.close()

print(f"Rows loaded: {len(df):,}")


# ============================================================
# BASIC CLEANING
# ============================================================

# Negative values are kept in the raw dataset,
# but are not suitable for the delay distribution tests.
df_clean = df[
    df["delay_in_min"] >= 0
].copy()

print(
    f"Rows after removing negative delays: "
    f"{len(df_clean):,}"
)


# ============================================================
# DESCRIPTIVE STATISTICS
# ============================================================

descriptive = (
    df_clean
    .groupby("train_type")["delay_in_min"]
    .agg(
        n="count",
        median="median",
        mean="mean",
        std="std",
        q1=lambda x: x.quantile(0.25),
        q3=lambda x: x.quantile(0.75),
        p95=lambda x: x.quantile(0.95)
    )
    .reset_index()
)

descriptive["iqr"] = (
    descriptive["q3"]
    - descriptive["q1"]
)

descriptive = descriptive[
    [
        "train_type",
        "n",
        "median",
        "mean",
        "std",
        "q1",
        "q3",
        "iqr",
        "p95"
    ]
]

descriptive.to_csv(
    RESULTS_DIR / "01_descriptive_statistics.csv",
    index=False
)

print("\nDESCRIPTIVE STATISTICS")
print(descriptive.to_string(index=False))


# ============================================================
# VISUALIZATION 1 – BOXPLOT
# ============================================================

plt.figure(figsize=(10, 6))

data_for_plot = [
    df_clean.loc[
        df_clean["train_type"] == train_type,
        "delay_in_min"
    ]
    for train_type in TRAIN_TYPES
]

plt.boxplot(
    data_for_plot,
    labels=TRAIN_TYPES,
    showfliers=False
)

plt.title(
    "Verspätungsverteilung nach Zugtyp – März 2025"
)

plt.xlabel("Zugtyp")
plt.ylabel("Verspätung (Minuten)")

plt.tight_layout()

plt.savefig(
    PLOTS_DIR / "01_delay_distribution_by_train_type.png",
    dpi=150
)

plt.close()


# ============================================================
# ANOVA
# ============================================================

groups = [
    df_clean.loc[
        df_clean["train_type"] == train_type,
        "delay_in_min"
    ].values
    for train_type in TRAIN_TYPES
]

anova = stats.f_oneway(*groups)

print("\nANOVA")
print(f"F-statistic: {anova.statistic:.4f}")
print(f"p-value:     {anova.pvalue:.6g}")


# ============================================================
# KRUSKAL-WALLIS
# ============================================================

kruskal_result = kruskal(*groups)

print("\nKRUSKAL-WALLIS")
print(
    f"H-statistic: {kruskal_result.statistic:.4f}"
)

print(
    f"p-value:     {kruskal_result.pvalue:.6g}"
)


# ============================================================
# EFFECT SIZE – ETA SQUARED
# ============================================================

grand_mean = df_clean["delay_in_min"].mean()

ss_between = sum(
    len(group) *
    (group.mean() - grand_mean) ** 2
    for group in groups
)

ss_total = (
    (df_clean["delay_in_min"] - grand_mean) ** 2
).sum()

eta_squared = ss_between / ss_total

print("\nANOVA EFFECT SIZE")
print(f"Eta squared: {eta_squared:.4f}")


# ============================================================
# ANOVA / KRUSKAL SUMMARY
# ============================================================

test_summary = pd.DataFrame({
    "test": [
        "One-way ANOVA",
        "Kruskal-Wallis"
    ],
    "statistic": [
        anova.statistic,
        kruskal_result.statistic
    ],
    "p_value": [
        anova.pvalue,
        kruskal_result.pvalue
    ]
})

test_summary.to_csv(
    RESULTS_DIR / "02_global_tests.csv",
    index=False
)

pd.DataFrame({
    "metric": ["eta_squared"],
    "value": [eta_squared]
}).to_csv(
    RESULTS_DIR / "03_effect_size.csv",
    index=False
)


# ============================================================
# TUKEY HSD
# ============================================================

tukey = pairwise_tukeyhsd(
    endog=df_clean["delay_in_min"],
    groups=df_clean["train_type"],
    alpha=0.05
)

print("\nTUKEY HSD")
print(tukey)

tukey_df = pd.DataFrame(
    data=tukey._results_table.data[1:],
    columns=tukey._results_table.data[0]
)

tukey_df.to_csv(
    RESULTS_DIR / "04_tukey_hsd.csv",
    index=False
)


# ============================================================
# CHI-SQUARE
# ============================================================

df_clean["delay_category"] = pd.cut(
    df_clean["delay_in_min"],
    bins=[
        -0.001,
        0,
        4,
        14,
        59,
        np.inf
    ],
    labels=[
        "0",
        "1-4",
        "5-14",
        "15-59",
        "60+"
    ]
)

contingency = pd.crosstab(
    df_clean["train_type"],
    df_clean["delay_category"]
)

chi2, p_value, dof, expected = chi2_contingency(
    contingency
)

print("\nCHI-SQUARE")
print(f"Chi-square: {chi2:.4f}")
print(f"p-value:    {p_value:.6g}")
print(f"df:         {dof}")


# ============================================================
# CRAMER'S V
# ============================================================

n = contingency.to_numpy().sum()

phi2 = chi2 / n

r, k = contingency.shape

cramers_v = np.sqrt(
    phi2 /
    min(k - 1, r - 1)
)

print(f"Cramer's V: {cramers_v:.4f}")


contingency.to_csv(
    RESULTS_DIR / "05_delay_category_by_train_type.csv"
)

pd.DataFrame({
    "metric": [
        "chi_square",
        "p_value",
        "degrees_of_freedom",
        "cramers_v"
    ],
    "value": [
        chi2,
        p_value,
        dof,
        cramers_v
    ]
}).to_csv(
    RESULTS_DIR / "06_chi_square_results.csv",
    index=False
)


# ============================================================
# VISUALIZATION 2 – DELAY CATEGORY SHARE
# ============================================================

category_share = (
    pd.crosstab(
        df_clean["train_type"],
        df_clean["delay_category"],
        normalize="index"
    )
    * 100
)

category_share = category_share[
    ["0", "1-4", "5-14", "15-59", "60+"]
]

category_share.plot(
    kind="bar",
    stacked=True,
    figsize=(10, 6)
)

plt.title(
    "Verspätungskategorien nach Zugtyp – März 2025"
)

plt.xlabel("Zugtyp")
plt.ylabel("Anteil (%)")

plt.legend(
    title="Verspätung"
)

plt.tight_layout()

plt.savefig(
    PLOTS_DIR / "02_delay_categories_by_train_type.png",
    dpi=150
)

plt.close()


# ============================================================
# CONFIDENCE INTERVALS FOR >=5 MIN
# ============================================================

ci_rows = []

for train_type in TRAIN_TYPES:

    values = df_clean.loc[
        df_clean["train_type"] == train_type,
        "delay_in_min"
    ]

    n_obs = len(values)

    successes = (
        values >= 5
    ).sum()

    proportion = successes / n_obs

    lower, upper = proportion_confint(
        count=successes,
        nobs=n_obs,
        alpha=0.05,
        method="wilson"
    )

    ci_rows.append({
        "train_type": train_type,
        "n": n_obs,
        "delay_ge_5_count": successes,
        "delay_ge_5_share": proportion * 100,
        "ci_95_lower": lower * 100,
        "ci_95_upper": upper * 100
    })


confidence_intervals = pd.DataFrame(
    ci_rows
)

confidence_intervals.to_csv(
    RESULTS_DIR / "07_confidence_intervals_ge5.csv",
    index=False
)

print("\n95% CONFIDENCE INTERVALS – DELAY >=5 MIN")
print(
    confidence_intervals.to_string(index=False)
)


# ============================================================
# VISUALIZATION 3 – CONFIDENCE INTERVALS
# ============================================================

plt.figure(figsize=(9, 6))

x = np.arange(
    len(confidence_intervals)
)

values = confidence_intervals[
    "delay_ge_5_share"
].values

lower = (
    values
    - confidence_intervals["ci_95_lower"].values
)

upper = (
    confidence_intervals["ci_95_upper"].values
    - values
)

plt.errorbar(
    x,
    values,
    yerr=[lower, upper],
    fmt="o",
    capsize=5
)

plt.xticks(
    x,
    confidence_intervals["train_type"]
)

plt.xlabel("Zugtyp")
plt.ylabel("Anteil Verspätungen ≥5 Min. (%)")

plt.title(
    "Anteil Verspätungen ≥5 Min. mit 95%-Konfidenzintervall"
)

plt.tight_layout()

plt.savefig(
    PLOTS_DIR / "03_confidence_intervals_ge5.png",
    dpi=150
)

plt.close()


# ============================================================
# FINAL SUMMARY
# ============================================================

summary = pd.DataFrame({
    "metric": [
        "rows_loaded",
        "rows_after_negative_filter",
        "anova_F",
        "anova_p_value",
        "kruskal_H",
        "kruskal_p_value",
        "eta_squared",
        "chi_square",
        "chi_square_p_value",
        "cramers_v"
    ],
    "value": [
        len(df),
        len(df_clean),
        anova.statistic,
        anova.pvalue,
        kruskal_result.statistic,
        kruskal_result.pvalue,
        eta_squared,
        chi2,
        p_value,
        cramers_v
    ]
})

summary.to_csv(
    RESULTS_DIR / "00_statistical_summary.csv",
    index=False
)


print("\n" + "=" * 70)
print("STATISTICAL ANALYSIS FINISHED")
print("=" * 70)

print(
    "\nResults directory:"
)

print(RESULTS_DIR)

print("\nPlots:")
for file in sorted(PLOTS_DIR.glob("*.png")):
    print(" ", file.name)