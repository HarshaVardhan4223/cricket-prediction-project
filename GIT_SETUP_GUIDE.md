# Teammate: How to Clone & Run This Project

Your teammate can get started with the project in **two simple steps** using Git.

## Prerequisites
- Python 3.10+
- Git
- Internet connection (to clone)

## Step 1: Clone the Repository
Replace `<YOUR_GITHUB_REPO_URL>` with the actual GitHub URL.

```powershell
git clone <YOUR_GITHUB_REPO_URL>
cd cricket-prediction-project
```

## Step 2: Run the Start Script
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\start_project.ps1
```

The script will:
1. Create a virtual environment (`.venv`)
2. Install all Python dependencies (`pip install -r requirements.txt`)
3. Start the Flask server on `http://localhost:5000`

**Done!** Open the browser to `http://localhost:5000`

---

## What to Expect

✅ **Console output shows**:
- Model loading: "✅ Match Predictor Model Loaded"
- Data loading: "✅ Players Database Loaded (260 players)"
- Server running: "Open: http://localhost:5000"

✅ **Then open your browser**:
- Home: `http://localhost:5000/`
- Coach Dashboard: `http://localhost:5000/coach-dashboard`

---

## Troubleshooting

**Q: Script execution is blocked**
A: Run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Q: Port 5000 is already in use**
A: Kill the process or change the port in `backend/web_complete.py`:
```powershell
Get-Process -Name python | Where-Object { $_.Path -like '*web_complete.py*' } | Stop-Process -Force
```

**Q: Module not found errors**
A: Ensure venv is activated and run pip install again:
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Q: Models or data missing**
A: The repo includes all required files (`models/*.pkl`, `data/*.json`).
If cloning from GitHub, they should be included. If not, ask the repo owner.

---

## GitHub Setup (For Project Owner)

If you don't have a GitHub repo yet:

1. **Create a new repo on GitHub** (e.g., `cricket-prediction-project`)
2. **Push the local Git repo**:
```powershell
git remote add origin <YOUR_GITHUB_REPO_URL>
git branch -M main
git push -u origin main
```

3. **Share the repo URL** with teammates (copy from GitHub's green "Code" button)

---

**That's it!** Your teammates can now clone and run with one command. 🏏
