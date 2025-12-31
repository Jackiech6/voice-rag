#!/bin/bash
# Quick script to push to GitHub
# Usage: ./QUICK_PUSH.sh YOUR_GITHUB_USERNAME REPO_NAME

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: ./QUICK_PUSH.sh YOUR_GITHUB_USERNAME REPO_NAME"
    echo "Example: ./QUICK_PUSH.sh johndoe voice-rag"
    exit 1
fi

USERNAME=$1
REPO_NAME=$2

echo "🚀 Setting up GitHub remote and pushing..."
echo ""

# Remove existing remote if it exists
git remote remove origin 2>/dev/null

# Add new remote
echo "Adding remote: https://github.com/$USERNAME/$REPO_NAME.git"
git remote add origin https://github.com/$USERNAME/$REPO_NAME.git

# Verify remote
echo ""
echo "Verifying remote:"
git remote -v

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ Done! Check your repo at: https://github.com/$USERNAME/$REPO_NAME"

