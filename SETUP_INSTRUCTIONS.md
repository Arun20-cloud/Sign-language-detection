# Hand Sign Detector - Setup Instructions

## Database Setup (Required First Step!)

The application uses Supabase for persistent user authentication. Follow these steps to set up the database:

### Step 1: Run the SQL Script

1. In the v0 UI, click the **Scripts** button in the left sidebar
2. Find the script: `001_create_users_table.sql`
3. Click **Run** to execute the script
4. This creates the `users` table in your Supabase database

### Step 2: Verify Setup (Optional)

1. Run the script: `002_verify_table.sql` to confirm the table was created
2. You should see the users table structure with columns: id, username, password, created_at

### Step 3: Test Registration

1. Go to the registration page
2. Create a new account
3. The error "Database not configured" should be gone
4. After registration, you'll be redirected to login

## AI Detection Setup (Optional)

To use AI Vision mode for automatic hand sign detection:

1. Get an OpenAI API key from https://platform.openai.com
2. In the v0 UI, go to **Vars** in the left sidebar
3. Add these environment variables:
   - `AI_API_KEY`: Your OpenAI API key (starts with sk-)
   - `AI_PROVIDER`: Set to `openai`
4. Redeploy your app

Note: AI Vision mode uses the OpenAI API which has rate limits and costs. KNN mode is free and works offline.

## Troubleshooting

### "Database not configured" error
- Make sure you ran the SQL script `001_create_users_table.sql`
- Check that Supabase integration is connected in the Connect section
- Verify environment variables are set in the Vars section

### "User not found" after registration
- This means the database table wasn't created yet
- Run the SQL setup script as described above

### AI Detection not working
- Check that `AI_API_KEY` and `AI_PROVIDER` are set in environment variables
- Verify you have billing enabled on your OpenAI account
- Try using KNN mode instead (no API key needed)

## Features After Setup

Once the database is configured, you can:

- Register new users with persistent accounts
- Login and access the hand sign detector
- Train custom gestures using KNN mode
- Use AI Vision mode for automatic detection (if API key configured)
- Build sentences from detected letters
- Text-to-speech for reading detected sentences

## Support

If you encounter issues:
1. Check the setup steps above
2. Review the console logs for error messages
3. Open a support ticket at vercel.com/help
