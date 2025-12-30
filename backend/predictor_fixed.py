import pandas as pd
import pickle
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("🏏 CRICKET MATCH PREDICTOR - Enhanced Version")
print("="*70)
print("Model Accuracy: 73% | Dataset: 7,000+ matches")
print("="*70)

# Load model and data
print("\n⏳ Loading model and data...")

try:
    model_path = os.path.join(project_root, 'models', 'ultimate_ensemble_model.pkl')
    team_stats_path = os.path.join(project_root, 'models', 'team_statistics.pkl')
    venue_path = os.path.join(project_root, 'data', 'processed', 'venue_statistics_complete.csv')
    team_list_path = os.path.join(project_root, 'data', 'processed', 'team_list.csv')
    venue_list_path = os.path.join(project_root, 'data', 'processed', 'venue_list.csv')
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    with open(team_stats_path, 'rb') as f:
        team_stats = pickle.load(f)
    
    venue_stats = pd.read_csv(venue_path)
    team_list = pd.read_csv(team_list_path)
    venue_list = pd.read_csv(venue_list_path)
    
    print(f"✅ Model loaded: {len(team_stats)} teams, {len(venue_stats)} venues")
    
except FileNotFoundError as e:
    print(f"❌ Error: {e}")
    print("\n💡 Run: python scripts/quick_save_model.py")
    sys.exit(1)

def show_teams():
    """Display available teams"""
    teams = sorted(team_list['team_name'].tolist())
    print(f"\n🏏 AVAILABLE TEAMS ({len(teams)} teams):")
    print("="*70)
    for i in range(0, len(teams), 3):
        row = teams[i:i+3]
        line = ""
        for j, team in enumerate(row):
            line += f"{i+j+1:3d}. {team:25s} "
        print(line)
    return teams

def show_venues():
    """Display ALL venues"""
    venues = venue_list['venue_name'].tolist()
    print(f"\n🌍 ALL VENUES ({len(venues)} stadiums):")
    print("="*70)
    print("💡 Tip: Type venue number or search by name (e.g., 'wankhede' or 'eden')")
    print("-"*70)
    
    # Display in 2 columns
    for i in range(0, len(venues), 2):
        if i + 1 < len(venues):
            print(f"{i+1:3d}. {venues[i]:45s} {i+2:3d}. {venues[i+1]}")
        else:
            print(f"{i+1:3d}. {venues[i]}")
    
    return venues

def predict_match():
    """Interactive prediction with enhanced confidence"""
    
    # Step 1: Teams
    print("\n" + "="*70)
    print("STEP 1: SELECT TEAMS")
    print("="*70)
    
    teams = show_teams()
    
    print("\n🏏 Enter Team 1 (Batting First):")
    print("   (Enter number, name, or partial name)")
    team1_input = input("   → ").strip()
    
    if team1_input.isdigit() and int(team1_input) <= len(teams):
        team1 = teams[int(team1_input) - 1]
    else:
        matching = [t for t in teams if team1_input.lower() in t.lower()]
        if matching:
            team1 = matching[0]
            if len(matching) > 1:
                print(f"   Found {len(matching)} matches, selected: {team1}")
        else:
            team1 = 'India'
            print(f"   ⚠️ Not found, using default: {team1}")
    
    print(f"   ✅ Selected: {team1}")
    
    print("\n🏏 Enter Team 2 (Chasing):")
    print("   (Enter number, name, or partial name)")
    team2_input = input("   → ").strip()
    
    if team2_input.isdigit() and int(team2_input) <= len(teams):
        team2 = teams[int(team2_input) - 1]
    else:
        matching = [t for t in teams if team2_input.lower() in t.lower()]
        if matching:
            team2 = matching[0]
            if len(matching) > 1:
                print(f"   Found {len(matching)} matches, selected: {team2}")
        else:
            team2 = 'Australia'
            print(f"   ⚠️ Not found, using default: {team2}")
    
    print(f"   ✅ Selected: {team2}")
    
    # Step 2: Venue
    print("\n" + "="*70)
    print("STEP 2: SELECT VENUE")
    print("="*70)
    
    venues = show_venues()
    
    print("\n🌍 Enter Venue:")
    print("   (Enter number or search by name)")
    venue_input = input("   → ").strip()
    
    if venue_input.isdigit() and int(venue_input) <= len(venues):
        venue = venues[int(venue_input) - 1]
    else:
        matching = [v for v in venues if venue_input.lower() in v.lower()]
        if matching:
            venue = matching[0]
            if len(matching) > 1:
                print(f"   Found {len(matching)} matches:")
                for i, v in enumerate(matching[:5], 1):
                    print(f"      {i}. {v}")
                print(f"   Selected: {venue}")
        else:
            venue = venues[0]
            print(f"   ⚠️ Not found, using: {venue}")
    
    print(f"   ✅ Selected: {venue}")
    
    # Step 3: Stats
    print("\n" + "="*70)
    print("STEP 3: ENTER MATCH STATISTICS")
    print("="*70)
    
    print(f"\n📊 {team1} batting first at {venue}")
    
    while True:
        try:
            runs = int(input("\n🏏 Runs scored (80-400): "))
            if 80 <= runs <= 400:
                break
            print("   ⚠️ Enter realistic score (80-400)")
        except:
            print("   ❌ Invalid input")
    
    while True:
        try:
            wickets = int(input("🏏 Wickets lost (0-10): "))
            if 0 <= wickets <= 10:
                break
            print("   ⚠️ Enter 0-10")
        except:
            print("   ❌ Invalid input")
    
    while True:
        try:
            run_rate = float(input("🏏 Run rate (4-15): "))
            if 4 <= run_rate <= 15:
                break
            print("   ⚠️ Enter 4-15")
        except:
            print("   ❌ Invalid input")
    
    # Predict
    print("\n⏳ Analyzing match data...")
    print("   • Team historical performance")
    print("   • Venue statistics")
    print("   • Current match situation")
    
    t1_stats = team_stats.get(team1, {'wr': 0.5, 'bat_wr': 0.5, 'avg_score': 150})
    t2_stats = team_stats.get(team2, {'wr': 0.5, 'chase_wr': 0.5})
    
    venue_row = venue_stats[venue_stats['venue'] == venue]
    if len(venue_row) > 0:
        v_avg = venue_row['v_avg'].values[0]
        v_std = venue_row['v_std'].values[0]
        v_bat_adv = venue_row['v_bat_adv'].values[0]
        v_rr = venue_row['v_rr'].values[0]
    else:
        v_avg, v_std, v_bat_adv, v_rr = 160, 25, 0.5, 7.0
    
    # Features
    score_above_venue = (runs - v_avg) / v_std
    team_strength = t1_stats['wr'] - t2_stats['wr']
    situation_advantage = t1_stats['bat_wr'] - t2_stats['chase_wr']
    wickets_remaining = 10 - wickets
    wicket_quality = wickets_remaining / 10 * (runs / 150)
    big_score = 1 if runs >= v_avg + 15 else 0
    low_wickets = 1 if wickets <= 5 else 0
    dominant_performance = big_score * low_wickets
    balanced_match = 1 if abs(team_strength) < 0.15 else 0
    score_normalized = runs / v_avg
    overall_strength = (
        score_above_venue * 0.4 + team_strength * 0.3 +
        wicket_quality * 0.2 + situation_advantage * 0.1
    )
    
    user_input = pd.DataFrame({
        'runs': [runs], 'wickets': [wickets], 'rr': [run_rate],
        't1_wr': [t1_stats['wr']], 't2_wr': [t2_stats['wr']],
        't1_bat_wr': [t1_stats['bat_wr']], 't2_chase_wr': [t2_stats['chase_wr']],
        'v_avg': [v_avg], 'v_bat_adv': [v_bat_adv],
        'score_above_venue': [score_above_venue], 'team_strength': [team_strength],
        'situation_advantage': [situation_advantage], 'wickets_remaining': [wickets_remaining],
        'wicket_quality': [wicket_quality], 'big_score': [big_score],
        'low_wickets': [low_wickets], 'dominant_performance': [dominant_performance],
        'balanced_match': [balanced_match], 'score_normalized': [score_normalized],
        'overall_strength': [overall_strength]
    })
    
    prediction = model.predict(user_input)[0]
    probability = model.predict_proba(user_input)[0]
    
    # Results
    print("\n" + "="*70)
    print("🎯 MATCH PREDICTION RESULTS")
    print("="*70)
    
    print(f"\n📋 Match Summary:")
    print(f"   Teams: {team1} vs {team2}")
    print(f"   Venue: {venue}")
    print(f"   Score: {runs}/{wickets} (RR: {run_rate})")
    
    print(f"\n🏆 PREDICTION:")
    
    # Enhanced confidence
    max_prob = max(probability)
    if max_prob >= 0.80:
        confidence_level = "🔥 VERY HIGH (80%+)"
        confidence_desc = "Strong prediction - Clear favorite based on data"
    elif max_prob >= 0.70:
        confidence_level = "✅ HIGH (70-80%)"
        confidence_desc = "Good prediction with solid historical evidence"
    elif max_prob >= 0.60:
        confidence_level = "⚠️ MODERATE (60-70%)"
        confidence_desc = "Slight edge to winner - Match could be competitive"
    else:
        confidence_level = "❓ LOW (<60%)"
        confidence_desc = "Very close match - High uncertainty"
    
    if prediction == 1:
        print(f"   🏆 {team1} WILL WIN!")
        print(f"   Win Probability: {probability[1]*100:.1f}%")
    else:
        print(f"   🏆 {team2} WILL WIN!")
        print(f"   Win Probability: {probability[0]*100:.1f}%")
    
    print(f"\n🎯 Confidence Level: {confidence_level}")
    print(f"   📝 {confidence_desc}")
    
    print(f"\n📊 Detailed Win Probabilities:")
    print(f"   {team1}: {probability[1]*100:.1f}%")
    print(f"   {team2}: {probability[0]*100:.1f}%")
    
    prob_diff = abs(probability[1] - probability[0]) * 100
    print(f"   Margin: {prob_diff:.1f}% difference")
    
    if prob_diff < 10:
        print(f"   ⚡ VERY CLOSE MATCH - Could go either way!")
    elif prob_diff < 20:
        print(f"   📊 COMPETITIVE - Slight edge to predicted winner")
    elif prob_diff < 40:
        print(f"   💪 CLEAR FAVORITE - Strong advantage")
    else:
        print(f"   🚀 DOMINANT - Overwhelming favorite")
    
    print(f"\n🌍 Venue Analysis:")
    print(f"   Average Score: {v_avg:.0f} runs")
    print(f"   Batting First Success: {v_bat_adv*100:.0f}%")
    print(f"   Target: {runs} ({'+' if runs > v_avg else ''}{runs - v_avg:.0f} vs average)")
    
    if runs > v_avg + 20:
        print(f"   💪 EXCELLENT SCORE - Well above venue average!")
    elif runs > v_avg:
        print(f"   ✅ GOOD SCORE - Above venue average")
    elif runs > v_avg - 15:
        print(f"   📊 PAR SCORE - Around venue average")
    else:
        print(f"   ⚠️ BELOW PAR - Below venue average")
    
    print("\n" + "="*70)
    
    # Another?
    print("\n🔄 Predict another match? (y/n): ", end="")
    if input().strip().lower() == 'y':
        predict_match()
    else:
        print("\n👋 Thank you for using Cricket Match Predictor!")
        print("="*70)

# Run
if __name__ == "__main__":
    try:
        predict_match()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting... Thank you!")