# 🚀 Push to GitHub (Option A) — Complete Instructions

Your Git repo is **ready to push**. Follow these exact steps to share on GitHub.

## Step 1: Create a GitHub Repository

1. Go to **https://github.com/new**
2. **Repository name**: `cricket-prediction-project`
3. **Description**: "Cricket prediction platform with coach dashboard and ML models"
4. **Visibility**: Public or Private (your choice)
5. **Do NOT initialize with README** (we already have one)
6. Click **"Create repository"**

## Step 2: Copy Your Repo URL

After creating, GitHub shows you commands. **Copy the HTTPS URL** (looks like):
```
https://github.com/YOUR_USERNAME/cricket-prediction-project.git
```

## Step 3: Push to GitHub (Run These Commands)

Replace `YOUR_USERNAME` with your actual GitHub username.

```powershell
cd e:\cricket-prediction-project

git remote add origin https://github.com/YOUR_USERNAME/cricket-prediction-project.git
git branch -M main
git push -u origin main
```

**What these do:**
- `git remote add origin` — Links your local repo to GitHub
- `git branch -M main` — Renames master branch to main (GitHub standard)
- `git push -u origin main` — Uploads all commits and sets upstream

## Step 4: Verify on GitHub

1. Refresh **https://github.com/YOUR_USERNAME/cricket-prediction-project**
2. You should see:
   - All folders: `backend/`, `frontend/`, `data/`, `models/`, etc.
   - All files: `README.md`, `requirements.txt`, `start_project.ps1`, etc.
   - Commit history showing "Initial commit..." and "Add GitHub setup guide..."

## Step 5: Share with Teammates

Give them this **one-liner**:

```powershell
git clone https://github.com/YOUR_USERNAME/cricket-prediction-project.git ; cd cricket-prediction-project ; .\start_project.ps1
```

Or just share the repo URL and point them to `GIT_SETUP_GUIDE.md` in the repo.

---

## Troubleshooting

**Q: "fatal: destination path 'cricket-prediction-project' already exists"**
A: You're in the repo folder. Run from parent directory:
```powershell
cd e:\
git clone https://github.com/YOUR_USERNAME/cricket-prediction-project.git
```

**Q: Git push fails with authentication**
A: You need to authenticate with GitHub:
- **Option 1**: Use GitHub CLI (recommended)
  ```powershell
  gh auth login
  ```
- **Option 2**: Use Personal Access Token (PAT)
  - Create PAT at https://github.com/settings/tokens
  - Use token as password when prompted

**Q: "remote origin already exists"**
A: Change remote URL:
```powershell
git remote set-url origin https://github.com/YOUR_USERNAME/cricket-prediction-project.git
```

---

## Summary

**You:**
1. Create repo on GitHub
2. Copy HTTPS URL
3. Run 3 git commands (remote, branch, push)
4. Share the GitHub URL with teammates

**Teammates:**
1. Clone repo: `git clone <URL>`
2. Run: `.\start_project.ps1`
3. Open: `http://localhost:5000`

**Project shared!** 🎉
