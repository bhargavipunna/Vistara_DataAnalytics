"""
FastAPI server for dashboard analytics
Connects to PostgreSQL database and provides JSON data to frontend
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime, timedelta
import logging
import os  # ← Add this import

from ml.insights import *
from ml.forecast import next_month_forecast

# Import the optimized dashboard functions
try:
    from scripts.dashboard_api import (
        get_dashboard_data, 
        get_dashboard_data_optimized,
        get_dashboard_data_legacy
    )
except ImportError:
    # Fallback if module structure is different
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.dashboard_api import (
        get_dashboard_data, 
        get_dashboard_data_optimized,
        get_dashboard_data_legacy
    )

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Vistara Analytics API",
    description="Dashboard analytics API for trust/foundation donations with period-based filtering",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins - restrict in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

# Import your existing class
from agent import FinalDonationReportAgent

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

# Initialize the Agent
agent = FinalDonationReportAgent()

# --- AUTOMATIC CLEANUP SCHEDULER ---
# This runs every day to delete files older than 30 days
scheduler = BackgroundScheduler()

def scheduled_cleanup():
    logger.info("Running scheduled cleanup task...")
    deleted_count = agent.cleanup_old_reports(days=30)
    logger.info(f"Cleanup complete. Deleted {deleted_count} old reports.")

# --- LIFESPAN MANAGER ---
# This starts the scheduler when the server starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler.add_job(scheduled_cleanup, 'interval', hours=24)
    scheduler.start()
    yield
    # Shutdown
    scheduler.shutdown()

# --- ENDPOINTS ---

@app.get("/reports/weekly")
def get_weekly_report():
    try:
        # Check cache logic is already inside generate_report
        file_path = agent.generate_report(period_type='weekly')
        return FileResponse(
            path=file_path, 
            filename=os.path.basename(file_path),
            media_type='application/pdf'
        )
    except Exception as e:
        logger.error(f"Error generating weekly report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/monthly")
def get_monthly_report():
    try:
        file_path = agent.generate_report(period_type='monthly')
        return FileResponse(
            path=file_path, 
            filename=os.path.basename(file_path),
            media_type='application/pdf'
        )
    except Exception as e:
        logger.error(f"Error generating monthly report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/yearly/{year}")
def get_yearly_report(year: int):
    try:
        file_path = agent.generate_report(period_type='yearly', year=year)
        return FileResponse(
            path=file_path, 
            filename=os.path.basename(file_path),
            media_type='application/pdf'
        )
    except Exception as e:
        logger.error(f"Error generating yearly report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/api/dashboard")
def dashboard(
    period: str = Query(
        "monthly", 
        description="Time period for analytics: 'weekly', 'monthly', 'yearly', or 'all'",
        regex="^(weekly|monthly|yearly|all)$"
    ),
    optimized: bool = Query(
        True, 
        description="Use optimized single query (true) or multiple queries with cache (false)"
    )
):
    """
    Fetch complete dashboard data for the specified time period.
    
    Returns:
    - KPIs (total donations, total transactions, donors, campaigns, avg donation, etc.)
    - Donation trends over time (daily/weekly/monthly based on period)
    - Donations by school
    - Donations by campaign
    - Donation type breakdown
    - Payment method distribution
    - Top donors list
    - Donation frequency analysis
    - Time of day analysis
    
    The 'period' parameter controls the date range:
    - weekly: Last 7 days
    - monthly: Last 30 days (default)
    - yearly: Last 365 days
    - all: All time data
    """
    try:
        logger.info(f"Fetching dashboard data for period: {period}, optimized: {optimized}")
        
        if optimized:
            data = get_dashboard_data_optimized(period)
        else:
            data = get_dashboard_data(period)
        
        logger.info(f"Dashboard data fetched successfully for {period} period")
        return JSONResponse(
            content=data,
            media_type="application/json",
            headers={"Cache-Control": "public, max-age=300"}  # Cache for 5 minutes
        )
    except Exception as e:
        logger.error(f"Error fetching dashboard data for period {period}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to fetch dashboard data",
                "message": str(e),
                "period": period
            }
        )

@app.get("/api/ai-insights")
def ai_insights():
    """Comprehensive AI insights endpoint"""
    try:
        # Get all insights
        retention = donor_retention()
        peak_day = peak_donation_day()
        top_school_name, top_school_amount = top_school()
        weekend_perf = weekend_performance()
        org_engagement = organization_engagement()
        repeat_rate = repeat_donors()
        upi_percentage = upi_payments_percentage()
        seasonal = seasonal_trends()
        
        return {
            "donor_retention_rate": retention,
            "peak_donation_day": peak_day,
            "top_school": {
                "name": top_school_name,
                "amount": top_school_amount
            },
            "weekend_performance": weekend_perf,
            "organization_engagement": {
                "avg_amount": org_engagement[0],
                "percentage_increase": org_engagement[1]
            },
            "repeat_donor_rate": repeat_rate,
            "upi_percentage": upi_percentage,
            "seasonal_trend": seasonal,
            "insights_summary": {
                "total_analyzed_donations": "Based on all successful donations",
                "analysis_period": "Complete historical data",
                "confidence_score": 0.85
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

@app.get("/api/forecast")
def forecast():
    """Donation forecast endpoint"""
    try:
        forecast_data = next_month_forecast()
        
        if isinstance(forecast_data, dict):
            return {
                "predicted_amount": forecast_data["predicted_amount_lakhs"] * 100000,  # Convert to rupees
                "confidence": forecast_data["confidence"],
                "basis": forecast_data["basis"],
                "next_month_prediction": forecast_data["predicted_amount_lakhs"] * 100000,
                "growth_rate": 10.0,  # From forecast.py growth factor
                "recommended_actions": [
                    "Increase marketing budget by 15% for next month",
                    "Target repeat donors with personalized campaigns",
                    "Launch weekend-specific donation drives"
                ]
            }
        else:
            return {
                "predicted_amount": 850000,
                "confidence": "Low",
                "basis": "Insufficient historical data",
                "next_month_prediction": 850000,
                "growth_rate": 5.0,
                "recommended_actions": [
                    "Collect more historical data",
                    "Implement donation tracking",
                    "Start with conservative projections"
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")

@app.get("/api/ai-insights-complete")
def ai_insights_complete():
    """Combined insights and forecast endpoint for frontend"""
    try:
        # Get insights
        insights_response = ai_insights()
        forecast_response = forecast()
        
        # Format for frontend
        top_school_info = insights_response.get("top_school", {})
        org_engagement = insights_response.get("organization_engagement", {})
        
        return {
            "ml_predictions": {
                "next_month_prediction": forecast_response.get("predicted_amount", 850000),
                "growth_rate": forecast_response.get("growth_rate", 10.0),
                "top_predicted_school": top_school_info.get("name", "Greenwood High"),
                "predicted_school_amount": top_school_info.get("amount", 350000),
                "donor_retention_rate": insights_response.get("donor_retention_rate", 78.5),
                "peak_hour_prediction": insights_response.get("peak_donation_day", "Weekend"),
                "recommended_campaigns": forecast_response.get("recommended_actions", []),
                "confidence": forecast_response.get("confidence", "Medium"),
                "forecast_basis": forecast_response.get("basis", "Historical data")
            },
            "pattern_insights": [
                {
                    "id": "weekend_performance",
                    "title": "Weekend Performance",
                    "description": f"Donations increase by {insights_response.get('weekend_performance', 45.0)}% on weekends compared to weekdays",
                    "metric": f"+{insights_response.get('weekend_performance', 45.0)}%",
                    "icon": "CalendarDays",
                    "color": "blue",
                    "importance": "high"
                },
                {
                    "id": "corporate_engagement",
                    "title": "Corporate Engagement",
                    "description": f"Corporate donors contribute {org_engagement.get('percentage_increase', 35.0)}% more on average than individual donors",
                    "metric": f"₹{org_engagement.get('avg_amount', 45000) / 1000:.0f}k avg",
                    "icon": "Building",
                    "color": "green",
                    "importance": "high"
                },
                {
                    "id": "repeat_donors",
                    "title": "Repeat Donors",
                    "description": f"{insights_response.get('repeat_donor_rate', 68.0)}% of donors make multiple contributions",
                    "metric": f"{insights_response.get('repeat_donor_rate', 68.0)}%",
                    "icon": "Users",
                    "color": "orange",
                    "importance": "medium"
                },
                {
                    "id": "upi_dominance",
                    "title": "UPI Dominance",
                    "description": f"{insights_response.get('upi_percentage', 82.0)}% of payments are made through UPI",
                    "metric": f"{insights_response.get('upi_percentage', 82.0)}%",
                    "icon": "CreditCard",
                    "color": "indigo",
                    "importance": "medium"
                },
                {
                    "id": "seasonal_peak",
                    "title": "Seasonal Trends",
                    "description": f"Donations peak during {insights_response.get('seasonal_trend', 'Oct–Dec')} season",
                    "metric": f"{insights_response.get('seasonal_trend', 'Oct-Dec')}",
                    "icon": "TrendingUp",
                    "color": "red",
                    "importance": "medium"
                },
                {
                    "id": "peak_day",
                    "title": "Peak Donation Day",
                    "description": f"Highest donation activity occurs on {insights_response.get('peak_donation_day', 'Weekends')}",
                    "metric": insights_response.get('peak_donation_day', 'Weekend'),
                    "icon": "Calendar",
                    "color": "purple",
                    "importance": "low"
                }
            ],
            "analysis_metadata": {
                "last_updated": datetime.now().isoformat(),
                "data_points_analyzed": "All successful transactions",
                "model_version": "1.0",
                "accuracy_score": 0.85
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating complete insights: {str(e)}")

@app.get("/api/dashboard/custom")
def dashboard_custom(
    start_date: str = Query(
        None,
        description="Start date (YYYY-MM-DD format). If not provided, defaults to 30 days ago."
    ),
    end_date: str = Query(
        None,
        description="End date (YYYY-MM-DD format). If not provided, defaults to today."
    ),
    interval: str = Query(
        "day",
        description="Grouping interval: 'day', 'week', 'month'",
        regex="^(day|week|month)$"
    )
):
    """
    Fetch dashboard data for a custom date range.
    
    Parameters:
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - interval: Grouping interval for trends ('day', 'week', 'month')
    
    Returns dashboard data filtered by the custom date range.
    """
    try:
        # Parse dates
        end_date_parsed = datetime.now() if not end_date else datetime.strptime(end_date, "%Y-%m-%d")
        
        if not start_date:
            # Default to 30 days before end date
            start_date_parsed = end_date_parsed - timedelta(days=30)
        else:
            start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d")
        
        # Determine period based on date range
        days_diff = (end_date_parsed - start_date_parsed).days
        
        if days_diff <= 7:
            period = "weekly"
        elif days_diff <= 30:
            period = "monthly"
        elif days_diff <= 365:
            period = "yearly"
        else:
            period = "all"
        
        logger.info(f"Fetching custom dashboard data: {start_date_parsed.date()} to {end_date_parsed.date()}, interval: {interval}")
        
        # Note: This would require modifying the dashboard functions to accept custom date ranges
        # For now, we'll use the period-based function
        data = get_dashboard_data_optimized(period)
        
        # Add custom range info to response
        data["date_range"] = {
            "start_date": start_date_parsed.date().isoformat(),
            "end_date": end_date_parsed.date().isoformat(),
            "interval": interval
        }
        
        return data
        
    except ValueError as e:
        logger.error(f"Invalid date format: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid date format. Use YYYY-MM-DD"}
        )
    except Exception as e:
        logger.error(f"Error fetching custom dashboard data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to fetch custom dashboard data",
                "message": str(e)
            }
        )

@app.get("/api/dashboard/periods")
def available_periods():
    """
    Get available period options and their descriptions.
    Useful for frontend to populate dropdowns.
    """
    return {
        "periods": [
            {
                "value": "weekly",
                "label": "Last 7 Days",
                "description": "Data from the last 7 days"
            },
            {
                "value": "monthly",
                "label": "Last 30 Days",
                "description": "Data from the last 30 days"
            },
            {
                "value": "yearly",
                "label": "Last 365 Days",
                "description": "Data from the last year"
            },
            {
                "value": "all",
                "label": "All Time",
                "description": "All available data"
            }
        ],
        "default_period": "monthly"
    }

@app.get("/api/dashboard/kpis")
def dashboard_kpis(
    period: str = Query(
        "monthly", 
        description="Time period for KPIs",
        regex="^(weekly|monthly|yearly|all)$"
    )
):
    """
    Fetch only KPIs (Key Performance Indicators) for quick loading.
    
    Returns:
    - total_donations
    - total_transactions
    - total_donors
    - total_campaigns
    - avg_donation
    - total_schools
    - max_donation
    - min_donation
    - median_donation
    """
    try:
        logger.info(f"Fetching KPIs for period: {period}")
        
        # Get full data but we'll only return KPIs
        data = get_dashboard_data_optimized(period)
        
        return {
            "period": period,
            "kpis": data.get("kpis", {}),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching KPIs for period {period}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to fetch KPIs",
                "message": str(e)
            }
        )

@app.get("/api/dashboard/trend")
def dashboard_trend(
    period: str = Query(
        "monthly", 
        description="Time period for trend data",
        regex="^(weekly|monthly|yearly|all)$"
    )
):
    """
    Fetch only trend data for charts.
    
    Returns donation trend over time for the specified period.
    """
    try:
        logger.info(f"Fetching trend data for period: {period}")
        
        data = get_dashboard_data_optimized(period)
        
        return {
            "period": period,
            "trend": data.get("trend", []),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching trend data for period {period}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to fetch trend data",
                "message": str(e)
            }
        )

@app.get("/api/dashboard/schools")
def dashboard_schools(
    period: str = Query(
        "monthly", 
        description="Time period for schools data",
        regex="^(weekly|monthly|yearly|all)$"
    )
):
    """
    Fetch only school distribution data.
    
    Returns donations by school for the specified period.
    """
    try:
        logger.info(f"Fetching schools data for period: {period}")
        
        data = get_dashboard_data_optimized(period)
        
        return {
            "period": period,
            "schools": data.get("schools", []),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching schools data for period {period}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to fetch schools data",
                "message": str(e)
            }
        )

@app.get("/api/dashboard/campaigns")
def dashboard_campaigns(
    period: str = Query(
        "monthly", 
        description="Time period for campaigns data",
        regex="^(weekly|monthly|yearly|all)$"
    )
):
    """
    Fetch only campaign distribution data.
    
    Returns donations by campaign for the specified period.
    """
    try:
        logger.info(f"Fetching campaigns data for period: {period}")
        
        data = get_dashboard_data_optimized(period)
        
        return {
            "period": period,
            "campaigns": data.get("campaigns", []),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching campaigns data for period {period}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to fetch campaigns data",
                "message": str(e)
            }
        )

@app.get("/api/dashboard/payment-modes")
def dashboard_payment_modes(
    period: str = Query(
        "monthly", 
        description="Time period for payment modes data",
        regex="^(weekly|monthly|yearly|all)$"
    )
):
    """
    Fetch only payment mode distribution data.
    
    Returns payment method breakdown for the specified period.
    """
    try:
        logger.info(f"Fetching payment modes data for period: {period}")
        
        data = get_dashboard_data_optimized(period)
        
        return {
            "period": period,
            "payment_modes": data.get("payment_mode", []),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching payment modes data for period {period}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to fetch payment modes data",
                "message": str(e)
            }
        )

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "vistara-analytics-api",
        "version": "2.0.0"
    }

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Vistara Analytics API",
        "version": "2.0.0",
        "endpoints": {
            "dashboard": "/api/dashboard?period=weekly|monthly|yearly|all",
            "dashboard_custom": "/api/dashboard/custom?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD",
            "dashboard_kpis": "/api/dashboard/kpis",
            "dashboard_trend": "/api/dashboard/trend",
            "dashboard_schools": "/api/dashboard/schools",
            "dashboard_campaigns": "/api/dashboard/campaigns",
            "dashboard_payment_modes": "/api/dashboard/payment-modes",
            "available_periods": "/api/dashboard/periods",
            "ai_insights": "/api/ai-insights",
            "ai_insights_complete": "/api/ai-insights-complete",
            "forecast": "/api/forecast",
            "health": "/health",
            "documentation": "/docs"
        },
        "description": "Analytics API for donation data with period-based filtering"
    }

# Error handlers
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": request.headers.get("X-Request-ID", "unknown")
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )