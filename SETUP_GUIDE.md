# Impact Dashboard - Setup Guide

A premium admin dashboard for trust/foundation websites displaying donation analytics with professional visualizations.

## Features

✅ **Real-time Analytics** - KPI cards showing total donations, donors, campaigns, and averages  
✅ **Advanced Visualizations** - Area charts, bar charts, donut charts for donation trends  
✅ **Top Donors Leaderboard** - Recognizes your community's most generous supporters  
✅ **Impact by Location** - School and campaign performance metrics  
✅ **Report Export** - Download weekly, monthly, or yearly reports  
✅ **Professional Design** - Foundation-inspired UI with trust-focused branding  
✅ **Responsive** - Works perfectly on desktop, tablet, and mobile  

## Prerequisites

- **Python 3.8+** for backend
- **Node.js 16+** for frontend
- **PostgreSQL** database with donation data
- **npm** or **yarn** for package management

## Backend Setup

### 1. Install Python Dependencies

```bash
# From project root
pip install fastapi uvicorn pandas sqlalchemy psycopg2-binary
```

### 2. Configure Database

Edit `/scripts/dashboard_api.py` and update the database connection:

```python
DATABASE_URL = "postgresql+psycopg2://username:password@localhost:5432/your_database"
```

### 3. Start Backend Server

```bash
# From project root
python -m scripts.main
```

The API will be available at `http://localhost:8000`

Test the connection:
```bash
curl http://localhost:8000/api/dashboard
```

## Frontend Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

Access the dashboard at `http://localhost:3000`

## Project Structure

```
/
├── app/
│   ├── page.tsx              # Main dashboard component (single file)
│   ├── layout.tsx            # Layout wrapper
│   └── globals.css           # Premium theme & styles
├── scripts/
│   ├── main.py               # FastAPI server
│   └── dashboard_api.py      # Database queries
└── SETUP_GUIDE.md            # This file
```

## Database Schema Requirements

Your PostgreSQL database must have a `donations_raw` table with these columns:

```sql
CREATE TABLE donations_raw (
    id SERIAL PRIMARY KEY,
    donor_name VARCHAR,
    donor_email VARCHAR,
    amount DECIMAL,
    payment_date TIMESTAMP,
    payment_status VARCHAR,  -- Must include 'Success' values
    payment_mode VARCHAR,     -- e.g., "Credit Card", "Bank Transfer"
    donation_type VARCHAR,    -- e.g., "Direct Donation", "Corporate Match"
    school_name VARCHAR,      -- e.g., "Lincoln High School"
    campaign_name VARCHAR     -- e.g., "Winter Drive 2026"
);
```

## Available API Endpoints

### GET `/api/dashboard`
Returns complete dashboard data:
- **KPIs**: total_donations, total_donors, total_campaigns, avg_donation
- **Trend**: Daily donation amounts
- **Schools**: Top 6 schools by donation amount
- **Campaigns**: Top 6 campaigns by donation amount
- **Donation Type**: Breakdown by donation type
- **Payment Mode**: Transaction count by payment method
- **Top Donors**: Top 5 donors by total amount

### GET `/health`
Returns server health status

## Export Reports

The dashboard provides three report formats:

1. **Weekly Report** - Summary of current week's performance
2. **Monthly Report** - Month-to-date metrics and trends
3. **Yearly Report** - Annual performance overview

Reports include:
- Key metrics (donations, donors, campaigns)
- Top performing schools and campaigns
- Donation type distribution
- Payment method breakdown
- Top 5 donors list

## Troubleshooting

### Backend Connection Error
- Ensure backend is running: `python -m scripts.main`
- Check database credentials in `dashboard_api.py`
- Verify PostgreSQL is running: `psql -U postgres`

### No Data Showing
- Verify database has records with `payment_status = 'Success'`
- Check browser console (F12) for errors
- The dashboard includes mock data fallback if backend unavailable

### Database Connection Failed
```python
# Test connection with:
python -c "from sqlalchemy import create_engine; 
engine = create_engine('postgresql+psycopg2://user:pass@localhost:5432/db')"
```

## Customization

### Change Colors
Edit `/app/globals.css` and update CSS variables:
```css
:root {
  --primary: #1a4d2e;        /* Dark green */
  --secondary: #2d7a4a;      /* Medium green */
  --accent: #f4a261;         /* Orange */
  /* ... */
}
```

### Modify Dashboard Layout
Edit `/app/page.tsx` - it's a single React component with:
- Header section
- Impact KPI cards
- Charts section
- Top donors leaderboard
- School/campaign performance
- Payment methods

### Add New Queries
Add queries to `/scripts/dashboard_api.py` and update the response in `get_dashboard_data()`

## Performance Optimization

- Dashboard loads with mock data instantly while backend connects
- Charts are optimized with Recharts library
- Database queries are optimized with proper indexing
- Frontend uses React hooks for efficient rendering

## Deployment

### Frontend to Vercel
```bash
npm run build
vercel deploy
```

### Backend to Heroku/Railway
```bash
git push heroku main
```

Set environment variables:
```
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db
```

## Support

- Check browser console (F12) for error messages
- Verify database connectivity
- Ensure all required environment variables are set
- Check backend logs: `python -m scripts.main --log-level debug`

## License

Internal use only. All rights reserved by the foundation.
