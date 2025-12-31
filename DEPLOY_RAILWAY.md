# Quick Railway Deployment Guide

## Why Railway?

✅ **Best Free Option:**
- $5 free credit monthly
- Automatic HTTPS
- Zero-config deployments
- GitHub integration
- Environment variable management

## Quick Start (5 minutes)

### 1. Push to GitHub (if not done)

```bash
# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/voice-rag.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (free)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `voice-rag` repository
5. Railway auto-detects Dockerfile and deploys

### 3. Set Environment Variables

1. Click on your service
2. Go to "Variables" tab
3. Add: `OPENAI_API_KEY` = `your_key_here`
4. Railway auto-redeploys

### 4. Get Your URL

1. Click "Generate Domain"
2. Your app is live at: `https://your-app.up.railway.app`
3. Access UI at: `https://your-app.up.railway.app/static/index.html`

### 5. Update CORS (Important!)

1. In Railway Variables, add:
   - `ALLOWED_ORIGINS` = `https://your-app.up.railway.app`
2. App will auto-redeploy

## That's It! 🎉

Your app is now live and accessible worldwide!

## Monitoring

- View logs: Railway dashboard → Service → Logs
- Monitor usage: Railway dashboard → Usage
- View metrics: Railway dashboard → Metrics

## Custom Domain (Optional)

1. Railway dashboard → Service → Settings → Domains
2. Add your domain
3. Update DNS records as instructed
4. Update `ALLOWED_ORIGINS` with your custom domain

## Troubleshooting

**Build fails?**
- Check Railway logs
- Verify Dockerfile is correct
- Check requirements.txt

**App crashes?**
- Check logs in Railway dashboard
- Verify `OPENAI_API_KEY` is set
- Check environment variables

**CORS errors?**
- Make sure `ALLOWED_ORIGINS` includes your Railway URL
- No trailing slash in URL

