# SSH Key Setup Guide

Complete guide for setting up SSH keys for secure repository access.

## 🔐 Overview

This repository uses SSH keys for secure Git operations. Follow this guide to set up SSH authentication for contributing to the project.

## 🔑 Generated SSH Key

A dedicated SSH key has been created for this repository:

**Key Details:**
- **Type**: ED25519 (modern, secure)
- **Comment**: sylectus-scraper-repo
- **Private Key**: `~/.ssh/sylectus_repo_key`
- **Public Key**: `~/.ssh/sylectus_repo_key.pub`

## 📋 Setup Instructions

### 1. Generate SSH Key (if needed)

```bash
# Generate new SSH key
ssh-keygen -t ed25519 -C "sylectus-scraper-repo" -f ~/.ssh/sylectus_repo_key -N ""

# Set correct permissions
chmod 600 ~/.ssh/sylectus_repo_key
chmod 644 ~/.ssh/sylectus_repo_key.pub
```

### 2. Add Public Key to GitHub

1. **Copy your public key**:
```bash
cat ~/.ssh/sylectus_repo_key.pub
```

2. **Add to GitHub**:
   - Go to https://github.com/settings/keys
   - Click "New SSH key"
   - Title: `Sylectus Scraper Repository Key`
   - Paste the public key content
   - Click "Add SSH key"

### 3. Configure Git Repository

```bash
# Set SSH URL for repository
git remote set-url origin git@github.com:Shawn5cents/API-SCRAPER.git

# Configure Git to use specific SSH key
git config --local core.sshCommand "ssh -i ~/.ssh/sylectus_repo_key"
```

### 4. Test SSH Connection

```bash
# Test GitHub SSH connection
ssh -T -i ~/.ssh/sylectus_repo_key git@github.com

# Expected response:
# Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

## 🔧 Usage

### Basic Git Operations

```bash
# Clone repository
git clone git@github.com:Shawn5cents/API-SCRAPER.git

# Pull latest changes
git pull origin main

# Push changes
git push origin main
```

### Verify Configuration

```bash
# Check remote URL
git remote -v

# Check SSH key configuration
git config --local core.sshCommand

# List SSH keys
ls -la ~/.ssh/
```

## 🛠 Troubleshooting

### Permission Denied

```bash
# Fix SSH key permissions
chmod 600 ~/.ssh/sylectus_repo_key
chmod 644 ~/.ssh/sylectus_repo_key.pub

# Check SSH agent
ssh-add -l
ssh-add ~/.ssh/sylectus_repo_key
```

### Key Not Found

```bash
# Regenerate SSH key
ssh-keygen -t ed25519 -C "sylectus-scraper-repo" -f ~/.ssh/sylectus_repo_key

# Re-add to GitHub (follow step 2 above)
```

### Connection Issues

```bash
# Debug SSH connection
ssh -vT -i ~/.ssh/sylectus_repo_key git@github.com

# Check GitHub status
curl -s https://kctbh9vrtdwd.statuspage.io/api/v2/status.json
```

## 🔒 Security Best Practices

### Key Management
- **Never share private keys** (`sylectus_repo_key`)
- **Use passphrase protection** for additional security
- **Rotate keys periodically** (every 6-12 months)
- **Remove old keys** from GitHub when no longer needed

### Access Control
- **Use dedicated keys** for different repositories
- **Limit key permissions** to specific repositories when possible
- **Monitor key usage** in GitHub settings

### Backup
```bash
# Backup SSH keys
cp ~/.ssh/sylectus_repo_key* ~/backup/ssh-keys/
```

## 📝 Current Repository Configuration

```bash
# Repository details
Remote URL: git@github.com:Shawn5cents/API-SCRAPER.git
SSH Key: ~/.ssh/sylectus_repo_key
Key Type: ED25519
Comment: sylectus-scraper-repo
```

## 🎯 Quick Reference

```bash
# Generate key
ssh-keygen -t ed25519 -C "sylectus-scraper-repo" -f ~/.ssh/sylectus_repo_key

# Copy public key
cat ~/.ssh/sylectus_repo_key.pub

# Configure Git
git config --local core.sshCommand "ssh -i ~/.ssh/sylectus_repo_key"

# Test connection
ssh -T -i ~/.ssh/sylectus_repo_key git@github.com
```

---

**🔐 Secure Repository Access**  
**✅ SSH Key Authentication**  
**🚀 Ready for Development**