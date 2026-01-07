# Deploying Hand Sign Detector to Vercel

## Quick Deployment Guide

### Prerequisites
- GitHub account
- Vercel account (free)
- Supabase account with your database configured

### Step-by-Step Instructions

#### 1. Prepare Your Repository

Make sure your code is pushed to GitHub:

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### 2. Import to Vercel

1. Go to https://vercel.com/new
2. Click **"Import Project"**
3. Select **"Import Git Repository"**
4. Choose your GitHub repository
5. Click **"Import"**

#### 3. Configure Build Settings

Vercel should auto-detect the settings, but verify:

- **Framework Preset:** Other
- **Build Command:** (leave empty for Flask)
- **Output Directory:** (leave empty)
- **Install Command:** `pip install -r requirements.txt`

Click **"Deploy"** - this first deployment will fail with "Database not configured" - that's expected!

#### 4. Add Environment Variables (Critical Step!)

After the first deployment:

1. In your Vercel project, click **"Settings"**
2. Click **"Environment Variables"** in the sidebar
3. Add the following variables:

**Required Variables:**

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
SECRET_KEY=any-random-secret-string
```

**How to get Supabase credentials:**
- Go to https://supabase.com/dashboard
- Select your project
- Go to **Settings** → **API**
- Copy **"Project URL"** → Use as `SUPABASE_URL`
- Click **"Reveal"** next to **"service_role"** → Use as `SUPABASE_SERVICE_ROLE_KEY`

**Optional Variables (for AI Vision detection):**

```
AI_API_KEY=your-openai-api-key
AI_PROVIDER=openai
```

**Important:** For each variable, select all three environments:
- ✓ Production
- ✓ Preview  
- ✓ Development

#### 5. Redeploy

After adding environment variables:

1. Go to **"Deployments"** tab
2. Find the latest deployment
3. Click the **"..."** menu button
4. Select **"Redeploy"**
5. **Uncheck** "Use existing Build Cache"
6. Click **"Redeploy"**

Wait 1-2 minutes for the deployment to complete.

#### 6. Verify Deployment

1. Visit your deployed URL (e.g., `https://your-app.vercel.app`)
2. The "Database not configured" error should be gone
3. Try creating a new account
4. Test logging in
5. Test the hand sign detection features

---

## Troubleshooting

### Error: "Database not configured"

**Problem:** Environment variables are not set or not loaded

**Solutions:**
1. Verify environment variables are added in Settings → Environment Variables
2. Make sure you clicked "Save" for each variable
3. Redeploy the app (changes only apply after redeployment)
4. Check that you selected all three environments (Production, Preview, Development)

### Error: "Build failed"

**Problem:** Dependencies not installing correctly

**Solutions:**
1. Check that `requirements.txt` is in your repository
2. Verify all dependencies are listed
3. Check the build logs for specific errors
4. Try redeploying with build cache disabled

### Login works locally but not on Vercel

**Problem:** Different database or environment variables

**Solutions:**
1. Make sure the `SUPABASE_URL` on Vercel matches your local `.env` file
2. Verify you're using the same Supabase project
3. Check that users exist in the Supabase database you're connecting to

### Training data not syncing across devices

**Problem:** Cloud storage not working

**Solutions:**
1. Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set correctly
2. Check that the `training_data` table exists in your Supabase database
3. Run the SQL script: `scripts/create_training_data_table.sql` in Supabase SQL Editor

### AI Detection not working on Vercel

**Problem:** Missing AI API credentials

**Solutions:**
1. Add `AI_API_KEY` environment variable with your OpenAI API key
2. Add `AI_PROVIDER=openai` environment variable
3. Redeploy the application
4. Alternatively, use the free KNN or Rule-Based detection methods

---

## Updating Your Deployment

When you make changes to your code:

1. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Your update message"
   git push origin main
   ```

2. **Automatic deployment:**
   - Vercel will automatically detect the push and redeploy
   - Wait 1-2 minutes for the new version to go live

3. **Manual deployment:**
   - Go to Vercel Dashboard → Your Project → Deployments
   - Click "Redeploy" on any previous deployment

---

## Environment Variables Reference

| Variable | Purpose | Required | Where to Get It |
|----------|---------|----------|-----------------|
| `SUPABASE_URL` | Database connection URL | ✓ Yes | Supabase Dashboard → Settings → API |
| `SUPABASE_SERVICE_ROLE_KEY` | Database admin key | ✓ Yes | Supabase Dashboard → Settings → API → service_role |
| `SECRET_KEY` | Flask session encryption | ✓ Yes | Any random string you create |
| `AI_API_KEY` | OpenAI API for vision detection | Optional | https://platform.openai.com/api-keys |
| `AI_PROVIDER` | AI provider name | Optional | Set to `openai` |

---

## Security Best Practices

1. **Never commit `.env` files to Git** - They contain secrets
2. **Use service_role key only on backend** - Never expose in frontend JavaScript
3. **Rotate keys periodically** - Update in Vercel dashboard when you do
4. **Enable Row Level Security (RLS)** in Supabase for production apps
5. **Use different Supabase projects** for development and production

---

## Support

If you encounter issues not covered here:

1. Check the Vercel deployment logs in the "Deployments" tab
2. Check your Supabase logs in the Supabase Dashboard
3. Verify environment variables are spelled correctly (case-sensitive!)
4. Try deploying to a new Vercel project to isolate the issue
