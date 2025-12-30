import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, StackingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

print("🚀 BOOSTING TO 80%+ ACCURACY - FIXED VERSION")
print("="*70)

matches = pd.read_csv('data/processed/quality_matches_dataset.csv')
print(f"✅ Loaded {len(matches)} matches")

# Team statistics
print("\n📊 Creating team statistics...")
team_stats = {}

for team in pd.concat([matches['team1'], matches['team2']]).unique():
    t1 = matches[matches['team1'] == team]
    t2 = matches[matches['team2'] == team]
    
    total = len(t1) + len(t2)
    if total == 0:
        continue
    
    wins_t1 = t1['team1_won'].sum()
    wins_t2 = len(t2) - t2['team1_won'].sum()
    
    team_stats[team] = {
        'overall_wr': (wins_t1 + wins_t2) / total,
        'bat_first_wr': wins_t1 / len(t1) if len(t1) > 0 else 0.5,
        'chase_wr': wins_t2 / len(t2) if len(t2) > 0 else 0.5,
        'avg_score': t1['team1_runs'].mean() if len(t1) > 0 else 150,
        'avg_rr': t1['team1_run_rate'].mean() if len(t1) > 0 else 6.5,
        'avg_boundaries': t1['team1_boundaries'].mean() if len(t1) > 0 else 15
    }

matches['t1_wr'] = matches['team1'].map(lambda x: team_stats.get(x, {}).get('overall_wr', 0.5))
matches['t2_wr'] = matches['team2'].map(lambda x: team_stats.get(x, {}).get('overall_wr', 0.5))
matches['t1_bat_wr'] = matches['team1'].map(lambda x: team_stats.get(x, {}).get('bat_first_wr', 0.5))
matches['t2_chase_wr'] = matches['team2'].map(lambda x: team_stats.get(x, {}).get('chase_wr', 0.5))
matches['t1_avg_score'] = matches['team1'].map(lambda x: team_stats.get(x, {}).get('avg_score', 150))
matches['t1_avg_rr'] = matches['team1'].map(lambda x: team_stats.get(x, {}).get('avg_rr', 6.5))
matches['t1_avg_bound'] = matches['team1'].map(lambda x: team_stats.get(x, {}).get('avg_boundaries', 15))

print(f"   ✅ {len(team_stats)} teams")

# Venue statistics
print("\n🌍 Creating venue statistics...")
venue_stats = matches.groupby('venue').agg({
    'team1_runs': ['mean', 'std', 'min', 'max'],
    'team1_won': 'mean',
    'team1_run_rate': 'mean',
    'team1_boundaries': 'mean'
}).reset_index()

venue_stats.columns = ['venue', 'v_avg_score', 'v_std', 'v_min', 'v_max', 
                       'v_bat_adv', 'v_avg_rr', 'v_avg_bound']

matches = matches.merge(venue_stats, on='venue', how='left')
matches.fillna({
    'v_avg_score': 160, 'v_std': 25, 'v_bat_adv': 0.5,
    'v_avg_rr': 7.0, 'v_avg_bound': 15, 'v_min': 100, 'v_max': 250
}, inplace=True)

print(f"   ✅ {matches['venue'].nunique()} venues")

# Create features
print("\n🔧 Creating features...")

matches['team_diff'] = matches['t1_wr'] - matches['t2_wr']
matches['match_adv'] = matches['t1_bat_wr'] - matches['t2_chase_wr']
matches['score_vs_venue'] = matches['team1_runs'] - matches['v_avg_score']
matches['score_vs_team'] = matches['team1_runs'] - matches['t1_avg_score']
matches['score_pct'] = ((matches['team1_runs'] - matches['v_min']) / (matches['v_max'] - matches['v_min'] + 1)).clip(0, 1)
matches['score_z'] = ((matches['team1_runs'] - matches['v_avg_score']) / (matches['v_std'] + 1)).clip(-3, 3)
matches['rr_vs_venue'] = matches['team1_run_rate'] - matches['v_avg_rr']
matches['rr_vs_team'] = matches['team1_run_rate'] - matches['t1_avg_rr']
matches['bound_vs_venue'] = matches['team1_boundaries'] - matches['v_avg_bound']
matches['bound_vs_team'] = matches['team1_boundaries'] - matches['t1_avg_bound']
matches['wkts_in_hand'] = 10 - matches['team1_wickets']
matches['wkts_per_run'] = matches['team1_wickets'] / (matches['team1_runs'] + 1)
matches['dominant'] = ((matches['team1_runs'] > matches['v_avg_score'] + 20) & (matches['team1_wickets'] <= 6)).astype(int)
matches['struggling'] = ((matches['team1_runs'] < matches['v_avg_score'] - 10) | (matches['team1_wickets'] >= 8)).astype(int)
matches['momentum'] = (matches['team1_run_rate'] / (matches['t1_avg_rr'] + 0.1)) * (matches['wkts_in_hand'] / 10)
matches['normalized'] = matches.apply(lambda x: x['team1_runs'] / 200 if x['match_format'] == 'ODI' else x['team1_runs'] / 160, axis=1)

features = [
    'team1_runs', 'team1_wickets', 'team1_run_rate', 'team1_boundaries',
    't1_wr', 't2_wr', 't1_bat_wr', 't2_chase_wr', 'team_diff', 'match_adv',
    'v_avg_score', 'v_bat_adv', 'v_avg_rr',
    'score_vs_venue', 'score_vs_team', 'score_pct', 'score_z',
    'rr_vs_venue', 'rr_vs_team', 'bound_vs_venue', 'bound_vs_team',
    'wkts_in_hand', 'wkts_per_run', 'dominant', 'struggling', 'momentum', 'normalized'
]

X = matches[features].replace([np.inf, -np.inf], 0).fillna(0)
y = matches['team1_won']

print(f"   ✅ {len(features)} features")

# Train
print("\n🤖 Training models...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

rf = RandomForestClassifier(n_estimators=1000, max_depth=35, class_weight='balanced', random_state=42, n_jobs=-1)
xgb_model = XGBClassifier(n_estimators=1000, max_depth=30, learning_rate=0.015, random_state=42, n_jobs=-1)
gb = GradientBoostingClassifier(n_estimators=800, max_depth=25, learning_rate=0.015, random_state=42)
lgbm = LGBMClassifier(n_estimators=1000, max_depth=30, learning_rate=0.015, random_state=42, n_jobs=-1, verbose=-1)

print("   Training stacking ensemble...")
stacking = StackingClassifier(
    estimators=[('rf', rf), ('xgb', xgb_model), ('gb', gb), ('lgbm', lgbm)],
    final_estimator=LogisticRegression(max_iter=1000),
    cv=5, n_jobs=-1
)

stacking.fit(X_train, y_train)

y_pred = stacking.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("\n" + "="*70)
print("🏆 RESULTS")
print("="*70)
print(f"🎯 ACCURACY: {accuracy*100:.2f}%")

if accuracy >= 0.80:
    print("🎉 SUCCESS! 80%+ ACHIEVED!")
else:
    print(f"📈 Improved: +{(accuracy-0.7359)*100:.2f}%")

cv_scores = cross_val_score(stacking, X, y, cv=5, scoring='accuracy', n_jobs=-1)
print(f"\n🔄 Cross-Val: {cv_scores.mean()*100:.2f}% (±{cv_scores.std()*100:.2f}%)")

print("\n" + classification_report(y_test, y_pred, target_names=['Team 2 Wins', 'Team 1 Wins']))

# Save
print("\n💾 Saving...")
os.makedirs('models', exist_ok=True)

with open('models/ultimate_ensemble_model.pkl', 'wb') as f:
    pickle.dump(stacking, f)
with open('models/team_statistics.pkl', 'wb') as f:
    pickle.dump(team_stats, f)

venue_stats.to_csv('data/processed/venue_statistics_complete.csv', index=False)

model_info = {'features': features, 'accuracy': accuracy, 'cv_mean': cv_scores.mean()}
with open('models/model_info.pkl', 'wb') as f:
    pickle.dump(model_info, f)

pd.DataFrame({'team_name': sorted(team_stats.keys())}).to_csv('data/processed/team_list.csv', index=False)
venue_stats[['venue']].rename(columns={'venue': 'venue_name'}).to_csv('data/processed/venue_list.csv', index=False)

print(f"\n✅ Final: {accuracy*100:.2f}%")
print("📝 Run: python backend/interactive_predictor.py")