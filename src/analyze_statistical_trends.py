
from pathlib import Path

import pandas as pd
from scipy.stats import linregress, spearmanr

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

# Use only Stage 3: one final-effluent record per sampling date.
final_stage = (
    df.loc[df["Stage"] == 3]
    .sort_values("SampleDate")
    .copy()
)

assert final_stage["SampleDate"].is_unique

final_stage["Year"] = final_stage["SampleDate"].dt.year

pollutants = {
    "BOD5": ("BOD5_inf", "BOD5_eff"),
    "TSS": ("TSS_inf", "TSS_eff"),
    "Coliform": ("Coliform_inf", "Coliform_eff"),
}

results = []

for pollutant, (influent_col, effluent_col) in pollutants.items():
    yearly = (
        final_stage.groupby("Year")
        .agg(
            influent_mean=(influent_col, "mean"),
            effluent_mean=(effluent_col, "mean"),
        )
        .reset_index()
    )

    # Trend in annual mean final-stage concentration.
    linear = linregress(
        yearly["Year"],
        yearly["effluent_mean"],
    )

    spearman = spearmanr(
        yearly["Year"],
        yearly["effluent_mean"],
    )

    results.append({
        "Pollutant": pollutant,
        "Trend_slope_per_year": linear.slope,
        "Linear_R_squared": linear.rvalue ** 2,
        "Linear_p_value": linear.pvalue,
        "Spearman_correlation": spearman.statistic,
        "Spearman_p_value": spearman.pvalue,
        "First_year_effluent_mean": yearly["effluent_mean"].iloc[0],
        "Last_year_effluent_mean": yearly["effluent_mean"].iloc[-1],
    })

results_df = pd.DataFrame(results).round(5)

print("\nSTATISTICAL TRENDS IN ANNUAL FINAL-STAGE CONCENTRATIONS")
print(results_df.to_string(index=False))

results_df.to_csv(
    REPORT_DIR / "statistical_trend_summary.csv",
    index=False,
)

print("\nSaved:", REPORT_DIR / "statistical_trend_summary.csv")
