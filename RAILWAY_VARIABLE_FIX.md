# Railway Variable Not Working - Fix Guide

## Issue
You've set `OPENAI_API_KEY` in Shared Variables, but the app still says it's not set.

## Solution: Set Variable at Service Level

Railway Shared Variables might not be automatically available to services. You need to set it at the **service level** instead.

### Step 1: Go to Your Service
1. Railway Dashboard → Your Project
2. Click on the **"web"** service (not the project settings)

### Step 2: Go to Service Variables
1. In the service view, click **"Variables"** tab
2. (Or "Settings" → "Variables" if available)

### Step 3: Add OPENAI_API_KEY
1. Click **"+ New Variable"** or **"Add Variable"**
2. **Name:** `OPENAI_API_KEY`
3. **Value:** Your API key (the same one you set in Shared Variables)
4. Click **"Add"**

### Step 4: Restart Service
1. After adding the variable, click **"Restart"** button
2. Or wait for Railway to auto-redeploy
3. Wait 1-2 minutes for restart

### Step 5: Test Again
1. Go to your webpage
2. Try uploading a document
3. Should work now! ✅

## Alternative: Reference Shared Variable

If Railway supports it, you can reference the shared variable:
- In service variables, set: `OPENAI_API_KEY` = `${{OPENAI_API_KEY}}`
- This references the shared variable

## Why This Happens

Railway has two levels of variables:
- **Shared Variables** (project level) - for sharing across services
- **Service Variables** (service level) - specific to each service

Your service needs the variable at the **service level** to access it.

## Verification

After setting at service level:
1. Check service → Variables tab
2. You should see `OPENAI_API_KEY` listed
3. Service should restart automatically
4. Check logs - should not show API key errors

## Still Not Working?

If it's still not working after setting at service level:
1. Check Railway Logs for the actual error
2. Verify the variable name is exactly `OPENAI_API_KEY` (case-sensitive)
3. Try restarting the service manually
4. Check that the service is using the latest deployment

