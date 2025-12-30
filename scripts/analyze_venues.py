import pandas as pd
import os

print("Analyzing venue statistics...")

def analyze_venues(folder_path):
    files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    venue_data = []
    
    for i, file in enumerate(files[:200], 1):
        try:
            df = pd.read_csv(os.path.join(folder_path, file))
            venue = df['venue'].iloc[0]
            
            # Calculate innings totals
            innings_totals = df.groupby('innings')['runs_off_bat'].sum()
            
            if len(innings_totals) >= 2:
                venue_data.append({
                    'venue': venue,
                    'innings1_runs': innings_totals.get(1, 0),
                    'innings2_runs': innings_totals.get(2, 0),
                    'total_runs': innings_totals.sum(),
                    'batting_first_won': innings_totals.get(1, 0) > innings_totals.get(2, 0)
                })
        except:
            continue
    
    return pd.DataFrame(venue_data)

# Process T20 and IPL
all_venues = []
for folder in ['data/raw/t20', 'data/raw/ipl']:
    if os.path.exists(folder):
        venues = analyze_venues(folder)
        all_venues.append(venues)

venue_df = pd.concat(all_venues, ignore_index=True)

# Aggregate by venue
venue_stats = venue_df.groupby('venue').agg({
    'innings1_runs': 'mean',
    'innings2_runs': 'mean',
    'total_runs': 'mean',
    'batting_first_won': 'mean',
    'venue': 'count'
}).rename(columns={'venue': 'matches_played'})

venue_stats['chase_success_rate'] = 1 - venue_stats['batting_first_won']
venue_stats = venue_stats.sort_values('matches_played', ascending=False)

# Save
venue_stats.to_csv('data/processed/venue_statistics.csv')
print(f"\n✅ Analyzed {len(venue_stats)} unique venues")
print("✅ Saved: data/processed/venue_statistics.csv")

print("\nTop 10 venues by matches:")
print(venue_stats.head(10))