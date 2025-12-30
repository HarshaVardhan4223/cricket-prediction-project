import pandas as pd
import numpy as np
import os

print("🏏 BUILDING COMPLETE PLAYER PERFORMANCE DATABASE")
print("="*70)

# Load match data
matches = pd.read_csv('data/processed/quality_matches_dataset.csv')
print(f"✅ Loaded {len(matches)} matches")

# Extract all player data from raw files
print("\n📊 Extracting detailed player statistics...")

all_batting_performances = []
all_bowling_performances = []

# Process raw match files
formats = {
    'T20': 'data/raw/t20/',
    'IPL': 'data/raw/ipl/',
    'ODI': 'data/raw/odi/'
}

processed_files = 0

for match_format, folder in formats.items():
    if not os.path.exists(folder):
        continue
    
    files = [f for f in os.listdir(folder) if f.endswith('.csv')][:300]  # Process 300 per format
    
    print(f"\n   Processing {match_format}...")
    
    for i, file in enumerate(files, 1):
        if i % 100 == 0:
            print(f"      {i}/{len(files)} files...")
        
        try:
            df = pd.read_csv(os.path.join(folder, file), low_memory=False)
            
            if len(df) < 20:
                continue
            
            # Get match info
            venue = df['venue'].iloc[0] if 'venue' in df.columns else 'Unknown'
            season = df['season'].iloc[0] if 'season' in df.columns else 'Unknown'
            
            innings_col = next((c for c in ['innings', 'inning'] if c in df.columns), None)
            if not innings_col:
                continue
            
            # Process each innings
            for innings_num in [1, 2]:
                innings_data = df[df[innings_col] == innings_num]
                
                if len(innings_data) < 10:
                    continue
                
                # BATTING ANALYSIS
                if 'striker' in innings_data.columns and 'runs_off_bat' in innings_data.columns:
                    for batsman in innings_data['striker'].unique():
                        if pd.isna(batsman):
                            continue
                        
                        batsman_balls = innings_data[innings_data['striker'] == batsman]
                        
                        runs = batsman_balls['runs_off_bat'].sum()
                        balls = len(batsman_balls)
                        
                        if balls < 3:  # Skip very short innings
                            continue
                        
                        fours = (batsman_balls['runs_off_bat'] == 4).sum()
                        sixes = (batsman_balls['runs_off_bat'] == 6).sum()
                        dots = (batsman_balls['runs_off_bat'] == 0).sum()
                        ones = (batsman_balls['runs_off_bat'] == 1).sum()
                        twos = (batsman_balls['runs_off_bat'] == 2).sum()
                        threes = (batsman_balls['runs_off_bat'] == 3).sum()
                        
                        # Check if dismissed
                        dismissed = 1 if 'wicket_type' in batsman_balls.columns and batsman_balls['wicket_type'].notna().any() else 0
                        
                        all_batting_performances.append({
                            'player': str(batsman),
                            'format': match_format,
                            'venue': str(venue),
                            'season': str(season),
                            'innings': innings_num,
                            'runs': int(runs),
                            'balls': int(balls),
                            'fours': int(fours),
                            'sixes': int(sixes),
                            'dots': int(dots),
                            'ones': int(ones),
                            'twos': int(twos),
                            'threes': int(threes),
                            'dismissed': dismissed,
                            'strike_rate': round(runs / balls * 100, 2) if balls > 0 else 0,
                            'boundary_percentage': round((fours + sixes) / balls * 100, 2) if balls > 0 else 0,
                            'dot_ball_percentage': round(dots / balls * 100, 2) if balls > 0 else 0
                        })
                
                # BOWLING ANALYSIS
                if 'bowler' in innings_data.columns:
                    for bowler in innings_data['bowler'].unique():
                        if pd.isna(bowler):
                            continue
                        
                        bowler_balls = innings_data[innings_data['bowler'] == bowler]
                        
                        balls_bowled = len(bowler_balls)
                        
                        if balls_bowled < 6:  # At least 1 over
                            continue
                        
                        runs_conceded = bowler_balls['runs_off_bat'].sum()
                        if 'extras' in bowler_balls.columns:
                            runs_conceded += bowler_balls['extras'].sum()
                        
                        wickets = 0
                        if 'wicket_type' in bowler_balls.columns:
                            wickets = bowler_balls['wicket_type'].notna().sum()
                        
                        dots = (bowler_balls['runs_off_bat'] == 0).sum()
                        fours_conceded = (bowler_balls['runs_off_bat'] == 4).sum()
                        sixes_conceded = (bowler_balls['runs_off_bat'] == 6).sum()
                        
                        all_bowling_performances.append({
                            'player': str(bowler),
                            'format': match_format,
                            'venue': str(venue),
                            'season': str(season),
                            'innings': innings_num,
                            'balls_bowled': int(balls_bowled),
                            'runs_conceded': int(runs_conceded),
                            'wickets': int(wickets),
                            'dots': int(dots),
                            'fours_conceded': int(fours_conceded),
                            'sixes_conceded': int(sixes_conceded),
                            'economy': round(runs_conceded / (balls_bowled / 6), 2) if balls_bowled > 0 else 0,
                            'strike_rate': round(balls_bowled / wickets, 2) if wickets > 0 else 0,
                            'dot_ball_percentage': round(dots / balls_bowled * 100, 2) if balls_bowled > 0 else 0
                        })
            
            processed_files += 1
            
        except Exception as e:
            continue

print(f"\n✅ Processed {processed_files} match files")

# Create DataFrames
batting_df = pd.DataFrame(all_batting_performances)
bowling_df = pd.DataFrame(all_bowling_performances)

print(f"\n📊 Extracted:")
print(f"   Batting innings: {len(batting_df)}")
print(f"   Bowling spells: {len(bowling_df)}")

# Save raw performance data
os.makedirs('data/processed/players', exist_ok=True)

batting_df.to_csv('data/processed/players/batting_performances.csv', index=False)
bowling_df.to_csv('data/processed/players/bowling_performances.csv', index=False)

print("\n✅ Saved raw performance data")

# Create aggregated player statistics
print("\n🔧 Calculating aggregated player statistics...")

# BATTING STATISTICS
batting_stats = batting_df.groupby('player').agg({
    'runs': ['sum', 'mean', 'std', 'max'],
    'balls': 'sum',
    'fours': 'sum',
    'sixes': 'sum',
    'dots': 'sum',
    'dismissed': 'sum',
    'strike_rate': 'mean',
    'boundary_percentage': 'mean',
    'dot_ball_percentage': 'mean',
    'player': 'count'
}).reset_index()

batting_stats.columns = ['player', 'total_runs', 'avg_runs_per_innings', 'consistency_std',
                         'highest_score', 'total_balls', 'total_fours', 'total_sixes',
                         'total_dots', 'times_dismissed', 'avg_strike_rate', 
                         'avg_boundary_pct', 'avg_dot_pct', 'innings_played']

# Calculate batting average - FIXED VERSION
batting_stats['batting_average'] = batting_stats.apply(
    lambda row: round(row['total_runs'] / row['times_dismissed'], 2) 
    if row['times_dismissed'] > 0 
    else row['avg_runs_per_innings'], 
    axis=1
)

# Consistency score (lower std = more consistent)
batting_stats['consistency_score'] = (100 - batting_stats['consistency_std'].fillna(0)).clip(0, 100)

# Filter to players with at least 5 innings
batting_stats = batting_stats[batting_stats['innings_played'] >= 5]

print(f"   ✅ Batting stats for {len(batting_stats)} players")

# BOWLING STATISTICS
bowling_stats = bowling_df.groupby('player').agg({
    'balls_bowled': 'sum',
    'runs_conceded': ['sum', 'mean'],
    'wickets': ['sum', 'mean'],
    'dots': 'sum',
    'economy': 'mean',
    'strike_rate': 'mean',
    'dot_ball_percentage': 'mean',
    'player': 'count'
}).reset_index()

bowling_stats.columns = ['player', 'total_balls_bowled', 'total_runs_conceded',
                         'avg_runs_per_spell', 'total_wickets', 'avg_wickets_per_spell',
                         'total_dots', 'avg_economy', 'avg_bowling_sr', 
                         'avg_dot_pct', 'spells_bowled']

# Calculate bowling average - FIXED VERSION
bowling_stats['bowling_average'] = bowling_stats.apply(
    lambda row: round(row['total_runs_conceded'] / row['total_wickets'], 2)
    if row['total_wickets'] > 0
    else row['avg_runs_per_spell'] * 6,
    axis=1
)

# Filter to bowlers with at least 5 spells
bowling_stats = bowling_stats[bowling_stats['spells_bowled'] >= 5]

print(f"   ✅ Bowling stats for {len(bowling_stats)} players")

# Save aggregated stats
batting_stats.to_csv('data/processed/players/batting_statistics.csv', index=False)
bowling_stats.to_csv('data/processed/players/bowling_statistics.csv', index=False)

print("\n✅ Saved aggregated statistics")

# Create SPECIAL SHOTS database (based on patterns)
print("\n🎯 Analyzing special shots...")

special_shots = []

for player in batting_stats['player'].head(200):  # Top 200 players
    player_data = batting_df[batting_df['player'] == player]
    
    if len(player_data) == 0:
        continue
    
    total_boundaries = player_data['fours'].sum() + player_data['sixes'].sum()
    total_runs = player_data['runs'].sum()
    avg_sr = player_data['strike_rate'].mean()
    six_ratio = player_data['sixes'].sum() / total_boundaries if total_boundaries > 0 else 0
    
    # Determine special shot based on stats
    special_shot = "Defensive Player"
    
    if six_ratio > 0.4 and avg_sr > 140:
        special_shot = "Power Hitter - Helicopter Shot"
    elif six_ratio > 0.35 and avg_sr > 130:
        special_shot = "Aggressive Batsman - Pull Shot"
    elif avg_sr > 140:
        special_shot = "Quick Scorer - Scoop Shot"
    elif avg_sr > 120:
        special_shot = "Stroke Player - Cover Drive"
    elif six_ratio < 0.2 and avg_sr < 110:
        special_shot = "Anchor - Straight Drive"
    else:
        special_shot = "Balanced Batsman - Square Cut"
    
    special_shots.append({
        'player': player,
        'special_shot': special_shot,
        'signature_style': 'Aggressive' if avg_sr > 130 else 'Balanced' if avg_sr > 110 else 'Defensive'
    })

special_shots_df = pd.DataFrame(special_shots)
special_shots_df.to_csv('data/processed/players/special_shots.csv', index=False)

print(f"   ✅ Special shots for {len(special_shots_df)} players")

# Create player roles classification
print("\n👥 Classifying player roles...")

player_roles = []

for player in batting_stats['player'].head(300):
    bat_data = batting_stats[batting_stats['player'] == player]
    bowl_data = bowling_stats[bowling_stats['player'] == player]
    
    has_batting = len(bat_data) > 0
    has_bowling = len(bowl_data) > 0
    
    if has_batting and has_bowling:
        avg_runs = bat_data['avg_runs_per_innings'].values[0]
        avg_wickets = bowl_data['avg_wickets_per_spell'].values[0]
        
        if avg_runs > 25 and avg_wickets > 1:
            role = "All-Rounder"
            batting_position = "5-7"
        elif avg_runs > 20:
            role = "Batting All-Rounder"
            batting_position = "6-7"
        else:
            role = "Bowling All-Rounder"
            batting_position = "7-9"
    elif has_batting:
        avg_runs = bat_data['avg_runs_per_innings'].values[0]
        avg_sr = bat_data['avg_strike_rate'].values[0]
        
        if avg_runs > 35 and avg_sr > 130:
            role = "Top-Order Batsman"
            batting_position = "1-3"
        elif avg_runs > 25:
            role = "Middle-Order Batsman"
            batting_position = "3-5"
        elif avg_sr > 140:
            role = "Finisher"
            batting_position = "5-7"
        else:
            role = "Lower-Order Batsman"
            batting_position = "7-9"
    elif has_bowling:
        avg_economy = bowl_data['avg_economy'].values[0]
        avg_wickets = bowl_data['avg_wickets_per_spell'].values[0]
        
        if avg_economy < 7 and avg_wickets > 1.5:
            role = "Strike Bowler"
        elif avg_economy < 7:
            role = "Economical Bowler"
        else:
            role = "Support Bowler"
        
        batting_position = "9-11"
    else:
        continue
    
    player_roles.append({
        'player': player,
        'role': role,
        'batting_position': batting_position
    })

player_roles_df = pd.DataFrame(player_roles)
player_roles_df.to_csv('data/processed/players/player_roles.csv', index=False)

print(f"   ✅ Roles for {len(player_roles_df)} players")

print("\n" + "="*70)
print("🎉 PLAYER DATABASE CREATED!")
print("="*70)
print(f"✅ Batting stats: {len(batting_stats)} players")
print(f"✅ Bowling stats: {len(bowling_stats)} players")
print(f"✅ Special shots: {len(special_shots_df)} players")
print(f"✅ Player roles: {len(player_roles_df)} players")
print("\nFiles saved in: data/processed/players/")
print("\n🚀 Next step: Run player_performance_module.py to analyze players!")