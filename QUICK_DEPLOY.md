# Quick Deployment Guide

Choose your deployment method:

## 🐳 Docker (Recommended for Local/Testing)

```bash
# 1. Set your OpenAI API key
export OPENAI_API_KEY=your_key_here

# 2. Run with Docker Compose
docker-compose up -d

# 3. Access at http://localhost:8000
```

## ☁️ Railway (Easiest Cloud Deployment)

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Add environment variable: `OPENAI_API_KEY`
5. Deploy!

## 🚀 Render (Free Tier Available)

1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repository
4. Add environment variable: `OPENAI_API_KEY`
5. Deploy!

## ✈️ Fly.io (Global Edge Deployment)

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch (follow prompts)
fly launch

# Set API key
fly secrets set OPENAI_API_KEY=your_key_here

# Deploy
fly deploy
```

## 📋 Environment Variables Required

- `OPENAI_API_KEY` - Your OpenAI API key (required)

Optional:
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `ALLOWED_ORIGINS` - Comma-separated list of allowed CORS origins

## 🔒 Production Checklist

- [ ] Set `OPENAI_API_KEY` environment variable
- [ ] Update `ALLOWED_ORIGINS` in `.env` or platform settings
- [ ] Enable HTTPS (most platforms do this automatically)
- [ ] Test deployment
- [ ] Monitor logs

## 📚 Full Documentation

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

