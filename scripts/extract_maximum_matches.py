import pandas as pd
import os
import numpy as np
from collections import defaultdict

print("🚀 ULTRA-ROBUST Match Extractor - Maximum Data Collection")
print("="*70)

def smart_extract_match(file_path, match_format):
    """Ultra-smart extraction - handles ALL CSV structures"""
    try:
        # Try reading with different encodings
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except:
            try:
                df = pd.read_csv(file_path, encoding='latin-1')
            except:
                return None
        
        if df.empty or len(df) < 20:
            return None
        
        # Find innings column (different names in different files)
        innings_col = None
        for col in ['innings', 'inning', 'innings_number']:
            if col in df.columns:
                innings_col = col
                break
        
        if innings_col is None:
            return None
        
        # Get teams
        batting_col = None
        for col in ['batting_team', 'team', 'batting_side']:
            if col in df.columns:
                batting_col = col
                break
        
        if batting_col is None:
            return None
        
        teams = df[batting_col].dropna().unique()
        if len(teams) < 2:
            return None
        
        team1, team2 = teams[0], teams[1]
        
        # Get venue
        venue = 'Unknown'
        for col in ['venue', 'ground', 'city']:
            if col in df.columns and pd.notna(df[col].iloc[0]):
                venue = str(df[col].iloc[0])
                break
        
        # Get season/date
        season = 'Unknown'
        for col in ['season', 'year', 'start_date', 'date']:
            if col in df.columns and pd.notna(df[col].iloc[0]):
                season = str(df[col].iloc[0])
                break
        
        # Split innings
        inn1 = df[df[innings_col] == 1]
        inn2 = df[df[innings_col] == 2]
        
        if len(inn1) < 10 or len(inn2) < 10:
            return None
        
        # Find runs column
        runs_col = None
        for col in ['runs_off_bat', 'runs', 'runs_scored']:
            if col in inn1.columns:
                runs_col = col
                break
        
        if runs_col is None:
            return None
        
        # Find extras column
        extras_col = None
        for col in ['extras', 'extra']:
            if col in inn1.columns:
                extras_col = col
                break
        
        # Calculate runs
        team1_runs = int(inn1[runs_col].sum())
        team2_runs = int(inn2[runs_col].sum())
        
        if extras_col:
            team1_runs += int(inn1[extras_col].sum())
            team2_runs += int(inn2[extras_col].sum())
        
        # Skip unrealistic scores
        if team1_runs < 30 or team2_runs < 30 or team1_runs > 500 or team2_runs > 500:
            return None
        
        # Wickets
        wicket_col = None
        for col in ['wicket_type', 'wicket', 'dismissal']:
            if col in inn1.columns:
                wicket_col = col
                break
        
        team1_wickets = int(inn1[wicket_col].notna().sum()) if wicket_col else 0
        team2_wickets = int(inn2[wicket_col].notna().sum()) if wicket_col else 0
        
        # Balls
        team1_balls = len(inn1)
        team2_balls = len(inn2)
        
        # Boundaries
        team1_fours = int((inn1[runs_col] == 4).sum())
        team1_sixes = int((inn1[runs_col] == 6).sum())
        team2_fours = int((inn2[runs_col] == 4).sum())
        team2_sixes = int((inn2[runs_col] == 6).sum())
        
        # Find ball/over column
        ball_col = None
        for col in ['ball', 'over', 'overs']:
            if col in inn1.columns:
                ball_col = col
                break
        
        # Phase analysis
        if ball_col:
            # Powerplay
            team1_pp = int(inn1[inn1[ball_col] <= 6.0][runs_col].sum())
            team2_pp = int(inn2[inn2[ball_col] <= 6.0][runs_col].sum())
            
            # Death overs
            death = 41.0 if match_format == 'ODI' else 17.0
            team1_death = int(inn1[inn1[ball_col] >= death][runs_col].sum())
            team2_death = int(inn2[inn2[ball_col] >= death][runs_col].sum())
            
            # Middle overs
            if match_format == 'ODI':
                mid_start, mid_end = 11.0, 40.0
            else:
                mid_start, mid_end = 7.0, 16.0
            
            team1_mid = int(inn1[(inn1[ball_col] >= mid_start) & 
                                 (inn1[ball_col] < mid_end)][runs_col].sum())
            team2_mid = int(inn2[(inn2[ball_col] >= mid_start) & 
                                 (inn2[ball_col] < mid_end)][runs_col].sum())
        else:
            # Estimate if no ball column
            team1_pp = int(team1_runs * 0.25)
            team1_death = int(team1_runs * 0.35)
            team1_mid = int(team1_runs * 0.40)
            team2_pp = int(team2_runs * 0.25)
            team2_death = int(team2_runs * 0.35)
            team2_mid = int(team2_runs * 0.40)
        
        # Calculate rates
        team1_sr = round((team1_runs / team1_balls * 100), 2)
        team2_sr = round((team2_runs / team2_balls * 100), 2)
        team1_rr = round((team1_runs / team1_balls * 6), 2)
        team2_rr = round((team2_runs / team2_balls * 6), 2)
        
        # Dots
        team1_dots = int((inn1[runs_col] == 0).sum())
        team2_dots = int((inn2[runs_col] == 0).sum())
        team1_dot_pct = round((team1_dots / team1_balls * 100), 2)
        team2_dot_pct = round((team2_dots / team2_balls * 100), 2)
        
        # Boundaries
        team1_boundaries = team1_fours + team1_sixes
        team2_boundaries = team2_fours + team2_sixes
        team1_bound_runs = (team1_fours * 4) + (team1_sixes * 6)
        team2_bound_runs = (team2_fours * 4) + (team2_sixes * 6)
        team1_bound_pct = round((team1_bound_runs / team1_runs * 100), 2)
        team2_bound_pct = round((team2_bound_runs / team2_runs * 100), 2)
        
        # Extras
        team1_extras = int(inn1[extras_col].sum()) if extras_col else 0
        team2_extras = int(inn2[extras_col].sum()) if extras_col else 0
        
        # Winner
        winner_col = None
        for col in ['winner', 'winning_team', 'match_winner']:
            if col in df.columns:
                winner_col = col
                break
        
        if winner_col and pd.notna(df[winner_col].iloc[0]):
            winner = df[winner_col].iloc[0]
        else:
            winner = team1 if team1_runs > team2_runs else team2
        
        team1_won = 1 if winner == team1 else 0
        
        return {
            'match_format': match_format,
            'venue': venue,
            'season': season,
            'team1': team1,
            'team2': team2,
            'team1_runs': team1_runs,
            'team1_wickets': team1_wickets,
            'team1_balls': team1_balls,
            'team1_strike_rate': team1_sr,
            'team1_run_rate': team1_rr,
            'team1_fours': team1_fours,
            'team1_sixes': team1_sixes,
            'team1_boundaries': team1_boundaries,
            'team1_boundary_percentage': team1_bound_pct,
            'team1_powerplay_runs': team1_pp,
            'team1_middle_runs': team1_mid,
            'team1_death_runs': team1_death,
            'team1_extras': team1_extras,
            'team1_dot_percentage': team1_dot_pct,
            'team2_runs': team2_runs,
            'team2_wickets': team2_wickets,
            'team2_balls': team2_balls,
            'team2_strike_rate': team2_sr,
            'team2_run_rate': team2_rr,
            'team2_fours': team2_fours,
            'team2_sixes': team2_sixes,
            'team2_boundaries': team2_boundaries,
            'team2_boundary_percentage': team2_bound_pct,
            'team2_powerplay_runs': team2_pp,
            'team2_middle_runs': team2_mid,
            'team2_death_runs': team2_death,
            'team2_extras': team2_extras,
            'team2_dot_percentage': team2_dot_pct,
            'total_runs': team1_runs + team2_runs,
            'run_difference': abs(team1_runs - team2_runs),
            'team1_won': team1_won,
            'winner': winner
        }
    
    except Exception as e:
        return None

# Process all formats
all_matches = []
formats = {
    'T20': 'data/raw/t20/',
    'IPL': 'data/raw/ipl/',
    'ODI': 'data/raw/odi/'
}

print("\n🏏 Processing ALL formats with maximum extraction:")
print("="*70)

total_attempted = 0
total_extracted = 0

for fmt, folder in formats.items():
    if not os.path.exists(folder):
        continue
    
    files = [f for f in os.listdir(folder) if f.endswith('.csv')]
    total_attempted += len(files)
    
    print(f"\n📂 {fmt} Format: {len(files)} files")
    
    extracted = 0
    for i, file in enumerate(files, 1):
        if i % 1000 == 0:
            print(f"   Progress: {i}/{len(files)} | Extracted: {extracted}")
        
        result = smart_extract_match(os.path.join(folder, file), fmt)
        if result:
            all_matches.append(result)
            extracted += 1
    
    total_extracted += extracted
    rate = (extracted / len(files) * 100) if files else 0
    print(f"   ✅ {fmt}: {extracted}/{len(files)} ({rate:.1f}%)")

# Create DataFrame
print("\n" + "="*70)
print("📊 Creating Dataset...")

df = pd.DataFrame(all_matches)
print(f"✅ Extracted: {len(df)} matches")
print(f"📊 Overall Success Rate: {(total_extracted/total_attempted*100):.1f}%")

# Clean
initial = len(df)
df = df.drop_duplicates(subset=['team1', 'team2', 'team1_runs', 'venue'], keep='first')
df = df[df['team1_runs'] >= 30]
df = df[df['team2_runs'] >= 30]
final = len(df)

print(f"✅ After cleaning: {final} matches ({initial-final} duplicates removed)")

# Save
df.to_csv('data/processed/complete_matches_dataset.csv', index=False)
print(f"💾 Saved: complete_matches_dataset.csv")

# Stats
print("\n" + "="*70)
print("📊 DATASET SUMMARY:")
print("="*70)
print(f"\n📈 Total Matches: {len(df)}")
print(f"\n🏏 By Format:")
print(df['match_format'].value_counts())
print(f"\n🌍 Unique Venues: {df['venue'].nunique()}")
print(f"🏏 Unique Teams: {pd.concat([df['team1'], df['team2']]).nunique()}")
print(f"\n📊 Batting First Win Rate: {df['team1_won'].mean()*100:.1f}%")

print("\n🏆 Top 15 Teams:")
teams = pd.concat([df['team1'], df['team2']]).value_counts().head(15)
for i, (team, count) in enumerate(teams.items(), 1):
    print(f"{i:2d}. {team:30s}: {count:4d} matches")

print("\n📍 Top 15 Venues:")
venues = df['venue'].value_counts().head(15)
for i, (venue, count) in enumerate(venues.items(), 1):
    print(f"{i:2d}. {venue:40s}: {count:4d} matches")

print("\n" + "="*70)
print("🎉 DATA EXTRACTION COMPLETE!")
print("="*70)