import pandas as pd
import os
import numpy as np

print("Creating ULTRA-COMPLETE match dataset...")
print("="*60)

def process_match_file(file_path, match_format):
    """Extract match details - IMPROVED VERSION"""
    try:
        df = pd.read_csv(file_path)
        
        # Skip if dataframe is empty
        if len(df) == 0:
            return None
        
        # Get basic info with fallbacks
        venue = str(df['venue'].iloc[0]) if 'venue' in df.columns and pd.notna(df['venue'].iloc[0]) else 'Unknown'
        season = str(df['season'].iloc[0]) if 'season' in df.columns and pd.notna(df['season'].iloc[0]) else 'Unknown'
        
        # Get teams - IMPROVED
        if 'batting_team' not in df.columns:
            return None
            
        teams = df['batting_team'].dropna().unique()
        if len(teams) < 2:
            return None
        
        team1, team2 = teams[0], teams[1]
        
        # CRITICAL: Check if we have innings data
        if 'innings' not in df.columns:
            return None
        
        # Get innings data
        innings1 = df[df['innings'] == 1].copy()
        innings2 = df[df['innings'] == 2].copy()
        
        # Skip if either innings is empty or too short
        if len(innings1) < 10 or len(innings2) < 10:
            return None
        
        # Ensure required columns exist
        required_cols = ['runs_off_bat', 'extras']
        if not all(col in innings1.columns for col in required_cols):
            return None
        
        # Team 1 (batting first) - with error handling
        team1_runs = int(innings1['runs_off_bat'].sum() + innings1['extras'].sum())
        team1_wickets = int(innings1['wicket_type'].notna().sum()) if 'wicket_type' in innings1.columns else 0
        team1_balls = len(innings1)
        
        # Team 2 (chasing)
        team2_runs = int(innings2['runs_off_bat'].sum() + innings2['extras'].sum())
        team2_wickets = int(innings2['wicket_type'].notna().sum()) if 'wicket_type' in innings2.columns else 0
        team2_balls = len(innings2)
        
        # Skip unrealistic scores
        if team1_runs < 30 or team2_runs < 30:
            return None
        if team1_runs > 500 or team2_runs > 500:
            return None
        
        # Calculate strike rates
        team1_sr = round((team1_runs / team1_balls * 100), 2) if team1_balls > 0 else 0
        team2_sr = round((team2_runs / team2_balls * 100), 2) if team2_balls > 0 else 0
        
        # Count boundaries
        team1_fours = int((innings1['runs_off_bat'] == 4).sum())
        team1_sixes = int((innings1['runs_off_bat'] == 6).sum())
        team1_boundaries = team1_fours + team1_sixes
        
        team2_fours = int((innings2['runs_off_bat'] == 4).sum())
        team2_sixes = int((innings2['runs_off_bat'] == 6).sum())
        team2_boundaries = team2_fours + team2_sixes
        
        # Phase-wise analysis with 'ball' or 'over' column
        if 'ball' in innings1.columns:
            ball_col = 'ball'
        elif 'over' in innings1.columns:
            ball_col = 'over'
        else:
            return None
        
        # Powerplay (first 6 overs)
        team1_powerplay = int(innings1[innings1[ball_col] <= 6.0]['runs_off_bat'].sum())
        team2_powerplay = int(innings2[innings2[ball_col] <= 6.0]['runs_off_bat'].sum())
        
        # Death overs
        if match_format == 'ODI':
            death_start = 41.0
            middle_start, middle_end = 11.0, 40.0
        else:  # T20/IPL
            death_start = 17.0
            middle_start, middle_end = 7.0, 16.0
        
        team1_death = int(innings1[innings1[ball_col] >= death_start]['runs_off_bat'].sum())
        team2_death = int(innings2[innings2[ball_col] >= death_start]['runs_off_bat'].sum())
        
        # Middle overs
        team1_middle = int(innings1[(innings1[ball_col] >= middle_start) & 
                                    (innings1[ball_col] < middle_end)]['runs_off_bat'].sum())
        team2_middle = int(innings2[(innings2[ball_col] >= middle_start) & 
                                    (innings2[ball_col] < middle_end)]['runs_off_bat'].sum())
        
        # Extras analysis
        team1_extras = int(innings1['extras'].sum())
        team2_extras = int(innings2['extras'].sum())
        
        # Dot balls
        team1_dots = int((innings1['runs_off_bat'] == 0).sum())
        team2_dots = int((innings2['runs_off_bat'] == 0).sum())
        team1_dot_pct = round((team1_dots / team1_balls * 100), 2)
        team2_dot_pct = round((team2_dots / team2_balls * 100), 2)
        
        # Run rate
        team1_rr = round((team1_runs / team1_balls * 6), 2)
        team2_rr = round((team2_runs / team2_balls * 6), 2)
        
        # Boundary percentage
        team1_boundary_runs = (team1_fours * 4) + (team1_sixes * 6)
        team2_boundary_runs = (team2_fours * 4) + (team2_sixes * 6)
        team1_boundary_pct = round((team1_boundary_runs / team1_runs * 100), 2) if team1_runs > 0 else 0
        team2_boundary_pct = round((team2_boundary_runs / team2_runs * 100), 2) if team2_runs > 0 else 0
        
        # Winner determination
        if 'winner' in df.columns and pd.notna(df['winner'].iloc[0]):
            winner = df['winner'].iloc[0]
        else:
            winner = team1 if team1_runs > team2_runs else team2
        
        team1_won = 1 if winner == team1 else 0
        
        # Win margin
        if team1_won:
            win_margin = team1_runs - team2_runs
            win_by = f"{win_margin} runs"
        else:
            wickets_left = 10 - team2_wickets
            win_by = f"{wickets_left} wickets"
        
        return {
            # Match info
            'match_format': match_format,
            'venue': venue,
            'season': season,
            'team1': team1,
            'team2': team2,
            
            # Team 1 stats (batting first)
            'team1_runs': team1_runs,
            'team1_wickets': team1_wickets,
            'team1_balls': team1_balls,
            'team1_strike_rate': team1_sr,
            'team1_fours': team1_fours,
            'team1_sixes': team1_sixes,
            'team1_boundaries': team1_boundaries,
            'team1_boundary_percentage': team1_boundary_pct,
            'team1_powerplay_runs': team1_powerplay,
            'team1_middle_runs': team1_middle,
            'team1_death_runs': team1_death,
            'team1_extras': team1_extras,
            'team1_dot_percentage': team1_dot_pct,
            'team1_run_rate': team1_rr,
            
            # Team 2 stats (chasing)
            'team2_runs': team2_runs,
            'team2_wickets': team2_wickets,
            'team2_balls': team2_balls,
            'team2_strike_rate': team2_sr,
            'team2_fours': team2_fours,
            'team2_sixes': team2_sixes,
            'team2_boundaries': team2_boundaries,
            'team2_boundary_percentage': team2_boundary_pct,
            'team2_powerplay_runs': team2_powerplay,
            'team2_middle_runs': team2_middle,
            'team2_death_runs': team2_death,
            'team2_extras': team2_extras,
            'team2_dot_percentage': team2_dot_pct,
            'team2_run_rate': team2_rr,
            
            # Match outcome
            'total_runs': team1_runs + team2_runs,
            'run_difference': abs(team1_runs - team2_runs),
            'team1_won': team1_won,
            'winner': winner,
            'win_by': win_by
        }
    
    except Exception as e:
        # Silently skip problematic files
        return None

# Process ALL formats
all_matches = []

formats = {
    'T20': 'data/raw/t20/',
    'IPL': 'data/raw/ipl/',
    'ODI': 'data/raw/odi/'
}

print("\n🏏 Processing ALL matches from all formats:")
print("="*60)

total_files = 0
total_successful = 0
total_skipped = 0

for match_format, folder_path in formats.items():
    if not os.path.exists(folder_path):
        print(f"⚠️  {match_format} folder not found!")
        continue
    
    files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    total_files += len(files)
    
    print(f"\n📂 {match_format}:")
    print(f"   Files: {len(files)}")
    
    successful = 0
    skipped = 0
    
    for i, file in enumerate(files, 1):
        if i % 1000 == 0:
            print(f"   Progress: {i}/{len(files)} ({successful} ✓, {skipped} ✗)")
        
        match_data = process_match_file(os.path.join(folder_path, file), match_format)
        
        if match_data:
            all_matches.append(match_data)
            successful += 1
        else:
            skipped += 1
    
    total_successful += successful
    total_skipped += skipped
    
    success_rate = (successful / len(files) * 100) if len(files) > 0 else 0
    print(f"   ✅ Success: {successful} matches ({success_rate:.1f}%)")
    print(f"   ⚠️  Skipped: {skipped} matches")

# Create DataFrame
print("\n" + "="*60)
print("📊 Creating final dataset...")

matches_df = pd.DataFrame(all_matches)
print(f"✅ Collected: {len(matches_df)} matches")

# Clean data
initial = len(matches_df)
matches_df = matches_df.dropna(subset=['team1_runs', 'team2_runs', 'venue'])
matches_df = matches_df[matches_df['team1_runs'] >= 30]
matches_df = matches_df[matches_df['team2_runs'] >= 30]
final = len(matches_df)

print(f"✅ After cleaning: {final} matches ({initial - final} removed)")

# Save
matches_df.to_csv('data/processed/complete_matches_dataset.csv', index=False)
print(f"💾 Saved: data/processed/complete_matches_dataset.csv")

# Statistics
print("\n" + "="*60)
print("📊 FINAL DATASET STATISTICS:")
print("="*60)

print(f"\n📈 Total matches: {len(matches_df)}")
print(f"📈 Success rate: {(total_successful/total_files*100):.1f}%")

print("\n🏏 By Format:")
print(matches_df['match_format'].value_counts())

print(f"\n🌍 Venues: {matches_df['venue'].nunique()}")
print(f"🏏 Teams: {pd.concat([matches_df['team1'], matches_df['team2']]).nunique()}")

print("\n🏆 Top 10 Teams:")
all_teams = pd.concat([matches_df['team1'], matches_df['team2']])
print(all_teams.value_counts().head(10))

print("\n📍 Top 10 Venues:")
print(matches_df['venue'].value_counts().head(10))

print("\n⚖️ Win Statistics:")
print(f"Batting First Win Rate: {matches_df['team1_won'].mean()*100:.2f}%")
print(f"Chasing Win Rate: {(1-matches_df['team1_won'].mean())*100:.2f}%")

print("\n📊 Average Scores:")
format_avg = matches_df.groupby('match_format')['team1_runs'].mean()
print(format_avg.round(1))

print("\n" + "="*60)
print("🎉 DATASET READY FOR MACHINE LEARNING!")
print("="*60)