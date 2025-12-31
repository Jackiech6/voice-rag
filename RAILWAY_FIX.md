# Railway Deployment Fix Guide

## Common Crash Causes & Fixes

### 1. Missing Environment Variables

**Check in Railway Dashboard:**
- Go to your service → Variables tab
- Ensure `OPENAI_API_KEY` is set
- Add if missing

### 2. Port Configuration

Railway automatically sets the `PORT` environment variable. The updated Dockerfile now uses this.

**If still having issues, manually set:**
- Variable: `PORT`
- Value: `8000`

### 3. Database Path Issues

The app needs write permissions for database files.

**Set these variables in Railway:**
- `DATABASE_PATH` = `/app/data/metadata.db`
- `VECTOR_DB_PATH` = `/app/data/chroma_db`

### 4. Restart the Service

After fixing variables:
1. Click "Restart" button in Railway dashboard
2. Or go to Deployments → Redeploy

## Updated Files

I've updated:
- ✅ `Dockerfile` - Better healthcheck and port handling
- ✅ `config.py` - Handles Railway PORT variable
- ✅ `railway.json` - Railway-specific configuration

## Steps to Fix

1. **Commit and push the fixes:**
   ```bash
   git add Dockerfile config.py railway.json
   git commit -m "Fix Railway deployment configuration"
   git push
   ```

2. **In Railway Dashboard:**
   - Go to Variables tab
   - Ensure `OPENAI_API_KEY` is set
   - (Optional) Set `DATABASE_PATH` = `/app/data/metadata.db`
   - (Optional) Set `VECTOR_DB_PATH` = `/app/data/chroma_db`

3. **Redeploy:**
   - Railway will auto-redeploy on push
   - Or click "Restart" button

4. **Check Logs:**
   - Go to Logs tab in Railway
   - Look for error messages
   - Common errors:
     - "OPENAI_API_KEY not set"
     - "Port already in use"
     - "Permission denied" (database files)

## Testing Locally

Test the Docker build locally:
```bash
docker build -t voice-rag .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key voice-rag
```

## Still Crashing?

Check Railway logs for specific error messages:
1. Go to Railway dashboard
2. Click on your service
3. Go to "Logs" tab
4. Look for error messages
5. Share the error and I'll help fix it

