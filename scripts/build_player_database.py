import pandas as pd
import os

os.makedirs('data/processed', exist_ok=True)

print("Building comprehensive player database from match data...")

# Function to process matches and extract player stats
def extract_player_stats(folder_path, match_type):
    files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    all_batting = []
    all_bowling = []
    
    print(f"\nProcessing {len(files)} {match_type} matches...")
    
    for i, file in enumerate(files[:200], 1):  # Process 200 matches
        if i % 50 == 0:
            print(f"  Processed {i} matches...")
        
        try:
            df = pd.read_csv(os.path.join(folder_path, file))
            
            # Extract batting stats
            for batsman in df['striker'].unique():
                batsman_balls = df[df['striker'] == batsman]
                
                all_batting.append({
                    'player': batsman,
                    'match_type': match_type,
                    'runs': batsman_balls['runs_off_bat'].sum(),
                    'balls_faced': len(batsman_balls),
                    'fours': (batsman_balls['runs_off_bat'] == 4).sum(),
                    'sixes': (batsman_balls['runs_off_bat'] == 6).sum()
                })
            
            # Extract bowling stats
            for bowler in df['bowler'].unique():
                bowler_balls = df[df['bowler'] == bowler]
                
                all_bowling.append({
                    'player': bowler,
                    'match_type': match_type,
                    'runs_conceded': bowler_balls['runs_off_bat'].sum(),
                    'balls_bowled': len(bowler_balls),
                    'wickets': bowler_balls['wicket_type'].notna().sum()
                })
        
        except Exception as e:
            continue
    
    return pd.DataFrame(all_batting), pd.DataFrame(all_bowling)

# Process all match types
batting_dfs = []
bowling_dfs = []

for folder, match_type in [('data/raw/t20', 'T20'), 
                            ('data/raw/ipl', 'IPL'),
                            ('data/raw/odi', 'ODI')]:
    if os.path.exists(folder):
        bat, bowl = extract_player_stats(folder, match_type)
        batting_dfs.append(bat)
        bowling_dfs.append(bowl)

# Combine all data
all_batting = pd.concat(batting_dfs, ignore_index=True)
all_bowling = pd.concat(bowling_dfs, ignore_index=True)

print(f"\n✅ Total batting records: {len(all_batting)}")
print(f"✅ Total bowling records: {len(all_bowling)}")

# Aggregate by player
batting_summary = all_batting.groupby('player').agg({
    'runs': 'sum',
    'balls_faced': 'sum',
    'fours': 'sum',
    'sixes': 'sum'
}).reset_index()

batting_summary['average'] = (batting_summary['runs'] / 
                               (batting_summary['balls_faced'] / 100)).round(2)
batting_summary['strike_rate'] = ((batting_summary['runs'] / 
                                   batting_summary['balls_faced']) * 100).round(2)

# Filter players with at least 100 balls faced
batting_summary = batting_summary[batting_summary['balls_faced'] >= 100]
batting_summary = batting_summary.sort_values('runs', ascending=False)

print(f"\n✅ Players with 100+ balls: {len(batting_summary)}")

# Save batting stats
batting_summary.to_csv('data/processed/player_batting_stats.csv', index=False)
print("✅ Saved: data/processed/player_batting_stats.csv")

# Aggregate bowling
bowling_summary = all_bowling.groupby('player').agg({
    'runs_conceded': 'sum',
    'balls_bowled': 'sum',
    'wickets': 'sum'
}).reset_index()

bowling_summary['economy'] = ((bowling_summary['runs_conceded'] / 
                               bowling_summary['balls_bowled']) * 6).round(2)
bowling_summary['bowling_average'] = (bowling_summary['runs_conceded'] / 
                                      bowling_summary['wickets']).round(2)
bowling_summary['strike_rate'] = (bowling_summary['balls_bowled'] / 
                                  bowling_summary['wickets']).round(2)

# Filter bowlers with at least 100 balls bowled
bowling_summary = bowling_summary[bowling_summary['balls_bowled'] >= 100]
bowling_summary = bowling_summary.sort_values('wickets', ascending=False)

print(f"✅ Bowlers with 100+ balls: {len(bowling_summary)}")

bowling_summary.to_csv('data/processed/player_bowling_stats.csv', index=False)
print("✅ Saved: data/processed/player_bowling_stats.csv")

print("\n🎉 Player database created successfully!")
print("\nTop 5 Run Scorers:")
print(batting_summary[['player', 'runs', 'average', 'strike_rate']].head())
print("\nTop 5 Wicket Takers:")
print(bowling_summary[['player', 'wickets', 'economy', 'bowling_average']].head())