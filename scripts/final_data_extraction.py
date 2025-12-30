import pandas as pd
import os
import numpy as np

print("🚀 EXTRACTING HIGH-QUALITY MATCH DATA FOR 85%+ ACCURACY")
print("="*70)

def extract_quality_match(file_path, match_format):
    """Extract only HIGH QUALITY matches with complete data"""
    try:
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
        
        if df.empty or len(df) < 30:
            return None
        
        # Find columns
        innings_col = next((c for c in ['innings', 'inning'] if c in df.columns), None)
        batting_col = next((c for c in ['batting_team', 'team'] if c in df.columns), None)
        runs_col = next((c for c in ['runs_off_bat', 'runs'] if c in df.columns), None)
        
        if not all([innings_col, batting_col, runs_col]):
            return None
        
        # Teams
        teams = df[batting_col].dropna().unique()
        if len(teams) < 2:
            return None
        team1, team2 = teams[0], teams[1]
        
        # Venue - MUST HAVE VALID VENUE
        venue = None
        for col in ['venue', 'ground', 'city']:
            if col in df.columns and pd.notna(df[col].iloc[0]):
                v = str(df[col].iloc[0]).strip()
                if len(v) > 2 and v != 'Unknown':
                    venue = v
                    break
        
        if not venue:
            return None
        
        # Season
        season = 'Unknown'
        for col in ['season', 'year']:
            if col in df.columns and pd.notna(df[col].iloc[0]):
                season = str(df[col].iloc[0])
                break
        
        # Innings
        inn1 = df[df[innings_col] == 1]
        inn2 = df[df[innings_col] == 2]
        
        # Quality check - must have substantial innings
        if len(inn1) < 50 or len(inn2) < 50:
            return None
        
        # Runs
        extras_col = next((c for c in ['extras', 'extra'] if c in inn1.columns), None)
        
        team1_runs = int(inn1[runs_col].sum())
        team2_runs = int(inn2[runs_col].sum())
        
        if extras_col:
            team1_runs += int(inn1[extras_col].sum())
            team2_runs += int(inn2[extras_col].sum())
        
        # Realistic score check
        if match_format == 'ODI':
            if team1_runs < 100 or team1_runs > 450 or team2_runs < 100 or team2_runs > 450:
                return None
        else:  # T20
            if team1_runs < 80 or team1_runs > 280 or team2_runs < 80 or team2_runs > 280:
                return None
        
        # Wickets
        wicket_col = next((c for c in ['wicket_type', 'wicket', 'player_dismissed'] if c in inn1.columns), None)
        team1_wickets = int(inn1[wicket_col].notna().sum()) if wicket_col else 0
        team2_wickets = int(inn2[wicket_col].notna().sum()) if wicket_col else 0
        
        # Balls
        team1_balls = len(inn1)
        team2_balls = len(inn2)
        
        # Run rates
        overs1 = team1_balls / 6
        overs2 = team2_balls / 6
        team1_rr = round(team1_runs / overs1, 2) if overs1 > 0 else 0
        team2_rr = round(team2_runs / overs2, 2) if overs2 > 0 else 0
        
        # Boundaries
        team1_fours = int((inn1[runs_col] == 4).sum())
        team1_sixes = int((inn1[runs_col] == 6).sum())
        team1_boundaries = team1_fours + team1_sixes
        
        team2_fours = int((inn2[runs_col] == 4).sum())
        team2_sixes = int((inn2[runs_col] == 6).sum())
        team2_boundaries = team2_fours + team2_sixes
        
        # Winner
        winner_col = next((c for c in ['winner', 'winning_team'] if c in df.columns), None)
        if winner_col and pd.notna(df[winner_col].iloc[0]):
            winner = str(df[winner_col].iloc[0])
        else:
            winner = team1 if team1_runs > team2_runs else team2
        
        team1_won = 1 if winner == team1 else 0
        
        return {
            'match_format': match_format,
            'venue': venue,
            'season': season,
            'team1': str(team1),
            'team2': str(team2),
            'team1_runs': team1_runs,
            'team1_wickets': team1_wickets,
            'team1_run_rate': team1_rr,
            'team1_boundaries': team1_boundaries,
            'team1_fours': team1_fours,
            'team1_sixes': team1_sixes,
            'team2_runs': team2_runs,
            'team2_wickets': team2_wickets,
            'team2_run_rate': team2_rr,
            'team2_boundaries': team2_boundaries,
            'team2_fours': team2_fours,
            'team2_sixes': team2_sixes,
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

print("\n📊 Processing with QUALITY FILTERS for maximum accuracy...")
print("="*70)

for fmt, folder in formats.items():
    if not os.path.exists(folder):
        continue
    
    files = [f for f in os.listdir(folder) if f.endswith('.csv')]
    print(f"\n📂 {fmt}: Processing {len(files)} files...")
    
    extracted = 0
    for i, file in enumerate(files, 1):
        if i % 1000 == 0:
            print(f"   Progress: {i}/{len(files)} | Extracted: {extracted}")
        
        result = extract_quality_match(os.path.join(folder, file), fmt)
        if result:
            all_matches.append(result)
            extracted += 1
    
    print(f"   ✅ {fmt}: {extracted} quality matches extracted")

# Create DataFrame
df = pd.DataFrame(all_matches)
print(f"\n✅ Total extracted: {len(df)} matches")

# Remove duplicates
initial = len(df)
df = df.drop_duplicates(subset=['team1', 'team2', 'team1_runs', 'venue', 'season'], keep='first')
print(f"✅ After deduplication: {len(df)} matches ({initial - len(df)} duplicates removed)")

# Save
df.to_csv('data/processed/quality_matches_dataset.csv', index=False)
print(f"💾 Saved: quality_matches_dataset.csv")

# Statistics
print("\n" + "="*70)
print("📊 DATASET STATISTICS:")
print("="*70)
print(f"\n📈 Total Matches: {len(df)}")
print(f"\n🏏 By Format:")
print(df['match_format'].value_counts())
print(f"\n🌍 Unique Venues: {df['venue'].nunique()}")
print(f"🏏 Unique Teams: {pd.concat([df['team1'], df['team2']]).nunique()}")

print("\n🏆 Top 15 Teams:")
teams = pd.concat([df['team1'], df['team2']]).value_counts().head(15)
for i, (team, count) in enumerate(teams.items(), 1):
    print(f"{i:2d}. {team:35s}: {count:4d} matches")

print("\n📍 Top 20 Venues:")
venues = df['venue'].value_counts().head(20)
for i, (venue, count) in enumerate(venues.items(), 1):
    print(f"{i:2d}. {venue:45s}: {count:3d} matches")

print("\n⚖️ Win Balance:")
print(f"Batting First Wins: {df['team1_won'].mean()*100:.1f}%")
print(f"Chasing Wins: {(1-df['team1_won'].mean())*100:.1f}%")

print("\n" + "="*70)
print("🎉 HIGH-QUALITY DATASET READY!")
print("="*70)