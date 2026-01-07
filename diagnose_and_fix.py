#!/usr/bin/env python3
"""
Comprehensive diagnostic tool for Hand Sign Detector database configuration
Run this to identify and fix database connection issues
"""

import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_success(text):
    print(f"✓ {text}")

def print_error(text):
    print(f"✗ {text}")

def print_warning(text):
    print(f"⚠ {text}")

def check_python_version():
    print_header("1. Checking Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 7:
        print_success("Python version is compatible")
        return True
    else:
        print_error("Python 3.7+ required")
        return False

def check_dotenv_installed():
    print_header("2. Checking python-dotenv Package")
    try:
        import dotenv
        print_success("python-dotenv is installed")
        return True
    except ImportError:
        print_error("python-dotenv is NOT installed")
        print("\nTo fix, run:")
        print("  pip install python-dotenv")
        return False

def check_env_file():
    print_header("3. Checking .env File")
    
    # Check if .env exists
    env_path = Path('.env')
    if not env_path.exists():
        print_error(".env file does NOT exist")
        print("\nTo fix:")
        print("  1. Create a file named '.env' in the project root")
        print("  2. Add your Supabase credentials:")
        print("\nExample .env file content:")
        print("-" * 40)
        print("SUPABASE_URL=https://your-project.supabase.co")
        print("SUPABASE_SERVICE_ROLE_KEY=your-key-here")
        print("SECRET_KEY=your-secret-key")
        print("-" * 40)
        return False
    
    print_success(".env file exists")
    
    # Check file location
    abs_path = env_path.resolve()
    print(f"Location: {abs_path}")
    
    # Check file is not empty
    content = env_path.read_text()
    if not content.strip():
        print_error(".env file is EMPTY")
        return False
    
    print_success(".env file has content")
    
    # Check for required variables
    lines = content.strip().split('\n')
    required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY', 'SECRET_KEY']
    found_vars = {}
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            if '=' in line:
                key = line.split('=')[0].strip()
                value = line.split('=', 1)[1].strip()
                found_vars[key] = value
    
    print("\nVariables found in .env:")
    all_found = True
    for var in required_vars:
        if var in found_vars:
            # Show first 20 chars of value
            value_preview = found_vars[var][:20] + "..." if len(found_vars[var]) > 20 else found_vars[var]
            print_success(f"{var} = {value_preview}")
        else:
            print_error(f"{var} is MISSING")
            all_found = False
    
    if not all_found:
        print("\nPlease add missing variables to .env file")
        return False
    
    return True

def check_env_loading():
    print_header("4. Testing Environment Variable Loading")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print_success("load_dotenv() executed successfully")
    except Exception as e:
        print_error(f"Failed to load .env: {e}")
        return False
    
    # Check if variables are accessible
    required_vars = {
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_SERVICE_ROLE_KEY': os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
        'SECRET_KEY': os.getenv('SECRET_KEY')
    }
    
    print("\nEnvironment variables loaded:")
    all_loaded = True
    for var_name, var_value in required_vars.items():
        if var_value:
            value_preview = var_value[:20] + "..." if len(var_value) > 20 else var_value
            print_success(f"{var_name} = {value_preview}")
        else:
            print_error(f"{var_name} is NOT loaded")
            all_loaded = False
    
    return all_loaded

def check_supabase_connection():
    print_header("5. Testing Supabase Connection")
    
    try:
        from supabase import create_client
        from dotenv import load_dotenv
        
        load_dotenv()
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not url or not key:
            print_error("Cannot test connection - environment variables not loaded")
            return False
        
        print(f"Connecting to: {url}")
        supabase = create_client(url, key)
        
        # Try a simple query
        response = supabase.table('users').select('id').limit(1).execute()
        
        print_success("Successfully connected to Supabase!")
        print_success("Database is configured correctly")
        return True
        
    except Exception as e:
        print_error(f"Connection failed: {str(e)}")
        print("\nPossible issues:")
        print("  - Invalid SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
        print("  - Network connection problem")
        print("  - 'users' table doesn't exist in database")
        return False

def main():
    print("\n" + "="*60)
    print("  HAND SIGN DETECTOR - DATABASE DIAGNOSTIC TOOL")
    print("="*60)
    
    checks = [
        check_python_version(),
        check_dotenv_installed(),
        check_env_file(),
        check_env_loading(),
        check_supabase_connection()
    ]
    
    print_header("DIAGNOSTIC SUMMARY")
    
    if all(checks):
        print_success("ALL CHECKS PASSED!")
        print("\nYour database is configured correctly.")
        print("\nNext steps:")
        print("  1. Make sure Flask server is stopped (Ctrl+C)")
        print("  2. Start Flask server: python app.py")
        print("  3. Open browser: http://localhost:5000")
        print("\nThe 'Database not configured' error should be gone.")
    else:
        print_error("SOME CHECKS FAILED")
        print("\nPlease fix the issues above and run this script again:")
        print("  python diagnose_and_fix.py")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
