# Getting Started — Run this project on your Windows laptop

This guide shows the exact commands to set up and run the cricket analytics project on a teammate's Windows laptop (PowerShell). Keep this file next to the project root folder.

Prerequisites
- Python 3.10+ installed and on PATH
- Git (if cloning the repo)

Quick steps (copy & paste into PowerShell from the project root `e:\cricket-prediction-project`)

1) Allow PowerShell scripts (one-time, run as user):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

2) Create & activate virtual environment, install dependencies:
```powershell
cd e:\cricket-prediction-project
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3) Verify required data and models are present (these must be in the repo):
- `data/global_cricket_players_fixed_augmented_rich_v2.json`
- `models/ultimate_ensemble_model.pkl`
- `models/team_statistics.pkl`

If any is missing, ask the project owner to copy them into the `data/` and `models/` folders before proceeding.

4) (Optional) Rebuild augmented data (only if you need to regenerate it):
```powershell
python .\data\augment_players_with_physiology.py --input .\data\global_cricket_players_fixed.json --output .\data\global_cricket_players_fixed_augmented_rich_v2.json --derive-insights-rich
```
This may take a few minutes.

5) Start the Flask server:
```powershell
cd backend
python web_complete.py
```
The console should show the models and data being loaded and then "Open: http://localhost:5000".

6) Open the app in a browser:
- Home: `http://localhost:5000/`
- Coach Dashboard: `http://localhost:5000/coach-dashboard`

Test a backend endpoint (PowerShell example):
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/coach-reports?type=knockouts&limit=3" -UseBasicParsing
```

Common issues & fixes
- "Port 5000 already in use": Kill existing process or change port
  ```powershell
  Get-Process -Name python | Where-Object { $_.Path -like '*web_complete.py*' } | Stop-Process -Force
  # or edit backend/web_complete.py to change app.run port
  ```
- Missing Python packages: re-run `pip install -r requirements.txt`
- Models or data missing: copy `models/*.pkl` and `data/*.json` from main machine
- Slow startup: model loading may take 20–60 seconds on first run

Tips for sharing
- Zip the entire project folder (include `models/` and `data/`) or use shared cloud storage
- Include `start_project.ps1` and this `GETTING_STARTED_TEAMMATE.md` at the root so teammates can run with one script

If you want, I can also:
- Create an automated zip builder that includes only required data/models
- Add a small `docker` config so the project runs identically on any machine

