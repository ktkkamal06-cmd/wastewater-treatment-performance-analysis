
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

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

daily["BOD5_removal_pct"] = (
    (daily["BOD5_inf"] - daily["BOD5_eff"])
    / daily["BOD5_inf"]
    * 100
)

# Log flow makes the flow coefficient easier to interpret
# approximately as the effect of a percentage change in flow.
daily["log_Flow"] = np.log(daily["Flow"])

# Center time to improve interpretability.
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

model_data = daily[
    ["BOD5_removal_pct"] + predictors
].dropna()

X = sm.add_constant(model_data[predictors])
y = model_data["BOD5_removal_pct"]

# HAC standard errors with a 7-day lag window.
# This is a diagnostic choice, not a guarantee that
# all temporal dependence has been handled.
model = sm.OLS(y, X).fit(
    cov_type="HAC",
    cov_kwds={"maxlags": 7},
)

print("\nMULTIVARIABLE MODEL: BOD5 REMOVAL")
print(model.summary())

results = pd.DataFrame({
    "Coefficient": model.params,
    "HAC_standard_error": model.bse,
    "p_value": model.pvalues,
    "CI_lower": model.conf_int()[0],
    "CI_upper": model.conf_int()[1],
})

results.to_csv(
    REPORT_DIR / "bod5_multivariable_model.csv"
)

print("\nMODEL COEFFICIENTS")
print(results.round(5).to_string())

print("\nSaved:", REPORT_DIR / "bod5_multivariable_model.csv")
