# GitHub Setup & Railway Deployment Guide

## Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right → "New repository"
3. Repository name: `voice-rag` (or your preferred name)
4. Description: "Voice to RAG System - Document Q&A with voice input"
5. Choose **Public** or **Private**
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

## Step 2: Push to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
cd /Users/chenjackie/Desktop/WRDS

# Add your GitHub repository as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/voice-rag.git

# Or if you prefer SSH:
# git remote add origin git@github.com:YOUR_USERNAME/voice-rag.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Deploy to Railway (Free Tier)

Railway offers the best free option with:
- ✅ $5 free credit monthly
- ✅ Automatic HTTPS
- ✅ Easy GitHub integration
- ✅ Environment variable management
- ✅ Automatic deployments

### Deploy Steps:

1. **Go to Railway:**
   - Visit [railway.app](https://railway.app)
   - Sign up with GitHub (free)

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize Railway to access your GitHub
   - Select your `voice-rag` repository

3. **Configure Deployment:**
   - Railway will auto-detect the Dockerfile
   - Click on the service to configure

4. **Set Environment Variables:**
   - Click on your service
   - Go to "Variables" tab
   - Add: `OPENAI_API_KEY` = `your_openai_api_key_here`
   - (Optional) Add: `ALLOWED_ORIGINS` = `https://your-app-name.up.railway.app`

5. **Deploy:**
   - Railway will automatically deploy
   - Wait for deployment to complete (2-5 minutes)
   - Click "Generate Domain" to get your public URL

6. **Access Your App:**
   - Your app will be available at: `https://your-app-name.up.railway.app`
   - Web UI: `https://your-app-name.up.railway.app/static/index.html`

## Step 4: Update CORS (Important!)

After getting your Railway URL:

1. Go to Railway dashboard → Your service → Variables
2. Add/Update: `ALLOWED_ORIGINS` = `https://your-app-name.up.railway.app`
3. Redeploy (Railway will auto-redeploy when you update variables)

## Alternative Free Options

### Render (Free Tier)
- ✅ Free tier available
- ⚠️ Spins down after inactivity (15 min cold start)
- Visit [render.com](https://render.com)

### Fly.io (Free Tier)
- ✅ Free tier with 3 shared VMs
- ✅ Global edge deployment
- Visit [fly.io](https://fly.io)

## Troubleshooting

### Git Push Issues
- **Authentication**: Use GitHub Personal Access Token or SSH keys
- **Large files**: Check `.gitignore` is working
- **Remote exists**: `git remote -v` to check, `git remote remove origin` to reset

### Railway Deployment Issues
- **Build fails**: Check Dockerfile is correct
- **App crashes**: Check logs in Railway dashboard
- **API key error**: Verify `OPENAI_API_KEY` is set correctly

### CORS Issues
- Make sure `ALLOWED_ORIGINS` includes your Railway domain
- Format: `https://your-app.up.railway.app` (no trailing slash)

## Next Steps After Deployment

1. ✅ Test all features (upload, query, delete)
2. ✅ Verify HTTPS is working
3. ✅ Test voice recording
4. ✅ Monitor usage in Railway dashboard
5. ✅ Set up custom domain (optional)

## Cost Estimate

**Railway Free Tier:**
- $5 credit/month
- ~500 hours of runtime
- Perfect for development and small projects

**If you exceed free tier:**
- Pay-as-you-go pricing
- Very affordable for small projects

