# Quick Start Guide - Hand Sign Detector

## For New Installation on Another Laptop

Follow these steps to get the Hand Sign Detector running on a new machine:

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Create `.env` File

Create a file named `.env` in the project root directory (same folder as `app.py`):

**Windows (Command Prompt):**
```cmd
type nul > .env
notepad .env
```

**Mac/Linux:**
```bash
touch .env
nano .env
```

**Or in VS Code:**
- Right-click in the file explorer → New File
- Name it `.env` (with the dot at the beginning)

### Step 3: Add Your Credentials to `.env`

Paste these lines into your `.env` file and replace with your actual values:

```plaintext
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SECRET_KEY=any-random-string-you-choose
