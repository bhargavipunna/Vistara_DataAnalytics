# """
# VISTARA Analytics - Ultra Professional Donation Report Generator
# =================================================================

# Times New Roman Font (Professional Typography)
# Fully Justified Text
# Tight, Clean Tables
# Stunning Business-Grade Cover Page
# Professional Layout & Spacing
# """

# import os
# import hashlib
# import pickle
# import redis  # Add this to your imports
# from datetime import datetime, timedelta
# from pathlib import Path
# from typing import Dict, List, Optional, Tuple, Any
# from dataclasses import dataclass
# import logging
# from decimal import Decimal

# # Database
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import QueuePool

# # PDF Generation with Professional Fonts
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch, mm
# from reportlab.platypus import (
#     SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
#     Image, PageBreak, HRFlowable, KeepTogether
# )
# from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont


# # ==================== LOGGING ====================

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('donation_reports.log'),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger(__name__)


# # ==================== DATA MODELS ====================

# @dataclass
# class ReportCache:
#     """Report caching structure"""
#     report_id: str
#     period_type: str
#     year: Optional[int]
#     start_date: str
#     end_date: str
#     generated_at: str
#     file_path: str
#     data_hash: str
#     version: str = "10.0.0"


# # ==================== ULTRA PROFESSIONAL DONATION REPORT AGENT ====================

# class FinalDonationReportAgent:
    
#     VERSION = "10.0.0"
    
#     def __init__(self, db_url: str = None, logo_path: str = None):
#         """Initialize the ultra professional report agent"""
        
#         # Database configuration
#         self.db_url = db_url or self._build_db_url()
#         self.engine = self._create_engine()
#         self.SessionLocal = sessionmaker(bind=self.engine)
        
#         # Company information
#         self.company_name = "Vidyaanidhi Educational Trust"
#         self.tagline = "Empowering Education Through Philanthropy"
#         self.logo_path = logo_path or "static/logo.png"
        
#         # Ultra Professional Color Scheme
#         self.primary_navy = colors.HexColor('#0A2463')      # Deep Navy Blue
#         self.accent_gold = colors.HexColor('#C5A572')        # Elegant Gold
#         self.dark_charcoal = colors.HexColor('#1E1E1E')      # Almost Black
#         self.text_charcoal = colors.HexColor('#2C2C2C')      # Dark Gray Text
#         self.light_silver = colors.HexColor('#F5F5F5')       # Light Silver Background
#         self.border_gray = colors.HexColor('#CCCCCC')        # Subtle Border
#         self.white = colors.white
        
#         # Directory setup
#         self.reports_dir = Path("reports")
#         self.cache_dir = Path("cache")
#         self.reports_dir.mkdir(exist_ok=True)
#         self.cache_dir.mkdir(exist_ok=True)
        
#         # Caching
#         self.cache_file = self.cache_dir / "report_cache.pkl"
#         self.cache = self._load_cache()
        
#         # Professional Styles
#         self.styles = getSampleStyleSheet()
#         self._setup_professional_styles()
        
#         logger.info(f"UltraProfessionalReportAgent v{self.VERSION} initialized")
    
#     def _build_db_url(self) -> str:
#         """Build database URL"""
#         host = os.getenv('DB_HOST', 'localhost')
#         port = os.getenv('DB_PORT', '5432')
#         database = os.getenv('DB_NAME', 'vistara_analytics')
#         user = os.getenv('DB_USER', 'bhargavi')
#         password = os.getenv('DB_PASSWORD', 'bindu')
#         return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
#     def _create_engine(self):
#         """Create SQLAlchemy engine"""
#         return create_engine(
#             self.db_url,
#             poolclass=QueuePool,
#             pool_size=10,
#             max_overflow=20,
#             pool_pre_ping=True,
#             echo=False
#         )
    
#     def _setup_professional_styles(self):
#         """Setup ultra professional styles with Times New Roman"""
#         styles = self.styles
        
#         # Times-Roman, Times-Bold, Times-Italic are built into ReportLab
        
#         # Cover Page - Company Name
#         styles.add(ParagraphStyle(
#             name='CoverCompany',
#             parent=styles['Title'],
#             fontSize=30,
#             textColor=self.primary_navy,
#             alignment=TA_CENTER,
#             fontName='Times-Bold',
#             leading=36,
#             spaceAfter=6,
#             letterSpacing=1
#         ))
        
#         # Cover Page - Tagline
#         styles.add(ParagraphStyle(
#             name='CoverTagline',
#             parent=styles['Normal'],
#             fontSize=11,
#             textColor=self.text_charcoal,
#             alignment=TA_CENTER,
#             fontName='Times-Italic',
#             leading=14,
#             spaceAfter=20
#         ))
        
#         # Cover Page - Report Title
#         styles.add(ParagraphStyle(
#             name='CoverTitle',
#             parent=styles['Heading1'],
#             fontSize=20,
#             textColor=self.primary_navy,
#             alignment=TA_CENTER,
#             fontName='Times-Bold',
#             leading=24,
#             spaceAfter=8,
#             letterSpacing=2
#         ))
        
#         # Cover Page - Period
#         styles.add(ParagraphStyle(
#             name='CoverPeriod',
#             parent=styles['Normal'],
#             fontSize=13,
#             textColor=self.dark_charcoal,
#             alignment=TA_CENTER,
#             fontName='Times-Roman',
#             leading=16,
#             spaceAfter=30
#         ))
        
#         # Section Header
#         styles.add(ParagraphStyle(
#             name='SectionHeader',
#             parent=styles['Heading1'],
#             fontSize=14,
#             textColor=self.primary_navy,
#             alignment=TA_LEFT,
#             fontName='Times-Bold',
#             leading=17,
#             spaceBefore=28,
#             spaceAfter=12,
#             leftIndent=0
#         ))
        
#         # Executive Summary Text - JUSTIFIED
#         styles.add(ParagraphStyle(
#             name='SummaryText',
#             parent=styles['BodyText'],
#             fontSize=11,
#             leading=18,
#             alignment=TA_JUSTIFY,  # JUSTIFIED
#             spaceAfter=10,
#             spaceBefore=0,
#             textColor=self.text_charcoal,
#             fontName='Times-Roman',
#             firstLineIndent=0
#         ))
        
#         # Body Text - JUSTIFIED
#         styles.add(ParagraphStyle(
#             name='BodyTextClean',
#             parent=styles['BodyText'],
#             fontSize=10,
#             leading=16,
#             alignment=TA_JUSTIFY,  # JUSTIFIED
#             spaceAfter=10,
#             textColor=self.text_charcoal,
#             fontName='Times-Roman',
#             firstLineIndent=0
#         ))
        
#         # Table Header
#         styles.add(ParagraphStyle(
#             name='TableHeader',
#             parent=styles['Normal'],
#             fontSize=9,
#             textColor=self.white,
#             fontName='Times-Bold',
#             alignment=TA_LEFT,
#             leading=11
#         ))
        
#         # Table Cell - Left Aligned
#         styles.add(ParagraphStyle(
#             name='TableCell',
#             parent=styles['Normal'],
#             fontSize=9,
#             textColor=self.text_charcoal,
#             fontName='Times-Roman',
#             alignment=TA_LEFT,
#             leading=11
#         ))
        
#         # Table Cell - Right Aligned (for numbers)
#         styles.add(ParagraphStyle(
#             name='TableCellRight',
#             parent=styles['Normal'],
#             fontSize=9,
#             textColor=self.text_charcoal,
#             fontName='Times-Roman',
#             alignment=TA_RIGHT,
#             leading=11
#         ))
        
#         # Table Cell - Bold
#         styles.add(ParagraphStyle(
#             name='TableCellBold',
#             parent=styles['Normal'],
#             fontSize=9,
#             textColor=self.text_charcoal,
#             fontName='Times-Bold',
#             alignment=TA_LEFT,
#             leading=11
#         ))
        
#         # Info Label (Cover Page)
#         styles.add(ParagraphStyle(
#             name='InfoLabel',
#             parent=styles['Normal'],
#             fontSize=11,
#             textColor=self.dark_charcoal,
#             fontName='Times-Bold',
#             alignment=TA_RIGHT,
#             leading=14
#         ))
        
#         # Info Value (Cover Page)
#         styles.add(ParagraphStyle(
#             name='InfoValue',
#             parent=styles['Normal'],
#             fontSize=11,
#             textColor=self.text_charcoal,
#             fontName='Times-Roman',
#             alignment=TA_LEFT,
#             leading=14
#         ))
    
#     # ==================== UTILITY FUNCTIONS ====================
    
#     def _safe_float(self, value: Any) -> float:
#         """Safely convert to float"""
#         if value is None:
#             return 0.0
#         try:
#             if isinstance(value, Decimal):
#                 return float(value)
#             return float(value)
#         except:
#             return 0.0
    
#     def _safe_int(self, value: Any) -> int:
#         """Safely convert to int"""
#         if value is None:
#             return 0
#         try:
#             if isinstance(value, Decimal):
#                 return int(value)
#             return int(value)
#         except:
#             return 0
    
#     def _format_currency(self, value: Any) -> str:
#         """Format currency"""
#         return f"Rs. {self._safe_float(value):,.2f}"
    
#     def _format_number(self, value: Any) -> str:
#         """Format number"""
#         return f"{self._safe_int(value):,}"
    
#     def _format_percentage(self, value: float) -> str:
#         """Format percentage"""
#         return f"{value:.1f}%"
    
#     # ==================== CACHING ====================
    
#     def _load_cache(self) -> Dict[str, ReportCache]:
#         """Load cache"""
#         try:
#             if self.cache_file.exists():
#                 with open(self.cache_file, 'rb') as f:
#                     return pickle.load(f)
#         except:
#             pass
#         return {}
    
#     def _save_cache(self):
#         """Save cache"""
#         try:
#             with open(self.cache_file, 'wb') as f:
#                 pickle.dump(self.cache, f)
#         except:
#             pass
    
#     def _generate_report_id(self, period_type: str, year: Optional[int], 
#                           start_date: str, end_date: str) -> str:
#         """Generate report ID"""
#         base_string = f"{period_type}_{year}_{start_date}_{end_date}_{self.VERSION}"
#         return hashlib.md5(base_string.encode()).hexdigest()[:16]
    
#     def _get_cached_report(self, report_id: str, max_age_days: int = 7) -> Optional[str]:
#         """Get cached report"""
#         if report_id in self.cache:
#             cache_entry = self.cache[report_id]
#             cache_time = datetime.fromisoformat(cache_entry.generated_at)
#             if (datetime.now() - cache_time).days < max_age_days:
#                 if Path(cache_entry.file_path).exists():
#                     logger.info(f"Using cached report: {cache_entry.file_path}")
#                     return cache_entry.file_path
#         return None
    
#     def _update_cache(self, report_id: str, period_type: str, year: Optional[int],
#                      start_date: str, end_date: str, file_path: str, data_hash: str):
#         """Update cache"""
#         self.cache[report_id] = ReportCache(
#             report_id=report_id,
#             period_type=period_type,
#             year=year,
#             start_date=start_date,
#             end_date=end_date,
#             generated_at=datetime.now().isoformat(),
#             file_path=file_path,
#             data_hash=data_hash,
#             version=self.VERSION
#         )
#         self._save_cache()
    
#     # ==================== DATABASE QUERIES ====================
    
#     def execute_query(self, query: str, params: dict = None) -> List[Dict]:
#         """Execute SQL query"""
#         session = self.SessionLocal()
#         try:
#             result = session.execute(text(query), params or {})
#             if query.strip().upper().startswith('SELECT'):
#                 columns = result.keys()
#                 rows = result.fetchall()
#                 return [dict(zip(columns, row)) for row in rows]
#             else:
#                 session.commit()
#                 return []
#         except Exception as e:
#             session.rollback()
#             logger.error(f"Query failed: {e}")
#             raise
#         finally:
#             session.close()
    
#     def get_date_range(self, period_type: str, year: int = None) -> Tuple[datetime, datetime, str, str]:
#         """Calculate date range"""
#         current_date = datetime.now()
        
#         if period_type == 'weekly':
#             end_date = current_date - timedelta(days=current_date.weekday() + 1)
#             start_date = end_date - timedelta(days=6)
#         elif period_type == 'monthly':
#             first_day_current = current_date.replace(day=1)
#             end_date = first_day_current - timedelta(days=1)
#             start_date = end_date.replace(day=1)
#         elif period_type == 'yearly':
#             year = year or (current_date.year - 1)
#             start_date = datetime(year, 1, 1)
#             end_date = datetime(year, 12, 31)
#             if year == current_date.year:
#                 end_date = current_date - timedelta(days=1)
#         else:
#             raise ValueError(f"Invalid period_type: {period_type}")
        
#         start_date_str = start_date.strftime('%Y-%m-%d 00:00:00')
#         end_date_str = end_date.strftime('%Y-%m-%d 23:59:59')
        
#         return start_date, end_date, start_date_str, end_date_str
    
#     def get_donations_summary(self, start_date: str, end_date: str) -> Dict:
#         """Get donations summary"""
#         query = """
#         SELECT 
#             COUNT(DISTINCT payment_id) as total_transactions,
#             COUNT(DISTINCT donor_email) as unique_donors,
#             COALESCE(SUM(CASE WHEN payment_status = 'Success' THEN amount ELSE 0 END), 0) as total_amount,
#             COALESCE(AVG(CASE WHEN payment_status = 'Success' THEN amount END), 0) as avg_donation,
#             COALESCE(MIN(CASE WHEN payment_status = 'Success' THEN amount END), 0) as min_donation,
#             COALESCE(MAX(CASE WHEN payment_status = 'Success' THEN amount END), 0) as max_donation,
#             COUNT(CASE WHEN payment_status = 'Success' THEN 1 END) as successful_transactions,
#             COUNT(CASE WHEN payment_status != 'Success' THEN 1 END) as failed_transactions
#         FROM donations_raw 
#         WHERE payment_date BETWEEN :start_date AND :end_date
#         """
#         results = self.execute_query(query, {'start_date': start_date, 'end_date': end_date})
#         return results[0] if results else {}
    
#     def get_top_donors(self, start_date: str, end_date: str, limit: int = 10) -> List[Dict]:
#         """Get top 10 donors"""
#         query = """
#         SELECT 
#             COALESCE(donor_name, donor_email, 'Anonymous') as donor_name,
#             COUNT(DISTINCT payment_id) as number_of_donations,
#             COALESCE(SUM(amount), 0) as total_donated,
#             COALESCE(AVG(amount), 0) as average_donation,
#             CASE 
#                 WHEN COUNT(DISTINCT payment_id) > 1 THEN 'Recurring'
#                 ELSE 'One-time'
#             END as donor_type
#         FROM donations_raw
#         WHERE payment_date BETWEEN :start_date AND :end_date 
#             AND payment_status = 'Success'
#         GROUP BY donor_name, donor_email
#         ORDER BY total_donated DESC
#         LIMIT :limit
#         """
#         return self.execute_query(query, {'start_date': start_date, 'end_date': end_date, 'limit': limit})
    
#     def get_top_schools(self, start_date: str, end_date: str, limit: int = 10) -> List[Dict]:
#         """Get top schools"""
#         query = """
#         SELECT 
#             COALESCE(school_name, 'Not Specified') as school_name,
#             COALESCE(school_location, 'Unknown') as school_location,
#             COUNT(DISTINCT payment_id) as donation_count,
#             COALESCE(SUM(amount), 0) as total_amount,
#             COUNT(DISTINCT donor_email) as unique_donors
#         FROM donations_raw
#         WHERE payment_date BETWEEN :start_date AND :end_date 
#             AND payment_status = 'Success'
#             AND school_name IS NOT NULL
#             AND school_name != ''
#         GROUP BY school_name, school_location
#         ORDER BY total_amount DESC
#         LIMIT :limit
#         """
#         return self.execute_query(query, {'start_date': start_date, 'end_date': end_date, 'limit': limit})
    
#     def get_top_campaigns(self, start_date: str, end_date: str, limit: int = 10) -> List[Dict]:
#         """Get top campaigns"""
#         query = """
#         SELECT 
#             COALESCE(campaign_name, 'General Fund') as campaign_name,
#             COALESCE(donation_type, 'N/A') as donation_type,
#             COUNT(DISTINCT payment_id) as donation_count,
#             COALESCE(SUM(amount), 0) as total_amount,
#             COUNT(DISTINCT donor_email) as unique_donors
#         FROM donations_raw
#         WHERE payment_date BETWEEN :start_date AND :end_date 
#             AND payment_status = 'Success'
#             AND campaign_name IS NOT NULL
#             AND campaign_name != ''
#         GROUP BY campaign_name, donation_type
#         ORDER BY total_amount DESC
#         LIMIT :limit
#         """
#         return self.execute_query(query, {'start_date': start_date, 'end_date': end_date, 'limit': limit})
    
#     def get_transaction_status_summary(self, start_date: str, end_date: str) -> Dict:
#         """Get transaction status"""
#         query = """
#         SELECT 
#             payment_status,
#             COUNT(*) as count,
#             COALESCE(SUM(amount), 0) as total_amount
#         FROM donations_raw
#         WHERE payment_date BETWEEN :start_date AND :end_date
#         GROUP BY payment_status
#         ORDER BY count DESC
#         """
#         results = self.execute_query(query, {'start_date': start_date, 'end_date': end_date})
        
#         summary = {
#             'success_count': 0,
#             'success_amount': 0,
#             'failed_count': 0,
#             'failed_amount': 0
#         }
        
#         for row in results:
#             status = str(row.get('payment_status', '')).lower()
#             count = self._safe_int(row.get('count', 0))
#             amount = self._safe_float(row.get('total_amount', 0))
            
#             if 'success' in status:
#                 summary['success_count'] += count
#                 summary['success_amount'] += amount
#             else:
#                 summary['failed_count'] += count
#                 summary['failed_amount'] += amount
        
#         return summary
    
#     def get_monthly_breakdown(self, year: int) -> List[Dict]:
#         """Get monthly donation breakdown for yearly reports"""
#         query = """
#         SELECT 
#             EXTRACT(MONTH FROM payment_date) as month_number,
#             TO_CHAR(payment_date, 'Month') as month_name,
#             COUNT(DISTINCT payment_id) as transaction_count,
#             COALESCE(SUM(CASE WHEN payment_status = 'Success' THEN amount ELSE 0 END), 0) as total_amount,
#             COUNT(DISTINCT donor_email) as unique_donors
#         FROM donations_raw
#         WHERE EXTRACT(YEAR FROM payment_date) = :year
#             AND payment_status = 'Success'
#         GROUP BY EXTRACT(MONTH FROM payment_date), TO_CHAR(payment_date, 'Month')
#         ORDER BY month_number
#         """
#         return self.execute_query(query, {'year': year})
    
#     # ==================== STUNNING COVER PAGE ====================
    
#     def _create_stunning_cover_page(self, period_type: str, start_date: datetime, 
#                                    end_date: datetime, year: int) -> List:
#         """Create stunning cover page with elegant gold accents"""
#         elements = []
        
#         # Top spacing
#         elements.append(Spacer(1, 5*mm))
        
#         # # Top decorative gold border
#         # elements.append(HRFlowable(
#         #     width="85%",
#         #     thickness=2,
#         #     color=self.accent_gold,
#         #     spaceBefore=0,
#         #     spaceAfter=15,
#         #     hAlign='CENTER'
#         # ))
        
#         # Logo (if exists)
#         if os.path.exists(self.logo_path):
#             try:
#                 logo = Image(self.logo_path, width=70*mm, height=70*mm, kind='proportional')
#                 logo.hAlign = 'CENTER'
#                 elements.append(logo)
#                 elements.append(Spacer(1, 3*mm))
#             except Exception as e:
#                 logger.warning(f"Logo error: {e}")
#                 elements.append(Spacer(1, 8*mm))
#         else:
#             elements.append(Spacer(1, 3*mm))
        
#         # Company Name - Large and Bold with gold underline
#         elements.append(Paragraph(self.company_name, self.styles['CoverCompany']))
        
#         # Gold underline under company name
#         elements.append(HRFlowable(
#             width="50%",
#             thickness=1,
#             color=self.accent_gold,
#             spaceBefore=5,
#             spaceAfter=8,
#             hAlign='CENTER'
#         ))
        
#         # Tagline - Elegant Italic
#         elements.append(Paragraph(self.tagline, self.styles['CoverTagline']))
        
#         # Navy divider
#         elements.append(HRFlowable(
#             width="70%",
#             thickness=0.5,
#             color=self.primary_navy,
#             spaceBefore=0,
#             spaceAfter=15,
#             hAlign='CENTER'
#         ))
        
#         # Report Title - Prominent
#         elements.append(Paragraph("DONATION PERFORMANCE REPORT", self.styles['CoverTitle']))
        
#         # Period Display with gold highlight box
#         period_display = self._get_period_display(period_type, year)
        
#         # Create a styled box for period
#         period_box_style = ParagraphStyle(
#             name='PeriodBox',
#             parent=self.styles['Normal'],
#             fontSize=14,
#             textColor=self.white,
#             alignment=TA_CENTER,
#             fontName='Times-Bold',
#             leading=18,
#             leftIndent=20,
#             rightIndent=20
#         )
        
#         period_table = Table([[Paragraph(period_display, period_box_style)]], colWidths=[120*mm])
#         period_table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (-1, -1), self.primary_navy),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('TOPPADDING', (0, 0), (-1, -1), 10),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
#             ('BOX', (0, 0), (-1, -1), 1, self.accent_gold),
#         ]))
        
#         elements.append(period_table)
#         elements.append(Spacer(1, 20*mm))
        
#         # Report Information Box - Professional with gold border
#         period_str = self._format_period_string(period_type, start_date, end_date)
        
#         info_data = [
#             [Paragraph("<b>Report Period:</b>", self.styles['InfoLabel']), 
#              Paragraph(period_str, self.styles['InfoValue'])],
#             [Paragraph("<b>Report Date:</b>", self.styles['InfoLabel']), 
#              Paragraph(datetime.now().strftime('%d %B %Y'), self.styles['InfoValue'])],
#             [Paragraph("<b>Prepared For:</b>", self.styles['InfoLabel']), 
#              Paragraph("Board of Trustees & Management Team", self.styles['InfoValue'])]
#         ]
        
#         info_table = Table(info_data, colWidths=[55*mm, 95*mm])
#         info_table.setStyle(TableStyle([
#             ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
#             ('ALIGN', (1, 0), (1, -1), 'LEFT'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
#             ('TOPPADDING', (0, 0), (-1, -1), 8),
#             ('LEFTPADDING', (0, 0), (0, -1), 10),
#             ('RIGHTPADDING', (0, 0), (0, -1), 15),
#             ('LEFTPADDING', (1, 0), (1, -1), 15),
#             ('RIGHTPADDING', (1, 0), (1, -1), 10),
#             ('BOX', (0, 0), (-1, -1), 1.5, self.accent_gold),
#             ('BACKGROUND', (0, 0), (-1, -1), self.light_silver),
#         ]))
        
#         elements.append(info_table)
        
#         # Bottom decorative gold border
#         elements.append(Spacer(1, 15*mm))
#         elements.append(HRFlowable(
#             width="85%",
#             thickness=2,
#             color=self.accent_gold,
#             spaceBefore=0,
#             spaceAfter=0,
#             hAlign='CENTER'
#         ))
        
#         return elements
    
#     # ==================== CONTENT SECTIONS ====================
    
#     def _create_executive_summary(self, summary: Dict, status_summary: Dict) -> List:
#         """Create executive summary with justified text"""
#         elements = []
        
#         elements.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))
        
#         total_amount = self._safe_float(summary.get('total_amount', 0))
#         total_transactions = self._safe_int(summary.get('total_transactions', 0))
#         unique_donors = self._safe_int(summary.get('unique_donors', 0))
#         successful = self._safe_int(status_summary.get('success_count', 0))
        
#         success_rate = (successful / total_transactions * 100) if total_transactions > 0 else 0
        
#         summary_text = f"""
#         During the reporting period, {self.company_name} successfully collected 
#         <b>{self._format_currency(total_amount)}</b> through <b>{self._format_number(successful)}</b> successful transactions 
#         out of <b>{self._format_number(total_transactions)}</b> total attempts, representing a success rate of 
#         <b>{self._format_percentage(success_rate)}</b>. These contributions came from <b>{self._format_number(unique_donors)}</b> unique donors, 
#         demonstrating strong community support for educational initiatives.
#         """
        
#         elements.append(Paragraph(summary_text, self.styles['SummaryText']))
        
#         return elements
    
#     def _create_tight_metrics_table(self, summary: Dict) -> List:
#         """Create tight, professional metrics table"""
#         elements = []
        
#         elements.append(Paragraph("KEY PERFORMANCE METRICS", self.styles['SectionHeader']))
        
#         total_amount = self._safe_float(summary.get('total_amount', 0))
#         total_transactions = self._safe_int(summary.get('total_transactions', 0))
#         unique_donors = self._safe_int(summary.get('unique_donors', 0))
#         avg_donation = self._safe_float(summary.get('avg_donation', 0))
#         max_donation = self._safe_float(summary.get('max_donation', 0))
#         successful = self._safe_int(summary.get('successful_transactions', 0))
#         failed = self._safe_int(summary.get('failed_transactions', 0))
        
#         success_pct = (successful / max(total_transactions, 1) * 100)
#         failed_pct = (failed / max(total_transactions, 1) * 100)
        
#         metrics_data = [
#             [Paragraph("<b>Metric</b>", self.styles['TableHeader']), 
#              Paragraph("<b>Value</b>", self.styles['TableHeader'])],
            
#             ["Total Donations Received", self._format_currency(total_amount)],
#             ["Total Number of Transactions", self._format_number(total_transactions)],
#             ["Successful Transactions", f"{self._format_number(successful)} ({self._format_percentage(success_pct)})"],
#             ["Failed Transactions", f"{self._format_number(failed)} ({self._format_percentage(failed_pct)})"],
#             ["Unique Donors", self._format_number(unique_donors)],
#             ["Average Donation Amount", self._format_currency(avg_donation)],
#             ["Largest Single Donation", self._format_currency(max_donation)],
#         ]
        
#         metrics_table = Table(metrics_data, colWidths=[95*mm, 70*mm])
#         metrics_table.setStyle(TableStyle([
#             # Header
#             ('BACKGROUND', (0, 0), (-1, 0), self.primary_navy),
#             ('TEXTCOLOR', (0, 0), (-1, 0), self.white),
#             ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
#             ('FONTSIZE', (0, 0), (-1, -1), 10),
#             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
#             ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            
#             # Data rows - TIGHT padding
#             ('TOPPADDING', (0, 0), (-1, -1), 5),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
#             ('LEFTPADDING', (0, 0), (-1, -1), 8),
#             ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            
#             # Styling
#             ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
#             ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.white, self.light_silver]),
#             ('GRID', (0, 0), (-1, -1), 0.5, self.border_gray),
#             ('LINEBELOW', (0, 0), (-1, 0), 1.5, self.white),
#         ]))
        
#         elements.append(metrics_table)
        
#         return elements
    
#     def _create_tight_donors_table(self, donors: List[Dict]) -> List:
#         """Create tight top donors table"""
#         elements = []
        
#         elements.append(Paragraph("TOP 10 DONORS", self.styles['SectionHeader']))
        
#         if not donors:
#             elements.append(Paragraph("No donor data available.", self.styles['BodyTextClean']))
#             return elements
        
#         table_data = [[
#             Paragraph("<b>#</b>", self.styles['TableHeader']),
#             Paragraph("<b>Donor Name</b>", self.styles['TableHeader']),
#             Paragraph("<b>Total Donated</b>", self.styles['TableHeader']),
#             Paragraph("<b>Count</b>", self.styles['TableHeader']),
#             Paragraph("<b>Average</b>", self.styles['TableHeader']),
#             Paragraph("<b>Type</b>", self.styles['TableHeader'])
#         ]]
        
#         for i, donor in enumerate(donors, 1):
#             donor_name = str(donor.get('donor_name', 'Anonymous'))[:35]
#             total = self._format_currency(donor.get('total_donated', 0))
#             count = self._format_number(donor.get('number_of_donations', 0))
#             avg = self._format_currency(donor.get('average_donation', 0))
#             dtype = str(donor.get('donor_type', 'One-time'))
            
#             table_data.append([
#                 str(i),
#                 donor_name,
#                 total,
#                 count,
#                 avg,
#                 dtype
#             ])
        
#         donor_table = Table(table_data, colWidths=[8*mm, 52*mm, 32*mm, 18*mm, 28*mm, 22*mm])
#         donor_table.setStyle(TableStyle([
#             # Header
#             ('BACKGROUND', (0, 0), (-1, 0), self.primary_navy),
#             ('TEXTCOLOR', (0, 0), (-1, 0), self.white),
#             ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
#             ('FONTSIZE', (0, 0), (-1, -1), 9),
#             ('ALIGN', (0, 0), (0, -1), 'CENTER'),
#             ('ALIGN', (2, 0), (4, -1), 'RIGHT'),
            
#             # Data rows - VERY TIGHT
#             ('TOPPADDING', (0, 0), (-1, -1), 4),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
#             ('LEFTPADDING', (0, 0), (-1, -1), 5),
#             ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            
#             # Styling
#             ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
#             ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.white, self.light_silver]),
#             ('GRID', (0, 0), (-1, -1), 0.5, self.border_gray),
#             ('LINEBELOW', (0, 0), (-1, 0), 1.5, self.white),
#         ]))
        
#         elements.append(donor_table)
        
#         return elements
    
#     def _create_tight_schools_table(self, schools: List[Dict]) -> List:
#         """Create tight schools table"""
#         elements = []
        
#         elements.append(Paragraph("TOP SCHOOLS BY DONATIONS", self.styles['SectionHeader']))
        
#         if not schools:
#             elements.append(Paragraph("No school data available.", self.styles['BodyTextClean']))
#             return elements
        
#         table_data = [[
#             Paragraph("<b>#</b>", self.styles['TableHeader']),
#             Paragraph("<b>School Name</b>", self.styles['TableHeader']),
#             Paragraph("<b>Location</b>", self.styles['TableHeader']),
#             Paragraph("<b>Total Donations</b>", self.styles['TableHeader']),
#             Paragraph("<b>Donors</b>", self.styles['TableHeader'])
#         ]]
        
#         for i, school in enumerate(schools, 1):
#             school_name = str(school.get('school_name', 'N/A'))[:32]
#             location = str(school.get('school_location', 'N/A'))[:18]
#             total = self._format_currency(school.get('total_amount', 0))
#             donors = self._format_number(school.get('unique_donors', 0))
            
#             table_data.append([
#                 str(i),
#                 school_name,
#                 location,
#                 total,
#                 donors
#             ])
        
#         school_table = Table(table_data, colWidths=[8*mm, 58*mm, 36*mm, 38*mm, 20*mm])
#         school_table.setStyle(TableStyle([
#             # Header
#             ('BACKGROUND', (0, 0), (-1, 0), self.primary_navy),
#             ('TEXTCOLOR', (0, 0), (-1, 0), self.white),
#             ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
#             ('FONTSIZE', (0, 0), (-1, -1), 9),
#             ('ALIGN', (0, 0), (0, -1), 'CENTER'),
#             ('ALIGN', (3, 0), (4, -1), 'RIGHT'),
            
#             # Data rows - VERY TIGHT
#             ('TOPPADDING', (0, 0), (-1, -1), 4),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
#             ('LEFTPADDING', (0, 0), (-1, -1), 5),
#             ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            
#             # Styling
#             ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
#             ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.white, self.light_silver]),
#             ('GRID', (0, 0), (-1, -1), 0.5, self.border_gray),
#             ('LINEBELOW', (0, 0), (-1, 0), 1.5, self.white),
#         ]))
        
#         elements.append(school_table)
        
#         return elements
    
#     def _create_tight_campaigns_table(self, campaigns: List[Dict]) -> List:
#         """Create tight campaigns table"""
#         elements = []
        
#         elements.append(Paragraph("TOP CAMPAIGNS PERFORMANCE", self.styles['SectionHeader']))
        
#         if not campaigns:
#             elements.append(Paragraph("No campaign data available.", self.styles['BodyTextClean']))
#             return elements
        
#         table_data = [[
#             Paragraph("<b>#</b>", self.styles['TableHeader']),
#             Paragraph("<b>Campaign Name</b>", self.styles['TableHeader']),
#             Paragraph("<b>Type</b>", self.styles['TableHeader']),
#             Paragraph("<b>Total Raised</b>", self.styles['TableHeader']),
#             Paragraph("<b>Donors</b>", self.styles['TableHeader'])
#         ]]
        
#         for i, campaign in enumerate(campaigns, 1):
#             campaign_name = str(campaign.get('campaign_name', 'N/A'))[:35]
#             ctype = str(campaign.get('donation_type', 'N/A'))[:15]
#             total = self._format_currency(campaign.get('total_amount', 0))
#             donors = self._format_number(campaign.get('unique_donors', 0))
            
#             table_data.append([
#                 str(i),
#                 campaign_name,
#                 ctype,
#                 total,
#                 donors
#             ])
        
#         campaign_table = Table(table_data, colWidths=[8*mm, 64*mm, 28*mm, 38*mm, 22*mm])
#         campaign_table.setStyle(TableStyle([
#             # Header
#             ('BACKGROUND', (0, 0), (-1, 0), self.primary_navy),
#             ('TEXTCOLOR', (0, 0), (-1, 0), self.white),
#             ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
#             ('FONTSIZE', (0, 0), (-1, -1), 9),
#             ('ALIGN', (0, 0), (0, -1), 'CENTER'),
#             ('ALIGN', (3, 0), (4, -1), 'RIGHT'),
            
#             # Data rows - VERY TIGHT
#             ('TOPPADDING', (0, 0), (-1, -1), 4),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
#             ('LEFTPADDING', (0, 0), (-1, -1), 5),
#             ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            
#             # Styling
#             ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
#             ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.white, self.light_silver]),
#             ('GRID', (0, 0), (-1, -1), 0.5, self.border_gray),
#             ('LINEBELOW', (0, 0), (-1, 0), 1.5, self.white),
#         ]))
        
#         elements.append(campaign_table)
        
#         return elements
    
#     def _create_monthly_breakdown_table(self, monthly_data: List[Dict]) -> List:
#         """Create monthly breakdown table for yearly reports"""
#         elements = []
        
#         elements.append(Paragraph("MONTHLY DONATION BREAKDOWN", self.styles['SectionHeader']))
        
#         if not monthly_data:
#             elements.append(Paragraph("No monthly data available.", self.styles['BodyTextClean']))
#             return elements
        
#         # Calculate month-over-month changes
#         table_data = [[
#             Paragraph("<b>Month</b>", self.styles['TableHeader']),
#             Paragraph("<b>Total Donations</b>", self.styles['TableHeader']),
#             Paragraph("<b>Transactions</b>", self.styles['TableHeader']),
#             Paragraph("<b>Donors</b>", self.styles['TableHeader']),
#             Paragraph("<b>Change</b>", self.styles['TableHeader'])
#         ]]
        
#         previous_amount = None
#         for month in monthly_data:
#             month_name = str(month.get('month_name', 'N/A')).strip()
#             total = self._safe_float(month.get('total_amount', 0))
#             transactions = self._format_number(month.get('transaction_count', 0))
#             donors = self._format_number(month.get('unique_donors', 0))
            
#             # Calculate change
#             if previous_amount is not None and previous_amount > 0:
#                 change = ((total - previous_amount) / previous_amount) * 100
#                 if change > 0:
#                     change_text = f"+{change:.1f}%"
#                     change_color = colors.HexColor('#2E7D32')  # Green
#                 elif change < 0:
#                     change_text = f"{change:.1f}%"
#                     change_color = colors.HexColor('#C62828')  # Red
#                 else:
#                     change_text = "0.0%"
#                     change_color = self.text_charcoal
#             else:
#                 change_text = "—"
#                 change_color = self.text_charcoal
            
#             table_data.append([
#                 month_name,
#                 self._format_currency(total),
#                 transactions,
#                 donors,
#                 change_text
#             ])
            
#             previous_amount = total
        
#         monthly_table = Table(table_data, colWidths=[30*mm, 45*mm, 30*mm, 25*mm, 30*mm])
#         monthly_table.setStyle(TableStyle([
#             # Header
#             ('BACKGROUND', (0, 0), (-1, 0), self.primary_navy),
#             ('TEXTCOLOR', (0, 0), (-1, 0), self.white),
#             ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
#             ('FONTSIZE', (0, 0), (-1, -1), 9),
#             ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
#             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            
#             # Data rows - VERY TIGHT
#             ('TOPPADDING', (0, 0), (-1, -1), 4),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
#             ('LEFTPADDING', (0, 0), (-1, -1), 5),
#             ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            
#             # Styling
#             ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
#             ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.white, self.light_silver]),
#             ('GRID', (0, 0), (-1, -1), 0.5, self.border_gray),
#             ('LINEBELOW', (0, 0), (-1, 0), 1.5, self.white),
#         ]))
        
#         elements.append(monthly_table)
        
#         # Add summary note
#         total_donations = sum(self._safe_float(m.get('total_amount', 0)) for m in monthly_data)
#         avg_monthly = total_donations / len(monthly_data) if monthly_data else 0
        
#         summary_note = f"""
#         <b>Monthly Summary:</b> Over the {len(monthly_data)} months shown, the average monthly donation total was 
#         {self._format_currency(avg_monthly)}. The month-over-month percentage changes indicate donation trends throughout the year.
#         """
        
#         elements.append(Spacer(1, 5*mm))
#         elements.append(Paragraph(summary_note, self.styles['BodyTextClean']))
        
#         return elements
    
#     def _create_comprehensive_analysis(self, summary: Dict, donors: List[Dict], 
#                                       schools: List[Dict], campaigns: List[Dict],
#                                       status_summary: Dict) -> List:
#         """Create comprehensive analysis with justified text"""
#         elements = []
        
#         elements.append(Paragraph("COMPREHENSIVE ANALYSIS", self.styles['SectionHeader']))
        
#         # Extract data
#         total_amount = self._safe_float(summary.get('total_amount', 0))
#         total_trans = self._safe_int(summary.get('total_transactions', 0))
#         successful = self._safe_int(status_summary.get('success_count', 0))
#         failed = self._safe_int(status_summary.get('failed_count', 0))
        
#         # Transaction analysis - JUSTIFIED
#         trans_text = f"""
#         <b>Transaction Performance:</b> Out of {self._format_number(total_trans)} total transaction attempts, 
#         {self._format_number(successful)} were successful ({self._format_percentage(successful/max(total_trans,1)*100)}) while 
#         {self._format_number(failed)} failed ({self._format_percentage(failed/max(total_trans,1)*100)}). The successful transactions 
#         generated a total revenue of {self._format_currency(total_amount)}, demonstrating robust payment processing and donor commitment.
#         """
#         elements.append(Paragraph(trans_text, self.styles['BodyTextClean']))
        
#         # Donor analysis - JUSTIFIED
#         if donors:
#             top_donor = donors[0]
#             recurring_donors = sum(1 for d in donors if d.get('donor_type') == 'Recurring')
            
#             donor_text = f"""
#             <b>Donor Performance:</b> The top donor, <b>{top_donor.get('donor_name', 'Anonymous')}</b>, contributed 
#             {self._format_currency(top_donor.get('total_donated', 0))} through 
#             {self._format_number(top_donor.get('number_of_donations', 0))} transaction(s). Among the top 10 donors, 
#             {recurring_donors} are recurring contributors, indicating strong donor loyalty and sustained support.
#             """
#             elements.append(Paragraph(donor_text, self.styles['BodyTextClean']))
        
#         # School analysis - JUSTIFIED
#         if schools:
#             top_school = schools[0]
#             total_school_amount = sum(self._safe_float(s.get('total_amount', 0)) for s in schools)
            
#             school_text = f"""
#             <b>Institutional Impact:</b> <b>{top_school.get('school_name', 'N/A')}</b> in {top_school.get('school_location', 'N/A')} 
#             received the highest support with {self._format_currency(top_school.get('total_amount', 0))} from 
#             {self._format_number(top_school.get('unique_donors', 0))} donors. The top {len(schools)} schools collectively received 
#             {self._format_currency(total_school_amount)}, representing {self._format_percentage(total_school_amount/max(total_amount,1)*100)} 
#             of total donations.
#             """
#             elements.append(Paragraph(school_text, self.styles['BodyTextClean']))
        
#         # Campaign analysis - JUSTIFIED
#         if campaigns:
#             top_campaign = campaigns[0]
#             total_campaign_amount = sum(self._safe_float(c.get('total_amount', 0)) for c in campaigns)
            
#             campaign_text = f"""
#             <b>Campaign Effectiveness:</b> The <b>{top_campaign.get('campaign_name', 'N/A')}</b> campaign emerged as the most successful, 
#             raising {self._format_currency(top_campaign.get('total_amount', 0))} from {self._format_number(top_campaign.get('unique_donors', 0))} donors. 
#             The top {len(campaigns)} campaigns collectively raised {self._format_currency(total_campaign_amount)}, demonstrating effective 
#             fundraising strategies and strong donor engagement.
#             """
#             elements.append(Paragraph(campaign_text, self.styles['BodyTextClean']))
        
#         return elements
    
#     def _create_header_footer(self, canvas_obj, doc):
#         """Create professional header and footer"""
#         canvas_obj.saveState()
        
#         # Header
#         header_y = A4[1] - 15*mm
#         line_y = A4[1] - 18*mm
        
#         canvas_obj.setFont("Times-Roman", 9)
#         canvas_obj.setFillColor(self.text_charcoal)
#         canvas_obj.drawString(20*mm, header_y, self.company_name)
#         canvas_obj.drawRightString(A4[0] - 20*mm, header_y, f"Page {doc.page}")
        
#         canvas_obj.setStrokeColor(self.border_gray)
#         canvas_obj.setLineWidth(0.5)
#         canvas_obj.line(20*mm, line_y, A4[0] - 20*mm, line_y)
        
#         # Footer
#         footer_y = 15*mm
#         canvas_obj.line(20*mm, footer_y + 4*mm, A4[0] - 20*mm, footer_y + 4*mm)
        
#         canvas_obj.setFont("Times-Roman", 8)
#         canvas_obj.setFillColor(self.text_charcoal)
#         canvas_obj.drawString(20*mm, footer_y, f"Generated: {datetime.now().strftime('%d %B %Y')}")
#         canvas_obj.drawCentredString(A4[0]/2, footer_y, "Donation Performance Report")
        
#         canvas_obj.restoreState()
    
#     def _format_period_string(self, period_type: str, start_date: datetime, end_date: datetime) -> str:
#         """Format period string"""
#         if period_type == 'weekly':
#             return f"{start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}"
#         elif period_type == 'monthly':
#             return f"{start_date.strftime('%B %Y')}"
#         else:
#             return f"Calendar Year {start_date.year}"
    
#     def _get_period_display(self, period_type: str, year: int) -> str:
#         """Get period display"""
#         if period_type == 'weekly':
#             return "Weekly Performance Analysis"
#         elif period_type == 'monthly':
#             return "Monthly Performance Analysis"
#         else:
#             return f"{year} Annual Performance Analysis"
    
#     # ==================== MAIN GENERATION ====================
    
#     def generate_report(self, period_type: str, year: int = None, 
#                        force_regenerate: bool = False) -> str:
#         """Generate ultra professional donation report"""
#         try:
#             logger.info(f"Generating ultra professional report: {period_type} {year or ''}")
            
#             # Get date range
#             start_date, end_date, start_date_str, end_date_str = self.get_date_range(period_type, year)
            
#             # Check cache
#             report_id = self._generate_report_id(period_type, year, start_date_str, end_date_str)
#             if not force_regenerate:
#                 cached_path = self._get_cached_report(report_id)
#                 if cached_path:
#                     return cached_path
            
#             # Fetch all data
#             logger.info("Fetching data...")
#             summary = self.get_donations_summary(start_date_str, end_date_str)
#             donors = self.get_top_donors(start_date_str, end_date_str, 10)
#             schools = self.get_top_schools(start_date_str, end_date_str, 10)
#             campaigns = self.get_top_campaigns(start_date_str, end_date_str, 10)
#             status_summary = self.get_transaction_status_summary(start_date_str, end_date_str)
            
#             # For yearly reports, get monthly breakdown
#             monthly_data = None
#             if period_type == 'yearly':
#                 report_year = year or (datetime.now().year - 1)
#                 monthly_data = self.get_monthly_breakdown(report_year)
#                 logger.info(f"Fetched monthly breakdown for {report_year}")
            
#             # Generate filename
#             timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#             filename = f"donation_report_{period_type}_{year or 'current'}_{timestamp}.pdf"
#             output_path = self.reports_dir / filename
            
#             # Build PDF
#             logger.info(f"Building ultra professional PDF: {output_path}")
#             self._build_ultra_professional_pdf(
#                 output_path=str(output_path),
#                 period_type=period_type,
#                 year=year,
#                 start_date=start_date,
#                 end_date=end_date,
#                 summary=summary,
#                 donors=donors,
#                 schools=schools,
#                 campaigns=campaigns,
#                 status_summary=status_summary,
#                 monthly_data=monthly_data
#             )
            
#             # Update cache
#             data_hash = hashlib.md5(str(summary).encode()).hexdigest()
#             self._update_cache(report_id, period_type, year, start_date_str, 
#                              end_date_str, str(output_path), data_hash)
            
#             logger.info(f"Ultra professional report generated: {output_path}")
#             return str(output_path)
            
#         except Exception as e:
#             logger.error(f"Report generation failed: {e}", exc_info=True)
#             raise
    
#     def _build_ultra_professional_pdf(self, output_path: str, period_type: str, year: int,
#                                      start_date: datetime, end_date: datetime, summary: Dict,
#                                      donors: List[Dict], schools: List[Dict], campaigns: List[Dict],
#                                      status_summary: Dict, monthly_data: List[Dict] = None):
#         """Build ultra professional PDF"""
        
#         doc = SimpleDocTemplate(
#             output_path,
#             pagesize=A4,
#             rightMargin=20*mm,
#             leftMargin=20*mm,
#             topMargin=25*mm,
#             bottomMargin=22*mm,
#             title=f"{self.company_name} - Donation Report",
#             author=self.company_name
#         )
        
#         story = []
        
#         # Stunning cover page
#         story.extend(self._create_stunning_cover_page(period_type, start_date, end_date, year))
#         story.append(PageBreak())
        
#         # Content sections - all with justified text and tight tables
#         story.extend(self._create_executive_summary(summary, status_summary))
#         story.extend(self._create_tight_metrics_table(summary))
        
#         # For yearly reports, add monthly breakdown BEFORE top donors
#         if period_type == 'yearly' and monthly_data:
#             story.extend(self._create_monthly_breakdown_table(monthly_data))
        
#         story.extend(self._create_tight_donors_table(donors))
#         story.extend(self._create_tight_schools_table(schools))
#         story.extend(self._create_tight_campaigns_table(campaigns))
#         story.extend(self._create_comprehensive_analysis(summary, donors, schools, campaigns, status_summary))
        
#         # Build with professional header/footer
#         doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)
    
#     # ==================== UTILITIES ====================
    
#     def list_reports(self) -> List[Dict]:
#         """List reports"""
#         reports = []
#         for file in sorted(self.reports_dir.glob("*.pdf"), key=lambda x: x.stat().st_mtime, reverse=True):
#             stats = file.stat()
#             reports.append({
#                 'filename': file.name,
#                 'path': str(file),
#                 'size_mb': stats.st_size / (1024 * 1024),
#                 'created': datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
#             })
#         return reports
    
#     def cleanup_old_reports(self, days: int = 30) -> int:
#         """Cleanup old reports"""
#         cutoff = datetime.now() - timedelta(days=days)
#         deleted = 0
#         for file in self.reports_dir.glob("*.pdf"):
#             if datetime.fromtimestamp(file.stat().st_ctime) < cutoff:
#                 file.unlink()
#                 deleted += 1
#         return deleted


# # ==================== CLI ====================

# def main():
#     """Command-line interface"""
#     print("=" * 80)
#     print("VIDYAANIDHI EDUCATIONAL TRUST")
#     print("Ultra Professional Donation Report Generator v10.0")
#     print("=" * 80)
#     print()
    
#     try:
#         agent = FinalDonationReportAgent()
#         print("Final donation report agent initialized\n")
#     except Exception as e:
#         print(f"Failed: {e}")
#         return
    
#     while True:
#         print("-" * 80)
#         print("DONATION REPORT MENU")
#         print("-" * 80)
#         print("1. Generate Weekly Report")
#         print("2. Generate Monthly Report")
#         print("3. Generate Yearly Report (current)")
#         print("4. Generate Yearly Report (custom year)")
#         print("5. List Reports")
#         print("6. Cleanup Old Reports")
#         print("7. Exit")
#         print()
        
#         choice = input("Select (1-7): ").strip()
        
#         try:
#             if choice == '1':
#                 print("\nGenerating weekly report...")
#                 path = agent.generate_report('weekly')
#                 print(f" Report: {path}\n")
                
#             elif choice == '2':
#                 print("\nGenerating monthly report...")
#                 path = agent.generate_report('monthly')
#                 print(f"Report: {path}\n")
                
#             elif choice == '3':
#                 year = datetime.now().year
#                 print(f"\nGenerating {year} report...")
#                 path = agent.generate_report('yearly', year=year)
#                 print(f"Report: {path}\n")
                
#             elif choice == '4':
#                 year_input = input("Enter year: ").strip()
#                 try:
#                     year = int(year_input)
#                     print(f"\nGenerating {year} report...")
#                     path = agent.generate_report('yearly', year=year)
#                     print(f"Report: {path}\n")
#                 except ValueError:
#                     print("Invalid year\n")
                    
#             elif choice == '5':
#                 reports = agent.list_reports()
#                 print(f"\nReports ({len(reports)}):")
#                 print("-" * 80)
#                 for i, r in enumerate(reports, 1):
#                     print(f"{i}. {r['filename']}")
#                     print(f"   {r['size_mb']:.2f} MB | {r['created']}\n")
                    
#             elif choice == '6':
#                 confirm = input("Delete 30+ day old reports? (y/N): ").strip().lower()
#                 if confirm == 'y':
#                     deleted = agent.cleanup_old_reports(30)
#                     print(f"Deleted {deleted} reports\n")
                    
#             elif choice == '7':
#                 print("\nThank you!\n")
#                 break
                
#             else:
#                 print("Invalid\n")
                
#         except Exception as e:
#             print(f"\n Error: {e}\n")
        
#         input("Press Enter...")
#         print()


# if __name__ == "__main__":
#     main()

"""
VISTARA Analytics - Ultra Professional Donation Report Generator
=================================================================

Times New Roman Font (Professional Typography)
Fully Justified Text
Tight, Clean Tables
Stunning Business-Grade Cover Page
Professional Layout & Spacing
"""

import os
import hashlib
import redis
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging
from decimal import Decimal
import json
from dotenv import load_dotenv
load_dotenv()

# Database
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# PDF Generation with Professional Fonts
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('donation_reports.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== DATA MODELS ====================
@dataclass
class ReportCache:
    """Report caching structure for Redis"""
    report_id: str
    period_type: str
    year: Optional[int]
    start_date: str
    end_date: str
    generated_at: str
    file_path: str
    data_fingerprint: str
    version: str = "10.0.0"

    def to_dict(self) -> dict:
        return {
            'report_id': self.report_id,
            'period_type': self.period_type,
            'year': self.year,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'generated_at': self.generated_at,
            'file_path': self.file_path,
            'data_fingerprint': self.data_fingerprint,
            'version': self.version
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            report_id=data['report_id'],
            period_type=data['period_type'],
            year=data['year'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            generated_at=data['generated_at'],
            file_path=data['file_path'],
            data_fingerprint=data['data_fingerprint'],
            version=data.get('version', '10.0.0')
        )

# ==================== ULTRA PROFESSIONAL DONATION REPORT AGENT ====================
class FinalDonationReportAgent:
    VERSION = "10.0.0"

    def __init__(self, db_url: str = None, logo_path: str = None,
             redis_host: str = None, redis_port: int = None,
             redis_db: int = None, redis_password: str = None):

        """Initialize the ultra professional report agent with Redis caching"""

        self.redis_host = redis_host or os.getenv("REDIS_HOST", "localhost")
        self.redis_port = redis_port or int(os.getenv("REDIS_PORT", 6379))
        self.redis_db = redis_db or int(os.getenv("REDIS_DB", 0))
        self.redis_password = redis_password or os.getenv("REDIS_PASSWORD")

        # Enable/disable Redis via env
        self.use_redis = os.getenv("USE_REDIS", "true").lower() == "true"

        self.redis_client = None
        if self.use_redis:
            self.redis_client = self._get_redis_connection()

        if self.redis_client:
            logger.info("UltraProfessionalReportAgent initialized WITH Redis cache")
        else:
            logger.warning("UltraProfessionalReportAgent initialized WITHOUT Redis cache")

        # Database configuration
        self.db_url = db_url or self._build_db_url()
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(bind=self.engine)

       
        # Company information
        self.company_name = "Vidyaanidhi Educational Trust"
        self.tagline = "Empowering Education Through Philanthropy"
        self.logo_path = logo_path or "static/logo.png"

        # Ultra Professional Color Scheme
        self.primary_navy = colors.HexColor('#0A2463')
        self.accent_gold = colors.HexColor('#C5A572')
        self.dark_charcoal = colors.HexColor('#1E1E1E')
        self.text_charcoal = colors.HexColor('#2C2C2C')
        self.light_silver = colors.HexColor('#F5F5F5')
        self.border_gray = colors.HexColor('#CCCCCC')
        self.white = colors.white

        # Directory setup
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

        # Professional Styles
        self.styles = getSampleStyleSheet()
        self._setup_professional_styles()

        logger.info(f"UltraProfessionalReportAgent v{self.VERSION} initialized with Redis")

    # ==================== DATABASE UTILITIES ====================
    def _build_db_url(self) -> str:
        """Build database URL"""
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        database = os.getenv('DB_NAME', 'vistara_analytics')
        user = os.getenv('DB_USER', 'bhargavi')
        password = os.getenv('DB_PASSWORD', 'bindu')
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    def _create_engine(self):
        """Create SQLAlchemy engine"""
        return create_engine(
            self.db_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=False
        )

    # ==================== REDIS CACHING ====================
    def _generate_report_id(self, period_type: str, year: Optional[int],
                            start_date: str, end_date: str) -> str:
        """Generate unique report ID"""
        base_string = f"{period_type}_{year}_{start_date}_{end_date}_{self.VERSION}"
        return hashlib.md5(base_string.encode()).hexdigest()[:16]

    
    def _generate_data_fingerprint(self, start_date: str, end_date: str) -> str:
        """
        Generate a fingerprint for the data within the date range.
        Uses MAX(updated_at | created_at) if available, otherwise COUNT(*).
        """
        session = self.SessionLocal()
        try:
            # Step 1: detect timestamp column
            timestamp_column = None

            column_check_query = """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'donations_raw'
                AND column_name IN ('updated_at', 'created_at')
                ORDER BY column_name = 'updated_at' DESC
                LIMIT 1
            """

            result = session.execute(text(column_check_query)).fetchone()
            if result:
                timestamp_column = result[0]

            # Step 2: build query safely
            if timestamp_column:
                query = f"""
                    SELECT 
                        COUNT(*) AS donation_count,
                        COALESCE(MAX({timestamp_column})::text, '') AS max_ts
                    FROM donations_raw
                    WHERE payment_date BETWEEN :start_date AND :end_date
                """
                result = session.execute(
                    text(query),
                    {"start_date": start_date, "end_date": end_date}
                ).fetchone()

                count = result[0] or 0
                max_ts = result[1] or ""
                raw_fingerprint = f"{count}|{max_ts}"

            else:
                # Step 3: fallback clean count
                query = """
                    SELECT COUNT(*)
                    FROM donations_raw
                    WHERE payment_date BETWEEN :start_date AND :end_date
                """
                count = session.execute(
                    text(query),
                    {"start_date": start_date, "end_date": end_date}
                ).scalar()

                raw_fingerprint = f"{count or 0}|"

        except Exception as e:
            session.rollback()  # 🔥 CRITICAL FIX
            logger.error(f"Fingerprint generation failed: {e}")
            raw_fingerprint = str(datetime.now().timestamp())

        finally:
            session.close()

        return hashlib.md5(raw_fingerprint.encode()).hexdigest()[:16]

    def _get_cached_report(self, report_id: str, data_fingerprint: str,
                           max_age_days: int = 7) -> Optional[str]:
        """Get cached report from Redis if valid"""
        if not self.redis_client:
            return None

        try:
            cache_key = f"report:{report_id}"
            cache_data = self.redis_client.hgetall(cache_key)

            if not cache_data:
                return None

            # Check version compatibility
            if cache_data.get('version') != self.VERSION:
                logger.info(f"Cache version mismatch, regenerating")
                self.redis_client.delete(cache_key)
                return None

            # Check data freshness
            stored_fingerprint = cache_data.get('data_fingerprint')
            if stored_fingerprint != data_fingerprint:
                logger.info("Data fingerprint mismatch, cache invalid")
                self.redis_client.delete(cache_key)
                return None

            # Check age
            generated_at = datetime.fromisoformat(cache_data['generated_at'])
            if (datetime.now() - generated_at).days >= max_age_days:
                logger.info("Cache entry too old, regenerating")
                self.redis_client.delete(cache_key)
                return None

            # Check if file still exists
            file_path = cache_data.get('file_path')
            if not file_path or not Path(file_path).exists():
                logger.info("Cached report file missing, regenerating")
                self.redis_client.delete(cache_key)
                return None

            logger.info(f"Using cached report: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Redis cache read error: {e}")
            return None

    def _update_cache(self, report_id: str, period_type: str, year: Optional[int],
                      start_date: str, end_date: str, file_path: str,
                      data_fingerprint: str):
        """Update Redis cache with new report entry"""
        if not self.redis_client:
            return

        try:
            cache_entry = ReportCache(
                report_id=report_id,
                period_type=period_type,
                year=year,
                start_date=start_date,
                end_date=end_date,
                generated_at=datetime.now().isoformat(),
                file_path=file_path,
                data_fingerprint=data_fingerprint,
                version=self.VERSION
            )

            cache_key = f"report:{report_id}"
            # self.redis_client.hset(cache_key, mapping=cache_entry.to_dict())
            safe_mapping = {
                k: (str(v) if v is not None else "")
                for k, v in cache_entry.to_dict().items()
            }

            self.redis_client.hset(cache_key, mapping=safe_mapping)


            # Set expiration (30 days)
            self.redis_client.expire(cache_key, 60 * 60 * 24 * 30)

            # Maintain a list of recent report IDs (for admin)
            self.redis_client.lpush("reports:recent", report_id)
            self.redis_client.ltrim("reports:recent", 0, 99)

            logger.info(f"Redis cache updated for {report_id}")
        except Exception as e:
            logger.error(f"Redis cache update error: {e}")

    def _invalidate_cache(self, report_id: str = None, pattern: str = None):
        """Invalidate specific report or all reports matching pattern"""
        if not self.redis_client:
            return
        try:
            if report_id:
                self.redis_client.delete(f"report:{report_id}")
                logger.info(f"Cache invalidated for {report_id}")
            elif pattern:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"Cache invalidated for {len(keys)} keys")
        except Exception as e:
            logger.error(f"Redis cache invalidation error: {e}")
    def _get_redis_connection(self) -> redis.Redis | None:
        """Establish Redis connection (Upstash + Local supported)"""
        try:
            redis_url = os.getenv("REDIS_URL")

            if redis_url:
                logger.info("Connecting to Redis via REDIS_URL (Upstash / TLS)")
                client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
            else:
                logger.info("Connecting to Redis via host/port (local)")
                client = redis.Redis(
                    host=self.redis_host,
                    port=self.redis_port,
                    db=self.redis_db,
                    password=self.redis_password,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )

            client.ping()
            logger.info("Redis connection established successfully")
            return client

        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}. Caching disabled.")
            return None
        except Exception as e:
            logger.error(f"Unexpected Redis error: {e}. Caching disabled.")
            return None

    # ==================== S3 CLOUD INTEGRATION (COMMENTED FOR FUTURE USE) ====================
    """
    def _upload_to_s3(self, local_path: str, s3_key: str = None) -> Optional[str]:
        # Upload report to S3 and return public URL
        import boto3
        from botocore.exceptions import ClientError

        if not s3_key:
            s3_key = f"reports/{Path(local_path).name}"

        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'ap-south-1')
        )

        try:
            bucket = os.getenv('S3_BUCKET', 'vistara-donation-reports')
            s3_client.upload_file(local_path, bucket, s3_key)
            # Generate presigned URL or public URL based on bucket policy
            url = f"https://{bucket}.s3.amazonaws.com/{s3_key}"
            logger.info(f"Uploaded report to S3: {url}")
            return url
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            return None

    def _download_from_s3(self, s3_key: str, local_path: str) -> bool:
        # Download report from S3
        import boto3
        from botocore.exceptions import ClientError

        s3_client = boto3.client('s3')
        try:
            bucket = os.getenv('S3_BUCKET', 'vistara-donation-reports')
            s3_client.download_file(bucket, s3_key, local_path)
            return True
        except ClientError as e:
            logger.error(f"S3 download failed: {e}")
            return False
    """

    # ==================== OTHER UTILITIES (unchanged) ====================
    def _safe_float(self, value: Any) -> float:
        if value is None:
            return 0.0
        try:
            if isinstance(value, Decimal):
                return float(value)
            return float(value)
        except:
            return 0.0

    def _safe_int(self, value: Any) -> int:
        if value is None:
            return 0
        try:
            if isinstance(value, Decimal):
                return int(value)
            return int(value)
        except:
            return 0

    def _format_currency(self, value: Any) -> str:
        return f"Rs. {self._safe_float(value):,.2f}"

    def _format_number(self, value: Any) -> str:
        return f"{self._safe_int(value):,}"

    def _format_percentage(self, value: float) -> str:
        return f"{value:.1f}%"

    # ==================== STYLES (unchanged) ====================
    def _setup_professional_styles(self):
        """Setup ultra professional styles with Times New Roman"""
        styles = self.styles

        # Cover Page - Company Name
        styles.add(ParagraphStyle(
            name='CoverCompany',
            parent=styles['Title'],
            fontSize=30,
            textColor=self.primary_navy,
            alignment=TA_CENTER,
            fontName='Times-Bold',
            leading=36,
            spaceAfter=6,
            letterSpacing=1
        ))

        # Cover Page - Tagline
        styles.add(ParagraphStyle(
            name='CoverTagline',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.text_charcoal,
            alignment=TA_CENTER,
            fontName='Times-Italic',
            leading=14,
            spaceAfter=20
        ))

        # Cover Page - Report Title
        styles.add(ParagraphStyle(
            name='CoverTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=self.primary_navy,
            alignment=TA_CENTER,
            fontName='Times-Bold',
            leading=24,
            spaceAfter=8,
            letterSpacing=2
        ))

        # Cover Page - Period
        styles.add(ParagraphStyle(
            name='CoverPeriod',
            parent=styles['Normal'],
            fontSize=13,
            textColor=self.dark_charcoal,
            alignment=TA_CENTER,
            fontName='Times-Roman',
            leading=16,
            spaceAfter=30
        ))

        # Section Header
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=self.primary_navy,
            alignment=TA_LEFT,
            fontName='Times-Bold',
            leading=17,
            spaceBefore=28,
            spaceAfter=12,
            leftIndent=0
        ))

        # Executive Summary Text - JUSTIFIED
        styles.add(ParagraphStyle(
            name='SummaryText',
            parent=styles['BodyText'],
            fontSize=11,
            leading=18,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            spaceBefore=0,
            textColor=self.text_charcoal,
            fontName='Times-Roman',
            firstLineIndent=0
        ))

        # Body Text - JUSTIFIED
        styles.add(ParagraphStyle(
            name='BodyTextClean',
            parent=styles['BodyText'],
            fontSize=10,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            textColor=self.text_charcoal,
            fontName='Times-Roman',
            firstLineIndent=0
        ))

        # Table Header
        styles.add(ParagraphStyle(
            name='TableHeader',
            parent=styles['Normal'],
            fontSize=9,
            textColor=self.white,
            fontName='Times-Bold',
            alignment=TA_LEFT,
            leading=11
        ))

        # Table Cell - Left Aligned
        styles.add(ParagraphStyle(
            name='TableCell',
            parent=styles['Normal'],
            fontSize=9,
            textColor=self.text_charcoal,
            fontName='Times-Roman',
            alignment=TA_LEFT,
            leading=11
        ))

        # Table Cell - Right Aligned
        styles.add(ParagraphStyle(
            name='TableCellRight',
            parent=styles['Normal'],
            fontSize=9,
            textColor=self.text_charcoal,
            fontName='Times-Roman',
            alignment=TA_RIGHT,
            leading=11
        ))

        # Table Cell - Bold
        styles.add(ParagraphStyle(
            name='TableCellBold',
            parent=styles['Normal'],
            fontSize=9,
            textColor=self.text_charcoal,
            fontName='Times-Bold',
            alignment=TA_LEFT,
            leading=11
        ))

        # Info Label (Cover Page)
        styles.add(ParagraphStyle(
            name='InfoLabel',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.dark_charcoal,
            fontName='Times-Bold',
            alignment=TA_RIGHT,
            leading=14
        ))

        # Info Value (Cover Page)
        styles.add(ParagraphStyle(
            name='InfoValue',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.text_charcoal,
            fontName='Times-Roman',
            alignment=TA_LEFT,
            leading=14
        ))

    # ==================== DATABASE QUERIES (unchanged) ====================
    def execute_query(self, query: str, params: dict = None) -> List[Dict]:
        """Execute SQL query"""
        session = self.SessionLocal()
        try:
            result = session.execute(text(query), params or {})
            if query.strip().upper().startswith('SELECT'):
                columns = result.keys()
                rows = result.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            else:
                session.commit()
                return []
        except Exception as e:
            session.rollback()
            logger.error(f"Query failed: {e}")
            raise
        finally:
            session.close()

    def get_date_range(self, period_type: str, year: int = None) -> Tuple[datetime, datetime, str, str]:
        """Calculate date range"""
        current_date = datetime.now()

        if period_type == 'weekly':
            end_date = current_date - timedelta(days=current_date.weekday() + 1)
            start_date = end_date - timedelta(days=6)
        elif period_type == 'monthly':
            first_day_current = current_date.replace(day=1)
            end_date = first_day_current - timedelta(days=1)
            start_date = end_date.replace(day=1)
        elif period_type == 'yearly':
            year = year or (current_date.year - 1)
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)
            if year == current_date.year:
                end_date = current_date - timedelta(days=1)
        else:
            raise ValueError(f"Invalid period_type: {period_type}")

        start_date_str = start_date.strftime('%Y-%m-%d 00:00:00')
        end_date_str = end_date.strftime('%Y-%m-%d 23:59:59')

        return start_date, end_date, start_date_str, end_date_str

    def get_donations_summary(self, start_date: str, end_date: str) -> Dict:
        query = """
        SELECT 
            COUNT(DISTINCT payment_id) as total_transactions,
            COUNT(DISTINCT donor_email) as unique_donors,
            COALESCE(SUM(CASE WHEN payment_status = 'Success' THEN amount ELSE 0 END), 0) as total_amount,
            COALESCE(AVG(CASE WHEN payment_status = 'Success' THEN amount END), 0) as avg_donation,
            COALESCE(MIN(CASE WHEN payment_status = 'Success' THEN amount END), 0) as min_donation,
            COALESCE(MAX(CASE WHEN payment_status = 'Success' THEN amount END), 0) as max_donation,
            COUNT(CASE WHEN payment_status = 'Success' THEN 1 END) as successful_transactions,
            COUNT(CASE WHEN payment_status != 'Success' THEN 1 END) as failed_transactions
        FROM donations_raw 
        WHERE payment_date BETWEEN :start_date AND :end_date
        """
        results = self.execute_query(query, {'start_date': start_date, 'end_date': end_date})
        return results[0] if results else {}

    def get_top_donors(self, start_date: str, end_date: str, limit: int = 10) -> List[Dict]:
        query = """
        SELECT 
            COALESCE(donor_name, donor_email, 'Anonymous') as donor_name,
            COUNT(DISTINCT payment_id) as number_of_donations,
            COALESCE(SUM(amount), 0) as total_donated,
            COALESCE(AVG(amount), 0) as average_donation,
            CASE 
                WHEN COUNT(DISTINCT payment_id) > 1 THEN 'Recurring'
                ELSE 'One-time'
            END as donor_type
        FROM donations_raw
        WHERE payment_date BETWEEN :start_date AND :end_date 
            AND payment_status = 'Success'
        GROUP BY donor_name, donor_email
        ORDER BY total_donated DESC
        LIMIT :limit
        """
        return self.execute_query(query, {'start_date': start_date, 'end_date': end_date, 'limit': limit})

    def get_top_schools(self, start_date: str, end_date: str, limit: int = 10) -> List[Dict]:
        query = """
        SELECT 
            COALESCE(school_name, 'Not Specified') as school_name,
            COALESCE(school_location, 'Unknown') as school_location,
            COUNT(DISTINCT payment_id) as donation_count,
            COALESCE(SUM(amount), 0) as total_amount,
            COUNT(DISTINCT donor_email) as unique_donors
        FROM donations_raw
        WHERE payment_date BETWEEN :start_date AND :end_date 
            AND payment_status = 'Success'
            AND school_name IS NOT NULL
            AND school_name != ''
        GROUP BY school_name, school_location
        ORDER BY total_amount DESC
        LIMIT :limit
        """
        return self.execute_query(query, {'start_date': start_date, 'end_date': end_date, 'limit': limit})

    def get_top_campaigns(self, start_date: str, end_date: str, limit: int = 10) -> List[Dict]:
        query = """
        SELECT 
            COALESCE(campaign_name, 'General Fund') as campaign_name,
            COALESCE(donation_type, 'N/A') as donation_type,
            COUNT(DISTINCT payment_id) as donation_count,
            COALESCE(SUM(amount), 0) as total_amount,
            COUNT(DISTINCT donor_email) as unique_donors
        FROM donations_raw
        WHERE payment_date BETWEEN :start_date AND :end_date 
            AND payment_status = 'Success'
            AND campaign_name IS NOT NULL
            AND campaign_name != ''
        GROUP BY campaign_name, donation_type
        ORDER BY total_amount DESC
        LIMIT :limit
        """
        return self.execute_query(query, {'start_date': start_date, 'end_date': end_date, 'limit': limit})

    def get_transaction_status_summary(self, start_date: str, end_date: str) -> Dict:
        query = """
        SELECT 
            payment_status,
            COUNT(*) as count,
            COALESCE(SUM(amount), 0) as total_amount
        FROM donations_raw
        WHERE payment_date BETWEEN :start_date AND :end_date
        GROUP BY payment_status
        ORDER BY count DESC
        """
        results = self.execute_query(query, {'start_date': start_date, 'end_date': end_date})

        summary = {
            'success_count': 0,
            'success_amount': 0,
            'failed_count': 0,
            'failed_amount': 0
        }

        for row in results:
            status = str(row.get('payment_status', '')).lower()
            count = self._safe_int(row.get('count', 0))
            amount = self._safe_float(row.get('total_amount', 0))

            if 'success' in status:
                summary['success_count'] += count
                summary['success_amount'] += amount
            else:
                summary['failed_count'] += count
                summary['failed_amount'] += amount

        return summary

    def get_monthly_breakdown(self, year: int) -> List[Dict]:
        query = """
        SELECT 
            EXTRACT(MONTH FROM payment_date) as month_number,
            TO_CHAR(payment_date, 'Month') as month_name,
            COUNT(DISTINCT payment_id) as transaction_count,
            COALESCE(SUM(CASE WHEN payment_status = 'Success' THEN amount ELSE 0 END), 0) as total_amount,
            COUNT(DISTINCT donor_email) as unique_donors
        FROM donations_raw
        WHERE EXTRACT(YEAR FROM payment_date) = :year
            AND payment_status = 'Success'
        GROUP BY EXTRACT(MONTH FROM payment_date), TO_CHAR(payment_date, 'Month')
        ORDER BY month_number
        """
        return self.execute_query(query, {'year': year})

    # ==================== COVER PAGE (unchanged) ====================
    def _create_stunning_cover_page(self, period_type: str, start_date: datetime,
                                    end_date: datetime, year: int) -> List:
        elements = []

        elements.append(Spacer(1, 5*mm))

        if os.path.exists(self.logo_path):
            try:
                logo = Image(self.logo_path, width=70*mm, height=70*mm, kind='proportional')
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 3*mm))
            except Exception as e:
                logger.warning(f"Logo error: {e}")
                elements.append(Spacer(1, 8*mm))
        else:
            elements.append(Spacer(1, 3*mm))

        elements.append(Paragraph(self.company_name, self.styles['CoverCompany']))

        elements.append(HRFlowable(
            width="50%",
            thickness=1,
            color=self.accent_gold,
            spaceBefore=5,
            spaceAfter=8,
            hAlign='CENTER'
        ))

        elements.append(Paragraph(self.tagline, self.styles['CoverTagline']))

        elements.append(HRFlowable(
            width="70%",
            thickness=0.5,
            color=self.primary_navy,
            spaceBefore=0,
            spaceAfter=15,
            hAlign='CENTER'
        ))

        elements.append(Paragraph("DONATION PERFORMANCE REPORT", self.styles['CoverTitle']))

        period_display = self._get_period_display(period_type, year)

        period_box_style = ParagraphStyle(
            name='PeriodBox',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=self.white,
            alignment=TA_CENTER,
            fontName='Times-Bold',
            leading=18,
            leftIndent=20,
            rightIndent=20
        )

        period_table = Table([[Paragraph(period_display, period_box_style)]], colWidths=[120*mm])
        period_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.primary_navy),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, self.accent_gold),
        ]))

        elements.append(period_table)
        elements.append(Spacer(1, 20*mm))

        period_str = self._format_period_string(period_type, start_date, end_date)

        info_data = [
            [Paragraph("<b>Report Period:</b>", self.styles['InfoLabel']),
             Paragraph(period_str, self.styles['InfoValue'])],
            [Paragraph("<b>Report Date:</b>", self.styles['InfoLabel']),
             Paragraph(datetime.now().strftime('%d %B %Y'), self.styles['InfoValue'])],
            [Paragraph("<b>Prepared For:</b>", self.styles['InfoLabel']),
             Paragraph("Board of Trustees & Management Team", self.styles['InfoValue'])]
        ]

        info_table = Table(info_data, colWidths=[55*mm, 95*mm])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (0, -1), 10),
            ('RIGHTPADDING', (0, 0), (0, -1), 15),
            ('LEFTPADDING', (1, 0), (1, -1), 15),
            ('RIGHTPADDING', (1, 0), (1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1.5, self.accent_gold),
            ('BACKGROUND', (0, 0), (-1, -1), self.light_silver),
        ]))

        elements.append(info_table)

        elements.append(Spacer(1, 15*mm))
        elements.append(HRFlowable(
            width="85%",
            thickness=2,
            color=self.accent_gold,
            spaceBefore=0,
            spaceAfter=0,
            hAlign='CENTER'
        ))

        return elements

    # ==================== CONTENT SECTIONS (unchanged) ====================
    def _create_executive_summary(self, summary: Dict, status_summary: Dict) -> List:
        elements = []
        elements.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))

        total_amount = self._safe_float(summary.get('total_amount', 0))
        total_transactions = self._safe_int(summary.get('total_transactions', 0))
        unique_donors = self._safe_int(summary.get('unique_donors', 0))
        successful = self._safe_int(status_summary.get('success_count', 0))

        success_rate = (successful / total_transactions * 100) if total_transactions > 0 else 0

        summary_text = f"""
        During the reporting period, {self.company_name} successfully collected 
        <b>{self._format_currency(total_amount)}</b> through <b>{self._format_number(successful)}</b> successful transactions 
        out of <b>{self._format_number(total_transactions)}</b> total attempts, representing a success rate of 
        <b>{self._format_percentage(success_rate)}</b>. These contributions came from <b>{self._format_number(unique_donors)}</b> unique donors, 
        demonstrating strong community support for educational initiatives.
        """

        elements.append(Paragraph(summary_text, self.styles['SummaryText']))
        return elements

    def _create_tight_metrics_table(self, summary: Dict) -> List:
        elements = []
        elements.append(Paragraph("KEY PERFORMANCE METRICS", self.styles['SectionHeader']))

        total_amount = self._safe_float(summary.get('total_amount', 0))
        total_transactions = self._safe_int(summary.get('total_transactions', 0))
        unique_donors = self._safe_int(summary.get('unique_donors', 0))
        avg_donation = self._safe_float(summary.get('avg_donation', 0))
        max_donation = self._safe_float(summary.get('max_donation', 0))
        successful = self._safe_int(summary.get('successful_transactions', 0))
        failed = self._safe_int(summary.get('failed_transactions', 0))

        success_pct = (successful / max(total_transactions, 1) * 100)
        failed_pct = (failed / max(total_transactions, 1) * 100)

        metrics_data = [
            [Paragraph("<b>Metric</b>", self.styles['TableHeader']),
             Paragraph("<b>Value</b>", self.styles['TableHeader'])],

            ["Total Donations Received", self._format_currency(total_amount)],
            ["Total Number of Transactions", self._format_number(total_transactions)],
            ["Successful Transactions", f"{self._format_number(successful)} ({self._format_percentage(success_pct)})"],
            ["Failed Transactions", f"{self._format_number(failed)} ({self._format_percentage(failed_pct)})"],
            ["Unique Donors", self._format_number(unique_donors)],
            ["Average Donation Amount", self._format_currency(avg_donation)],
            ["Largest Single Donation", self._format_currency(max_donation)],
        ]

        metrics_table = Table(metrics_data, colWidths=[95*mm, 70*mm])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.white, self.light_silver]),
            ('GRID', (0, 0), (-1, -1), 0.5, self.border_gray),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, self.white),
        ]))

        elements.append(metrics_table)
        return elements

    def _create_tight_donors_table(self, donors: List[Dict]) -> List:
        elements = []
        elements.append(Paragraph("TOP 10 DONORS", self.styles['SectionHeader']))

        if not donors:
            elements.append(Paragraph("No donor data available.", self.styles['BodyTextClean']))
            return elements

        table_data = [[
            Paragraph("<b>#</b>", self.styles['TableHeader']),
            Paragraph("<b>Donor Name</b>", self.styles['TableHeader']),
            Paragraph("<b>Total Donated</b>", self.styles['TableHeader']),
            Paragraph("<b>Count</b>", self.styles['TableHeader']),
            Paragraph("<b>Average</b>", self.styles['TableHeader']),
            Paragraph("<b>Type</b>", self.styles['TableHeader'])
        ]]

        for i, donor in enumerate(donors, 1):
            donor_name = str(donor.get('donor_name', 'Anonymous'))[:35]
            total = self._format_currency(donor.get('total_donated', 0))
            count = self._format_number(donor.get('number_of_donations', 0))
            avg = self._format_currency(donor.get('average_donation', 0))
            dtype = str(donor.get('donor_type', 'One-time'))

            table_data.append([
                str(i),
                donor_name,
                total,
                count,
                avg,
                dtype
            ])

        donor_table = Table(table_data, colWidths=[8*mm, 52*mm, 32*mm, 18*mm, 28*mm, 22*mm])
        donor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (4, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.white, self.light_silver]),
            ('GRID', (0, 0), (-1, -1), 0.5, self.border_gray),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, self.white),
        ]))

        elements.append(donor_table)
        return elements

    def _create_tight_schools_table(self, schools: List[Dict]) -> List:
        elements = []
        elements.append(Paragraph("TOP SCHOOLS BY DONATIONS", self.styles['SectionHeader']))

        if not schools:
            elements.append(Paragraph("No school data available.", self.styles['BodyTextClean']))
            return elements

        table_data = [[
            Paragraph("<b>#</b>", self.styles['TableHeader']),
            Paragraph("<b>School Name</b>", self.styles['TableHeader']),
            Paragraph("<b>Location</b>", self.styles['TableHeader']),
            Paragraph("<b>Total Donations</b>", self.styles['TableHeader']),
            Paragraph("<b>Donors</b>", self.styles['TableHeader'])
        ]]

        for i, school in enumerate(schools, 1):
            school_name = str(school.get('school_name', 'N/A'))[:32]
            location = str(school.get('school_location', 'N/A'))[:18]
            total = self._format_currency(school.get('total_amount', 0))
            donors = self._format_number(school.get('unique_donors', 0))

            table_data.append([
                str(i),
                school_name,
                location,
                total,
                donors
            ])

        school_table = Table(table_data, colWidths=[8*mm, 58*mm, 36*mm, 38*mm, 20*mm])
        school_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (3, 0), (4, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.white, self.light_silver]),
            ('GRID', (0, 0), (-1, -1), 0.5, self.border_gray),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, self.white),
        ]))

        elements.append(school_table)
        return elements

    def _create_tight_campaigns_table(self, campaigns: List[Dict]) -> List:
        elements = []
        elements.append(Paragraph("TOP CAMPAIGNS PERFORMANCE", self.styles['SectionHeader']))

        if not campaigns:
            elements.append(Paragraph("No campaign data available.", self.styles['BodyTextClean']))
            return elements

        table_data = [[
            Paragraph("<b>#</b>", self.styles['TableHeader']),
            Paragraph("<b>Campaign Name</b>", self.styles['TableHeader']),
            Paragraph("<b>Type</b>", self.styles['TableHeader']),
            Paragraph("<b>Total Raised</b>", self.styles['TableHeader']),
            Paragraph("<b>Donors</b>", self.styles['TableHeader'])
        ]]

        for i, campaign in enumerate(campaigns, 1):
            campaign_name = str(campaign.get('campaign_name', 'N/A'))[:35]
            ctype = str(campaign.get('donation_type', 'N/A'))[:15]
            total = self._format_currency(campaign.get('total_amount', 0))
            donors = self._format_number(campaign.get('unique_donors', 0))

            table_data.append([
                str(i),
                campaign_name,
                ctype,
                total,
                donors
            ])

        campaign_table = Table(table_data, colWidths=[8*mm, 64*mm, 28*mm, 38*mm, 22*mm])
        campaign_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (3, 0), (4, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.white, self.light_silver]),
            ('GRID', (0, 0), (-1, -1), 0.5, self.border_gray),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, self.white),
        ]))

        elements.append(campaign_table)
        return elements

    def _create_monthly_breakdown_table(self, monthly_data: List[Dict]) -> List:
        elements = []
        elements.append(Paragraph("MONTHLY DONATION BREAKDOWN", self.styles['SectionHeader']))

        if not monthly_data:
            elements.append(Paragraph("No monthly data available.", self.styles['BodyTextClean']))
            return elements

        table_data = [[
            Paragraph("<b>Month</b>", self.styles['TableHeader']),
            Paragraph("<b>Total Donations</b>", self.styles['TableHeader']),
            Paragraph("<b>Transactions</b>", self.styles['TableHeader']),
            Paragraph("<b>Donors</b>", self.styles['TableHeader']),
            Paragraph("<b>Change</b>", self.styles['TableHeader'])
        ]]

        previous_amount = None
        for month in monthly_data:
            month_name = str(month.get('month_name', 'N/A')).strip()
            total = self._safe_float(month.get('total_amount', 0))
            transactions = self._format_number(month.get('transaction_count', 0))
            donors = self._format_number(month.get('unique_donors', 0))

            if previous_amount is not None and previous_amount > 0:
                change = ((total - previous_amount) / previous_amount) * 100
                if change > 0:
                    change_text = f"+{change:.1f}%"
                    change_color = colors.HexColor('#2E7D32')
                elif change < 0:
                    change_text = f"{change:.1f}%"
                    change_color = colors.HexColor('#C62828')
                else:
                    change_text = "0.0%"
                    change_color = self.text_charcoal
            else:
                change_text = "—"
                change_color = self.text_charcoal

            table_data.append([
                month_name,
                self._format_currency(total),
                transactions,
                donors,
                change_text
            ])

            previous_amount = total

        monthly_table = Table(table_data, colWidths=[30*mm, 45*mm, 30*mm, 25*mm, 30*mm])
        monthly_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.white, self.light_silver]),
            ('GRID', (0, 0), (-1, -1), 0.5, self.border_gray),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, self.white),
        ]))

        elements.append(monthly_table)

        total_donations = sum(self._safe_float(m.get('total_amount', 0)) for m in monthly_data)
        avg_monthly = total_donations / len(monthly_data) if monthly_data else 0

        summary_note = f"""
        <b>Monthly Summary:</b> Over the {len(monthly_data)} months shown, the average monthly donation total was 
        {self._format_currency(avg_monthly)}. The month-over-month percentage changes indicate donation trends throughout the year.
        """

        elements.append(Spacer(1, 5*mm))
        elements.append(Paragraph(summary_note, self.styles['BodyTextClean']))

        return elements

    def _create_comprehensive_analysis(self, summary: Dict, donors: List[Dict],
                                       schools: List[Dict], campaigns: List[Dict],
                                       status_summary: Dict) -> List:
        elements = []
        elements.append(Paragraph("COMPREHENSIVE ANALYSIS", self.styles['SectionHeader']))

        total_amount = self._safe_float(summary.get('total_amount', 0))
        total_trans = self._safe_int(summary.get('total_transactions', 0))
        successful = self._safe_int(status_summary.get('success_count', 0))
        failed = self._safe_int(status_summary.get('failed_count', 0))

        trans_text = f"""
        <b>Transaction Performance:</b> Out of {self._format_number(total_trans)} total transaction attempts, 
        {self._format_number(successful)} were successful ({self._format_percentage(successful/max(total_trans,1)*100)}) while 
        {self._format_number(failed)} failed ({self._format_percentage(failed/max(total_trans,1)*100)}). The successful transactions 
        generated a total revenue of {self._format_currency(total_amount)}, demonstrating robust payment processing and donor commitment.
        """
        elements.append(Paragraph(trans_text, self.styles['BodyTextClean']))

        if donors:
            top_donor = donors[0]
            recurring_donors = sum(1 for d in donors if d.get('donor_type') == 'Recurring')

            donor_text = f"""
            <b>Donor Performance:</b> The top donor, <b>{top_donor.get('donor_name', 'Anonymous')}</b>, contributed 
            {self._format_currency(top_donor.get('total_donated', 0))} through 
            {self._format_number(top_donor.get('number_of_donations', 0))} transaction(s). Among the top 10 donors, 
            {recurring_donors} are recurring contributors, indicating strong donor loyalty and sustained support.
            """
            elements.append(Paragraph(donor_text, self.styles['BodyTextClean']))

        if schools:
            top_school = schools[0]
            total_school_amount = sum(self._safe_float(s.get('total_amount', 0)) for s in schools)

            school_text = f"""
            <b>Institutional Impact:</b> <b>{top_school.get('school_name', 'N/A')}</b> in {top_school.get('school_location', 'N/A')} 
            received the highest support with {self._format_currency(top_school.get('total_amount', 0))} from 
            {self._format_number(top_school.get('unique_donors', 0))} donors. The top {len(schools)} schools collectively received 
            {self._format_currency(total_school_amount)}, representing {self._format_percentage(total_school_amount/max(total_amount,1)*100)} 
            of total donations.
            """
            elements.append(Paragraph(school_text, self.styles['BodyTextClean']))

        if campaigns:
            top_campaign = campaigns[0]
            total_campaign_amount = sum(self._safe_float(c.get('total_amount', 0)) for c in campaigns)

            campaign_text = f"""
            <b>Campaign Effectiveness:</b> The <b>{top_campaign.get('campaign_name', 'N/A')}</b> campaign emerged as the most successful, 
            raising {self._format_currency(top_campaign.get('total_amount', 0))} from {self._format_number(top_campaign.get('unique_donors', 0))} donors. 
            The top {len(campaigns)} campaigns collectively raised {self._format_currency(total_campaign_amount)}, demonstrating effective 
            fundraising strategies and strong donor engagement.
            """
            elements.append(Paragraph(campaign_text, self.styles['BodyTextClean']))

        return elements

    def _create_header_footer(self, canvas_obj, doc):
        """Create professional header and footer"""
        canvas_obj.saveState()

        header_y = A4[1] - 15*mm
        line_y = A4[1] - 18*mm

        canvas_obj.setFont("Times-Roman", 9)
        canvas_obj.setFillColor(self.text_charcoal)
        canvas_obj.drawString(20*mm, header_y, self.company_name)
        canvas_obj.drawRightString(A4[0] - 20*mm, header_y, f"Page {doc.page}")

        canvas_obj.setStrokeColor(self.border_gray)
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(20*mm, line_y, A4[0] - 20*mm, line_y)

        footer_y = 15*mm
        canvas_obj.line(20*mm, footer_y + 4*mm, A4[0] - 20*mm, footer_y + 4*mm)

        canvas_obj.setFont("Times-Roman", 8)
        canvas_obj.setFillColor(self.text_charcoal)
        canvas_obj.drawString(20*mm, footer_y, f"Generated: {datetime.now().strftime('%d %B %Y')}")
        canvas_obj.drawCentredString(A4[0]/2, footer_y, "Donation Performance Report")

        canvas_obj.restoreState()

    def _format_period_string(self, period_type: str, start_date: datetime, end_date: datetime) -> str:
        if period_type == 'weekly':
            return f"{start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}"
        elif period_type == 'monthly':
            return f"{start_date.strftime('%B %Y')}"
        else:
            return f"Calendar Year {start_date.year}"

    def _get_period_display(self, period_type: str, year: int) -> str:
        if period_type == 'weekly':
            return "Weekly Performance Analysis"
        elif period_type == 'monthly':
            return "Monthly Performance Analysis"
        else:
            return f"{year} Annual Performance Analysis"

    # ==================== MAIN GENERATION ====================
    def generate_report(self, period_type: str, year: int = None,
                        force_regenerate: bool = False) -> str:
        """Generate ultra professional donation report with Redis cache validation"""
        try:
            logger.info(f"Generating ultra professional report: {period_type} {year or ''}")

            # Get date range
            start_date, end_date, start_date_str, end_date_str = self.get_date_range(period_type, year)

            # Generate data fingerprint to check freshness
            data_fingerprint = self._generate_data_fingerprint(start_date_str, end_date_str)

            # Check cache if not forced to regenerate
            report_id = self._generate_report_id(period_type, year, start_date_str, end_date_str)

            if not force_regenerate:
                cached_path = self._get_cached_report(report_id, data_fingerprint)
                if cached_path:
                    logger.info(f"Returning cached report: {cached_path}")
                    return cached_path

            # Fetch all data
            logger.info("Fetching data...")
            summary = self.get_donations_summary(start_date_str, end_date_str)
            donors = self.get_top_donors(start_date_str, end_date_str, 10)
            schools = self.get_top_schools(start_date_str, end_date_str, 10)
            campaigns = self.get_top_campaigns(start_date_str, end_date_str, 10)
            status_summary = self.get_transaction_status_summary(start_date_str, end_date_str)

            # For yearly reports, get monthly breakdown
            monthly_data = None
            if period_type == 'yearly':
                report_year = year or (datetime.now().year - 1)
                monthly_data = self.get_monthly_breakdown(report_year)
                logger.info(f"Fetched monthly breakdown for {report_year}")

            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"donation_report_{period_type}_{year or 'current'}_{timestamp}.pdf"
            output_path = self.reports_dir / filename

            # Build PDF
            logger.info(f"Building ultra professional PDF: {output_path}")
            self._build_ultra_professional_pdf(
                output_path=str(output_path),
                period_type=period_type,
                year=year,
                start_date=start_date,
                end_date=end_date,
                summary=summary,
                donors=donors,
                schools=schools,
                campaigns=campaigns,
                status_summary=status_summary,
                monthly_data=monthly_data
            )

            # Update Redis cache
            self._update_cache(
                report_id, period_type, year,
                start_date_str, end_date_str,
                str(output_path), data_fingerprint
            )

            # (Optional) Upload to S3 - commented for future use
            # self._upload_to_s3(str(output_path))

            logger.info(f"Ultra professional report generated: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Report generation failed: {e}", exc_info=True)
            raise

    def _build_ultra_professional_pdf(self, output_path: str, period_type: str, year: int,
                                      start_date: datetime, end_date: datetime, summary: Dict,
                                      donors: List[Dict], schools: List[Dict], campaigns: List[Dict],
                                      status_summary: Dict, monthly_data: List[Dict] = None):
        """Build ultra professional PDF"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=25*mm,
            bottomMargin=22*mm,
            title=f"{self.company_name} - Donation Report",
            author=self.company_name
        )

        story = []

        # Stunning cover page
        story.extend(self._create_stunning_cover_page(period_type, start_date, end_date, year))
        story.append(PageBreak())

        # Content sections
        story.extend(self._create_executive_summary(summary, status_summary))
        story.extend(self._create_tight_metrics_table(summary))

        if period_type == 'yearly' and monthly_data:
            story.extend(self._create_monthly_breakdown_table(monthly_data))

        story.extend(self._create_tight_donors_table(donors))
        story.extend(self._create_tight_schools_table(schools))
        story.extend(self._create_tight_campaigns_table(campaigns))
        story.extend(self._create_comprehensive_analysis(summary, donors, schools, campaigns, status_summary))

        doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)

    # ==================== UTILITIES ====================
    def list_reports(self) -> List[Dict]:
        """List all generated reports from filesystem"""
        reports = []
        for file in sorted(self.reports_dir.glob("*.pdf"), key=lambda x: x.stat().st_mtime, reverse=True):
            stats = file.stat()
            reports.append({
                'filename': file.name,
                'path': str(file),
                'size_mb': stats.st_size / (1024 * 1024),
                'created': datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            })
        return reports

    def cleanup_old_reports(self, days: int = 30) -> int:
        """Delete reports older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        deleted = 0
        for file in self.reports_dir.glob("*.pdf"):
            if datetime.fromtimestamp(file.stat().st_ctime) < cutoff:
                file.unlink()
                deleted += 1
        return deleted

# ==================== CLI ====================
def main():
    """Command-line interface"""
    print("=" * 80)
    print("VIDYAANIDHI EDUCATIONAL TRUST")
    print("Ultra Professional Donation Report Generator v10.0 (Redis Cache)")
    print("=" * 80)
    print()

    try:
        agent = FinalDonationReportAgent()
        print("Final donation report agent initialized with Redis\n")
    except Exception as e:
        print(f"Failed: {e}")
        return

    while True:
        print("-" * 80)
        print("DONATION REPORT MENU")
        print("-" * 80)
        print("1. Generate Weekly Report")
        print("2. Generate Monthly Report")
        print("3. Generate Yearly Report (current)")
        print("4. Generate Yearly Report (custom year)")
        print("5. List Reports")
        print("6. Cleanup Old Reports")
        print("7. Exit")
        print()

        choice = input("Select (1-7): ").strip()

        try:
            if choice == '1':
                print("\nGenerating weekly report...")
                path = agent.generate_report('weekly')
                print(f"Report: {path}\n")

            elif choice == '2':
                print("\nGenerating monthly report...")
                path = agent.generate_report('monthly')
                print(f"Report: {path}\n")

            elif choice == '3':
                year = datetime.now().year
                print(f"\nGenerating {year} report...")
                path = agent.generate_report('yearly', year=year)
                print(f"Report: {path}\n")

            elif choice == '4':
                year_input = input("Enter year: ").strip()
                try:
                    year = int(year_input)
                    print(f"\nGenerating {year} report...")
                    path = agent.generate_report('yearly', year=year)
                    print(f"Report: {path}\n")
                except ValueError:
                    print("Invalid year\n")

            elif choice == '5':
                reports = agent.list_reports()
                print(f"\nReports ({len(reports)}):")
                print("-" * 80)
                for i, r in enumerate(reports, 1):
                    print(f"{i}. {r['filename']}")
                    print(f"   {r['size_mb']:.2f} MB | {r['created']}\n")

            elif choice == '6':
                confirm = input("Delete 30+ day old reports? (y/N): ").strip().lower()
                if confirm == 'y':
                    deleted = agent.cleanup_old_reports(30)
                    print(f"Deleted {deleted} reports\n")

            elif choice == '7':
                print("\nThank you!\n")
                break

            else:
                print("Invalid\n")

        except Exception as e:
            print(f"\nError: {e}\n")

        input("Press Enter...")
        print()

if __name__ == "__main__":
    main()