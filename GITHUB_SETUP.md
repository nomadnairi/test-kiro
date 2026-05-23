# GitHub Repository Setup Guide

This guide will help you set up the CyberIntel Platform repository on GitHub with all features enabled.

## 📋 Prerequisites

- GitHub account
- Git installed locally
- Repository cloned locally

## 🚀 Initial Setup

### 1. Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the **"+"** icon in the top right → **"New repository"**
3. Fill in the details:
   - **Repository name**: `cyberintel-platform` (or your preferred name)
   - **Description**: "Enterprise-grade AI-powered cyber intelligence platform"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README (we already have one)
4. Click **"Create repository"**

### 2. Push Your Code

```bash
# Navigate to your project directory
cd cyberintel-platform

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: CyberIntel Platform"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/cyberintel-platform.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 🌐 Enable GitHub Pages

### Option 1: Using GitHub UI

1. Go to your repository on GitHub
2. Click **"Settings"** tab
3. Scroll down to **"Pages"** in the left sidebar
4. Under **"Source"**, select:
   - **Source**: Deploy from a branch
   - **Branch**: `main`
   - **Folder**: `/docs`
5. Click **"Save"**
6. Wait a few minutes for deployment
7. Your documentation will be available at: `https://YOUR_USERNAME.github.io/cyberintel-platform/`

### Option 2: Using GitHub Actions (Recommended)

The repository includes a GitHub Actions workflow (`.github/workflows/pages.yml`) that automatically deploys documentation.

1. Go to your repository on GitHub
2. Click **"Settings"** tab
3. Click **"Pages"** in the left sidebar
4. Under **"Source"**, select:
   - **Source**: GitHub Actions
5. The workflow will automatically deploy on every push to `main` that modifies the `docs/` folder

## ⚙️ Enable GitHub Actions

1. Go to your repository on GitHub
2. Click **"Actions"** tab
3. If prompted, click **"I understand my workflows, go ahead and enable them"**
4. The CI workflow (`.github/workflows/setup.yml`) will run automatically on:
   - Every push
   - Every pull request
   - Manual trigger

## 🔒 Configure Repository Settings

### Branch Protection (Recommended for teams)

1. Go to **Settings** → **Branches**
2. Click **"Add rule"**
3. Branch name pattern: `main`
4. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
5. Click **"Create"**

### Issue Templates

Issue templates are already configured in `.github/ISSUE_TEMPLATE/`:
- `bug_report.md` - For bug reports
- `feature_request.md` - For feature requests
- `integration_request.md` - For OSINT integration requests

They will appear automatically when users create new issues.

### Pull Request Template

The PR template is configured in `.github/PULL_REQUEST_TEMPLATE.md` and will appear automatically when creating pull requests.

## 🏷️ Add Topics

Add topics to help others discover your repository:

1. Go to your repository on GitHub
2. Click the **⚙️ gear icon** next to "About"
3. Add topics:
   - `osint`
   - `cybersecurity`
   - `threat-intelligence`
   - `ai`
   - `reconnaissance`
   - `graph-database`
   - `neo4j`
   - `typescript`
   - `python`
   - `docker`
4. Click **"Save changes"**

## 📝 Update README Badges

Replace `YOUR_USERNAME` in `README.md` with your actual GitHub username:

```markdown
[![Build Status](https://github.com/YOUR_USERNAME/cyberintel-platform/workflows/CI/badge.svg)](https://github.com/YOUR_USERNAME/cyberintel-platform/actions)
```

## 🔐 Add Secrets (for CI/CD)

If you plan to add automated deployments or tests that require API keys:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Add secrets as needed (e.g., `DOCKER_USERNAME`, `DOCKER_PASSWORD`)

## 📊 Enable Discussions (Optional)

1. Go to **Settings**
2. Scroll to **"Features"**
3. Check **"Discussions"**
4. Click **"Set up discussions"**

## 🎯 Enable Projects (Optional)

1. Go to **Settings**
2. Scroll to **"Features"**
3. Check **"Projects"**

## 📢 Create First Release

1. Go to **"Releases"** on the right sidebar
2. Click **"Create a new release"**
3. Click **"Choose a tag"** → Type `v1.0.0` → Click **"Create new tag"**
4. **Release title**: `v1.0.0 - Initial Release`
5. **Description**: Add release notes
6. Click **"Publish release"**

## ✅ Verification Checklist

After setup, verify:

- [ ] Repository is accessible
- [ ] README displays correctly with badges
- [ ] GitHub Pages is deployed and accessible
- [ ] GitHub Actions workflows are enabled and passing
- [ ] Issue templates appear when creating issues
- [ ] PR template appears when creating pull requests
- [ ] Topics are added to repository
- [ ] License file is present
- [ ] Contributing guidelines are accessible

## 🔗 Share Your Repository

Your repository is now ready! Share it:

- **Repository URL**: `https://github.com/YOUR_USERNAME/cyberintel-platform`
- **Documentation**: `https://YOUR_USERNAME.github.io/cyberintel-platform/`
- **Clone command**: `git clone https://github.com/YOUR_USERNAME/cyberintel-platform.git`

## 🆘 Troubleshooting

### GitHub Pages not deploying

1. Check **Settings** → **Pages** for error messages
2. Ensure `docs/index.html` exists
3. Wait 5-10 minutes after enabling Pages
4. Check **Actions** tab for workflow status

### GitHub Actions failing

1. Go to **Actions** tab
2. Click on the failed workflow
3. Review error logs
4. Common issues:
   - Missing dependencies in workflow file
   - Incorrect Node.js/Python versions
   - Permission issues

### Badges not showing

1. Ensure workflows have run at least once
2. Replace `YOUR_USERNAME` with actual username
3. Check workflow names match badge URLs

## 📚 Additional Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [About Issue Templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)

---

**Need help?** Open an issue or check the [CONTRIBUTING.md](CONTRIBUTING.md) guide.
