"""
VISTARA Analytics - Ultra Professional Donation Report Generator
=================================================================

Times New Roman Font (Professional Typography)
Fully Justified Text
Tight, Clean Tables
Stunning Business-Grade Cover Page
Professional Layout & Spacing

NEW FEATURES:
- Smart data validation BEFORE using cache
- Automatic 7-day cleanup for weekly/monthly reports
- Permanent storage for yearly reports
- Redis cache with TTL-based expiration
- AWS S3 storage with lifecycle (ENABLED)
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
import pickle
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
    version: str = "11.0.0"

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
            year=data.get('year'),
            start_date=data['start_date'],
            end_date=data['end_date'],
            generated_at=data['generated_at'],
            file_path=data['file_path'],
            data_fingerprint=data['data_fingerprint'],
            version=data.get('version', '11.0.0')
        )

# ==================== ULTRA PROFESSIONAL DONATION REPORT AGENT ====================
class FinalDonationReportAgent:
    VERSION = "11.0.0"

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
            logger.info("Redis cache enabled - Smart validation active")
        else:
            logger.warning("Redis cache disabled - No caching available")

        # S3 Storage (NOW ENABLED)
        self.use_s3 = os.getenv("USE_S3", "false").lower() == "true"
        self.s3_bucket = os.getenv("S3_BUCKET_NAME")
        self.s3_client = None

        if self.use_s3 and self.s3_bucket:
            self.s3_client = self._get_s3_client()
            if self.s3_client:
                logger.info(f"S3 enabled: {self.s3_bucket}")
                logger.info("Lifecycle: Files auto-delete after 7 days")

        if not self.s3_client and self.use_s3:
            logger.warning("S3 requested but unavailable — using local storage")

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
        self.cache_dir   = Path("cache")
        self.reports_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        self.pickle_cache_file = self.cache_dir / "report_cache.pkl"

        # Professional Styles
        self.styles = getSampleStyleSheet()
        self._setup_professional_styles()

        logger.info(f"UltraProfessionalReportAgent v{self.VERSION} initialized")

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
        Generate comprehensive data fingerprint to detect ANY changes.

        IMPORTANT: Always scans up to NOW (not end_date) so that records
        added today for any date within the period are caught immediately.

        Checks:
        1. COUNT(*)          — number of records in period
        2. SUM(amount)       — total amount (catches edits)
        3. MAX(payment_date) — latest payment date
        4. COUNT(Success)    — catches status changes (pending→success)
        5. MAX(updated_at/created_at) — catches any row-level update
        """
        session = self.SessionLocal()
        try:
            # Always scan to NOW so today's inserts are visible
            scan_end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Use IDENTICAL counting logic as the report queries
            query = """
                SELECT
                    COUNT(DISTINCT payment_id)                                                          AS record_count,
                    COALESCE(SUM(CASE WHEN payment_status = 'Success' THEN amount ELSE 0 END), 0)       AS total_amount,
                    COALESCE(MAX(payment_date)::text, '')                                               AS max_payment_date,
                    COUNT(CASE WHEN payment_status = 'Success' THEN 1 END)                              AS success_count,
                    (SELECT COUNT(*) FROM (
                        SELECT DISTINCT donor_name, donor_email
                        FROM donations_raw d2
                        WHERE d2.payment_date >= :start_date
                          AND d2.payment_date <= :scan_end
                    ) sub) AS unique_donors
                FROM donations_raw
                WHERE payment_date >= :start_date
                  AND payment_date <= :scan_end
            """

            result = session.execute(
                text(query),
                {"start_date": start_date, "scan_end": scan_end}
            ).fetchone()

            record_count     = result[0] or 0
            total_amount     = result[1] or 0
            max_payment_date = result[2] or ""
            success_count    = result[3] or 0
            unique_donors    = result[4] or 0

            # Also check for a timestamp column to catch silent row updates
            ts_col_query = """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'donations_raw'
                  AND column_name IN ('updated_at','created_at','inserted_at','modified_at')
                ORDER BY CASE column_name
                    WHEN 'updated_at'  THEN 1
                    WHEN 'modified_at' THEN 2
                    WHEN 'created_at'  THEN 3
                    WHEN 'inserted_at' THEN 4
                END
                LIMIT 1
            """
            ts_result = session.execute(text(ts_col_query)).fetchone()
            max_timestamp = ""

            if ts_result:
                ts_col = ts_result[0]
                # Check the whole table for ANY recent modification
                # (catches status updates on old records too)
                max_timestamp = session.execute(
                    text(f"""
                        SELECT COALESCE(MAX({ts_col})::text, '')
                        FROM donations_raw
                        WHERE payment_date >= :start_date
                    """),
                    {"start_date": start_date}
                ).scalar() or ""

            raw_fingerprint = (
                f"{record_count}|{total_amount}|"
                f"{max_payment_date}|{success_count}|{unique_donors}|{max_timestamp}"
            )

            logger.info(
                f"DB scan: records={record_count}, "
                f"amount=Rs.{float(total_amount):,.2f}, "
                f"success={success_count}, "
                f"unique_donors={unique_donors}, "
                f"latest_payment={max_payment_date[:10] if max_payment_date else 'N/A'}, "
                f"last_modified={max_timestamp[:19] if max_timestamp else 'N/A'}, "
                f"fingerprint={hashlib.md5(raw_fingerprint.encode()).hexdigest()[:16]}"
            )

        except Exception as e:
            session.rollback()
            logger.error(f"Fingerprint generation failed: {e}", exc_info=True)
            raw_fingerprint = f"error|{datetime.now().timestamp()}"
        finally:
            session.close()

        return hashlib.md5(raw_fingerprint.encode()).hexdigest()[:16]

    def _get_cached_report(self, report_id: str, data_fingerprint: str,
                           period_type: str) -> Optional[str]:
        """
        Lookup cached report.
        Tries Redis first; falls back to local pickle cache if Redis is unavailable.

        Validation:
        1. Version must match
        2. Data fingerprint must match (detects ANY DB change)
        3. PDF file must exist on disk OR S3
        4. Weekly/Monthly: expire after 7 days
        5. Yearly: keep for 30 days (past years never change)
        """
        cache_key = f"report:{report_id}"

        # ── Try Redis first ──────────────────────────────────────────────────
        if self.redis_client:
            try:
                cache_data = self.redis_client.hgetall(cache_key)
            except Exception as e:
                logger.warning(f"Redis read error: {e} — falling back to pickle")
                cache_data = {}
        else:
            cache_data = {}

        # ── Fall back to pickle if Redis returned nothing ────────────────────
        using_pickle = False
        if not cache_data:
            cache_data = self._pickle_get(cache_key) or {}
            if cache_data:
                using_pickle = True
                logger.info("Using local pickle cache (Redis unavailable)")

        if not cache_data:
            logger.info("No cache found — will generate fresh report")
            return None

        # ── Validate version ─────────────────────────────────────────────────
        if cache_data.get("version") != self.VERSION:
            logger.info(f"Cache version mismatch, regenerating")
            self._evict_cache(cache_key, using_pickle)
            return None

        # ── Validate data fingerprint (core: detects any DB change) ─────────
        stored_fp = cache_data.get("data_fingerprint", "")
        if stored_fp != data_fingerprint:
            logger.info(
                f"Data changed — cached fingerprint={stored_fp} "
                f"current fingerprint={data_fingerprint} — regenerating"
            )
            self._evict_cache(cache_key, using_pickle)
            return None

        # ── Validate file still exists (disk or S3) ──────────────────────────
        file_path = cache_data.get("file_path", "")
        
        # Check if it's an S3 URL
        if file_path.startswith('http'):
            # S3 URL - just return it
            logger.info(f"Cache hit (S3) — returning URL")
            return file_path
        
        # Check if local file exists
        if not file_path or not Path(file_path).exists():
            logger.info("Cached PDF missing from disk, regenerating")
            self._evict_cache(cache_key, using_pickle)
            return None

        # ── Age check for weekly/monthly (7-day max) ─────────────────────────
        if period_type in ["weekly", "monthly"]:
            generated_at = datetime.fromisoformat(cache_data["generated_at"])
            age_days = (datetime.now() - generated_at).days
            if age_days >= 7:
                logger.info(f"Cache expired ({age_days} days old), deleting")
                self._evict_cache(cache_key, using_pickle, delete_file=True,
                                  file_path=file_path)
                return None

        logger.info(f"Cache hit — returning {'pickle' if using_pickle else 'Redis'} "
                    f"cached report: {file_path}")
        return file_path

    def _evict_cache(self, cache_key: str, from_pickle: bool,
                     delete_file: bool = False, file_path: str = ""):
        """Remove a cache entry from Redis and/or pickle, optionally delete PDF."""
        if self.redis_client:
            try:
                self.redis_client.delete(cache_key)
            except Exception:
                pass
        self._pickle_delete(cache_key)

        # Don't delete S3 files (lifecycle handles it)
        if delete_file and file_path and not file_path.startswith('http'):
            try:
                Path(file_path).unlink()
                logger.info(f"Deleted expired file: {file_path}")
            except Exception:
                pass

    def _update_cache(self, report_id: str, period_type: str, year: Optional[int],
                      start_date: str, end_date: str, file_path: str,
                      data_fingerprint: str):
        """
        Save report metadata to Redis (primary) and local pickle (fallback).
        TTL rules:
        - Weekly/Monthly: 7 days
        - Yearly: 30 days
        Both stores are always written so cache works even when Redis is down.
        """
        cache_key = f"report:{report_id}"

        if period_type in ["weekly", "monthly"]:
            ttl_seconds = 60 * 60 * 24 * 7
            ttl_label   = "7 days"
        else:
            ttl_seconds = 60 * 60 * 24 * 30
            ttl_label   = "30 days"

        mapping = {
            "report_id":        report_id,
            "period_type":      period_type,
            "year":             str(year) if year is not None else "",
            "start_date":       start_date,
            "end_date":         end_date,
            "generated_at":     datetime.now().isoformat(),
            "file_path":        file_path,  # Can be local path or S3 URL
            "data_fingerprint": data_fingerprint,
            "version":          self.VERSION,
        }

        # ── 1. Write to Redis ────────────────────────────────────────────────
        redis_ok = False
        if self.redis_client:
            try:
                self.redis_client.hset(cache_key, mapping=mapping)
                self.redis_client.expire(cache_key, ttl_seconds)

                # Verify
                saved_fp = self.redis_client.hget(cache_key, "data_fingerprint")
                if saved_fp == data_fingerprint:
                    logger.info(f"Redis cache saved  TTL={ttl_label}  fingerprint={data_fingerprint}")
                    redis_ok = True
                else:
                    logger.error("Redis save verification failed")

                self.redis_client.lpush("reports:recent", report_id)
                self.redis_client.ltrim("reports:recent", 0, 99)

            except Exception as e:
                logger.error(f"Redis cache write error: {e}", exc_info=True)

        # ── 2. Always write to local pickle (works offline / Redis down) ─────
        try:
            self._pickle_set(cache_key, mapping.copy(), ttl_seconds)
            logger.info(f"Pickle cache saved   TTL={ttl_label}")
        except Exception as e:
            logger.error(f"Pickle cache write error: {e}")

        if not redis_ok and not self.redis_client:
            logger.info("Redis unavailable — only pickle cache active")

    def _cleanup_old_files(self):
        """
        Automatic cleanup of old report files.
        
        Rules:
        - Weekly/Monthly reports older than 7 days: DELETE
        - Yearly reports: KEEP (past years are permanent)
        - S3 files are handled by lifecycle rules
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=7)
            deleted_count = 0
            
            for file in self.reports_dir.glob("*.pdf"):
                filename = file.name
                
                # Check if weekly or monthly report
                if 'weekly' in filename or 'monthly' in filename:
                    file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
                    
                    if file_mtime < cutoff_date:
                        file.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old {filename}")
            
            if deleted_count > 0:
                logger.info(f"Cleanup complete: {deleted_count} old reports deleted")
                
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    def _get_redis_connection(self) -> redis.Redis | None:
        """
        Establish Redis connection.
        Supports:
        - Upstash (rediss://... with TLS)
        - Local Redis (redis://localhost:6379)
        - Host/port config
        """
        try:
            redis_url = os.getenv("REDIS_URL", "").strip()

            if redis_url:
                logger.info(f"🔌 Connecting to Redis via URL...")

                # Upstash uses rediss:// (TLS). Enforce correct SSL params.
                is_tls = redis_url.startswith("rediss://")

                client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=10,
                    socket_timeout=10,
                    retry_on_timeout=True,
                    health_check_interval=30,
                    ssl_cert_reqs=None if is_tls else None,
                )
            else:
                logger.info("🔌 Connecting to local Redis")
                client = redis.Redis(
                    host=self.redis_host,
                    port=self.redis_port,
                    db=self.redis_db,
                    password=self.redis_password,
                    decode_responses=True,
                    socket_connect_timeout=10,
                    socket_timeout=10,
                    retry_on_timeout=True,
                )

            client.ping()
            logger.info("Redis connected successfully")
            return client

        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}")
            logger.info("Falling back to local pickle cache")
            return None
        except redis.TimeoutError as e:
            logger.error(f"Redis timeout — check REDIS_URL or network: {e}")
            logger.info("Falling back to local pickle cache")
            return None
        except Exception as e:
            logger.error(f"Redis error: {e}")
            logger.info("Falling back to local pickle cache")
            return None


    # ==================== PICKLE FALLBACK CACHE ====================
    def _pickle_load(self) -> dict:
        """Load local pickle cache"""
        try:
            if self.pickle_cache_file.exists():
                with open(self.pickle_cache_file, 'rb') as f:
                    return pickle.load(f)
        except Exception:
            pass
        return {}

    def _pickle_save(self, store: dict):
        """Save local pickle cache"""
        try:
            with open(self.pickle_cache_file, 'wb') as f:
                pickle.dump(store, f)
        except Exception as e:
            logger.error(f"Pickle save error: {e}")

    def _pickle_get(self, cache_key: str) -> Optional[dict]:
        """Get entry from pickle cache — returns None if expired"""
        store = self._pickle_load()
        entry = store.get(cache_key)
        if entry is None:
            return None
        # Check expiry
        expires_at_str = entry.get("_expires_at", "")
        if expires_at_str:
            try:
                if datetime.now() > datetime.fromisoformat(expires_at_str):
                    logger.info(f"🗑️  Pickle cache expired for key={cache_key}")
                    self._pickle_delete(cache_key)
                    return None
            except Exception:
                pass
        return entry

    def _pickle_set(self, cache_key: str, mapping: dict, ttl_seconds: int):
        """Set entry in pickle cache with expiry timestamp"""
        store = self._pickle_load()
        mapping["_expires_at"] = (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat()
        store[cache_key] = mapping
        self._pickle_save(store)

    def _pickle_delete(self, cache_key: str):
        """Delete entry from pickle cache"""
        store = self._pickle_load()
        if cache_key in store:
            del store[cache_key]
            self._pickle_save(store)
            
    # ==================== S3 STORAGE ====================
    def _get_s3_client(self):
        """Initialize S3 client using AWS default credential chain (IAM Role / env / config)"""
        try:
            import boto3

            # IMPORTANT: Do NOT pass access keys explicitly
            s3 = boto3.client(
                "s3",
                region_name=os.getenv("AWS_REGION", "ap-southeast-2")
            )

            # Test connection
            s3.head_bucket(Bucket=self.s3_bucket)
            logger.info(f"S3 connection verified: {self.s3_bucket}")
            return s3

        except ImportError:
            logger.error("boto3 not installed — run: pip install boto3")
            return None
        except Exception as e:
            logger.error(f"S3 connection failed: {e}")
            return None

    def _upload_to_s3(self, local_path: str) -> Optional[str]:
        """Upload generated PDF to S3 and return presigned URL"""
        if not self.s3_client:
            logger.warning("S3 client not initialized")
            return None

        try:
            filename = Path(local_path).name
            s3_key = f"reports/{filename}"

            # Upload file
            self.s3_client.upload_file(
                local_path,
                self.s3_bucket,
                s3_key,
                ExtraArgs={
                    "ContentType": "application/pdf",
                    "ServerSideEncryption": "AES256"
                }
            )

            # Generate presigned URL (7 days)
            s3_url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.s3_bucket,
                    "Key": s3_key
                },
                ExpiresIn=604800  # 7 days
            )

            logger.info(f"Uploaded to S3: {s3_key}")
            return s3_url

        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            return None
            
    # ==================== UTILITY FUNCTIONS ====================
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

    # ==================== STYLES ====================
    def _setup_professional_styles(self):
        """Setup ultra professional styles with Times New Roman"""
        styles = self.styles

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

        styles.add(ParagraphStyle(
            name='TableHeader',
            parent=styles['Normal'],
            fontSize=9,
            textColor=self.white,
            fontName='Times-Bold',
            alignment=TA_LEFT,
            leading=11
        ))

        styles.add(ParagraphStyle(
            name='TableCell',
            parent=styles['Normal'],
            fontSize=9,
            textColor=self.text_charcoal,
            fontName='Times-Roman',
            alignment=TA_LEFT,
            leading=11
        ))

        styles.add(ParagraphStyle(
            name='TableCellRight',
            parent=styles['Normal'],
            fontSize=9,
            textColor=self.text_charcoal,
            fontName='Times-Roman',
            alignment=TA_RIGHT,
            leading=11
        ))

        styles.add(ParagraphStyle(
            name='TableCellBold',
            parent=styles['Normal'],
            fontSize=9,
            textColor=self.text_charcoal,
            fontName='Times-Bold',
            alignment=TA_LEFT,
            leading=11
        ))

        styles.add(ParagraphStyle(
            name='InfoLabel',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.dark_charcoal,
            fontName='Times-Bold',
            alignment=TA_RIGHT,
            leading=14
        ))

        styles.add(ParagraphStyle(
            name='InfoValue',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.text_charcoal,
            fontName='Times-Roman',
            alignment=TA_LEFT,
            leading=14
        ))

    # ==================== DATABASE QUERIES ====================
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

    def get_date_range(self, period_type: str, year: int = None) -> Tuple[datetime, datetime, str, str, str]:
        """
        Calculate date range for the report period.

        Weekly  : last complete Mon–Sun week
        Monthly : last complete calendar month
        Yearly  : Jan 1 – Dec 31 for past years
                  Jan 1 – RIGHT NOW for current year (includes today's data)
        """
        current_date = datetime.now()

        if period_type == 'weekly':
            end_date = current_date - timedelta(days=current_date.weekday() + 1)
            start_date = end_date - timedelta(days=6)

        elif period_type == 'monthly':
            first_day_current = current_date.replace(day=1)
            end_date   = first_day_current - timedelta(days=1)
            start_date = end_date.replace(day=1)

        elif period_type == 'yearly':
            year = year or (current_date.year - 1)
            start_date = datetime(year, 1, 1)
            if year == current_date.year:
                # Current year: include everything up to this exact moment
                end_date = current_date
            else:
                # Past year: full calendar year
                end_date = datetime(year, 12, 31, 23, 59, 59)

        else:
            raise ValueError(f"Invalid period_type: {period_type}")

        start_date_str = start_date.strftime('%Y-%m-%d 00:00:00')

        # Query end: full timestamp so today's records are included
        end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')

        # Cache key end: date only so report_id is STABLE all day
        # (prevents a new cache key every second for current-year reports)
        end_date_key = end_date.strftime('%Y-%m-%d')

        return start_date, end_date, start_date_str, end_date_str, end_date_key

    def get_donations_summary(self, start_date: str, end_date: str) -> Dict:
        query = """
        SELECT 
            COUNT(DISTINCT payment_id) as total_transactions,
            (SELECT COUNT(*) FROM (
                SELECT DISTINCT donor_name, donor_email
                FROM donations_raw d2
                WHERE d2.payment_date BETWEEN :start_date AND :end_date
            ) sub) as unique_donors,
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
            COUNT(DISTINCT (donor_name, donor_email)) as unique_donors
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
            CASE 
                WHEN COUNT(DISTINCT payment_id) > COUNT(DISTINCT (donor_name, donor_email))
                THEN 'Recurring'
                ELSE 'One-time'
            END as donation_type,
            COUNT(DISTINCT payment_id) as donation_count,
            COALESCE(SUM(amount), 0) as total_amount,
            COUNT(DISTINCT (donor_name, donor_email)) as unique_donors
        FROM donations_raw
        WHERE payment_date BETWEEN :start_date AND :end_date 
            AND payment_status = 'Success'
            AND campaign_name IS NOT NULL
            AND campaign_name != ''
        GROUP BY campaign_name
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
            COUNT(DISTINCT (donor_name, donor_email)) as unique_donors
        FROM donations_raw
        WHERE EXTRACT(YEAR FROM payment_date) = :year
            AND payment_status = 'Success'
        GROUP BY EXTRACT(MONTH FROM payment_date), TO_CHAR(payment_date, 'Month')
        ORDER BY month_number
        """
        return self.execute_query(query, {'year': year})

    # ==================== COVER PAGE ====================
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

    # ==================== CONTENT SECTIONS ====================
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
            Paragraph("<b>Transactions</b>", self.styles['TableHeader']),
            Paragraph("<b>Avg per Transaction</b>", self.styles['TableHeader']),
            Paragraph("<b>Donor Type</b>", self.styles['TableHeader'])
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
            Paragraph("<b>Total Raised</b>", self.styles['TableHeader']),
            Paragraph("<b>Unique Donors</b>", self.styles['TableHeader'])
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
            Paragraph("<b>Donation Type</b>", self.styles['TableHeader']),
            Paragraph("<b>Total Raised</b>", self.styles['TableHeader']),
            Paragraph("<b>Unique Donors</b>", self.styles['TableHeader'])
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
                elif change < 0:
                    change_text = f"{change:.1f}%"
                else:
                    change_text = "0.0%"
            else:
                change_text = "—"

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
        """
        Generate ultra professional donation report with smart caching.

        Process:
        1. Resolve year once — used consistently for date range, report_id, filename, cache
        2. Auto-cleanup old weekly/monthly files (> 7 days)
        3. Generate data fingerprint by querying DB (ALWAYS runs, even on cache hit)
        4. Lookup Redis cache — valid only if fingerprint matches AND file exists
        5. Cache hit → return cached path instantly
        6. Cache miss / data changed → generate fresh PDF and save to Redis
        7. If S3 enabled: upload to S3 and cache S3 URL
        """
        try:
            # ── Step 1: Resolve year ONCE ──────────────────────────────────────
            # This prevents report_id / filename / date-range from diverging
            if period_type == 'yearly':
                resolved_year = year if year is not None else datetime.now().year
            else:
                resolved_year = None   # not relevant for weekly/monthly

            logger.info(
                f"📊 Generating {period_type} report"
                f"{f' (year={resolved_year})' if resolved_year else ''}"
            )

            # ── Step 2: Auto-cleanup ───────────────────────────────────────────
            self._cleanup_old_files()

            # ── Step 3: Date range ─────────────────────────────────────────────
            start_date, end_date, start_date_str, end_date_str, end_date_key = \
                self.get_date_range(period_type, resolved_year)

            # ── Step 4: Fingerprint — ALWAYS queries the database ──────────────
            logger.info("Querying database to check for new/changed data...")
            data_fingerprint = self._generate_data_fingerprint(start_date_str, end_date_str)

            # ── Step 5: Cache lookup ───────────────────────────────────────────
            # Use end_date_KEY (date only) for report_id so the cache key is
            # stable throughout the day, not changing every second
            report_id = self._generate_report_id(
                period_type, resolved_year, start_date_str, end_date_key
            )

            if not force_regenerate:
                cached_path = self._get_cached_report(
                    report_id, data_fingerprint, period_type
                )
                if cached_path:
                    return cached_path

            # ── Step 6: Generate fresh report ─────────────────────────────────
            logger.info("Generating fresh report (data changed or no cache)...")
            summary        = self.get_donations_summary(start_date_str, end_date_str)
            donors         = self.get_top_donors(start_date_str, end_date_str, 10)
            schools        = self.get_top_schools(start_date_str, end_date_str, 10)
            campaigns      = self.get_top_campaigns(start_date_str, end_date_str, 10)
            status_summary = self.get_transaction_status_summary(start_date_str, end_date_str)

            monthly_data = None
            if period_type == 'yearly':
                monthly_data = self.get_monthly_breakdown(resolved_year)

            timestamp   = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename    = (
                f"donation_report_{period_type}"
                f"_{resolved_year if resolved_year else 'current'}"
                f"_{timestamp}.pdf"
            )
            output_path = self.reports_dir / filename

            logger.info(f"Building PDF: {output_path}")
            self._build_ultra_professional_pdf(
                output_path    = str(output_path),
                period_type    = period_type,
                year           = resolved_year,
                start_date     = start_date,
                end_date       = end_date,
                summary        = summary,
                donors         = donors,
                schools        = schools,
                campaigns      = campaigns,
                status_summary = status_summary,
                monthly_data   = monthly_data,
            )

            # ── Step 7: Upload to S3 (if enabled) ──────────────────────────────
            final_path = str(output_path)
            if self.s3_client:
                s3_url = self._upload_to_s3(str(output_path))
                if s3_url:
                    # Use S3 URL in cache instead of local path
                    final_path = s3_url
                    logger.info(f"S3 URL available: {s3_url[:80]}...")

            # ── Step 8: Save to Redis ──────────────────────────────────────────
            self._update_cache(
                report_id, period_type, resolved_year,
                start_date_str, end_date_key,
                final_path,  # S3 URL or local path
                data_fingerprint
            )

            logger.info(f"Report ready: {final_path}")
            return final_path

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
        story.extend(self._create_stunning_cover_page(period_type, start_date, end_date, year))
        story.append(PageBreak())

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
        """List all generated reports"""
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
        """Manual cleanup with custom days threshold"""
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
    print("Ultra Professional Donation Report Generator v11.0")
    print("Smart Caching + Auto-Cleanup + S3 Storage Enabled")
    print("=" * 80)
    print()

    try:
        agent = FinalDonationReportAgent()
        print("Agent initialized successfully\n")
    except Exception as e:
        print(f"Initialization failed: {e}")
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
        print("6. Cleanup Old Reports (30+ days)")
        print("7. Force Regenerate (Bypass Cache)")
        print("8. Exit")
        print()

        choice = input("Select (1-8): ").strip()

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
                confirm = input("Delete reports older than 30 days? (y/N): ").strip().lower()
                if confirm == 'y':
                    deleted = agent.cleanup_old_reports(30)
                    print(f" Deleted {deleted} reports\n")

            elif choice == '7':
                print("\nForce Regenerate (bypassing cache):")
                print("1. Weekly Report")
                print("2. Monthly Report")
                print("3. Yearly Report (current)")
                print("4. Yearly Report (custom year)")
                
                sub = input("Select: ").strip()
                
                if sub == '1':
                    path = agent.generate_report('weekly', force_regenerate=True)
                    print(f"Fresh weekly report: {path}\n")
                elif sub == '2':
                    path = agent.generate_report('monthly', force_regenerate=True)
                    print(f"Fresh monthly report: {path}\n")
                elif sub == '3':
                    year = datetime.now().year
                    path = agent.generate_report('yearly', year=year, force_regenerate=True)
                    print(f"Fresh {year} report: {path}\n")
                elif sub == '4':
                    year = int(input("Year: ").strip())
                    path = agent.generate_report('yearly', year=year, force_regenerate=True)
                    print(f"Fresh {year} report: {path}\n")

            elif choice == '8':
                print("\nThank you!\n")
                break

            else:
                print("Invalid choice\n")

        except Exception as e:
            print(f"\n Error: {e}\n")

        input("Press Enter to continue...")
        print()

if __name__ == "__main__":
    main()