# Push to GitHub - Step by Step

## Step 1: Create GitHub Repository First

**IMPORTANT:** You must create the repository on GitHub FIRST before pushing.

1. Go to https://github.com and sign in
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Fill in:
   - **Repository name:** `voice-rag` (or any name you prefer)
   - **Description:** "Voice to RAG System - Document Q&A with voice input"
   - **Visibility:** Choose Public or Private
   - **DO NOT** check "Add a README file"
   - **DO NOT** check "Add .gitignore"
   - **DO NOT** check "Choose a license"
5. Click **"Create repository"**

## Step 2: Copy Your Repository URL

After creating the repo, GitHub will show you a page with setup instructions. You'll see a URL like:

- HTTPS: `https://github.com/YOUR_USERNAME/voice-rag.git`
- SSH: `git@github.com:YOUR_USERNAME/voice-rag.git`

**Copy this URL** - you'll need it in the next step.

## Step 3: Push from Your Computer

Run these commands in your terminal (replace `YOUR_USERNAME` and `voice-rag` with your actual values):

```bash
cd /Users/chenjackie/Desktop/WRDS

# Add GitHub as remote (use the URL from Step 2)
git remote add origin https://github.com/YOUR_USERNAME/voice-rag.git

# Verify it was added
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

## If You Get Authentication Errors

### Option A: Use Personal Access Token (Recommended)

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name like "Voice RAG Deployment"
4. Select scopes: Check `repo` (full control of private repositories)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)
7. When pushing, use the token as your password:
   ```bash
   git push -u origin main
   # Username: your_github_username
   # Password: paste_your_token_here
   ```

### Option B: Use SSH (Alternative)

1. Generate SSH key (if you don't have one):
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```
2. Add to GitHub:
   - Copy: `cat ~/.ssh/id_ed25519.pub`
   - GitHub → Settings → SSH and GPG keys → New SSH key
   - Paste and save
3. Use SSH URL:
   ```bash
   git remote set-url origin git@github.com:YOUR_USERNAME/voice-rag.git
   git push -u origin main
   ```

## Verify It Worked

1. Go to https://github.com/YOUR_USERNAME/voice-rag
2. You should see all your files
3. You should see 53 files in the repository

## Troubleshooting

### "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/voice-rag.git
```

### "repository not found"
- Make sure you created the repo on GitHub first
- Check the repository name matches exactly
- Make sure you're using the correct username

### "authentication failed"
- Use Personal Access Token (see Option A above)
- Or set up SSH keys (see Option B above)

### "refusing to merge unrelated histories"
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

