"""
Quick Test Script - Verify Your Setup
======================================
Run this to check if everything is configured correctly
"""

import sys
import os
from pathlib import Path

print("=" * 80)
print("SETUP VERIFICATION TEST")
print("=" * 80)
print()

# Test 1: Python Version
print("1. Checking Python version...")
version = sys.version_info
if version.major == 3 and version.minor >= 9:
    print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
else:
    print(f"   ❌ Python {version.major}.{version.minor} (need 3.9+)")
    sys.exit(1)

# Test 2: Required Packages
print("\n2. Checking required packages...")
required_packages = {
    'dotenv': 'python-dotenv',
    'sqlalchemy': 'sqlalchemy',
    'psycopg2': 'psycopg2-binary',
    'reportlab': 'reportlab'
}

missing = []
for package, pip_name in required_packages.items():
    try:
        __import__(package)
        print(f"   ✅ {pip_name}")
    except ImportError:
        print(f"   ❌ {pip_name} (run: pip install {pip_name})")
        missing.append(pip_name)

if missing:
    print(f"\n   Install missing packages:")
    print(f"   pip install {' '.join(missing)}")
    sys.exit(1)

# Test 3: .env File
print("\n3. Checking .env file...")
if Path('.env').exists():
    print("   ✅ .env file exists")
    
    # Load and check
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == 'DB_PASSWORD':
                print(f"   ✅ {var}=****")
            else:
                print(f"   ✅ {var}={value}")
        else:
            print(f"   ❌ {var} not set in .env")
            sys.exit(1)
else:
    print("   ❌ .env file not found")
    print("   Create .env file from .env.example")
    sys.exit(1)

# Test 4: Database Connection
print("\n4. Testing database connection...")
try:
    from sqlalchemy import create_engine, text
    
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASSWORD')
    
    url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(url)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        conn.commit()
    
    print(f"   ✅ Connected to {db_name}")
    
except Exception as e:
    print(f"   ❌ Database connection failed")
    print(f"   Error: {e}")
    print("\n   Check:")
    print("   - Is PostgreSQL running?")
    print("   - Are credentials correct?")
    print("   - Does database exist?")
    sys.exit(1)

# Test 5: Folders
print("\n5. Checking folders...")
folders = ['reports', 'logs', 'static']
for folder in folders:
    if Path(folder).exists():
        print(f"   ✅ {folder}/")
    else:
        print(f"   ⚠️  {folder}/ not found (creating...)")
        Path(folder).mkdir(exist_ok=True)
        print(f"   ✅ {folder}/ created")

# Test 6: Logo
print("\n6. Checking logo...")
logo_path = os.getenv('LOGO_PATH', 'static/logo.png')
if Path(logo_path).exists():
    print(f"   ✅ Logo found: {logo_path}")
else:
    print(f"   ⚠️  Logo not found: {logo_path}")
    print("   Report will work but without logo")

# Test 7: Redis/S3 Status
print("\n7. Checking optional services...")
use_redis = os.getenv('USE_REDIS', 'false').lower() == 'true'
use_s3 = os.getenv('USE_S3', 'false').lower() == 'true'

print(f"   Redis: {'✅ Enabled' if use_redis else '⚪ Disabled (OK for local testing)'}")
print(f"   S3:    {'✅ Enabled' if use_s3 else '⚪ Disabled (OK for local testing)'}")

# Success!
print("\n" + "=" * 80)
print("✅ ALL CHECKS PASSED!")
print("=" * 80)
print("\nYou're ready to run the report generator:")
print("  python beautiful_agent.py")
print()