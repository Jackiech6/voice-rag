# Railway Troubleshooting Guide

## Application Failed to Respond - Quick Fixes

### Step 1: Check Railway Logs

1. Go to Railway dashboard
2. Click on your service
3. Go to **"Logs"** tab
4. Look for error messages

**Common errors to look for:**
- `ModuleNotFoundError` - Missing dependency
- `OPENAI_API_KEY` not set - Missing environment variable
- `Port already in use` - Port configuration issue
- `Permission denied` - File permission issue
- `ImportError` - Python import issue

### Step 2: Verify Environment Variables

Go to Railway → Your Service → **Variables** tab

**Required:**
- ✅ `OPENAI_API_KEY` - Must be set!

**Optional but recommended:**
- `PORT` - Railway sets this automatically, but you can set it to `8000` if needed
- `DATABASE_PATH` - Set to `/app/data/metadata.db`
- `VECTOR_DB_PATH` - Set to `/app/data/chroma_db`

### Step 3: Check Service Status

In Railway dashboard:
- Status should be **"Running"** (green)
- If **"Crashed"** (red), check logs
- If **"Building"**, wait for it to finish

### Step 4: Common Fixes

#### Fix 1: Missing OPENAI_API_KEY
```
Error: OPENAI_API_KEY not set
Solution: Add it in Railway Variables
```

#### Fix 2: Port Issues
```
Error: Port already in use
Solution: Railway handles this automatically, but ensure PORT is not manually set to a conflicting value
```

#### Fix 3: Import Errors
```
Error: ModuleNotFoundError: No module named 'X'
Solution: Check requirements.txt includes all dependencies
```

#### Fix 4: Database Permissions
```
Error: Permission denied
Solution: Ensure DATABASE_PATH and VECTOR_DB_PATH point to /app/data/
```

### Step 5: Restart Service

After fixing variables:
1. Click **"Restart"** button in Railway
2. Or trigger a new deployment by pushing to GitHub

### Step 6: Test Health Endpoint

Once running, test:
```
https://your-app.up.railway.app/health
```

Should return: `{"status": "healthy"}`

## Still Not Working?

### Get Detailed Logs

1. Railway dashboard → Service → Logs
2. Copy the error message
3. Look for the first error (usually at the bottom of logs)
4. Share the error and I'll help fix it

### Manual Debugging

If you want to test locally with Railway's setup:
```bash
# Test with Railway-like environment
export PORT=8000
export OPENAI_API_KEY=your_key_here
uvicorn api:app --host 0.0.0.0 --port $PORT
```

## Quick Checklist

- [ ] `OPENAI_API_KEY` is set in Railway Variables
- [ ] Service status is "Running" (not "Crashed")
- [ ] Latest code is pushed to GitHub
- [ ] Railway has redeployed after latest push
- [ ] Checked logs for specific error messages
- [ ] Health endpoint returns `{"status": "healthy"}`

