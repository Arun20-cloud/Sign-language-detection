# URGENT: Fix Database Configuration

You're getting the "Database not configured" error because Row Level Security (RLS) is blocking database operations.

## Quick Fix Steps:

1. **Go to your Supabase Dashboard:**
   - Visit: https://supabase.com/dashboard
   - Select your project

2. **Open SQL Editor:**
   - Click "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Run this SQL:**
   \`\`\`sql
   -- Remove all RLS policies
   DROP POLICY IF EXISTS users_delete_own ON users;
   DROP POLICY IF EXISTS users_insert_new ON users;
   DROP POLICY IF EXISTS users_select_own ON users;
   DROP POLICY IF EXISTS users_update_own ON users;
   
   -- Disable RLS completely
   ALTER TABLE users DISABLE ROW LEVEL SECURITY;
   \`\`\`

4. **Click "Run"** (or press Ctrl+Enter)

5. **Refresh your registration page** - it should work immediately!

## Why This Is Necessary:

- Your app uses custom username/password authentication
- Supabase RLS policies expect Supabase Auth (JWT tokens)
- Since you're using SERVICE_ROLE_KEY, RLS should be disabled
- The policies are blocking INSERT and SELECT operations

## Alternative: Use Supabase Auth Instead

If you want to keep RLS enabled, you would need to migrate to Supabase's built-in authentication system instead of custom username/password storage.
