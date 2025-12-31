# Deployment Guide

This guide covers multiple deployment options for the Voice to RAG System.

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Railway Deployment](#railway-deployment)
3. [Render Deployment](#render-deployment)
4. [Fly.io Deployment](#flyio-deployment)
5. [Heroku Deployment](#heroku-deployment)
6. [VPS Deployment](#vps-deployment)
7. [Production Considerations](#production-considerations)

---

## Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose installed (optional)

### Quick Start

1. **Build and run with Docker Compose:**
```bash
# Copy environment file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

2. **Build and run with Docker:**
```bash
# Build image
docker build -t voice-rag .

# Run container
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  -v $(pwd)/data:/app/data \
  --name voice-rag \
  voice-rag
```

### Access
- Web UI: http://localhost:8000/static/index.html
- API: http://localhost:8000

---

## Railway Deployment

Railway is a modern platform for deploying applications.

### Steps

1. **Install Railway CLI:**
```bash
npm i -g @railway/cli
railway login
```

2. **Initialize project:**
```bash
railway init
```

3. **Set environment variables:**
```bash
railway variables set OPENAI_API_KEY=your_key_here
```

4. **Deploy:**
```bash
railway up
```

### Alternative: GitHub Integration

1. Push code to GitHub
2. Go to [Railway](https://railway.app)
3. New Project → Deploy from GitHub
4. Select your repository
5. Add environment variable: `OPENAI_API_KEY`
6. Deploy

### Railway Configuration

Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "python api.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## Render Deployment

Render provides easy deployment with automatic HTTPS.

### Steps

1. **Create `render.yaml`:**
```yaml
services:
  - type: web
    name: voice-rag
    env: docker
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: OPENAI_API_KEY
        sync: false
    healthCheckPath: /health
```

2. **Deploy:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - New → Web Service
   - Connect GitHub repository
   - Select repository
   - Add environment variable: `OPENAI_API_KEY`
   - Deploy

### Manual Setup

1. Create new Web Service
2. Connect GitHub repository
3. Build command: (leave empty, uses Dockerfile)
4. Start command: `python api.py`
5. Add environment variable: `OPENAI_API_KEY`
6. Deploy

---

## Fly.io Deployment

Fly.io provides global deployment with edge computing.

### Steps

1. **Install Fly CLI:**
```bash
curl -L https://fly.io/install.sh | sh
```

2. **Login:**
```bash
fly auth login
```

3. **Create `fly.toml`:**
```toml
app = "voice-rag"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"

[[services]]
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

  [services.concurrency]
    type = "connections"
    hard_limit = 25
    soft_limit = 20

  [[services.http_checks]]
    interval = "10s"
    timeout = "2s"
    grace_period = "5s"
    method = "GET"
    path = "/health"
```

4. **Launch:**
```bash
fly launch
# Follow prompts, set OPENAI_API_KEY when asked
```

5. **Set secrets:**
```bash
fly secrets set OPENAI_API_KEY=your_key_here
```

6. **Deploy:**
```bash
fly deploy
```

---

## Heroku Deployment

Heroku is a popular platform-as-a-service.

### Steps

1. **Install Heroku CLI:**
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Or download from https://devcenter.heroku.com/articles/heroku-cli
```

2. **Login:**
```bash
heroku login
```

3. **Create app:**
```bash
heroku create your-app-name
```

4. **Create `Procfile`:**
```
web: python api.py
```

5. **Set environment variables:**
```bash
heroku config:set OPENAI_API_KEY=your_key_here
```

6. **Deploy:**
```bash
git push heroku main
```

### Alternative: Container Deployment

1. **Enable container registry:**
```bash
heroku container:login
```

2. **Create `heroku.yml`:**
```yaml
build:
  docker:
    web: Dockerfile
run:
  web: python api.py
```

3. **Deploy:**
```bash
heroku container:push web
heroku container:release web
```

---

## VPS Deployment

Deploy to a Virtual Private Server (DigitalOcean, AWS EC2, Linode, etc.).

### Steps

1. **SSH into server:**
```bash
ssh user@your-server-ip
```

2. **Install dependencies:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.11 python3-pip python3-venv -y

# Install Nginx (for reverse proxy)
sudo apt install nginx -y
```

3. **Clone repository:**
```bash
git clone https://github.com/yourusername/voice-rag.git
cd voice-rag
```

4. **Set up virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Set environment variables:**
```bash
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY
```

6. **Create systemd service:**
```bash
sudo nano /etc/systemd/system/voice-rag.service
```

Add:
```ini
[Unit]
Description=Voice to RAG System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/voice-rag
Environment="PATH=/path/to/voice-rag/venv/bin"
ExecStart=/path/to/voice-rag/venv/bin/python api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

7. **Start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable voice-rag
sudo systemctl start voice-rag
```

8. **Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/voice-rag
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

9. **Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/voice-rag /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

10. **Set up SSL (Let's Encrypt):**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## Production Considerations

### Security

1. **Environment Variables:**
   - Never commit `.env` file
   - Use platform secrets management
   - Rotate API keys regularly

2. **CORS:**
   - Update `api.py` to restrict origins:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],  # Specific origins
       allow_credentials=True,
       allow_methods=["GET", "POST", "DELETE"],
       allow_headers=["*"],
   )
   ```

3. **Rate Limiting:**
   - Consider adding rate limiting for API endpoints
   - Use libraries like `slowapi`

4. **HTTPS:**
   - Always use HTTPS in production
   - Most platforms provide automatic HTTPS

### Performance

1. **Database:**
   - Consider PostgreSQL for production (instead of SQLite)
   - Use connection pooling

2. **Caching:**
   - Current implementation has basic caching
   - Consider Redis for distributed caching

3. **File Storage:**
   - Use cloud storage (S3, GCS) for uploaded files
   - Don't store files in container filesystem

4. **Monitoring:**
   - Add logging
   - Set up error tracking (Sentry)
   - Monitor API usage

### Scaling

1. **Horizontal Scaling:**
   - Use load balancer
   - Share database and vector store
   - Consider managed services

2. **Database:**
   - Use managed database service
   - Set up backups

3. **Vector Store:**
   - Consider managed vector database
   - Or use shared storage for ChromaDB

### Backup

1. **Database:**
   - Regular backups of `metadata.db`
   - Store backups off-server

2. **Vector Store:**
   - Backup `chroma_db/` directory
   - Regular snapshots

---

## Quick Deployment Checklist

- [ ] Set `OPENAI_API_KEY` environment variable
- [ ] Update CORS origins in `api.py`
- [ ] Test locally with Docker
- [ ] Choose deployment platform
- [ ] Set up domain (optional)
- [ ] Configure HTTPS
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test production deployment
- [ ] Update documentation

---

## Troubleshooting

### Common Issues

1. **Port already in use:**
   - Change `PORT` in `.env`
   - Or use different port mapping

2. **Database errors:**
   - Check file permissions
   - Ensure data directory exists

3. **Vector store errors:**
   - Check ChromaDB path
   - Ensure write permissions

4. **API key errors:**
   - Verify `OPENAI_API_KEY` is set
   - Check key is valid

### Getting Help

- Check logs: `docker-compose logs` or platform logs
- Verify environment variables
- Test API endpoint: `curl http://localhost:8000/health`
- Check database files exist

---

## Next Steps

After deployment:
1. Test all features
2. Monitor performance
3. Set up alerts
4. Configure backups
5. Update documentation

