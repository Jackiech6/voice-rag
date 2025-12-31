# Railway Debugging Guide

## Current Status: Application Failed to Respond

If the app is still not loading after fixes, follow these steps:

### Step 1: Check Railway Logs

1. Go to Railway dashboard
2. Click on your service ("web")
3. Go to **"Logs"** tab
4. Scroll to the bottom (most recent)
5. Look for:
   - Error messages
   - Tracebacks
   - Startup messages
   - Port binding errors

### Step 2: Common Issues to Check

#### Issue 1: Missing OPENAI_API_KEY
**Symptom:** App crashes on startup
**Fix:** Set `OPENAI_API_KEY` in Railway Variables

#### Issue 2: NumPy/ChromaDB Compatibility
**Symptom:** `AttributeError: np.float_ was removed`
**Status:** ✅ Fixed (NumPy pinned to <2.0)

#### Issue 3: Port Configuration
**Symptom:** Port binding errors
**Status:** ✅ Fixed (startup script handles PORT)

#### Issue 4: Database Initialization
**Symptom:** Database errors on startup
**Status:** ✅ Fixed (added error handling)

#### Issue 5: Static Files Not Found
**Symptom:** 404 errors for static files
**Status:** ✅ Fixed (root endpoint serves index.html)

### Step 3: Verify Environment Variables

In Railway → Service → Variables, ensure:
- ✅ `OPENAI_API_KEY` is set
- (Optional) `PORT` - Railway sets this automatically
- (Optional) `DATABASE_PATH` = `/app/data/metadata.db`
- (Optional) `VECTOR_DB_PATH` = `/app/data/chroma_db`

### Step 4: Test Endpoints

Once deployed, test in order:

1. **Health Check:**
   ```
   https://web-production-fe897.up.railway.app/health
   ```
   Should return: `{"status": "healthy"}`

2. **API Docs:**
   ```
   https://web-production-fe897.up.railway.app/docs
   ```
   Should show FastAPI Swagger UI

3. **Root/Web UI:**
   ```
   https://web-production-fe897.up.railway.app/
   ```
   Should show the web interface

### Step 5: Check Deployment Status

In Railway dashboard:
- **Deployments** tab → Latest deployment
- Status should be "Active" (green)
- If "Crashed" (red), check logs

### Step 6: Restart Service

After fixing variables:
1. Click **"Restart"** button
2. Watch logs for startup messages
3. Wait 1-2 minutes for full startup

## What to Share for Help

If still not working, share:
1. **Latest error from Railway Logs** (last 20-30 lines)
2. **Service status** (Active/Crashed)
3. **Environment variables set** (without values)
4. **Health endpoint response** (if accessible)

## Recent Fixes Applied

✅ NumPy compatibility (pinned to <2.0)
✅ Root endpoint serves index.html
✅ API_URL uses window.location.origin
✅ Startup script with better error handling
✅ Database initialization error handling

All fixes are pushed to GitHub and should auto-deploy.

