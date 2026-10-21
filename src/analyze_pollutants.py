
from pathlib import Path

import numpy as np
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
df["SampleDate"] = pd.to_datetime(
    df["SampleDate"],
    format="%d-%m-%y",
    errors="raise",
)

# Each date should have one observation for each stage.
assert not df.duplicated(["SampleDate", "Stage"]).any()

pollutants = {
    "BOD5": ("BOD5_inf", "BOD5_eff", "mg/L"),
    "TSS": ("TSS_inf", "TSS_eff", "mg/L"),
    "Coliform": (
        "Coliform_inf",
        "Coliform_eff",
        "MPN/100 mL",
    ),
}

# Influent and effluent concentrations arranged by date and stage.
results = []

for pollutant, (in_col, out_col, unit) in pollutants.items():
    wide = df.pivot(
        index="SampleDate",
        columns="Stage",
        values=out_col,
    ).rename(
        columns={
            1: "Stage1",
            2: "Stage2",
            3: "Stage3",
        }
    )

    influent = (
        df.groupby("SampleDate")[in_col]
        .first()
        .rename("Influent")
    )
    wide = wide.join(influent)

    # Ensure the influent value is consistent within each date.
    counts = df.groupby("SampleDate")[in_col].nunique()
    assert (counts == 1).all(), (
        f"Inconsistent {pollutant} influent values."
    )

    # Stage 3 represents the final treatment-stage outlet.
    final = wide["Stage3"]
    initial = wide["Influent"]

    # Concentration-based removal using mean concentrations.
    mean_initial = initial.mean()
    mean_final = final.mean()

    overall_removal = (
        (mean_initial - mean_final) / mean_initial * 100
    )

    # Mean of daily percentage removals.
    daily_removal = (initial - final) / initial * 100

    row = {
        "Pollutant": pollutant,
        "Unit": unit,
        "Mean_influent": mean_initial,
        "Mean_final_effluent": mean_final,
        "Removal_from_mean_concentrations_pct": overall_removal,
        "Mean_daily_removal_pct": daily_removal.mean(),
        "Median_daily_removal_pct": daily_removal.median(),
        "Dates_with_higher_final_than_influent": (
            final > initial
        ).sum(),
    }

    # Log reduction is meaningful only for positive values.
    if pollutant == "Coliform":
        valid = (initial > 0) & (final > 0)
        log_reduction = np.log10(
            initial[valid] / final[valid]
        )
        row["Mean_daily_log10_reduction"] = (
            log_reduction.mean()
        )
    else:
        row["Mean_daily_log10_reduction"] = np.nan

    results.append(row)

    # Save date-level stage data for further analysis.
    wide.to_csv(
        REPORT_DIR / f"{pollutant.lower()}_by_stage.csv"
    )

    # Chart mean concentration at inlet and stage outlets.
    means = [
        initial.mean(),
        wide["Stage1"].mean(),
        wide["Stage2"].mean(),
        wide["Stage3"].mean(),
    ]

    plt.figure(figsize=(9, 5))
    plt.bar(
        ["Influent", "Stage 1", "Stage 2", "Stage 3"],
        means,
    )
    plt.title(f"{pollutant}: Mean Concentration Through Treatment")
    plt.ylabel(f"Concentration ({unit})")
    plt.tight_layout()
    plt.savefig(
        REPORT_DIR / f"{pollutant.lower()}_stage_means.png",
        dpi=200,
    )
    plt.close()

summary = pd.DataFrame(results)
summary = summary.round(4)

print("\nPOLLUTANT PERFORMANCE SUMMARY")
print(summary.to_string(index=False))

summary.to_csv(
    REPORT_DIR / "pollutant_performance_summary.csv",
    index=False,
)

print("\nSaved results to:", REPORT_DIR)
