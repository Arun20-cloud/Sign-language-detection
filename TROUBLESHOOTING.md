# Troubleshooting Guide

## Common Issues and Solutions

### 1. Dataset Not Showing in Detect Mode

**Symptoms:**
- Trained gestures in Train mode
- Detect mode shows "0 Total Gestures"
- Stats say "No gestures trained yet"

**Cause:**
- localStorage key mismatch between pages

**Solution:**
✅ **Already Fixed!** The latest version uses consistent localStorage keys across Train and Detect pages.

**How to verify it's fixed:**
1. Go to Train mode
2. Open browser DevTools (F12)
3. Go to Console tab
4. Look for logs like `[v0] Dataset loaded: 5 samples`
5. Go to Detect mode
6. You should see the same logs with your dataset

**If still not working:**
1. Clear browser localStorage: DevTools → Application → localStorage → Clear
2. Re-train your gestures
3. Check console for errors

---

### 2. "User Not Found" After Registration

**Symptoms:**
- Register a new account successfully
- Server restarts or you refresh
- Login shows "User not found"

**Cause:**
- App uses in-memory storage (resets on restart)
- This is intentional for demo/development

**Solutions:**

**Option A: Re-register (Quick Fix)**
1. Just register again with the same username
2. Train gestures again (or import your exported dataset)

**Option B: Keep Server Running**
- Don't restart the Flask server during your session
- Users persist until server stops

**Option C: Add Database (Production)**
For permanent user storage, integrate PostgreSQL:

\`\`\`python
# Install database
pip install psycopg2-binary sqlalchemy

# Add to requirements.txt
psycopg2-binary==2.9.9
sqlalchemy==2.0.23

# Update api/index.py with database code
# See README.md for full instructions
\`\`\`

---

### 3. Hand Detection Not Working

**Symptoms:**
- Camera starts successfully
- Video feed shows
- No hand skeleton appears
- No landmarks detected

**Debugging Steps:**

1. **Check MediaPipe Loading**
   - Open browser console (F12)
   - Look for MediaPipe errors
   - Wait 5-10 seconds for CDN scripts to load

2. **Verify Camera Feed**
   - Ensure your hand is fully visible
   - Try different hand positions
   - Check lighting (bright, even lighting works best)

3. **Check Console Logs**
   - Look for `[v0] Hand detected. Landmarks count: 21`
   - If you don't see this, MediaPipe isn't detecting your hand

4. **Try Different Browser**
   - Chrome/Edge work best
   - Firefox and Safari also supported

5. **Check Camera Permissions**
   - Click lock icon in address bar
   - Ensure camera is allowed
   - Reload page after granting permission

---

### 4. Recording Not Working

**Symptoms:**
- Camera works
- Hand is detected
- Click "Record Sample" but nothing happens

**Debugging:**
1. Check console for `[v0] Recording flag set to true`
2. Look for `[v0] Sample added. Total samples: X`
3. If you see errors, check:
   - Is gesture name filled in?
   - Is hand visible when you click Record?

**How recording works:**
1. Click "Record Sample"
2. Show your hand
3. System captures landmarks on next frame
4. Sample added to localStorage

**Tips:**
- Hold your hand steady while recording
- Use "Record Multiple (x5)" for quick batch recording
- Check Dataset section to see sample count increase

---

### 5. Low Prediction Accuracy

**Symptoms:**
- Gestures are detected
- Wrong labels appear frequently
- Confidence is low (< 60%)

**Solutions:**

1. **Record More Samples**
   - Aim for 10-15 samples per gesture minimum
   - Use "Record Multiple (x5)" button 2-3 times

2. **Vary Hand Positions**
   - Slightly rotate your hand while recording
   - Move hand closer/farther from camera
   - Change hand position slightly (not drastically)

3. **Train Distinct Gestures**
   - Avoid similar hand shapes
   - Make gestures clearly different
   - Examples of good pairs:
     - ✅ peace, fist, thumbs-up, ok
     - ❌ peace, victory (too similar)

4. **Consistent Conditions**
   - Train and detect in similar lighting
   - Same distance from camera
   - Same hand orientation

5. **Adjust K Value**
   - Lower K (1-3) for few samples
   - Higher K (5-7) for many samples
   - Default K=3 works well for 5-10 samples

---

### 6. Speech Not Working

**Symptoms:**
- Gestures detected correctly
- No audio output
- "Speak" button doesn't work

**Solutions:**

1. **Check Browser Support**
   - Chrome/Edge: Full support
   - Firefox: Full support
   - Safari: Partial support (may not work)

2. **Enable Audio**
   - Unmute your computer/browser
   - Check browser audio permissions
   - Try clicking "Speak" button manually first

3. **Auto-Speak Settings**
   - Enable "Auto-speak predictions" in settings
   - Requires 60%+ confidence to trigger
   - 2-second cooldown between repeats

---

### 7. Export/Import Not Working

**Symptoms:**
- Click Export but no download
- Import doesn't load data

**Export Issues:**
1. Check browser download permissions
2. Look in Downloads folder
3. File format: `handsign_dataset_USERNAME_timestamp.json`

**Import Issues:**
1. Ensure file is valid JSON
2. Check file format matches:
   \`\`\`json
   [
     {"label": "peace", "landmarks": [...]},
     {"label": "thumbs-up", "landmarks": [...]}
   ]
   \`\`\`
3. Check console for import errors

---

### 8. Deployment Issues

#### Vercel Deployment

**Error: "Function Runtimes must have a valid version"**
- ✅ Fixed in latest version
- Ensure you have the correct `vercel.json`

**Error: "Module not found"**
- Check `requirements.txt` has all dependencies
- Flask, secrets (built-in)

#### Render Deployment

**Error: "Build failed"**
- Ensure `Procfile` exists: `web: gunicorn app:app`
- Check `runtime.txt`: `python-3.11.0`
- Verify `requirements.txt` includes gunicorn

#### Replit Deployment

**Error: "Port already in use"**
- Replit auto-detects Flask apps
- Just click "Run" button
- No additional configuration needed

---

## Still Having Issues?

1. **Check Browser Console**
   - Press F12
   - Go to Console tab
   - Look for errors (red text)
   - Share errors for help

2. **Clear Everything and Start Fresh**
   \`\`\`javascript
   // Run in browser console
   localStorage.clear();
   location.reload();
   \`\`\`

3. **Verify File Structure**
   - All template files in `templates/` folder
   - `app.py` or `api/index.py` present
   - `requirements.txt` has Flask

4. **Test Basic Functionality**
   - Can you access login page?
   - Can you register?
   - Does camera permission prompt appear?
   - Do you see video feed?

---

## Debug Mode

To enable verbose logging, add this to your browser console:

\`\`\`javascript
// Enable all console logs
localStorage.setItem('debug', 'true');
location.reload();
\`\`\`

This will show detailed logs for:
- Dataset loading
- Hand detection
- Landmark normalization
- Prediction process
- Sample recording
