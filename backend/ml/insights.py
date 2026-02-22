import pandas as pd
from sqlalchemy import create_engine

import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


# ---------- BASE DATA ----------
def load_data():
    q = "SELECT * FROM donations_raw WHERE payment_status='Success'"
    return pd.read_sql(q, engine)


# ---------- AI INSIGHTS ----------
def donor_retention():
    df = load_data()
    donors = df.groupby("donor_email").size()
    retained = (donors > 1).sum()
    return round((retained / len(donors)) * 100, 1)


def peak_donation_day():
    q = """
    SELECT
      TO_CHAR(payment_date, 'Day') AS day,
      COUNT(*) cnt
    FROM donations_raw
    WHERE payment_status='Success'
    GROUP BY day
    ORDER BY cnt DESC
    LIMIT 1
    """
    df = pd.read_sql(q, engine)
    return df.iloc[0]["day"].strip()


def top_school():
    q = """
    SELECT school_name, SUM(amount) total
    FROM donations_raw
    WHERE payment_status='Success'
    GROUP BY school_name
    ORDER BY total DESC
    LIMIT 1
    """
    df = pd.read_sql(q, engine)
    return df.iloc[0]["school_name"], int(df.iloc[0]["total"])


def weekend_performance():
    q = """
    SELECT
        DATE(payment_date) AS d,
        SUM(amount) AS daily_total,
        CASE
            WHEN EXTRACT(DOW FROM payment_date) IN (0,6)
            THEN 'Weekend'
            ELSE 'Weekday'
        END AS day_type
    FROM donations_raw
    WHERE payment_status = 'Success'
    GROUP BY d, day_type
    """
    df = pd.read_sql(q, engine)

    if df.empty:
        return 0.0

    avg = df.groupby("day_type")["daily_total"].mean()

    if "Weekend" not in avg or "Weekday" not in avg:
        return 0.0

    return round(((avg["Weekend"] / avg["Weekday"]) - 1) * 100, 1)



def organization_engagement():
    q = """
    SELECT donor_type, AVG(amount) avg_amt
    FROM donations_raw
    WHERE payment_status='Success'
    GROUP BY donor_type
    """
    df = pd.read_sql(q, engine).set_index("donor_type")

    org = df.loc["Organization"]["avg_amt"]
    indiv = df.loc["Individual"]["avg_amt"]

    return int(org), round(((org / indiv) - 1) * 100, 1)


def repeat_donors():
    df = load_data()
    donors = df.groupby("donor_email").size()
    repeat = (donors > 1).sum()
    return round((repeat / len(donors)) * 100, 1)


def upi_payments_percentage():
    q = """
    SELECT payment_mode, COUNT(*) cnt
    FROM donations_raw
    WHERE payment_status='Success'
    GROUP BY payment_mode
    """
    df = pd.read_sql(q, engine)

    total = df["cnt"].sum()
    upi = df[df["payment_mode"].str.contains("upi", case=False, na=False)]["cnt"].sum()

    return round((upi / total) * 100, 1)


def seasonal_trends():
    q = """
    SELECT EXTRACT(MONTH FROM payment_date) m, SUM(amount) total
    FROM donations_raw
    WHERE payment_status='Success'
    GROUP BY m
    """
    df = pd.read_sql(q, engine)
    peak_month = int(df.sort_values("total", ascending=False).iloc[0]["m"])

    return "Oct–Dec" if peak_month in (10, 11, 12) else "Other"


# ---------- MAIN (for testing) ----------
if __name__ == "__main__":
    print("Donor Retention %:", donor_retention())
    print("Peak Donation Day:", peak_donation_day())
    print("Top School:", top_school())
    print("Weekend Boost %:", weekend_performance())
    print("Organization Engagement:", organization_engagement())
    print("Repeat Donors %:", repeat_donors())
    print("UPI Payments %:", upi_payments_percentage())
    print("Seasonal Trend:", seasonal_trends())
