# How to Set OPENAI_API_KEY in Railway

## Quick Steps

1. **Go to Railway Dashboard:**
   - Visit https://railway.app
   - Sign in to your account

2. **Navigate to Your Service:**
   - Click on your project
   - Click on the "web" service

3. **Go to Variables Tab:**
   - Click on "Variables" tab (or "Settings" → "Variables")

4. **Add OPENAI_API_KEY:**
   - Click "+ New Variable" or "Add Variable"
   - **Name:** `OPENAI_API_KEY`
   - **Value:** Your OpenAI API key (starts with `sk-proj-...`)
   - Click "Add" or "Save"

5. **Wait for Redeploy:**
   - Railway will automatically redeploy when you add variables
   - Wait 1-2 minutes for deployment to complete

6. **Test:**
   - Try uploading a document again
   - The error should be gone

## Your OpenAI API Key

Your API key should look like:
```
sk-proj-...your-key-here...
```

**Note:** Use the API key you have. It should start with `sk-proj-` and be quite long.

**⚠️ Important:** Never share your API key publicly or commit it to GitHub!

## Verification

After setting the variable:
1. Check Railway → Service → Variables
2. You should see `OPENAI_API_KEY` listed
3. The value should be hidden (showing as `••••••••`)
4. Service should automatically redeploy

## Troubleshooting

**Variable not saving?**
- Make sure you're in the correct service
- Check that the name is exactly `OPENAI_API_KEY` (case-sensitive)
- Try refreshing the page

**Still getting errors?**
- Wait for Railway to finish redeploying (check Deployments tab)
- Check that the variable name is correct
- Verify the API key is valid (starts with `sk-proj-`)

**App still not working?**
- Check Railway Logs for specific errors
- Verify the service status is "Active"
- Try restarting the service

