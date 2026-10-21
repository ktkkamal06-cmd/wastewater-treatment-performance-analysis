
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "Ismailia_WWTP_monitoring_2000-2008.csv"
)

df = pd.read_csv(DATA_FILE)
df["SampleDate"] = pd.to_datetime(
    df["SampleDate"],
    format="%Y-%m-%d",
    errors="raise",
)
# One row per date, with each stage's outlet concentration
wide = df.pivot(
    index="SampleDate",
    columns="Stage",
    values="BOD5_eff",
)
wide.columns = [f"Stage{stage}_BOD5" for stage in wide.columns]

# Add the common influent concentration once per date
influent = (
    df.groupby("SampleDate")["BOD5_inf"]
    .first()
    .rename("Influent_BOD5")
)
wide = wide.join(influent)

# Concentration-based removal, using ratios of mean concentrations
mean_influent = wide["Influent_BOD5"].mean()

print("MEAN CONCENTRATIONS (mg/L)")
print(f"Influent: {mean_influent:.2f}")

for stage in [1, 2, 3]:
    column = f"Stage{stage}_BOD5"
    mean_effluent = wide[column].mean()

    removal = (
        (mean_influent - mean_effluent)
        / mean_influent
        * 100
    )

    print(
        f"Stage {stage}: mean = {mean_effluent:.2f}, "
        f"removal from influent based on means = {removal:.2f}%"
    )

print("\nPAIRED STAGE-TO-STAGE CHANGES")

for previous, current in [(1, 2), (2, 3)]:
    previous_col = f"Stage{previous}_BOD5"
    current_col = f"Stage{current}_BOD5"

    daily_removal = (
        (wide[previous_col] - wide[current_col])
        / wide[previous_col]
        * 100
    )

    print(
        f"Stage {previous} -> {current}: "
        f"mean daily removal = {daily_removal.mean():.2f}%, "
        f"median daily removal = {daily_removal.median():.2f}%, "
        f"dates with increased BOD5 = "
        f"{(wide[current_col] > wide[previous_col]).sum()}"
    )

# Check the distribution of final-stage readings
final = wide["Stage3_BOD5"]

print("\nFINAL STAGE DISTRIBUTION (mg/L)")
print(final.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).round(2))

print("\nNumber of dates:", len(wide))
print("Date range:", wide.index.min().date(), "to", wide.index.max().date())
