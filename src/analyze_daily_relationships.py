
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr, pearsonr

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "Ismailia_WWTP_monitoring_2000-2008.csv"
)
REPORT_DIR = PROJECT_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE)

df["SampleDate"] = pd.to_datetime(
    df["SampleDate"],
    format="%d-%m-%y",
    errors="raise",
)

# Keep one final-stage measurement per date.
daily = (
    df.loc[df["Stage"] == 3]
    .sort_values("SampleDate")
    .copy()
)

assert daily["SampleDate"].is_unique

daily["BOD5_removal_pct"] = (
    (daily["BOD5_inf"] - daily["BOD5_eff"])
    / daily["BOD5_inf"]
    * 100
)

daily["BOD5_influent_load_kg_d"] = (
    daily["BOD5_inf"] * daily["Flow"] / 1000
)

daily["Year"] = daily["SampleDate"].dt.year

variables = [
    "Flow",
    "BOD5_inf",
    "TSS_inf",
    "Coliform_inf",
    "Temp",
    "DO_inf",
    "pH_inf",
]

targets = [
    "BOD5_eff",
    "BOD5_removal_pct",
]

results = []

for target in targets:
    for variable in variables:
        x = daily[variable]
        y = daily[target]

        pearson_r, pearson_p = pearsonr(x, y)
        spearman_r, spearman_p = spearmanr(x, y)

        results.append({
            "Outcome": target,
            "Variable": variable,
            "Pearson_r": pearson_r,
            "Pearson_p": pearson_p,
            "Spearman_rho": spearman_r,
            "Spearman_p": spearman_p,
        })

results_df = pd.DataFrame(results)

print("\nDAILY ASSOCIATIONS")
print(
    results_df.sort_values(
        ["Outcome", "Spearman_p"]
    ).round(5).to_string(index=False)
)

results_df.to_csv(
    REPORT_DIR / "daily_bod5_associations.csv",
    index=False,
)

# Compare flow and treatment performance by flow quartile.
daily["Flow_quartile"] = pd.qcut(
    daily["Flow"],
    q=4,
    labels=["Q1: Lowest", "Q2", "Q3", "Q4: Highest"],
)

quartile_summary = daily.groupby(
    "Flow_quartile",
    observed=True,
).agg(
    observations=("Flow", "size"),
    mean_flow=("Flow", "mean"),
    mean_influent_BOD5=("BOD5_inf", "mean"),
    mean_final_BOD5=("BOD5_eff", "mean"),
    mean_BOD5_removal_pct=("BOD5_removal_pct", "mean"),
).round(3)

print("\nBOD5 PERFORMANCE BY FLOW QUARTILE")
print(quartile_summary.to_string())

quartile_summary.to_csv(
    REPORT_DIR / "bod5_by_flow_quartile.csv"
)

print("\nSaved daily analysis reports to:", REPORT_DIR)
