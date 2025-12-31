# Set OPENAI_API_KEY in Railway - Step by Step

## ⚠️ Current Issue
Your app is running, but `OPENAI_API_KEY` is not set in Railway Variables. This is why uploads are failing.

## ✅ Quick Fix (2 minutes)

### Step 1: Go to Railway Dashboard
1. Open https://railway.app
2. Sign in to your account
3. Click on your project (e.g., "bubbly-fulfillment" or "voice-rag")

### Step 2: Open Your Service
1. Click on the "web" service (the one that's deployed)

### Step 3: Go to Variables Tab
1. Click on **"Variables"** tab (or "Settings" → "Variables")
2. You should see a list of environment variables (might be empty)

### Step 4: Add OPENAI_API_KEY
1. Click **"+ New Variable"** or **"Add Variable"** button
2. In the form that appears:
   - **Variable Name:** `OPENAI_API_KEY`
   - **Variable Value:** Paste your OpenAI API key here (starts with `sk-proj-`)
3. Click **"Add"** or **"Save"**

### Step 5: Wait for Redeploy
- Railway will automatically detect the new variable
- It will trigger a new deployment
- Wait 1-2 minutes for deployment to complete
- Status should change to "Active"

### Step 6: Test
1. Go to your webpage: `https://web-production-fe897.up.railway.app/`
2. Try uploading a document
3. It should work now! ✅

## Visual Guide

```
Railway Dashboard
  └── Your Project
      └── web (service)
          └── Variables (tab)
              └── + New Variable
                  ├── Name: OPENAI_API_KEY
                  ├── Value: sk-proj-...
                  └── Add
```

## Verification

After adding the variable:
- ✅ You should see `OPENAI_API_KEY` in the Variables list
- ✅ The value will be hidden (showing as `••••••••`)
- ✅ Railway will automatically redeploy
- ✅ Service status should be "Active"

## Your API Key

Your OpenAI API key should:
- Start with `sk-proj-`
- Be quite long (50+ characters)
- Be the same key you used during development

**⚠️ Security Note:** Never commit API keys to GitHub. Always use environment variables.

## Troubleshooting

**Can't find Variables tab?**
- Make sure you're in the service view, not the project view
- Look for "Settings" → "Variables"

**Variable not saving?**
- Check the name is exactly `OPENAI_API_KEY` (case-sensitive, no spaces)
- Make sure you clicked "Add" or "Save"

**Still getting errors after setting?**
- Wait for Railway to finish redeploying (check Deployments tab)
- Refresh your webpage
- Try uploading again

**Service not redeploying?**
- Click "Restart" button manually
- Or make a small code change and push to trigger redeploy

## After Setting the Key

Once `OPENAI_API_KEY` is set:
- ✅ Document uploads will work
- ✅ Voice transcription will work
- ✅ Query/answer generation will work
- ✅ All features will be functional

---

**Next Step:** Go to Railway → Your Service → Variables → Add `OPENAI_API_KEY` now!

