
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

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

daily = (
    df.loc[df["Stage"] == 3]
    .sort_values("SampleDate")
    .copy()
)

assert daily["SampleDate"].is_unique

daily["log_Flow"] = np.log(daily["Flow"])
daily["time_years"] = (
    (daily["SampleDate"] - daily["SampleDate"].min()).dt.days
    / 365.25
)

predictors = [
    "log_Flow",
    "BOD5_inf",
    "pH_inf",
    "Temp",
    "time_years",
]

data = daily[["BOD5_eff"] + predictors].dropna()

# Standardize predictors so their scales are comparable.
X_scaled = data[predictors].copy()
X_scaled = (X_scaled - X_scaled.mean()) / X_scaled.std(ddof=0)
X = sm.add_constant(X_scaled)
y = data["BOD5_eff"]

# Compare different HAC lag windows as a sensitivity check.
for lag in [7, 30, 60]:
    model = sm.OLS(y, X).fit(
        cov_type="HAC",
        cov_kwds={"maxlags": lag},
    )

    print(f"\nFINAL-STAGE BOD5 MODEL — HAC LAGS = {lag}")
    print(
        pd.DataFrame({
            "Coefficient": model.params,
            "HAC_SE": model.bse,
            "p_value": model.pvalues,
            "CI_lower": model.conf_int()[0],
            "CI_upper": model.conf_int()[1],
        }).round(4).to_string()
    )

    print(
        f"R-squared: {model.rsquared:.3f}; "
        f"Durbin-Watson: "
        f"{sm.stats.stattools.durbin_watson(model.resid):.3f}"
    )

# Variance inflation factors diagnose predictor collinearity.
vif = pd.DataFrame({
    "Variable": X_scaled.columns,
    "VIF": [
        variance_inflation_factor(
            X_scaled.values, i
        )
        for i in range(X_scaled.shape[1])
    ],
})

print("\nVARIANCE INFLATION FACTORS")
print(vif.round(3).to_string(index=False))

vif.to_csv(REPORT_DIR / "bod5_model_vif.csv", index=False)

print("\nSaved VIF report:", REPORT_DIR / "bod5_model_vif.csv")
