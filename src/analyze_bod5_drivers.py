
from pathlib import Path

import pandas as pd

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

# One record per sampling date: Stage 3 contains final-stage effluent.
final_stage = (
    df.loc[df["Stage"] == 3]
    .sort_values("SampleDate")
    .copy()
)

assert final_stage["SampleDate"].is_unique

final_stage["Year"] = final_stage["SampleDate"].dt.year

# Variables that may help explain variation in final-stage BOD5.
variables = [
    "BOD5_inf",
    "TSS_inf",
    "Coliform_inf",
    "Flow",
    "Temp",
    "DO_inf",
    "pH_inf",
    "BOD5_eff",
]

annual = (
    final_stage.groupby("Year")[variables]
    .mean()
    .round(3)
)

print("\nANNUAL OPERATING CONDITIONS AND BOD5")
print(annual.to_string())

annual.to_csv(REPORT_DIR / "annual_bod5_drivers.csv")

# Correlations between annual conditions and final-stage BOD5.
target = annual["BOD5_eff"]

correlations = []

for variable in variables:
    if variable == "BOD5_eff":
        continue

    pearson = annual[variable].corr(target, method="pearson")
    spearman = annual[variable].corr(target, method="spearman")

    correlations.append({
        "Variable": variable,
        "Pearson_correlation": pearson,
        "Spearman_correlation": spearman,
    })

corr_df = (
    pd.DataFrame(correlations)
    .sort_values("Spearman_correlation", key=lambda s: s.abs(), ascending=False)
    .round(3)
)

print("\nASSOCIATION WITH ANNUAL FINAL-STAGE BOD5")
print(corr_df.to_string(index=False))

corr_df.to_csv(REPORT_DIR / "annual_bod5_correlations.csv", index=False)

print("\nSaved reports to:", REPORT_DIR)
