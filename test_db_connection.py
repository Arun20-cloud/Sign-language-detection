"""
Test script to verify .env file loading and database connection
Run this with: python test_db_connection.py
"""

import os
import sys

print("=" * 60)
print("DATABASE CONNECTION TEST")
print("=" * 60)

# Step 1: Check if python-dotenv is installed
print("\n1. Checking python-dotenv installation...")
try:
    from dotenv import load_dotenv
    print("   ✓ python-dotenv is installed")
except ImportError:
    print("   ✗ python-dotenv is NOT installed")
    print("   → Run: pip install python-dotenv")
    sys.exit(1)

# Step 2: Load .env file
print("\n2. Loading .env file...")
load_dotenv()
print("   ✓ load_dotenv() executed")

# Step 3: Check if environment variables are loaded
print("\n3. Checking environment variables...")
supabase_url = os.environ.get('SUPABASE_URL')
service_role_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
secret_key = os.environ.get('SECRET_KEY')

if supabase_url:
    print(f"   ✓ SUPABASE_URL: {supabase_url}")
else:
    print("   ✗ SUPABASE_URL: NOT FOUND")

if service_role_key:
    print(f"   ✓ SUPABASE_SERVICE_ROLE_KEY: {service_role_key[:20]}...")
else:
    print("   ✗ SUPABASE_SERVICE_ROLE_KEY: NOT FOUND")

if secret_key:
    print(f"   ✓ SECRET_KEY: {secret_key[:10]}...")
else:
    print("   ✗ SECRET_KEY: NOT FOUND")

# Step 4: Test Supabase connection
if supabase_url and service_role_key:
    print("\n4. Testing Supabase connection...")
    try:
        import requests
        
        # Test connection with a simple REST API call
        headers = {
            'apikey': service_role_key,
            'Authorization': f'Bearer {service_role_key}'
        }
        
        response = requests.get(
            f"{supabase_url}/rest/v1/users?limit=1",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"   ✓ Successfully connected to Supabase!")
            print(f"   ✓ Database is accessible")
        elif response.status_code == 404:
            print(f"   ⚠ Connected but 'users' table not found")
            print(f"   → You may need to run database setup scripts")
        else:
            print(f"   ✗ Connection failed with status: {response.status_code}")
            print(f"   → Response: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Connection error: {str(e)}")
    except ImportError:
        print("   ⚠ 'requests' package not installed")
        print("   → Run: pip install requests")
else:
    print("\n4. Skipping connection test (missing credentials)")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
