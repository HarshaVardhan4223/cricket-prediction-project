# 🏏 Cricket Prediction System - Getting Started Guide

## Quick Start (60 seconds)

### Prerequisites
- Python 3.10+
- Flask, Pandas, scikit-learn (see requirements below)
- Browser (Chrome, Firefox, Safari, Edge)

### Step 1: Navigate to Project
```powershell
cd e:\cricket-prediction-project\backend
```

### Step 2: Activate Virtual Environment (if not already)
```powershell
..\venv\Scripts\Activate.ps1
```

### Step 3: Start Flask Server
```powershell
python web_complete.py
```

**Expected Output**:
```
🌐 LOADING ENHANCED CRICKET ANALYSIS SYSTEM...
✅ All models loaded successfully
🔗 Open: http://localhost:5000
```

### Step 4: Open in Browser
Click or navigate to: `http://localhost:5000`

---

## 📱 Access All Pages

| Feature | URL | Purpose |
|---------|-----|---------|
| **Home** | `http://localhost:5000/` | Dashboard with all features |
| **Coach Dashboard** | `http://localhost:5000/coach-dashboard` | Intelligence reports (Knockouts, Readiness, Fatigue) |
| **Player Analysis** | `http://localhost:5000/player-analysis` | Compare players, view augmented insights |
| **Team Selector** | `http://localhost:5000/team-selector` | AI picks best 11 for a match |
| **Match Predictor** | `http://localhost:5000/match-predictor` | Predict match outcomes (73%+ accuracy) |

---

## 🎯 Typical Use Cases

### Case 1: Coach Needs to Select Tournament Squad
1. Open **Coach Dashboard** (`/coach-dashboard`)
2. View **"Knockout Specialists"** report → See elite big-game performers
3. Cross-check **"Readiness Status"** → Ensure no key players are fatigued
4. Go to **"Playing XI Selector"** → Get AI recommendations for different venues
5. Finalize squad based on insights

### Case 2: Player Comparison
1. Open **Player Analysis** (`/player-analysis`)
2. Select two players (e.g., Rohit Sharma vs Virat Kohli)
3. View side-by-side comparison:
   - Career stats (runs, average, strike rate)
   - **Highlight**: Main strength (e.g., "Elite big-game performer")
   - **Physiological**: Heart rate, HRV, mental toughness
   - **Pressure Handling**: Big-game probability rating
4. Make selection decision

### Case 3: Match-Specific Team Selection
1. Open **Playing XI Selector** (`/team-selector`)
2. Input: Match venue, Opposing team (optional)
3. System returns: Best 11 players + batting order
4. System has already considered: Player form, fatigue, readiness
5. Review and confirm XI

### Case 4: Match Outcome Prediction
1. Open **Match Predictor** (`/match-predictor`)
2. Select: Team A, Team B, Venue
3. Get: Predicted outcome with confidence score (73%+ accuracy)
4. Use for: Tournament planning, betting insights, strategy planning

---

## 📊 Understanding the Dashboard Reports

### Knockout Specialists
```
Shows: Players with Elite (80%+) big-game performance probability
Use for: Selecting players for knockout matches, death overs, pressure situations
Key metric: big_game_probability (Elite/High/Medium/Low)
```

### Readiness Status
```
Shows: Players sorted by HRV (Heart Rate Variability) and ANS stability
Use for: Rotation planning, injury prevention, workload management
Key metric: readiness (High/Moderate/Low)
High = ANS stable, player fresh
Low = Player may need rest
```

### Fatigue Risk
```
Shows: Players with high accumulated fatigue
Use for: Identifying who needs rest, preventing burnout
Key metric: fatigue_risk (Low/Medium/High)
High = Significant fatigue, prioritize rest
```

---

## 🔧 Troubleshooting

### Issue: "Port 5000 already in use"
**Solution**: Kill the existing process
```powershell
Get-Process python | Where-Object { $_.Name -like "*web_complete*" } | Stop-Process -Force
python web_complete.py
```

### Issue: "Module not found" error
**Solution**: Install dependencies
```powershell
pip install flask pandas scikit-learn openpyxl
```

### Issue: "Models not found"
**Solution**: Ensure `models/` folder exists with `.pkl` files
```powershell
ls models/
# Should show: ultimate_ensemble_model.pkl, team_statistics.pkl
```

### Issue: "JSON file not found"
**Solution**: Ensure augmented data file exists
```powershell
ls data/global_cricket_players_fixed_augmented_rich_v2.json
```

### Issue: Slow initial startup
**Solution**: Normal - ML models load on first run (~30-60 seconds)
- Subsequent requests will be fast
- Debug mode enabled for development

---

## 📈 Key Features Explained

### Player Highlights
**What**: One-line summary of player's main strength
**Example**: "Strong big-game performer — Elite (80%+ chance)"
**Where**: Displayed under player name in Analysis page
**Use**: Quick decision-making for coaches

### Augmented Insights
**What**: Enriched player data with physiological + pressure metrics
**Fields**:
- Heart rate + HRV (physiological)
- Big-game probability (pressure handling)
- Mental toughness rating (psychology)
- ANS stability (readiness)
- Coach notes (qualitative assessment)
**Where**: Displayed in player cards and analysis pages

### Fatigue & Readiness Integration
**What**: XI selector penalizes players by form
**High Fatigue**: -15% to player selection score
**Low Readiness**: -10% to player selection score
**Use**: System automatically considers recovery in team selection

### Model Accuracy
**73%+ accuracy** means out of 100 predictions:
- ~73 predictions are correct
- ~27 are incorrect
- Confidence based on venue, team strength, recent form

---

## 💾 Data Management

### Add New Players
Edit `data/augment_players_with_physiology.py`:
```python
python augment_players_with_physiology.py --merge-csv data/new_players.csv --populate-defaults
```

### Update Augmented Data
```python
python augment_players_with_physiology.py --derive-insights-rich
```

### Backup Database
```powershell
Copy-Item data/global_cricket_players_fixed_augmented_rich_v2.json data/backup_$(Get-Date -Format yyyyMMdd).json
```

---

## 🎨 Customization

### Change Colors
Edit `frontend/templates/index.html` (CSS section):
```css
.feature-card:hover {
    background: linear-gradient(145deg, #28a745 0%, #f8f9fa 100%); /* Green color */
}
```

### Add New Feature Page
1. Create HTML file: `frontend/templates/new_feature.html`
2. Add route in `backend/web_complete.py`:
   ```python
   @app.route('/new-feature')
   def new_feature():
       return render_template('new_feature.html')
   ```
3. Add card in `index.html`:
   ```html
   <div class="feature-card" onclick="window.location='/new-feature'">
   ```

### Change Port
In `backend/web_complete.py`, change:
```python
app.run(debug=True, port=5001)  # Change 5000 to your port
```

---

## 📚 File Reference

| File | Purpose |
|------|---------|
| `backend/web_complete.py` | Flask server, all API endpoints, data loading |
| `frontend/templates/index.html` | Home page with feature cards |
| `frontend/templates/coach_dashboard.html` | NEW - Coach intelligence reports |
| `frontend/templates/player_analysis.html` | Player stats, highlights, augmented data |
| `frontend/templates/team_selector.html` | AI team selection interface |
| `frontend/templates/match_predictor.html` | Match outcome prediction |
| `data/global_cricket_players_fixed_augmented_rich_v2.json` | 260 players with augmented insights |
| `data/augment_players_with_physiology.py` | Data augmentation script |
| `models/ultimate_ensemble_model.pkl` | ML prediction model (73% accuracy) |
| `models/team_statistics.pkl` | Team performance metrics |

---

## 🔌 API Quick Reference

### Get Coach Reports
```bash
# Knockout specialists
curl "http://localhost:5000/api/coach-reports?type=knockouts&limit=10"

# Readiness status
curl "http://localhost:5000/api/coach-reports?type=readiness&limit=10"

# Fatigue risk
curl "http://localhost:5000/api/coach-reports?type=fatigue&limit=10"
```

### Get Player Insights
```bash
# Single player
curl "http://localhost:5000/api/player-insights/Rohit%20Sharma"

# All players with insights
curl "http://localhost:5000/api/players-with-insights"
```

### Select Playing XI
```bash
# POST request with JSON body
curl -X POST "http://localhost:5000/api/select-xi" \
  -H "Content-Type: application/json" \
  -d '{"venue": "MCG", "opposition": "Australia"}'
```

---

## ✅ Verification Checklist

- [ ] Flask server running on `http://localhost:5000`
- [ ] Home page loads with 4 feature cards (including Coach Dashboard)
- [ ] Coach Dashboard loads with 3 report cards (Knockouts, Readiness, Fatigue)
- [ ] Player Analysis shows augmented insights + highlights
- [ ] Playing XI Selector returns 11 players with batting order
- [ ] Match Predictor gives outcome prediction with confidence
- [ ] All API endpoints responding (test one with curl)
- [ ] No console errors in browser Developer Tools

---

## 📞 Support Resources

- **This File**: Getting started + troubleshooting
- **COACH_DASHBOARD_README.md**: Coach dashboard features + workflows
- **SYSTEM_COMPLETION_SUMMARY.md**: Complete project overview + checklist
- **PLAYER_INSIGHTS_README.md**: Data augmentation details

---

## 🚀 Next Steps

**Immediate**:
1. ✅ Run server: `python web_complete.py`
2. ✅ Open home page: `http://localhost:5000`
3. ✅ Explore Coach Dashboard: `http://localhost:5000/coach-dashboard`

**Extended Usage**:
1. Compare different players to understand insights
2. Use XI Selector for different venues
3. Check prediction accuracy over time
4. Export top candidates CSV for reporting

**Customization** (Optional):
1. Add new players to database
2. Adjust fatigue/readiness penalties in XI selector
3. Customize dashboard colors and styling
4. Integrate with external cricket data APIs

---

## 📋 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.8 | 3.10+ |
| RAM | 2 GB | 4 GB |
| Disk | 500 MB | 1 GB |
| Browser | Chrome 90+ | Latest |
| Network | 1 Mbps | 10 Mbps |

---

**Status**: ✅ READY TO USE
**Created**: December 28, 2024
**Version**: 2.0

Good luck with your cricket analytics journey! 🏏
