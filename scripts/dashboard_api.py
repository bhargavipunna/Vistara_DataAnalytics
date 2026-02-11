import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from functools import lru_cache
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql+psycopg2://bhargavi:bindu@localhost:5432/vistara_analytics"
engine = create_engine(DATABASE_URL)

def get_date_filter(period):
    """Helper function to generate date filter SQL based on period"""
    end_date = datetime.now()
    
    if period == 'weekly':
        start_date = end_date - timedelta(days=7)
        return "AND payment_date >= :start_date", {'start_date': start_date}, "DATE(payment_date)"
    elif period == 'monthly':
        start_date = end_date - timedelta(days=30)
        return "AND payment_date >= :start_date", {'start_date': start_date}, "DATE(payment_date)"
    elif period == 'yearly':
        start_date = end_date - timedelta(days=365)
        return "AND payment_date >= :start_date", {'start_date': start_date}, "DATE_TRUNC('month', payment_date)"
    else:  # 'all' or any other value
        return "", {}, "DATE_TRUNC('month', payment_date)"

def convert_datetime_columns(df):
    """Convert all datetime columns in dataframe to string for JSON serialization"""
    if df.empty:
        return df
    
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            try:
                df[col] = df[col].dt.strftime('%Y-%m-%d')
            except Exception as e:
                logger.warning(f"Could not convert column {col}: {e}")
                df[col] = df[col].astype(str)
    return df

def safe_to_dict(df):
    """Safely convert dataframe to dict, handling non-serializable types"""
    if df.empty:
        return []
    
    # Convert datetime columns first
    df = convert_datetime_columns(df)
    
    # Convert to dict
    result = df.to_dict(orient='records')
    
    # Additional cleanup for any remaining non-serializable types
    for record in result:
        for key, value in list(record.items()):
            if isinstance(value, (pd.Timestamp, pd.DatetimeIndex)):
                record[key] = str(value)
            elif isinstance(value, (np.integer, np.int64, np.int32)):
                record[key] = int(value)
            elif isinstance(value, (np.floating, np.float64, np.float32)):
                record[key] = float(value)
            elif pd.isna(value):
                record[key] = None
            elif hasattr(value, 'isoformat'):
                record[key] = value.isoformat()
    
    return result

@lru_cache(maxsize=32)
def get_dashboard_data(period='monthly'):
    """
    Get dashboard data for the specified period using multiple optimized queries.
    
    Parameters:
    - period: 'weekly', 'monthly', 'yearly', or 'all' for all time
    """
    date_filter, params, trend_interval = get_date_filter(period)
    
    # ---------------- KPIs ----------------
    kpi_query = text(f"""
    SELECT
        COALESCE(SUM(amount), 0) AS total_donations,
        COALESCE(COUNT(*), 0) AS total_transactions,
        COALESCE(COUNT(DISTINCT donor_email), 0) AS total_donors,
        COALESCE(COUNT(DISTINCT campaign_name), 0) AS total_campaigns,
        COALESCE(COUNT(DISTINCT school_name), 0) AS total_schools,
        COALESCE(AVG(amount), 0) AS avg_donation,
        COALESCE(MAX(amount), 0) AS max_donation,
        COALESCE(MIN(amount), 0) AS min_donation,
        COALESCE(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount), 0) AS median_donation
    FROM donations_raw
    WHERE payment_status = 'Success'
    {date_filter}
""")

    
    with engine.connect() as connection:
        kpis = pd.read_sql(kpi_query, connection, params=params).iloc[0]

    # ---------------- Trend ----------------
    trend_query = text(f"""
        SELECT
            {trend_interval} AS date,
            COALESCE(SUM(amount), 0) AS total,
            COUNT(*) AS transaction_count,
            COUNT(DISTINCT donor_email) AS unique_donors
        FROM donations_raw
        WHERE payment_status = 'Success'
        {date_filter}
        GROUP BY {trend_interval}
        ORDER BY date
    """)
    
    with engine.connect() as connection:
        trend = pd.read_sql(trend_query, connection, params=params)
    
    # Convert trend date to datetime and format for display
    if not trend.empty and 'date' in trend.columns:
        try:
            # Convert to datetime first
            trend['date'] = pd.to_datetime(trend['date'])
            
            # Format based on period
            if period in ['yearly', 'all']:
                trend['date'] = trend['date'].dt.strftime('%b %Y')
            elif period in ['weekly', 'monthly']:
                trend['date'] = trend['date'].dt.strftime('%b %d')
        except Exception as e:
            logger.warning(f"Could not format trend dates: {e}")
            trend['date'] = trend['date'].astype(str)

    # ---------------- Donations by School ----------------
    schools_query = text(f"""
        SELECT
            school_name AS name,
            COALESCE(SUM(amount), 0) AS value,
            COUNT(*) AS donation_count,
            COUNT(DISTINCT donor_email) AS unique_donors
        FROM donations_raw
        WHERE payment_status = 'Success'
        {date_filter}
        GROUP BY school_name
        HAVING COALESCE(SUM(amount), 0) > 0
        ORDER BY value DESC
        LIMIT 8
    """)
    
    with engine.connect() as connection:
        schools = pd.read_sql(schools_query, connection, params=params)

    # ---------------- Donations by Campaign ----------------
    campaigns_query = text(f"""
        SELECT
            campaign_name AS name,
            COALESCE(SUM(amount), 0) AS value,
            COUNT(*) AS donation_count,
            COUNT(DISTINCT donor_email) AS unique_donors
        FROM donations_raw
        WHERE payment_status = 'Success'
        {date_filter}
        GROUP BY campaign_name
        HAVING COALESCE(SUM(amount), 0) > 0
        ORDER BY value DESC
        LIMIT 8
    """)
    
    with engine.connect() as connection:
        campaigns = pd.read_sql(campaigns_query, connection, params=params)

    # ---------------- Donation Type ----------------
    donation_type_query = text(f"""
        SELECT
            donation_type AS name,
            COALESCE(SUM(amount), 0) AS value,
            COUNT(*) AS count,
            ROUND(AVG(amount), 2) AS avg_amount
        FROM donations_raw
        WHERE payment_status = 'Success'
        {date_filter}
        GROUP BY donation_type
        HAVING COALESCE(SUM(amount), 0) > 0
    """)
    
    with engine.connect() as connection:
        donation_type = pd.read_sql(donation_type_query, connection, params=params)

    # ---------------- Donor Type (Individual, Group, Organization) ----------------
    donor_type_query = text(f"""
        SELECT
            CASE 
                WHEN donor_email LIKE '%@company.%' OR donor_email LIKE '%@org.%' THEN 'Organization'
                WHEN donor_name LIKE '%&%' OR donor_name LIKE '%Group%' THEN 'Group'
                ELSE 'Individual'
            END AS donor_type,
            COALESCE(SUM(amount), 0) AS value,
            COUNT(*) AS count,
            COUNT(DISTINCT donor_email) AS unique_count
        FROM donations_raw
        WHERE payment_status = 'Success'
        {date_filter}
        GROUP BY 
            CASE 
                WHEN donor_email LIKE '%@company.%' OR donor_email LIKE '%@org.%' THEN 'Organization'
                WHEN donor_name LIKE '%&%' OR donor_name LIKE '%Group%' THEN 'Group'
                ELSE 'Individual'
            END
    """)
    
    with engine.connect() as connection:
        donor_type = pd.read_sql(donor_type_query, connection, params=params)

    # ---------------- Payment Mode ----------------
    payment_mode_query = text(f"""
        SELECT
            payment_mode AS name,
            COALESCE(COUNT(*), 0) AS value,
            COALESCE(SUM(amount), 0) AS total_amount,
            ROUND(AVG(amount), 2) AS avg_amount
        FROM donations_raw
        WHERE payment_status = 'Success'
        {date_filter}
        GROUP BY payment_mode
        HAVING COALESCE(COUNT(*), 0) > 0
    """)
    
    with engine.connect() as connection:
        payment_mode = pd.read_sql(payment_mode_query, connection, params=params)

    # ---------------- Top Donors ----------------
    top_donors_query = text(f"""
        SELECT
            donor_name,
            COALESCE(SUM(amount), 0) AS total_amount,
            COUNT(*) AS donation_count,
            MAX(payment_date) AS last_donation,
            ROUND(AVG(amount), 2) AS avg_donation
        FROM donations_raw
        WHERE payment_status = 'Success'
        {date_filter}
        GROUP BY donor_name
        HAVING COALESCE(SUM(amount), 0) > 0
        ORDER BY total_amount DESC
        LIMIT 10
    """)
    
    with engine.connect() as connection:
        top_donors = pd.read_sql(top_donors_query, connection, params=params)
    
    # Convert last_donation to string format
    if not top_donors.empty and 'last_donation' in top_donors.columns:
        try:
            top_donors['last_donation'] = pd.to_datetime(top_donors['last_donation']).dt.strftime('%Y-%m-%d')
        except:
            top_donors['last_donation'] = top_donors['last_donation'].astype(str)

    # ---------------- Donation Frequency ----------------
    frequency_query = text(f"""
        WITH donor_frequency AS (
            SELECT
                donor_email,
                COUNT(*) as donation_count
            FROM donations_raw
            WHERE payment_status = 'Success'
            {date_filter}
            GROUP BY donor_email
        )
        SELECT
            CASE
                WHEN donation_count = 1 THEN 'One-time'
                WHEN donation_count BETWEEN 2 AND 5 THEN 'Occasional (2-5)'
                WHEN donation_count BETWEEN 6 AND 10 THEN 'Regular (6-10)'
                ELSE 'Frequent (10+)'
            END as frequency,
            COUNT(*) as donor_count,
            SUM(donation_count) as total_donations
        FROM donor_frequency
        GROUP BY 
            CASE
                WHEN donation_count = 1 THEN 'One-time'
                WHEN donation_count BETWEEN 2 AND 5 THEN 'Occasional (2-5)'
                WHEN donation_count BETWEEN 6 AND 10 THEN 'Regular (6-10)'
                ELSE 'Frequent (10+)'
            END
    """)
    
    with engine.connect() as connection:
        donation_frequency = pd.read_sql(frequency_query, connection, params=params)

    # ---------------- Time of Day Analysis ----------------
    time_of_day_query = text(f"""
        SELECT
            EXTRACT(HOUR FROM payment_date) as hour,
            COUNT(*) as donation_count,
            COALESCE(SUM(amount), 0) as total_amount
        FROM donations_raw
        WHERE payment_status = 'Success'
        {date_filter}
        GROUP BY EXTRACT(HOUR FROM payment_date)
        ORDER BY hour
    """)
    
    with engine.connect() as connection:
        time_of_day = pd.read_sql(time_of_day_query, connection, params=params)
    
    # Format time of day
    if not time_of_day.empty and 'hour' in time_of_day.columns:
        time_of_day['hour'] = time_of_day['hour'].apply(
            lambda x: f'{int(x):02d}:00' if pd.notnull(x) else x
        )

    # Return all data using safe conversion
    return {
        "period": period,
        "kpis": {
            "total_donations": int(kpis.total_donations),
            "total_transactions": int(kpis.total_transactions),  
            "total_donors": int(kpis.total_donors),
            "total_campaigns": int(kpis.total_campaigns),
            "total_schools": int(kpis.total_schools),
            "avg_donation": round(float(kpis.avg_donation), 2),
            "max_donation": round(float(kpis.max_donation), 2),
            "min_donation": round(float(kpis.min_donation), 2),
            "median_donation": round(float(kpis.median_donation), 2)
        },

        "trend": safe_to_dict(trend),
        "schools": safe_to_dict(schools),
        "campaigns": safe_to_dict(campaigns),
        "donation_type": safe_to_dict(donation_type),
        "donor_type": safe_to_dict(donor_type),
        "payment_mode": safe_to_dict(payment_mode),
        "top_donors": safe_to_dict(top_donors),
        "donation_frequency": safe_to_dict(donation_frequency),
        "time_of_day": safe_to_dict(time_of_day)
    }

# For backward compatibility
def get_dashboard_data_optimized(period='monthly'):
    return get_dashboard_data(period)

def get_dashboard_data_legacy():
    return get_dashboard_data('all')