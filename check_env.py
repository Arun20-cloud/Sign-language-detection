#!/usr/bin/env python3
"""
Quick script to verify .env file is being loaded correctly
Run this to diagnose environment variable issues
"""

import os
from pathlib import Path

print("=" * 60)
print("ENVIRONMENT DIAGNOSTICS")
print("=" * 60)

# Check if .env file exists
env_file = Path(".env")
print(f"\n1. .env file location: {env_file.absolute()}")
print(f"   .env exists: {env_file.exists()}")

if env_file.exists():
    print(f"   .env file size: {env_file.stat().st_size} bytes")
    print("\n2. .env file contents (sanitized):")
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    if 'KEY' in key or 'SECRET' in key:
                        print(f"   {key}=***HIDDEN*** (length: {len(value)})")
                    else:
                        print(f"   {key}={value}")
else:
    print("   WARNING: .env file not found!")

# Check if python-dotenv is installed
print("\n3. python-dotenv installation:")
try:
    import dotenv
    print(f"   ✓ python-dotenv is installed (version: {dotenv.__version__})")
except ImportError:
    print("   ✗ python-dotenv is NOT installed")
    print("   Run: pip install python-dotenv")

# Try to load .env and check variables
print("\n4. Loading .env file:")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("   ✓ load_dotenv() executed successfully")
except Exception as e:
    print(f"   ✗ Error loading .env: {e}")

# Check environment variables
print("\n5. Environment variables after loading:")
env_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY', 'SECRET_KEY']
for var in env_vars:
    value = os.environ.get(var)
    if value:
        if 'KEY' in var or 'SECRET' in var:
            print(f"   ✓ {var}: ***SET*** (length: {len(value)})")
        else:
            print(f"   ✓ {var}: {value}")
    else:
        print(f"   ✗ {var}: NOT FOUND")

print("\n6. Current working directory:")
print(f"   {Path.cwd()}")

print("\n7. Files in current directory:")
files = [f.name for f in Path.cwd().iterdir() if f.is_file()]
print(f"   {', '.join(files[:10])}")
if len(files) > 10:
    print(f"   ... and {len(files) - 10} more files")

print("\n" + "=" * 60)
print("DIAGNOSIS:")
print("=" * 60)

# Provide diagnosis
issues = []
if not env_file.exists():
    issues.append("❌ .env file is missing - create it in the project root")
    
try:
    import dotenv
except ImportError:
    issues.append("❌ python-dotenv not installed - run: pip install python-dotenv")

if not os.environ.get('SUPABASE_URL'):
    issues.append("❌ SUPABASE_URL not loaded - check .env file format")
    
if not os.environ.get('SUPABASE_SERVICE_ROLE_KEY'):
    issues.append("❌ SUPABASE_SERVICE_ROLE_KEY not loaded - check .env file format")

if issues:
    print("\nISSUES FOUND:")
    for issue in issues:
        print(f"  {issue}")
    print("\nFIXES:")
    print("  1. Ensure .env is in the same folder as app.py")
    print("  2. Run: pip install python-dotenv")
    print("  3. Restart your Flask server after fixing")
else:
    print("\n✓ All checks passed! Environment is configured correctly.")
    print("  If you still see 'Database not configured' error:")
    print("  1. Stop your Flask server (Ctrl+C)")
    print("  2. Run: python app.py")
    print("  3. The environment variables should now be loaded")

print("=" * 60)
