# Connection Error Fix Guide

## Issue: "Connection error" when uploading documents

This error means the app can't connect to OpenAI's API. Here's how to fix it:

## Possible Causes & Fixes

### 1. API Key Not Set at Service Level ⚠️ MOST LIKELY

**Problem:** API key is in Shared Variables but not accessible to the service

**Fix:**
1. Go to Railway → Your Project → **"web" service** (not project settings)
2. Click **"Variables"** tab
3. Add `OPENAI_API_KEY` with your API key value
4. Click **"Restart"** button
5. Wait 1-2 minutes

### 2. Invalid API Key

**Problem:** API key is incorrect or expired

**Fix:**
1. Verify your API key is correct
2. Check it starts with `sk-proj-`
3. Make sure there are no extra spaces
4. Try regenerating the key from OpenAI dashboard if needed

### 3. Network/Timeout Issues

**Problem:** Railway can't reach OpenAI API

**Fix:**
1. Wait a few minutes and try again
2. Check OpenAI status: https://status.openai.com
3. Check Railway status: https://status.railway.app

### 4. Rate Limiting

**Problem:** Too many API calls

**Fix:**
1. Wait a few minutes
2. Check your OpenAI usage dashboard
3. Try again later

## Quick Diagnostic Steps

1. **Check Railway Logs:**
   - Railway → Service → Logs
   - Look for specific error messages
   - Share the error if you need help

2. **Verify API Key:**
   - Railway → Service → Variables
   - Should see `OPENAI_API_KEY` listed
   - Value should be hidden (`••••••••`)

3. **Test API Key:**
   - Go to OpenAI dashboard
   - Verify the key is active
   - Check usage limits

## Most Common Fix

**90% of connection errors are due to API key not being set at service level.**

Make sure:
- ✅ API key is in **Service Variables** (not just Shared Variables)
- ✅ Service has been restarted after adding the variable
- ✅ Variable name is exactly `OPENAI_API_KEY` (case-sensitive)

## After Fixing

Once the API key is properly set:
1. Service should restart automatically
2. Wait 1-2 minutes
3. Try uploading again
4. Should work! ✅

