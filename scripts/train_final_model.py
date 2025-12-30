import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier, StackingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

print("🚀 BOOSTING TO 80%+ ACCURACY")
print("="*70)

# Load data
matches = pd.read_csv('data/processed/quality_matches_dataset.csv')
print(f"✅ Loaded {len(matches)} matches")

# =============================================================================
# ADVANCED TEAM STATISTICS (MORE DEPTH)
# =============================================================================
print("\n📊 Creating ADVANCED team statistics...")

team_stats = {}

for team in pd.concat([matches['team1'], matches['team2']]).unique():
    t1_matches = matches[matches['team1'] == team]
    t2_matches = matches[matches['team2'] == team]
    
    total = len(t1_matches) + len(t2_matches)
    if total == 0:
        continue
    
    wins_t1 = t1_matches['team1_won'].sum()
    wins_t2 = len(t2_matches) - t2_matches['team1_won'].sum()
    
    # Recent form (last 20 matches)
    all_team_matches = pd.concat([
        t1_matches[['season', 'team1_won']].rename(columns={'team1_won': 'won'}),
        t2_matches[['season']].assign(won=lambda x: 1 - matches.loc[x.index, 'team1_won'])
    ]).sort_values('season', ascending=False).head(20)
    
    recent_form = all_team_matches['won'].mean() if len(all_team_matches) > 0 else 0.5
    
    # Win rate by score range
    high_scores = t1_matches[t1_matches['team1_runs'] >= 180]
    medium_scores = t1_matches[(t1_matches['team1_runs'] >= 150) & (t1_matches['team1_runs'] < 180)]
    low_scores = t1_matches[t1_matches['team1_runs'] < 150]
    
    team_stats[team] = {
        'overall_win_rate': (wins_t1 + wins_t2) / total,
        'bat_first_win_rate': wins_t1 / len(t1_matches) if len(t1_matches) > 0 else 0.5,
        'chase_win_rate': wins_t2 / len(t2_matches) if len(t2_matches) > 0 else 0.5,
        'recent_form': recent_form,
        'avg_score': t1_matches['team1_runs'].mean() if len(t1_matches) > 0 else 150,
        'median_score': t1_matches['team1_runs'].median() if len(t1_matches) > 0 else 150,
        'avg_run_rate': t1_matches['team1_run_rate'].mean() if len(t1_matches) > 0 else 6.5,
        'avg_boundaries': t1_matches['team1_boundaries'].mean() if len(t1_matches) > 0 else 15,
        'score_consistency': t1_matches['team1_runs'].std() if len(t1_matches) > 0 else 30,
        'high_score_wr': high_scores['team1_won'].mean() if len(high_scores) > 0 else 0.5,
        'medium_score_wr': medium_scores['team1_won'].mean() if len(medium_scores) > 0 else 0.5,
        'low_score_wr': low_scores['team1_won'].mean() if len(low_scores) > 0 else 0.5,
        'total_matches': total
    }

# Add to matches
for key in ['overall_win_rate', 'bat_first_win_rate', 'chase_win_rate', 'recent_form', 
            'avg_score', 'median_score', 'avg_run_rate', 'avg_boundaries', 'score_consistency']:
    matches[f'team1_{key}'] = matches['team1'].map(lambda x: team_stats.get(x, {}).get(key, 0.5 if 'rate' in key or 'form' in key else 150))
    if key in ['overall_win_rate', 'chase_win_rate']:
        matches[f'team2_{key}'] = matches['team2'].map(lambda x: team_stats.get(x, {}).get(key, 0.5))

print(f"   ✅ {len(team_stats)} teams processed")

# =============================================================================
# ADVANCED VENUE STATISTICS
# =============================================================================
print("\n🌍 Creating ADVANCED venue statistics...")

# Venue stats by format
venue_format = matches.groupby(['venue', 'match_format']).agg({
    'team1_runs': ['mean', 'median', 'std', 'count'],
    'team1_won': 'mean',
    'team1_run_rate': 'mean',
    'team1_boundaries': 'mean',
    'team1_wickets': 'mean'
}).reset_index()

venue_format.columns = ['venue', 'match_format', 'vf_avg_score', 'vf_median_score', 
                        'vf_score_std', 'vf_matches', 'vf_bat_first_adv', 
                        'vf_avg_rr', 'vf_avg_boundaries', 'vf_avg_wickets']

matches = matches.merge(venue_format, on=['venue', 'match_format'], how='left')

# Overall venue stats
venue_stats = matches.groupby('venue').agg({
    'team1_runs': ['mean', 'median', 'std', 'min', 'max'],
    'team1_won': 'mean',
    'team1_run_rate': ['mean', 'std'],
    'team1_boundaries': 'mean',
    'venue': 'count'
}).reset_index()

venue_stats.columns = ['venue', 'venue_avg_score', 'venue_median_score', 'venue_score_std',
                       'venue_min_score', 'venue_max_score', 'venue_bat_first_adv',
                       'venue_avg_rr', 'venue_rr_std', 'venue_avg_boundaries', 'venue_matches']

matches = matches.merge(venue_stats, on='venue', how='left')

# Fill NaNs
for col in matches.columns:
    if 'vf_' in col or 'venue_' in col:
        if 'adv' in col or 'rate' in col:
            matches[col].fillna(0.5 if 'adv' in col else 7.0, inplace=True)
        elif 'score' in col:
            matches[col].fillna(160, inplace=True)
        elif 'boundaries' in col:
            matches[col].fillna(15, inplace=True)
        elif 'wickets' in col:
            matches[col].fillna(5, inplace=True)
        elif 'std' in col:
            matches[col].fillna(25, inplace=True)
        else:
            matches[col].fillna(matches[col].mean(), inplace=True)

print(f"   ✅ {matches['venue'].nunique()} venues processed")

# =============================================================================
# SUPER ADVANCED FEATURES
# =============================================================================
print("\n🔧 Creating SUPER ADVANCED features...")

# Team strength features
matches['team_strength_diff'] = matches['team1_overall_win_rate'] - matches['team2_overall_win_rate']
matches['match_situation_adv'] = matches['team1_bat_first_win_rate'] - matches['team2_chase_win_rate']
matches['form_difference'] = matches['team1_recent_form'] - matches['team2_recent_form']

# Score analysis features
matches['score_vs_venue_avg'] = matches['team1_runs'] - matches['vf_avg_score']
matches['score_vs_venue_median'] = matches['team1_runs'] - matches['vf_median_score']
matches['score_vs_team_avg'] = matches['team1_runs'] - matches['team1_avg_score']
matches['score_vs_team_median'] = matches['team1_runs'] - matches['team1_median_score']

# Performance percentile
matches['score_percentile'] = ((matches['team1_runs'] - matches['venue_min_score']) / 
                               (matches['venue_max_score'] - matches['venue_min_score'] + 1))
matches['score_percentile'] = matches['score_percentile'].clip(0, 1).fillna(0.5)

# Z-score (standardized score)
matches['score_zscore'] = ((matches['team1_runs'] - matches['vf_avg_score']) / 
                          (matches['vf_score_std'] + 1))
matches['score_zscore'] = matches['score_zscore'].clip(-3, 3).fillna(0)

# Run rate features
matches['rr_vs_venue_avg'] = matches['team1_run_rate'] - matches['vf_avg_rr']
matches['rr_vs_team_avg'] = matches['team1_run_rate'] - matches['team1_avg_run_rate']
matches['rr_ratio'] = (matches['team1_run_rate'] / (matches['vf_avg_rr'] + 0.1)).clip(0.5, 2.0)

# Boundaries features
matches['boundaries_vs_venue'] = matches['team1_boundaries'] - matches['vf_avg_boundaries']
matches['boundaries_vs_team'] = matches['team1_boundaries'] - matches['team1_avg_boundaries']
matches['boundary_ratio'] = (matches['team1_boundaries'] / (matches['vf_avg_boundaries'] + 1)).clip(0.5, 2.0)

# Wickets features
matches['wickets_in_hand'] = 10 - matches['team1_wickets']
matches['wickets_vs_venue'] = matches['team1_wickets'] - matches['vf_avg_wickets']
matches['wickets_per_run'] = matches['team1_wickets'] / (matches['team1_runs'] + 1)
matches['wickets_impact'] = matches['wickets_in_hand'] * matches['team1_runs'] / 1000

# Performance indicators
matches['dominant_score'] = ((matches['team1_runs'] > matches['vf_avg_score'] + 20) & 
                            (matches['team1_wickets'] <= 6)).astype(int)
matches['struggling_innings'] = ((matches['team1_runs'] < matches['vf_avg_score'] - 10) | 
                                 (matches['team1_wickets'] >= 8)).astype(int)
matches['balanced_innings'] = (1 - matches['dominant_score'] - matches['struggling_innings']).clip(0, 1)

# Momentum features
matches['batting_momentum'] = ((matches['team1_run_rate'] / (matches['team1_avg_run_rate'] + 0.1)) * 
                               (matches['wickets_in_hand'] / 10))
matches['pressure_handling'] = ((matches['team1_runs'] / (matches['vf_avg_score'] + 1)) * 
                                matches['team1_recent_form'])

# Match context
matches['high_stakes'] = (abs(matches['team_strength_diff']) < 0.1).astype(int)
matches['mismatch'] = (abs(matches['team_strength_diff']) > 0.3).astype(int)

# Format-specific normalization
matches['normalized_score'] = matches.apply(
    lambda x: (x['team1_runs'] - 200) / 50 if x['match_format'] == 'ODI' else (x['team1_runs'] - 160) / 30,
    axis=1
)

print(f"   ✅ Created 40+ advanced features")

# =============================================================================
# SELECT BEST FEATURES
# =============================================================================
features = [
    # Core inputs
    'team1_runs', 'team1_wickets', 'team1_run_rate', 'team1_boundaries',
    
    # Team strength & form
    'team1_overall_win_rate', 'team2_overall_win_rate', 
    'team1_bat_first_win_rate', 'team2_chase_win_rate',
    'team1_recent_form', 'team2_recent_form',
    'team_strength_diff', 'match_situation_adv', 'form_difference',
    
    # Venue intelligence
    'vf_avg_score', 'vf_median_score', 'vf_bat_first_adv', 'vf_avg_rr',
    'venue_bat_first_adv', 'venue_avg_score',
    
    # Score analysis
    'score_vs_venue_avg', 'score_vs_venue_median', 
    'score_vs_team_avg', 'score_vs_team_median',
    'score_percentile', 'score_zscore',
    
    # Run rate analysis
    'rr_vs_venue_avg', 'rr_vs_team_avg', 'rr_ratio',
    
    # Boundaries
    'boundaries_vs_venue', 'boundaries_vs_team', 'boundary_ratio',
    
    # Wickets
    'wickets_in_hand', 'wickets_vs_venue', 'wickets_per_run', 'wickets_impact',
    
    # Performance indicators
    'dominant_score', 'struggling_innings', 'balanced_innings',
    'batting_momentum', 'pressure_handling',
    
    # Context
    'high_stakes', 'mismatch', 'normalized_score'
]

X = matches[features].replace([np.inf, -np.inf], 0).fillna(0)
y = matches['team1_won']

print(f"\n✅ Features: {len(features)}")
print(f"✅ Samples: {len(X)}")

# =============================================================================
# TRAIN WITH STACKING ENSEMBLE
# =============================================================================
print("\n🤖 Training STACKING ENSEMBLE...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

# Base models
rf = RandomForestClassifier(n_estimators=1000, max_depth=35, min_samples_split=2, 
                            class_weight='balanced', random_state=42, n_jobs=-1)
xgb_model = XGBClassifier(n_estimators=1000, max_depth=30, learning_rate=0.015,
                         subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1)
gb = GradientBoostingClassifier(n_estimators=800, max_depth=25, learning_rate=0.015,
                                subsample=0.8, random_state=42)
lgbm = LGBMClassifier(n_estimators=1000, max_depth=30, learning_rate=0.015,
                     random_state=42, n_jobs=-1, verbose=-1)

# Stacking with Logistic Regression as meta-learner
stacking = StackingClassifier(
    estimators=[
        ('rf', rf),
        ('xgb', xgb_model),
        ('gb', gb),
        ('lgbm', lgbm)
    ],
    final_estimator=LogisticRegression(max_iter=1000),
    cv=5,
    n_jobs=-1
)

print("   Training stacking ensemble (5-10 minutes)...")
stacking.fit(X_train, y_train)

y_pred = stacking.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("\n" + "="*70)
print("🏆 STACKING ENSEMBLE RESULTS")
print("="*70)
print(f"🎯 ACCURACY: {accuracy*100:.2f}%")

if accuracy >= 0.85:
    print("🎉🎉🎉 EXCELLENT! 85%+ ACHIEVED!")
elif accuracy >= 0.80:
    print("🎉 SUCCESS! 80%+ ACHIEVED!")
elif accuracy >= 0.77:
    print("✅ Great! 77%+ - Very close to 80%!")
else:
    print(f"📈 Improved from 73.59% → {accuracy*100:.2f}%")

# Cross-validation
print("\n🔄 Cross-Validation:")
cv_scores = cross_val_score(stacking, X, y, cv=5, scoring='accuracy', n_jobs=-1)
print(f"   Scores: {[f'{s*100:.1f}%' for s in cv_scores]}")
print(f"   Mean: {cv_scores.mean()*100:.2f}% (±{cv_scores.std()*100:.2f}%)")

print("\n" + classification_report(y_test, y_pred, 
                                  target_names=['Team 2 Wins', 'Team 1 Wins']))

# Save
print("\n💾 Saving improved model...")
os.makedirs('models', exist_ok=True)

with open('models/ultimate_ensemble_model.pkl', 'wb') as f:
    pickle.dump(stacking, f)

with open('models/team_statistics.pkl', 'wb') as f:
    pickle.dump(team_stats, f)

venue_stats.to_csv('data/processed/venue_statistics_complete.csv', index=False)

model_info = {
    'features': features,
    'accuracy': accuracy,
    'cv_mean': cv_scores.mean(),
    'model_type': 'StackingClassifier'
}

with open('models/model_info.pkl', 'wb') as f:
    pickle.dump(model_info, f)

team_list = pd.DataFrame({'team_name': sorted(team_stats.keys())})
team_list.to_csv('data/processed/team_list.csv', index=False)

venue_list = venue_stats[['venue', 'venue_matches']].copy()
venue_list.columns = ['venue_name', 'matches_played']
venue_list.to_csv('data/processed/venue_list.csv', index=False)

print("\n" + "="*70)
print("🎉 BOOSTED MODEL COMPLETE!")
print("="*70)
print(f"✅ New Accuracy: {accuracy*100:.2f}%")
print(f"✅ Improvement: +{(accuracy-0.7359)*100:.2f}% from baseline")
print("\n📝 Run: python backend/interactive_predictor.py")