
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "Ismailia_WWTP_monitoring_2000-2008.csv"
)
REPORT_DIR = PROJECT_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Load and prepare the data
df = pd.read_csv(DATA_FILE)
df["SampleDate"] = pd.to_datetime(df["SampleDate"])

df = df.sort_values(["SampleDate", "Stage"]).copy()

# Basic structural checks
assert df["Stage"].isin([1, 2, 3]).all()
assert not df.duplicated(["SampleDate", "Stage"]).any()

# Verify that influent BOD5 is consistent across stages
influent_counts = df.groupby("SampleDate")["BOD5_inf"].nunique()
assert (influent_counts == 1).all(), (
    "Influent BOD5 varies across stages on some dates."
)

# 2. Calculate cumulative removal relative to the plant inlet
df["BOD5_removal_pct"] = (
    (df["BOD5_inf"] - df["BOD5_eff"])
    / df["BOD5_inf"]
    * 100
)

# 3. Calculate incremental removal within each stage
# For Stage 1, the reference is the plant influent.
# For Stages 2 and 3, the reference is the preceding stage outlet.
df["Previous_BOD5_mg_L"] = df["BOD5_eff"].groupby(
    df["SampleDate"]
).shift(1)

stage1_mask = df["Stage"] == 1
df.loc[stage1_mask, "Previous_BOD5_mg_L"] = (
    df.loc[stage1_mask, "BOD5_inf"]
)

df["Stage_removal_pct"] = (
    (
        df["Previous_BOD5_mg_L"] - df["BOD5_eff"]
    )
    / df["Previous_BOD5_mg_L"]
    * 100
)

# 4. Summarize the performance of each stage
summary = (
    df.groupby("Stage")
    .agg(
        observations=("BOD5_eff", "size"),
        mean_influent_BOD5=("BOD5_inf", "mean"),
        mean_effluent_BOD5=("BOD5_eff", "mean"),
        median_effluent_BOD5=("BOD5_eff", "median"),
        mean_cumulative_removal_pct=("BOD5_removal_pct", "mean"),
        median_cumulative_removal_pct=("BOD5_removal_pct", "median"),
        mean_stage_removal_pct=("Stage_removal_pct", "mean"),
    )
    .round(2)
)

print("\nBOD5 PERFORMANCE BY STAGE")
print(summary.to_string())

# Save the results
df.to_csv(REPORT_DIR / "bod5_stage_results.csv", index=False)
summary.to_csv(REPORT_DIR / "bod5_stage_summary.csv")

# 5. Chart: effluent BOD5 distribution by stage
stage_labels = {
    1: "Stage 1 - Aerated",
    2: "Stage 2 - Facultative",
    3: "Stage 3 - Maturation",
}

df["StageLabel"] = df["Stage"].map(stage_labels)

plt.figure(figsize=(10, 6))
df.boxplot(column="BOD5_eff", by="StageLabel", grid=False)
plt.title("Effluent BOD5 Distribution by Treatment Stage")
plt.suptitle("")
plt.xlabel("Treatment stage")
plt.ylabel("Effluent BOD5 (mg/L)")
plt.xticks(rotation=10)
plt.tight_layout()
plt.savefig(
    REPORT_DIR / "bod5_stage_distribution.png",
    dpi=200
)
plt.close()

# 6. Chart: annual mean effluent BOD5 by stage
annual = (
    df.groupby(["Year", "Stage"])["BOD5_eff"]
    .mean()
    .unstack("Stage")
    .rename(columns=stage_labels)
)

plt.figure(figsize=(11, 6))
for column in annual.columns:
    plt.plot(
        annual.index,
        annual[column],
        marker="o",
        markersize=3,
        label=column,
    )

plt.title("Annual Mean Effluent BOD5 by Treatment Stage")
plt.xlabel("Year")
plt.ylabel("Mean effluent BOD5 (mg/L)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    REPORT_DIR / "bod5_annual_trend.png",
    dpi=200
)
plt.close()

print("\nFiles saved in:", REPORT_DIR)
print("- bod5_stage_results.csv")
print("- bod5_stage_summary.csv")
print("- bod5_stage_distribution.png")
print("- bod5_annual_trend.png")
