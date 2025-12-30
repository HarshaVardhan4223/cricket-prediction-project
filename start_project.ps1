# PowerShell script to set up and run the Cricket Prediction project on Windows
# Run in project root: e:\cricket-prediction-project

# If PowerShell script execution is blocked, run as administrator or set:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 1) Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 3) Ensure required data and models are present
# - data/global_cricket_players_fixed_augmented_rich_v2.json
# - models/ultimate_ensemble_model.pkl
# - models/team_statistics.pkl
# If you don't have augmented JSON, run the augmentation script (optional):
# python .\data\augment_players_with_physiology.py --input .\data\global_cricket_players_fixed.json --output .\data\global_cricket_players_fixed_augmented_rich_v2.json --derive-insights-rich

# 4) Start the Flask server
cd backend
python web_complete.py

# Note: If port 5000 is in use, change the port in web_complete.py or run:
# python web_complete.py --port 5001

# 5) Open the app in browser: http://localhost:5000/

# Troubleshooting hints are in GETTING_STARTED_TEAMMATE.md
