# Local Development Setup Guide

Follow these steps to run the Hand Sign Detector on a new laptop or development machine.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- A Supabase account and project

## Step 1: Clone the Repository

\`\`\`bash
git clone <your-repository-url>
cd hand-sign-detector
\`\`\`

## Step 2: Install Python Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

Or if you're using Python 3:
\`\`\`bash
pip3 install -r requirements.txt
\`\`\`

## Step 3: Get Supabase Credentials

Your app uses Supabase for user authentication and data storage. You need to get your Supabase credentials:

### Option A: Use Existing Supabase Project

1. Go to https://supabase.com/dashboard
2. Select your existing project (the one used in your Vercel deployment)
3. Click on "Settings" (gear icon) in the left sidebar
4. Click on "API" section
5. Copy these values:
   - **Project URL** (looks like `https://xxxxx.supabase.co`)
   - **service_role key** (under "Project API keys" section - click "Reveal" button)

### Option B: Create New Supabase Project

If you don't have a Supabase project:

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Fill in project details and click "Create project"
4. Wait 2-3 minutes for setup to complete
5. Run the SQL script to create the users table:
   - Click "SQL Editor" in left sidebar
   - Click "New Query"
   - Paste this SQL:

\`\`\`sql
-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Disable RLS (Row Level Security) for custom authentication
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- Add index for faster username lookups
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
\`\`\`

   - Click "Run" to execute
6. Go to Settings → API and copy your credentials

## Step 4: Create `.env` File

1. In the project root directory, create a file named `.env` (no extension)
2. Copy the contents of `.env.example` into `.env`
3. Replace the placeholder values with your actual Supabase credentials:

\`\`\`bash
# Flask Secret Key - generate a random string or keep default
SECRET_KEY=your-secret-key-here-replace-with-random-string

# Supabase Database Configuration - REQUIRED
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-from-supabase-dashboard

# AI Vision API (Optional - only needed for AI detection mode)
AI_API_KEY=sk-your-openai-api-key-here
AI_PROVIDER=openai

# Server Configuration
PORT=5000
\`\`\`

**IMPORTANT**: Replace `your-project-id` and `your-service-role-key` with the actual values from Step 3.

## Step 5: Run the Application

\`\`\`bash
python app.py
\`\`\`

Or if you're using Python 3:
\`\`\`bash
python3 app.py
\`\`\`

You should see output like:
\`\`\`
╔═══════════════════════════════════════════════════════════╗
║  Hand Sign Detector Server                                ║
║  Running on http://localhost:5000                        ║
║                                                           ║
║  Features:                                                ║
║  - User Authentication                                    ║
║  - Train Mode (Record Gestures)                          ║
║  - Detect Mode (Recognize Gestures)                      ║
║                                                           ║
║  Press Ctrl+C to stop                                     ║
╚═══════════════════════════════════════════════════════════╝
\`\`\`

## Step 6: Access the Application

Open your web browser and go to:
\`\`\`
http://localhost:5000
\`\`\`

## Step 7: Login with Your Existing Credentials

If you have an existing account from your Vercel deployment:
1. Click "Login" 
2. Enter your username and password
3. You should now be logged in!

**Note**: Your training data (hand sign samples) is stored in your browser's localStorage, NOT in the database. So you'll need to retrain your hand signs on the new laptop, or export/import your training data from the old laptop.

## Troubleshooting

### Error: "Database not configured"

**Cause**: The `.env` file is missing or the Supabase credentials are incorrect.

**Solution**:
1. Make sure you created the `.env` file in the project root
2. Double-check that `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are correct
3. Make sure there are no extra spaces or quotes around the values
4. Restart the Flask server after creating/editing `.env`

### Error: "Module not found"

**Cause**: Python dependencies not installed.

**Solution**:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### Error: "Port 5000 already in use"

**Cause**: Another application is using port 5000.

**Solution**: Change the port in `.env`:
\`\`\`bash
PORT=8000
\`\`\`
Then access at `http://localhost:8000`

### Can't login with existing credentials

**Cause 1**: Using a different Supabase database than your Vercel deployment.

**Solution**: Make sure you're using the same Supabase project credentials from your Vercel environment variables.

**Cause 2**: The user doesn't exist in this database.

**Solution**: Register a new account on this installation.

### Training data is missing

**Cause**: Training data is stored in browser localStorage, not the database.

**Solution**: 
- Export your training data from the old laptop (Train page → Export button)
- Import it on the new laptop (Train page → Import button)
- Or retrain your hand signs

## Environment Variables Explained

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Flask session encryption key (can be any random string) |
| `SUPABASE_URL` | Yes | Your Supabase project URL from dashboard |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Service role key from Supabase API settings (has full database access) |
| `AI_API_KEY` | No | OpenAI API key for AI vision detection mode |
| `AI_PROVIDER` | No | AI provider (openai, anthropic, or groq) |
| `PORT` | No | Server port (defaults to 5000) |

## Exporting Training Data (Optional)

If you want to transfer your hand sign training data from one laptop to another:

1. On the **old laptop**:
   - Open the app and login
   - Go to Train Mode
   - Click "Export" button
   - Save the JSON file

2. On the **new laptop**:
   - Open the app and login
   - Go to Train Mode
   - Click "Import" button
   - Select the JSON file you exported

Your training data will now be available on the new laptop!

## Next Steps

After setup is complete:
1. Register a new account or login with existing credentials
2. Go to Train Mode to record hand sign samples
3. Go to Detect Mode to test real-time detection
4. Check out the AI Vision mode (requires OpenAI API key)

## Need More Help?

- Check the main [README.md](README.md) for features and usage
- Open browser console (F12) to see detailed error messages
- Check Flask server terminal for backend errors
- Verify Supabase connection in Supabase dashboard
