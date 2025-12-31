# Railway Deployment Checklist - Final Steps

## ✅ Code Updates Complete

All fixes have been pushed to GitHub:
- ✅ Startup script added (`start.sh`)
- ✅ Dockerfile updated with proper port handling
- ✅ Railway configuration file added

## 🔧 Action Required in Railway Dashboard

### Step 1: Verify Environment Variables

1. Go to Railway dashboard: https://railway.app
2. Click on your project → Click on "web" service
3. Go to **"Variables"** tab
4. **CRITICAL:** Ensure `OPENAI_API_KEY` is set with your actual API key
   - If missing, click "+ New Variable"
   - Name: `OPENAI_API_KEY`
   - Value: `sk-proj-...` (your actual OpenAI API key)

### Step 2: Check Service Status

1. Go to **"Deployments"** tab
2. Look at the latest deployment
3. Status should be:
   - ✅ **"Active"** (green) = Working!
   - ❌ **"Crashed"** (red) = Need to check logs

### Step 3: View Logs (If Crashed)

1. Go to **"Logs"** tab
2. Scroll to the bottom (most recent errors)
3. Look for error messages

**Common errors:**
- `OPENAI_API_KEY` not found → Add it in Variables
- `ModuleNotFoundError` → Dependencies issue (should be fixed)
- `Port already in use` → Port issue (should be fixed)
- `Permission denied` → File permission (should be fixed)

### Step 4: Restart/Redeploy

After setting `OPENAI_API_KEY`:
1. Click **"Restart"** button (top right of service)
2. Or wait for Railway to auto-redeploy from GitHub push
3. Watch the deployment status

### Step 5: Test Your App

Once status shows "Active":
1. Go to: `https://web-production-fe897.up.railway.app/health`
   - Should return: `{"status": "healthy"}`
2. Go to: `https://web-production-fe897.up.railway.app/static/index.html`
   - Should show your Voice to RAG interface

## 🎯 Most Likely Issue

**90% of Railway crashes are due to missing `OPENAI_API_KEY`**

Make sure it's set in Railway Variables!

## 📋 Quick Verification

Run through this checklist:
- [ ] `OPENAI_API_KEY` is set in Railway Variables
- [ ] Latest code is pushed to GitHub (✅ Done)
- [ ] Railway has redeployed (check Deployments tab)
- [ ] Service status is "Active" (not "Crashed")
- [ ] Health endpoint works: `/health`
- [ ] Web UI loads: `/static/index.html`

## 🆘 Still Not Working?

If it's still crashing after setting `OPENAI_API_KEY`:

1. **Copy the error from Railway Logs**
2. **Check these common issues:**
   - Missing environment variable
   - Port configuration
   - Import errors
   - Database permissions

3. **Share the error message** and I'll help fix it

## ✅ Success Indicators

You'll know it's working when:
- ✅ Service status = "Active" (green)
- ✅ `/health` endpoint returns `{"status": "healthy"}`
- ✅ Web UI loads at `/static/index.html`
- ✅ You can upload documents
- ✅ You can ask questions

---

**Next Step:** Go to Railway dashboard and verify `OPENAI_API_KEY` is set!

