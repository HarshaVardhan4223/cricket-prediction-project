# Player Physiological Insights & Performance Analysis System

## Overview

This system augments cricket player data with detailed physiological profiles, pressure-handling mechanics, mental toughness ratings, and performance predictions. It enables coaches and analysts to understand how players perform under pressure and what their physiological readiness indicators are.

## What's New

### 1. **Augmented Player JSON with Rich Insights** (`data/global_cricket_players_fixed_augmented_rich_v2.json`)

Every player now has a `player_insights` block containing:

#### Physiological Profile
- **Resting Heart Rate (RHR)**: Range in BPM, derived from age and fitness level
- **Optimal In-Game HR**: Target HR range during peak performance
- **HRV Readiness Level**: "High (ANS Stability)", "Moderate-High", or "Moderate" based on match experience
- **HRV Score Range**: Heart Rate Variability score range indicating nervous system balance
- **Recovery Speed**: Elite, Good, or Moderate based on age and role
- **Pressure Zone Performance**: How well the player handles high arousal (Inverted-U relationship)
- **Stress Management Technique**: Breathing and mindfulness strategies

#### Pressure Handling Mechanics
- **Situation Response**: Narrative describing physiological stability in high-leverage moments
- **Clutch Play Style**: Approach to pressure chases (calculative risk, etc.)
- **Mental Toughness Rating**: 0-10 scale, derived from career batting/bowling averages
- **Leadership Under Fire**: Leadership style during pressure
- **Routine Strength**: Pre-action ritual effectiveness

#### Wearable Tech Usage
- **Device**: WHOOP / Oura / Ultrahuman
- **Daily Monitoring**: Metrics tracked (HRV, Sleep, Strain)
- **Readiness Prediction**: Threshold for peak performance

#### Performance Prediction
- **Big Game Probability**: Elite, High, Good, or Moderate chance of impactful performance in knockouts
- **Fatigue Risk**: Low or Moderate-High based on age, role, and workload
- **Injury Risk**: Low or Moderate based on playing style

#### Coach's Note
- Personalized recommendations for HRV monitoring and workload management

### 2. **Backend API Endpoints**

Two new Flask endpoints added to `backend/web_complete.py`:

#### GET `/api/player-insights/<player_name>`
Returns full player details + `player_insights` block

**Example Request:**
```
GET http://localhost:5000/api/player-insights/Rohit%20Sharma
```

**Response:**
```json
{
  "success": true,
  "player": {
    "name": "Rohit Sharma",
    "country": "India",
    "age": 38,
    "role": "Opening Batsman / Captain",
    "career_statistics": {...}
  },
  "player_insights": {
    "physiological_profile": {...},
    "pressure_handling_mechanics": {...},
    "wearable_tech_usage": {...},
    "performance_prediction": {...},
    "coach_note": "..."
  }
}
```

#### GET `/api/players-with-insights?limit=100&country=India`
Returns list of players with insights summary

**Response:**
```json
{
  "success": true,
  "count": 50,
  "players": [
    {
      "name": "Rohit Sharma",
      "country": "India",
      "age": 38,
      "role": "Opening Batsman / Captain",
      "is_young_star": "No",
      "insights_summary": {
        "mental_toughness_rating": "9.9/10",
        "big_game_probability": "Elite (80%+...)",
        "recovery_speed": "Good (28-35 BPM drop in 60s)",
        "hrv_readiness_level": "High (ANS Stability)",
        "fatigue_risk": "Low"
      }
    },
    ...
  ]
}
```

### 3. **Interactive Frontend Page** (`frontend/templates/player_insights.html`)

A responsive, single-page application with:
- **Real-time player search** by name and country
- **Player directory listing** with quick insights summary
- **Detailed player insights dashboard** showing:
  - Career statistics and personal info
  - Physiological profile with HR ranges
  - Mental toughness and pressure handling breakdown
  - Wearable technology readiness indicators
  - Performance prediction with risk assessment
  - Coach's personalized notes

**Access via:** `http://localhost:5000/player-insights`

### 4. **Data Generation Script** (`data/augment_players_with_physiology.py`)

Standalone Python script to generate/merge player insights:

**Usage:**
```bash
# Generate rich narrative insights from player stats
python augment_players_with_physiology.py \
  --input data/global_cricket_players_fixed.json \
  --output data/global_cricket_players_fixed_augmented_rich_v2.json \
  --derive-insights-rich

# Merge Gemini AI estimates from a CSV
python augment_players_with_physiology.py \
  --input data/global_cricket_players_fixed.json \
  --output data/global_cricket_players_fixed_augmented.json \
  --merge-csv data/gemini_player_insights.csv \
  --id-key player_id
```

**Supported CSV format (dot-separated nested columns):**
```csv
player_id,player_insights.physiological_profile.resting_heart_rate_bpm,player_insights.pressure_handling_mechanics.mental_toughness_rating,...
Rohit Sharma,50-54,9.8,...
```

## How Insights Are Derived

The system uses **population percentiles** and **player-specific heuristics** to generate realistic, varied insights for each player:

1. **Physiological Profile**
   - Resting HR: Derived from age and match-experience percentile
   - Optimal HR: Higher for fast bowlers, lower for specialist batsmen
   - HRV Readiness: Based on experience level and match frequency
   - Recovery Speed: Inferred from age, role, and career workload

2. **Mental Toughness Rating**
   - Calculated from ODI/IPL averages and T20I strike rates
   - Scale: 4.0 (low experience) to 10.0 (elite performers)
   - Example: Shubman Gill (high average, young star) → 10/10

3. **Big Game Probability**
   - "Elite (80%+)" if mental_toughness ≥ 8.5
   - "High (60-80%)" if mental_toughness ≥ 7.0
   - "Moderate (40-60%)" otherwise

4. **Performance Prediction**
   - Fatigue Risk: Higher for fast bowlers >30 years or >400 career matches
   - Injury Risk: Low for style-based players, moderate for physical players

## File Structure

```
cricket-prediction-project/
├── data/
│   ├── global_cricket_players_fixed.json (original)
│   ├── global_cricket_players_fixed_augmented_rich_v2.json (✨ NEW - with insights)
│   ├── global_cricket_players_fixed.backup.json (backup)
│   └── augment_players_with_physiology.py (✨ NEW - generator script)
├── backend/
│   └── web_complete.py (✨ UPDATED - new API endpoints)
└── frontend/
    └── templates/
        └── player_insights.html (✨ NEW - interactive dashboard)
```

## Running the System

### 1. Start Backend Server
```bash
cd backend
python web_complete.py
# Server runs on http://localhost:5000
```

### 2. Open Dashboard
Navigate to: **http://localhost:5000/player-insights**

### 3. Search & View Insights
- Type player name or filter by country
- Click player to view detailed insights
- Review mental toughness, big-game probability, recovery speed, coach notes

## Future Enhancements

1. **Real Sensor Data Integration**
   - Connect to WHOOP / Fitbit / Oura APIs to pull real HRV, sleep, strain data
   - Update insights dynamically based on current readiness

2. **Gemini AI Estimates**
   - Export this CSV template to Gemini AI for expert estimates
   - Merge AI-generated values to replace heuristics

3. **Time-Series Analysis**
   - Track HRV trends over tours
   - Predict form dips based on recovery metrics

4. **Team Selection Optimization**
   - Use insights to recommend XI based on venue, opposition, and player readiness
   - Workload balancing recommendations

## API Response Examples

### Get Rohit Sharma's Full Insights
```bash
curl http://localhost:5000/api/player-insights/Rohit%20Sharma
```

### List Top 50 Indian Players with Insights
```bash
curl "http://localhost:5000/api/players-with-insights?limit=50&country=India"
```

## Notes

- All insights are **heuristic-derived** from available stats and player metadata
- Physiological thresholds (HR ranges, HRV scores) are **sport science-informed approximations**
- Real sensor data (WHOOP, Fitbit, Garmin) would significantly improve accuracy
- Mental toughness ratings are derived from career performance; they don't account for recent form or external factors
- The system is designed for **coach decision-making support**, not medical diagnosis

## Support

For updates to player insights, either:
1. **Edit the augmented JSON** directly and reload
2. **Export to Gemini**, get AI estimates, and merge via CSV
3. **Integrate real wearable APIs** for continuous updates

---

**Generated with:** Python 3.10 | Flask 3.1 | Pandas 2.3 | JSON-based persistence
