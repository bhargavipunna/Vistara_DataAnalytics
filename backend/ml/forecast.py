import pandas as pd
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression
import numpy as np

import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


# --------------------------------
# LOAD MONTHLY DATA
# --------------------------------
def load_monthly_data():
    q = """
    SELECT
        DATE_TRUNC('month', payment_date) AS month,
        SUM(amount) AS total
    FROM donations_raw
    WHERE payment_status = 'Success'
    GROUP BY month
    ORDER BY month
    """
    return pd.read_sql(q, engine)


# --------------------------------
# STATISTICAL FORECAST (BASELINE)
# --------------------------------
def statistical_forecast(df):
    recent = df.tail(3)
    median_val = recent["total"].median()

    # Trend-based growth
    m1, m2, m3 = recent["total"].values
    if m3 > m2 > m1:
        growth = 1.12
    elif m3 > m2:
        growth = 1.08
    else:
        growth = 1.05

    return median_val * growth


# --------------------------------
# ML FORECAST (WHEN DATA IS GOOD)
# --------------------------------
def ml_forecast(df):
    if len(df) < 8:   # ML gate
        return None

    df = df.copy()
    df["t"] = np.arange(len(df))

    X = df[["t"]]
    y = df["total"]

    model = LinearRegression()
    model.fit(X, y)

    next_t = [[df["t"].max() + 1]]
    return model.predict(next_t)[0]


# --------------------------------
# FINAL DECISION ENGINE
# --------------------------------
def next_month_forecast():
    df = load_monthly_data()

    if len(df) < 3:
        return {
            "predicted_amount_lakhs": None,
            "confidence": "Low",
            "basis": "Insufficient data"
        }

    stat_pred = statistical_forecast(df)
    ml_pred = ml_forecast(df)

    # Decision logic
    if ml_pred is not None:
        # Blend for stability
        final_pred = (0.6 * stat_pred) + (0.4 * ml_pred)
        basis = "Hybrid: Statistical + ML"
        confidence = "High"
    else:
        final_pred = stat_pred
        basis = "Statistical (ML warming up)"
        confidence = "Medium"

    # Safety clamp
    final_pred = min(max(final_pred, 5_00_000), 30_00_000)

    return {
        "predicted_amount_lakhs": round(final_pred / 100000, 1),
        "confidence": confidence,
        "basis": basis
    }


# --------------------------------
# LOCAL TEST
# --------------------------------
if __name__ == "__main__":
    res = next_month_forecast()
    print("Next Month Forecast")
    print(f"₹{res['predicted_amount_lakhs']} L")
    print(res["basis"], "| Confidence:", res["confidence"])
