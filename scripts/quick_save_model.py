import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
import pickle
import os

print("🚀 Quick Model Training & Save")
print("="*70)

# Load data
matches = pd.read_csv('data/processed/quality_matches_dataset.csv')
print(f"✅ Loaded {len(matches)} matches")

# Quick clean
matches = matches[
    (matches['team1_runs'] >= 80) & 
    (matches['team1_runs'] <= 350) &
    (matches['team1_wickets'] <= 10)
]
print(f"   Cleaned: {len(matches)} matches")

# Team stats
team_stats = {}
for team in pd.concat([matches['team1'], matches['team2']]).unique():
    t1 = matches[matches['team1'] == team]
    t2 = matches[matches['team2'] == team]
    total = len(t1) + len(t2)
    if total == 0:
        continue
    
    wins = t1['team1_won'].sum() + (len(t2) - t2['team1_won'].sum())
    
    team_stats[team] = {
        'wr': wins / total,
        'bat_wr': t1['team1_won'].mean() if len(t1) > 0 else 0.5,
        'chase_wr': (1 - t2['team1_won'].mean()) if len(t2) > 0 else 0.5,
        'avg_score': t1['team1_runs'].mean() if len(t1) > 0 else 150
    }

matches['t1_wr'] = matches['team1'].map(lambda x: team_stats.get(x, {}).get('wr', 0.5))
matches['t2_wr'] = matches['team2'].map(lambda x: team_stats.get(x, {}).get('wr', 0.5))
matches['t1_bat_wr'] = matches['team1'].map(lambda x: team_stats.get(x, {}).get('bat_wr', 0.5))
matches['t2_chase_wr'] = matches['team2'].map(lambda x: team_stats.get(x, {}).get('chase_wr', 0.5))
matches['t1_avg_score'] = matches['team1'].map(lambda x: team_stats.get(x, {}).get('avg_score', 150))

# Venue stats
venue_stats = matches.groupby('venue').agg({
    'team1_runs': ['mean', 'std'],
    'team1_won': 'mean',
    'team1_run_rate': 'mean'
}).reset_index()
venue_stats.columns = ['venue', 'v_avg', 'v_std', 'v_bat_adv', 'v_rr']
matches = matches.merge(venue_stats, on='venue', how='left')
matches.fillna({'v_avg': 160, 'v_std': 25, 'v_bat_adv': 0.5, 'v_rr': 7.0}, inplace=True)

# Features
matches['runs'] = matches['team1_runs']
matches['wickets'] = matches['team1_wickets']
matches['rr'] = matches['team1_run_rate']
matches['score_above_venue'] = (matches['runs'] - matches['v_avg']) / matches['v_std']
matches['team_strength'] = matches['t1_wr'] - matches['t2_wr']
matches['situation_advantage'] = matches['t1_bat_wr'] - matches['t2_chase_wr']
matches['wickets_remaining'] = 10 - matches['wickets']
matches['wicket_quality'] = matches['wickets_remaining'] / 10 * (matches['runs'] / 150)
matches['big_score'] = (matches['runs'] >= matches['v_avg'] + 15).astype(int)
matches['low_wickets'] = (matches['wickets'] <= 5).astype(int)
matches['dominant_performance'] = matches['big_score'] * matches['low_wickets']
matches['balanced_match'] = (abs(matches['team_strength']) < 0.15).astype(int)
matches['score_normalized'] = matches['runs'] / matches['v_avg']
matches['overall_strength'] = (
    matches['score_above_venue'] * 0.4 +
    matches['team_strength'] * 0.3 +
    matches['wicket_quality'] * 0.2 +
    matches['situation_advantage'] * 0.1
)

features = [
    'runs', 'wickets', 'rr', 't1_wr', 't2_wr', 't1_bat_wr', 't2_chase_wr',
    'v_avg', 'v_bat_adv', 'score_above_venue', 'team_strength', 'situation_advantage',
    'wickets_remaining', 'wicket_quality', 'big_score', 'low_wickets', 'dominant_performance',
    'balanced_match', 'score_normalized', 'overall_strength'
]

X = matches[features].fillna(0)
y = matches['team1_won']

print(f"✅ Features: {len(features)}")

# Train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("\n🤖 Training models...")
rf = RandomForestClassifier(n_estimators=500, max_depth=30, random_state=42, n_jobs=-1)
xgb_model = XGBClassifier(n_estimators=500, max_depth=25, learning_rate=0.02, random_state=42, n_jobs=-1)
gb = GradientBoostingClassifier(n_estimators=400, max_depth=20, learning_rate=0.02, random_state=42)

rf.fit(X_train, y_train)
xgb_model.fit(X_train, y_train)
gb.fit(X_train, y_train)

ensemble = VotingClassifier(
    estimators=[('rf', rf), ('xgb', xgb_model), ('gb', gb)],
    voting='soft'
)
ensemble.fit(X_train, y_train)

accuracy = accuracy_score(y_test, ensemble.predict(X_test))
print(f"✅ Accuracy: {accuracy*100:.2f}%")

# Save everything
print("\n💾 Saving...")
os.makedirs('models', exist_ok=True)

with open('models/ultimate_ensemble_model.pkl', 'wb') as f:
    pickle.dump(ensemble, f)
print("   ✅ Model saved")

with open('models/team_statistics.pkl', 'wb') as f:
    pickle.dump(team_stats, f)
print("   ✅ Team stats saved")

venue_stats.to_csv('data/processed/venue_statistics_complete.csv', index=False)
print("   ✅ Venue stats saved")

model_info = {'features': features, 'accuracy': accuracy}
with open('models/model_info.pkl', 'wb') as f:
    pickle.dump(model_info, f)
print("   ✅ Model info saved")

pd.DataFrame({'team_name': sorted(team_stats.keys())}).to_csv('data/processed/team_list.csv', index=False)
venue_stats[['venue']].rename(columns={'venue': 'venue_name'}).to_csv('data/processed/venue_list.csv', index=False)
print("   ✅ Lists saved")

print("\n" + "="*70)
print("🎉 ALL FILES SAVED!")
print("="*70)
print(f"✅ Model: {accuracy*100:.2f}% accuracy")
print("\n📝 Now run: python backend/interactive_predictor.py")