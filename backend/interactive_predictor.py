import pandas as pd
import pickle
import sys
import os

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(project_root, 'models', 'ultimate_ensemble_model.pkl'), 'rb') as f:
    model = pickle.load(f)

with open(os.path.join(project_root, 'models', 'team_statistics.pkl'), 'rb') as f:
    team_stats = pickle.load(f)

venue_stats = pd.read_csv(os.path.join(project_root, 'data', 'processed', 'venue_statistics_complete.csv'))
team_list = pd.read_csv(os.path.join(project_root, 'data', 'processed', 'team_list.csv'))
venue_list = pd.read_csv(os.path.join(project_root, 'data', 'processed', 'venue_list.csv'))

print("🏏 CRICKET MATCH PREDICTOR - Interactive Mode")
print("="*70)

# Load model and data
print("\n⏳ Loading model and data...")


venue_stats = pd.read_csv('../data/processed/venue_statistics_complete.csv')
team_list = pd.read_csv('../data/processed/team_list.csv')
venue_list = pd.read_csv('../data/processed/venue_list.csv')

print("✅ Model loaded successfully!")

def show_teams():
    """Display available teams"""
    teams = sorted(team_list['team_name'].tolist())
    print("\n🏏 AVAILABLE TEAMS:")
    print("="*70)
    for i in range(0, len(teams), 3):
        row = teams[i:i+3]
        print(f"{i+1:3d}. {row[0]:25s}", end="")
        if len(row) > 1:
            print(f"{i+2:3d}. {row[1]:25s}", end="")
        if len(row) > 2:
            print(f"{i+3:3d}. {row[2]:25s}")
        else:
            print()
    return teams

def show_venues():
    """Display top venues"""
    venues = venue_list.sort_values('matches_played', ascending=False).head(50)
    print("\n🌍 TOP 50 VENUES:")
    print("="*70)
    for i, row in venues.iterrows():
        idx = i + 1
        print(f"{idx:3d}. {row['venue_name']:50s} ({row['matches_played']} matches)")
    return venues['venue_name'].tolist()

def predict_match_interactive():
    """Interactive prediction function"""
    
    # Step 1: Select Teams
    print("\n" + "="*70)
    print("STEP 1: SELECT TEAMS")
    print("="*70)
    
    teams = show_teams()
    
    print("\n🏏 Enter Team 1 (Batting First):")
    team1_input = input("   Team name or number: ").strip()
    
    if team1_input.isdigit():
        team1 = teams[int(team1_input) - 1]
    else:
        # Find matching team
        matching = [t for t in teams if team1_input.lower() in t.lower()]
        if matching:
            team1 = matching[0]
        else:
            print(f"❌ Team not found! Using 'India' as default")
            team1 = 'India'
    
    print(f"✅ Selected: {team1}")
    
    print("\n🏏 Enter Team 2 (Chasing):")
    team2_input = input("   Team name or number: ").strip()
    
    if team2_input.isdigit():
        team2 = teams[int(team2_input) - 1]
    else:
        matching = [t for t in teams if team2_input.lower() in t.lower()]
        if matching:
            team2 = matching[0]
        else:
            print(f"❌ Team not found! Using 'Australia' as default")
            team2 = 'Australia'
    
    print(f"✅ Selected: {team2}")
    
    # Step 2: Select Venue
    print("\n" + "="*70)
    print("STEP 2: SELECT VENUE")
    print("="*70)
    
    venues = show_venues()
    
    print("\n🌍 Enter Venue:")
    venue_input = input("   Venue name or number: ").strip()
    
    if venue_input.isdigit():
        venue = venues[int(venue_input) - 1]
    else:
        matching = [v for v in venues if venue_input.lower() in v.lower()]
        if matching:
            venue = matching[0]
        else:
            print(f"❌ Venue not found! Using first venue as default")
            venue = venues[0]
    
    print(f"✅ Selected: {venue}")
    
    # Step 3: Enter Match Stats
    print("\n" + "="*70)
    print("STEP 3: ENTER MATCH STATISTICS")
    print("="*70)
    
    print(f"\n📊 {team1} batting first at {venue}")
    
    while True:
        try:
            runs = int(input("\n🏏 Enter runs scored: "))
            if runs < 50 or runs > 500:
                print("   ⚠️ Please enter a realistic score (50-500)")
                continue
            break
        except:
            print("   ❌ Invalid input! Please enter a number")
    
    while True:
        try:
            wickets = int(input("🏏 Enter wickets lost: "))
            if wickets < 0 or wickets > 10:
                print("   ⚠️ Wickets must be between 0 and 10")
                continue
            break
        except:
            print("   ❌ Invalid input! Please enter a number")
    
    while True:
        try:
            run_rate = float(input("🏏 Enter run rate: "))
            if run_rate < 2 or run_rate > 15:
                print("   ⚠️ Please enter a realistic run rate (2-15)")
                continue
            break
        except:
            print("   ❌ Invalid input! Please enter a number")
    
    # Make prediction
    print("\n⏳ Analyzing match...")
    
    # Get stats
    t1_stats = team_stats.get(team1, {
        'overall_win_rate': 0.5,
        'bat_first_win_rate': 0.5,
        'avg_score': 150,
        'avg_run_rate': 6.0
    })
    
    t2_stats = team_stats.get(team2, {
        'overall_win_rate': 0.5,
        'chase_win_rate': 0.5
    })
    
    venue_row = venue_stats[venue_stats['venue'] == venue]
    
    if len(venue_row) > 0:
        venue_avg_score = venue_row['venue_avg_score'].values[0]
        venue_bat_first_adv = venue_row['venue_bat_first_advantage'].values[0]
        venue_avg_rr = venue_row['venue_avg_rr'].values[0]
        venue_avg_boundaries = venue_row['venue_avg_boundaries'].values[0]
    else:
        venue_avg_score = 165
        venue_bat_first_adv = 0.5
        venue_avg_rr = 7.0
        venue_avg_boundaries = 16
    
    estimated_boundaries = int(runs / 10)
    team_strength_diff = t1_stats['overall_win_rate'] - t2_stats['overall_win_rate']
    score_vs_venue_avg = runs - venue_avg_score
    rr_vs_venue_avg = run_rate - venue_avg_rr
    wickets_in_hand = 10 - wickets
    rr_quality = run_rate - t1_stats['avg_run_rate']
    normalized_score = runs / 200 if runs > 250 else runs / 160
    
    # Create input
    user_input = pd.DataFrame({
        'team1_runs': [runs],
        'team1_wickets': [wickets],
        'team1_run_rate': [run_rate],
        'team1_overall_wr': [t1_stats['overall_win_rate']],
        'team2_overall_wr': [t2_stats['overall_win_rate']],
        'team1_bat_first_wr': [t1_stats['bat_first_win_rate']],
        'team2_chase_wr': [t2_stats['chase_win_rate']],
        'team_strength_diff': [team_strength_diff],
        'h2h_advantage': [0.5],
        'venue_avg_score': [venue_avg_score],
        'venue_bat_first_advantage': [venue_bat_first_adv],
        'venue_avg_rr': [venue_avg_rr],
        'venue_avg_boundaries': [venue_avg_boundaries],
        'team1_boundaries': [estimated_boundaries],
        'score_vs_venue_avg': [score_vs_venue_avg],
        'rr_vs_venue_avg': [rr_vs_venue_avg],
        'wickets_in_hand': [wickets_in_hand],
        'rr_quality': [rr_quality],
        'normalized_score': [normalized_score]
    })
    
    prediction = model.predict(user_input)[0]
    probability = model.predict_proba(user_input)[0]
    
    # Display results
    print("\n" + "="*70)
    print("🎯 MATCH PREDICTION RESULTS")
    print("="*70)
    
    print(f"\n📋 Match Summary:")
    print(f"   Teams: {team1} vs {team2}")
    print(f"   Venue: {venue}")
    print(f"   Score: {runs}/{wickets} (RR: {run_rate})")
    
    print(f"\n🏆 PREDICTION:")
    if prediction == 1:
        print(f"   ✅ {team1} WILL WIN!")
        print(f"   Confidence: {probability[1]*100:.1f}%")
    else:
        print(f"   ✅ {team2} WILL WIN!")
        print(f"   Confidence: {probability[0]*100:.1f}%")
    
    print(f"\n📊 Win Probabilities:")
    print(f"   {team1}: {probability[1]*100:.1f}%")
    print(f"   {team2}: {probability[0]*100:.1f}%")
    
    print(f"\n🌍 Venue Analysis:")
    print(f"   Average Score: {venue_avg_score:.0f}")
    print(f"   Batting First Advantage: {venue_bat_first_adv*100:.0f}%")
    print(f"   Score Comparison: {'+' if score_vs_venue_avg > 0 else ''}{score_vs_venue_avg:.0f} runs vs venue average")
    
    print("\n" + "="*70)
    
    # Ask for another prediction
    print("\n🔄 Predict another match? (y/n): ", end="")
    if input().strip().lower() == 'y':
        predict_match_interactive()
    else:
        print("\n👋 Thank you for using Cricket Match Predictor!")

# Run interactive mode
if __name__ == "__main__":
    try:
        predict_match_interactive()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting... Thank you!")
        sys.exit(0)