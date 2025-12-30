# 🏏 Coach's Quick Reference Card

## 📱 Access Your Dashboard

**Open**: `http://localhost:5000/coach-dashboard`

---

## 🎯 Three Key Reports at a Glance

### 1️⃣ KNOCKOUT SPECIALISTS
**See**: Players who perform best under pressure
**Use**: Select for knockout matches, death overs
**Look for**: "Elite (80%+)" tag
**Examples**: Rohit Sharma, Shubman Gill, KL Rahul

### 2️⃣ READINESS STATUS
**See**: Player recovery & freshness levels
**Use**: Plan rotation, prevent injuries
**High Readiness** = Ready for action
**Low Readiness** = Needs rest
**Key metric**: HRV (Heart Rate Variability)

### 3️⃣ FATIGUE RISK
**See**: Players carrying accumulated fatigue
**Use**: Identify who needs rest
**High Risk** = Prioritize rotation next match
**Medium Risk** = Monitor closely
**Low Risk** = Fresh, good for intensive play

---

## ⚡ Quick Actions

| Need | Go To | Action |
|------|-------|--------|
| **Select Tournament Squad** | Coach Dashboard → Knockouts | Pick elite big-game performers |
| **Check Player Recovery** | Coach Dashboard → Readiness | Ensure key players are fresh |
| **Plan Rotation** | Coach Dashboard → Fatigue | Rest high-fatigue players |
| **Compare Two Players** | Player Analysis | View side-by-side stats + highlights |
| **Get AI Team Picks** | Playing XI Selector | Input venue, get best 11 |
| **Predict Match Outcome** | Match Predictor | Check prediction before fixture |

---

## 📊 Understanding Player Metrics

### Big-Game Probability
```
🟢 Elite (80%+)     → Thrives under pressure
🟢 High (60-80%)    → Elevates performance
🟡 Medium (40-60%)  → Normal regardless
🔴 Low (<40%)       → Struggles in pressure
```

### Readiness Status
```
🟢 High    → ANS Stable, Player Fresh
🟡 Moderate → Manageable, Monitor
🔴 Low     → Fatigued, Needs Rest
```

### Fatigue Risk
```
🟢 Low     → Fresh, High Intensity OK
🟡 Medium  → Manageable, Watch
🔴 High    → Significant, Prioritize Rest
```

---

## 🎓 Typical Day Scenarios

### Scenario 1: Before Tournament
1. Open **Coach Dashboard**
2. Check **Knockouts** → See elite performers
3. Check **Readiness** → Ensure no key player fatigue
4. Go **XI Selector** → Get AI picks for first match
5. ✅ Finalize squad

### Scenario 2: Mid-Tournament (Injury/Fatigue)
1. Open **Coach Dashboard**
2. Check **Fatigue Risk** → See who needs rest
3. Go **XI Selector** → System penalizes fatigued players, suggests alternatives
4. ✅ Select fresh XI

### Scenario 3: Scouting New Player
1. Open **Player Analysis**
2. Search player name
3. View **Highlights** → "Strong big-game performer" etc
4. Compare with similar player → Side-by-side view
5. ✅ Make recruitment decision

---

## 🔢 Dashboard Numbers Explained

### "Elite (80%+ chance)"
Means: Out of 100 knockout matches, this player performs at elite level ~80+ times

### "High Readiness / ANS Stability"
Means: Heart rate variability shows nervous system is calm and stable = ready to play

### "High Fatigue"
Means: Accumulated match stress, training load, travel = needs rest to recover

### "Batting Avg 45.2"
Means: Over last 5 matches, player averaged 45.2 runs per game

---

## 💡 Pro Tips for Coaches

✅ **Before Tournament**: Use Knockout Report to identify tournament specialists
✅ **During Tournament**: Check Fatigue Report before each match to plan rotation
✅ **For Motivation**: Show player their "Elite" status to boost confidence
✅ **For Strategy**: Use readiness levels to determine intensity of training
✅ **For Planning**: Pair high-fatigue players with fresh alternatives

---

## 🚨 Warning Signs

🔴 **All top 3 players showing High Fatigue** → Risk of injury spike
🔴 **Readiness drops suddenly** → Check for illness/overtraining
🔴 **XI Selector suggesting unusual picks** → Fatigue/readiness penalties at play

---

## ⚙️ System Navigation

```
HOME PAGE (http://localhost:5000/)
    ├── Coach Dashboard ← You are here! 🎯
    ├── Player Analysis
    ├── Team Selector
    └── Match Predictor
```

---

## 📞 Quick Support

| Issue | Solution |
|-------|----------|
| **Page won't load** | Refresh browser or restart server |
| **Data looks old** | Server auto-updates from database on startup |
| **Player missing** | Database has 260 players - check spelling |
| **Slow response** | First load takes ~30s as models initialize |

---

## ✅ Checklist for Match Day

- [ ] Opened Coach Dashboard
- [ ] Reviewed Knockout Specialists for opposition
- [ ] Checked Readiness of key players
- [ ] Reviewed Fatigue of recent players
- [ ] Used XI Selector for match-specific recommendations
- [ ] Compared opposition players in Player Analysis
- [ ] Checked Match Predictor for confidence level
- [ ] Finalized 11-player squad
- [ ] Ready for match!

---

## 🎯 Key Takeaways

1. **Three Reports** = Knockouts, Readiness, Fatigue
2. **One Goal** = Help you select best team with data
3. **Three Metrics** = Big-game probability, HRV status, Fatigue level
4. **One System** = Everything integrated in XI Selector

**Result**: Better team selection, fewer injuries, more victories! 🏆

---

**Last Updated**: December 28, 2024
**Version**: 2.0 Coach Dashboard

---

**Ready to win? Open** `http://localhost:5000/coach-dashboard`
