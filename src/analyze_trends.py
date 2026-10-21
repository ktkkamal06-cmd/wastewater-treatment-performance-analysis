
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

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

# CSV dates use day-month-two-digit-year format.
df["SampleDate"] = pd.to_datetime(
    df["SampleDate"],
    format="%d-%m-%y",
    errors="raise",
)

# Retain the final-stage outlet and one influent record per date.
final_stage = (
    df.loc[df["Stage"] == 3]
    .sort_values("SampleDate")
    .copy()
)

assert final_stage["SampleDate"].is_unique

pollutants = {
    "BOD5": ("BOD5_inf", "BOD5_eff"),
    "TSS": ("TSS_inf", "TSS_eff"),
    "Coliform": ("Coliform_inf", "Coliform_eff"),
}

# Calculate date-level removal and then annual summaries.
for name, (influent_col, effluent_col) in pollutants.items():
    final_stage[f"{name}_removal_pct"] = (
        (
            final_stage[influent_col]
            - final_stage[effluent_col]
        )
        / final_stage[influent_col]
        * 100
    )

annual = final_stage.groupby(
    final_stage["SampleDate"].dt.year
).agg(
    BOD5_influent_mean=("BOD5_inf", "mean"),
    BOD5_final_mean=("BOD5_eff", "mean"),
    TSS_influent_mean=("TSS_inf", "mean"),
    TSS_final_mean=("TSS_eff", "mean"),
    Coliform_influent_mean=("Coliform_inf", "mean"),
    Coliform_final_mean=("Coliform_eff", "mean"),
    BOD5_removal_mean=("BOD5_removal_pct", "mean"),
    TSS_removal_mean=("TSS_removal_pct", "mean"),
    Coliform_removal_mean=("Coliform_removal_pct", "mean"),
)

annual = annual.round(3)

print("\nANNUAL TREATMENT PERFORMANCE")
print(annual.to_string())

annual.to_csv(REPORT_DIR / "annual_treatment_performance.csv")

# Plot annual mean influent and final effluent concentrations.
for name, (influent_col, effluent_col) in pollutants.items():
    yearly = final_stage.groupby(
        final_stage["SampleDate"].dt.year
    )[[influent_col, effluent_col]].mean()

    plt.figure(figsize=(10, 5))
    plt.plot(
        yearly.index,
        yearly[influent_col],
        marker="o",
        label="Influent",
    )
    plt.plot(
        yearly.index,
        yearly[effluent_col],
        marker="o",
        label="Final-stage effluent",
    )

    plt.title(f"Annual Mean {name} Concentration")
    plt.xlabel("Year")
    plt.ylabel(
        "Concentration (MPN/100 mL)"
        if name == "Coliform"
        else "Concentration (mg/L)"
    )
    plt.xticks(yearly.index)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        REPORT_DIR / f"{name.lower()}_annual_concentrations.png",
        dpi=200,
    )
    plt.close()

print("\nSaved annual summary and trend charts in:", REPORT_DIR)
