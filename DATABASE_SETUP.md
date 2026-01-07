# Database Setup Instructions

## Supabase Database Configuration

The Hand Sign Detector uses Supabase for persistent user authentication. Follow these steps to set up the database:

### Step 1: Run the SQL Script

1. **Navigate to v0 Scripts Section:**
   - In the v0 interface, look for the "Scripts" section in your sidebar
   - Find the file: `scripts/001_create_users_table.sql`

2. **Execute the Script:**
   - Click the "Run" or "Execute" button next to the SQL script
   - This will create the `users` table in your Supabase database

### Step 2: Verify Database Setup

After running the script, you should have:

- ✅ A `users` table with columns: `id`, `username`, `password`, `created_at`
- ✅ Row Level Security (RLS) enabled
- ✅ Policies configured for secure data access

### Step 3: Test the Application

1. Visit your deployed application
2. Click "Register" to create a new account
3. After registration, you'll be redirected to the login page
4. Login with your credentials
5. You should now see the dashboard with Detect and Train options

## Environment Variables

Make sure these Supabase environment variables are configured in your Vercel project:

- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Your Supabase anonymous key
- `POSTGRES_URL` - PostgreSQL connection string (auto-configured)

## Troubleshooting

### "Database not configured" Error

If you see this error:
1. Check that all Supabase environment variables are set
2. Verify the SQL script was executed successfully
3. Check Vercel deployment logs for connection errors

### "User not found" After Registration

If users can't login after registering:
1. Verify the `users` table exists in Supabase
2. Check that the SQL script created the table correctly
3. Run the script again if needed (it's safe to re-run)

## Security Notes

⚠️ **Important:** This setup uses plain text passwords for simplicity. For production use, implement proper password hashing (bcrypt, argon2, etc.).

## Need Help?

- Check Supabase dashboard for table structure
- View Vercel logs for detailed error messages
- Ensure all environment variables are properly configured
