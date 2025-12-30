import pandas as pd
import numpy as np
import os
import json

print("🏏 CRICKET PLAYER PERFORMANCE ANALYZER")
print("="*70)
print("Analyzing 373 batsmen & 327 bowlers")
print("="*70)

# Load all player data
try:
    batting_stats = pd.read_csv('data/processed/players/batting_statistics.csv')
    bowling_stats = pd.read_csv('data/processed/players/bowling_statistics.csv')
    special_shots = pd.read_csv('data/processed/players/special_shots.csv')
    player_roles = pd.read_csv('data/processed/players/player_roles.csv')
    batting_performances = pd.read_csv('data/processed/players/batting_performances.csv')
    bowling_performances = pd.read_csv('data/processed/players/bowling_performances.csv')
    
    print("✅ All player data loaded successfully!")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    exit()

# Attempt to load augmented player insights (optional)
augmented_players = {}
augmented_path = os.path.join('..', 'data', 'global_cricket_players_fixed_augmented_rich_v2.json')
if not os.path.exists(augmented_path):
    # fallback to project root data path
    augmented_path = os.path.join('..', '..', 'data', 'global_cricket_players_fixed_augmented_rich_v2.json')

if os.path.exists(augmented_path):
    try:
        with open(augmented_path, 'r', encoding='utf-8') as f:
            aug_list = json.load(f)
            # aug_list may be list of players or dict; normalize to name->record
            if isinstance(aug_list, dict):
                # assume keys are player names
                augmented_players = aug_list
            elif isinstance(aug_list, list):
                for p in aug_list:
                    name = p.get('player') or p.get('name')
                    if name:
                        augmented_players[name] = p
    except Exception as e:
        print(f"⚠️ Warning: failed to load augmented players file: {e}")
else:
    # look for file in data/ (sibling of project root) as final fallback
    alt = os.path.join('..', 'data', 'global_cricket_players_fixed_augmented_rich_v2.json')
    if os.path.exists(alt):
        try:
            with open(alt, 'r', encoding='utf-8') as f:
                aug_list = json.load(f)
                if isinstance(aug_list, dict):
                    augmented_players = aug_list
                elif isinstance(aug_list, list):
                    for p in aug_list:
                        name = p.get('player') or p.get('name')
                        if name:
                            augmented_players[name] = p
        except Exception as e:
            print(f"⚠️ Warning: failed to load augmented players file (alt): {e}")

if len(augmented_players) > 0:
    print(f"✅ Loaded augmented player insights for {len(augmented_players)} players")
else:
    print("ℹ️ No augmented player insights file found; continuing without it")

def analyze_player_complete(player_name):
    """
    Complete analysis with all 12 feature categories
    """
    
    print("\n" + "="*70)
    print(f"🏏 COMPLETE PLAYER ANALYSIS: {player_name}")
    print("="*70)
    
    # Find player
    player_batting = batting_stats[batting_stats['player'].str.contains(player_name, case=False, na=False)]
    player_bowling = bowling_stats[bowling_stats['player'].str.contains(player_name, case=False, na=False)]
    
    if len(player_batting) == 0 and len(player_bowling) == 0:
        print(f"❌ Player '{player_name}' not found in database")
        return None
    
    # Get exact player name
    if len(player_batting) > 0:
        exact_name = player_batting.iloc[0]['player']
    else:
        exact_name = player_bowling.iloc[0]['player']
    
    print(f"\n✅ Found: {exact_name}")
    
    # Get role
    role_data = player_roles[player_roles['player'] == exact_name]
    role = role_data.iloc[0]['role'] if len(role_data) > 0 else "Unknown"
    batting_position = role_data.iloc[0]['batting_position'] if len(role_data) > 0 else "Unknown"
    
    # Get special shot
    shot_data = special_shots[special_shots['player'] == exact_name]
    special_shot = shot_data.iloc[0]['special_shot'] if len(shot_data) > 0 else "Not Available"
    signature_style = shot_data.iloc[0]['signature_style'] if len(shot_data) > 0 else "Balanced"
    
    print(f"\n👤 PLAYER PROFILE:")
    print(f"   Role: {role}")
    print(f"   Batting Position: {batting_position}")
    print(f"   Playing Style: {signature_style}")
    print(f"   Signature Shot: {special_shot}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 1️⃣ BATTING PERFORMANCE FEATURES
    # ═══════════════════════════════════════════════════════════════════
    
    if len(player_batting) > 0:
        bat_stats = player_batting.iloc[0]
        
        print(f"\n{'='*70}")
        print("1️⃣ BATTING PERFORMANCE")
        print('='*70)
        
        print(f"\n📊 Career Statistics:")
        print(f"   Innings Played: {int(bat_stats['innings_played'])}")
        print(f"   Total Runs: {int(bat_stats['total_runs'])}")
        print(f"   Batting Average: {bat_stats['batting_average']:.2f}")
        print(f"   Strike Rate: {bat_stats['avg_strike_rate']:.2f}")
        print(f"   Highest Score: {int(bat_stats['highest_score'])}")
        
        print(f"\n🎯 Boundary Analysis:")
        print(f"   Total Fours: {int(bat_stats['total_fours'])}")
        print(f"   Total Sixes: {int(bat_stats['total_sixes'])}")
        print(f"   Boundary %: {bat_stats['avg_boundary_pct']:.1f}%")
        print(f"   Dot Ball %: {bat_stats['avg_dot_pct']:.1f}%")
        
        print(f"\n⚡ Performance Metrics:")
        print(f"   Runs per Innings: {bat_stats['avg_runs_per_innings']:.2f}")
        print(f"   Consistency Score: {bat_stats['consistency_score']:.1f}/100")
        
        # Calculate ratings
        sr_rating = min(bat_stats['avg_strike_rate'] / 150 * 100, 100)
        avg_rating = min(bat_stats['batting_average'] / 50 * 100, 100)
        boundary_rating = bat_stats['avg_boundary_pct'] * 5
        
        overall_batting = (sr_rating * 0.3 + avg_rating * 0.4 + boundary_rating * 0.3)
        
        print(f"\n⭐ Overall Batting Rating: {overall_batting:.1f}/100")
        
        if overall_batting >= 80:
            grade = "A+ (Elite)"
        elif overall_batting >= 70:
            grade = "A (Excellent)"
        elif overall_batting >= 60:
            grade = "B (Good)"
        elif overall_batting >= 50:
            grade = "C (Average)"
        else:
            grade = "D (Below Average)"
        
        print(f"   Grade: {grade}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 2️⃣ BOWLING PERFORMANCE FEATURES
    # ═══════════════════════════════════════════════════════════════════
    
    if len(player_bowling) > 0:
        bowl_stats = player_bowling.iloc[0]
        
        print(f"\n{'='*70}")
        print("2️⃣ BOWLING PERFORMANCE")
        print('='*70)
        
        print(f"\n📊 Career Statistics:")
        print(f"   Spells Bowled: {int(bowl_stats['spells_bowled'])}")
        print(f"   Total Wickets: {int(bowl_stats['total_wickets'])}")
        print(f"   Bowling Average: {bowl_stats['bowling_average']:.2f}")
        print(f"   Economy Rate: {bowl_stats['avg_economy']:.2f}")
        print(f"   Strike Rate: {bowl_stats['avg_bowling_sr']:.2f} balls/wicket")
        
        print(f"\n🎯 Control Metrics:")
        print(f"   Dot Ball %: {bowl_stats['avg_dot_pct']:.1f}%")
        print(f"   Wickets per Spell: {bowl_stats['avg_wickets_per_spell']:.2f}")
        
        # Calculate ratings
        economy_rating = max(100 - (bowl_stats['avg_economy'] - 5) * 10, 0)
        wicket_rating = min(bowl_stats['total_wickets'] / 50 * 100, 100)
        dot_rating = bowl_stats['avg_dot_pct']
        
        overall_bowling = (economy_rating * 0.4 + wicket_rating * 0.3 + dot_rating * 0.3)
        
        print(f"\n⭐ Overall Bowling Rating: {overall_bowling:.1f}/100")
        
        if overall_bowling >= 80:
            grade = "A+ (Elite)"
        elif overall_bowling >= 70:
            grade = "A (Excellent)"
        elif overall_bowling >= 60:
            grade = "B (Good)"
        elif overall_bowling >= 50:
            grade = "C (Average)"
        else:
            grade = "D (Below Average)"
        
        print(f"   Grade: {grade}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 3️⃣ FIELDING PERFORMANCE (Estimated)
    # ═══════════════════════════════════════════════════════════════════
    
    print(f"\n{'='*70}")
    print("3️⃣ FIELDING PERFORMANCE")
    print('='*70)
    
    # Estimate based on role
    if 'Wicket' in role or 'keeper' in role.lower():
        fielding_role = "Wicket-Keeper"
        estimated_catches = "High (WK)"
    elif 'All-Rounder' in role:
        fielding_role = "Key Fielder"
        estimated_catches = "Above Average"
    else:
        fielding_role = "Regular Fielder"
        estimated_catches = "Average"
    
    print(f"   Fielding Role: {fielding_role}")
    print(f"   Estimated Catching: {estimated_catches}")
    print(f"   💡 Detailed fielding stats not available in dataset")
    
    # ═══════════════════════════════════════════════════════════════════
    # 4️⃣ FORM AND CONSISTENCY METRICS
    # ═══════════════════════════════════════════════════════════════════
    
    print(f"\n{'='*70}")
    print("4️⃣ FORM & CONSISTENCY ANALYSIS")
    print('='*70)
    
    if len(player_batting) > 0:
        # Get recent performances
        recent_batting = batting_performances[batting_performances['player'] == exact_name].tail(10)
        
        if len(recent_batting) > 0:
            recent_avg = recent_batting['runs'].mean()
            recent_sr = recent_batting['strike_rate'].mean()
            career_avg = bat_stats['avg_runs_per_innings']
            
            form_indicator = (recent_avg / career_avg) if career_avg > 0 else 1
            
            print(f"\n📈 Recent Form (Last 10 innings):")
            print(f"   Recent Average: {recent_avg:.2f}")
            print(f"   Recent Strike Rate: {recent_sr:.2f}")
            print(f"   Career Average: {career_avg:.2f}")
            
            if form_indicator > 1.2:
                form_status = "🔥 EXCELLENT FORM"
            elif form_indicator > 1.0:
                form_status = "✅ GOOD FORM"
            elif form_indicator > 0.8:
                form_status = "📊 AVERAGE FORM"
            else:
                form_status = "⚠️ POOR FORM"
            
            print(f"\n   Current Form: {form_status}")
            print(f"   Form Index: {form_indicator:.2f}x career average")
            
            print(f"\n🎯 Consistency:")
            print(f"   Consistency Score: {bat_stats['consistency_score']:.1f}/100")
            
            if bat_stats['consistency_score'] > 70:
                consistency_desc = "Very Consistent - Reliable performer"
            elif bat_stats['consistency_score'] > 50:
                consistency_desc = "Moderately Consistent"
            else:
                consistency_desc = "Inconsistent - Fluctuating performances"
            
            print(f"   Assessment: {consistency_desc}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 5️⃣ PLAYER IMPACT & CONTRIBUTION INDEX
    # ═══════════════════════════════════════════════════════════════════
    
    print(f"\n{'='*70}")
    print("5️⃣ PLAYER IMPACT & CONTRIBUTION")
    print('='*70)
    
    impact_score = 0
    contributions = []
    
    if len(player_batting) > 0:
        batting_impact = (bat_stats['total_runs'] / 1000) * 30  # Up to 30 points
        batting_impact += (bat_stats['avg_strike_rate'] / 150) * 20  # Up to 20 points
        impact_score += min(batting_impact, 50)
        contributions.append(f"Batting: {batting_impact:.1f} points")
    
    if len(player_bowling) > 0:
        bowling_impact = (bowl_stats['total_wickets'] / 50) * 30  # Up to 30 points
        bowling_impact += max(0, (8 - bowl_stats['avg_economy'])) * 5  # Up to 15 points
        impact_score += min(bowling_impact, 50)
        contributions.append(f"Bowling: {bowling_impact:.1f} points")
    
    print(f"\n🌟 Total Impact Score: {impact_score:.1f}/100")
    
    for contrib in contributions:
        print(f"   • {contrib}")
    
    if impact_score >= 80:
        impact_level = "⭐⭐⭐⭐⭐ Match Winner"
    elif impact_score >= 60:
        impact_level = "⭐⭐⭐⭐ Key Player"
    elif impact_score >= 40:
        impact_level = "⭐⭐⭐ Regular Contributor"
    else:
        impact_level = "⭐⭐ Squad Member"
    
    print(f"\n   Impact Level: {impact_level}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 6️⃣ VENUE-BASED PERFORMANCE
    # ═══════════════════════════════════════════════════════════════════
    
    print(f"\n{'='*70}")
    print("6️⃣ VENUE-SPECIFIC PERFORMANCE")
    print('='*70)
    
    if len(player_batting) > 0:
        player_venue_data = batting_performances[batting_performances['player'] == exact_name]
        
        venue_performance = player_venue_data.groupby('venue').agg({
            'runs': ['sum', 'mean', 'count'],
            'strike_rate': 'mean'
        }).reset_index()
        
        venue_performance.columns = ['venue', 'total_runs', 'avg_runs', 'matches', 'avg_sr']
        venue_performance = venue_performance.sort_values('total_runs', ascending=False).head(5)
        
        print(f"\n🏟️ Top 5 Venues:")
        for i, row in venue_performance.iterrows():
            print(f"\n   {row['venue'][:40]}")
            print(f"      Matches: {int(row['matches'])} | Avg: {row['avg_runs']:.1f} | SR: {row['avg_sr']:.1f}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 7️⃣ MATCH SITUATION PERFORMANCE
    # ═══════════════════════════════════════════════════════════════════
    
    print(f"\n{'='*70}")
    print("7️⃣ MATCH SITUATION ANALYSIS")
    print('='*70)
    
    if len(player_batting) > 0:
        player_innings = batting_performances[batting_performances['player'] == exact_name]
        
        # Batting first vs chasing
        batting_first = player_innings[player_innings['innings'] == 1]
        chasing = player_innings[player_innings['innings'] == 2]
        
        print(f"\n📊 Innings-wise Performance:")
        print(f"   Batting First: {len(batting_first)} innings, Avg: {batting_first['runs'].mean():.1f}")
        print(f"   Chasing: {len(chasing)} innings, Avg: {chasing['runs'].mean():.1f}")
        
        if batting_first['runs'].mean() > chasing['runs'].mean():
            situation_strength = "Better when batting first"
        else:
            situation_strength = "Better when chasing"
        
        print(f"\n   Strength: {situation_strength}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 8️⃣ AI & PREDICTIVE ANALYTICS
    # ═══════════════════════════════════════════════════════════════════
    
    print(f"\n{'='*70}")
    print("8️⃣ AI-POWERED PREDICTIONS")
    print('='*70)
    
    if len(player_batting) > 0:
        # Predict next innings score based on recent form
        recent = batting_performances[batting_performances['player'] == exact_name].tail(10)
        
        if len(recent) >= 5:
            predicted_runs = recent['runs'].mean()
            predicted_sr = recent['strike_rate'].mean()
            
            print(f"\n🔮 Next Innings Prediction:")
            print(f"   Expected Runs: {predicted_runs:.0f} (±15)")
            print(f"   Expected Strike Rate: {predicted_sr:.0f}")
            
            if predicted_runs > 40:
                prediction_conf = "High probability of good performance"
            elif predicted_runs > 25:
                prediction_conf = "Moderate performance expected"
            else:
                prediction_conf = "Below-average performance likely"
            
            print(f"   Confidence: {prediction_conf}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 9️⃣ PLAYER COMPARISON
    # ═══════════════════════════════════════════════════════════════════
    
    print(f"\n{'='*70}")
    print("9️⃣ PLAYER COMPARISON & RANKING")
    print('='*70)
    
    if len(player_batting) > 0:
        # Rank among all players
        batting_stats_sorted = batting_stats.sort_values('total_runs', ascending=False)
        rank = batting_stats_sorted[batting_stats_sorted['player'] == exact_name].index[0] + 1
        
        print(f"\n📊 Rankings:")
        print(f"   Overall Rank: #{rank} out of {len(batting_stats)} batsmen")
        print(f"   Percentile: Top {rank/len(batting_stats)*100:.1f}%")
        
        # Find similar players
        player_sr = bat_stats['avg_strike_rate']
        player_avg = bat_stats['batting_average']
        
        similar = batting_stats[
            (abs(batting_stats['avg_strike_rate'] - player_sr) < 15) &
            (abs(batting_stats['batting_average'] - player_avg) < 10) &
            (batting_stats['player'] != exact_name)
        ].head(3)
        
        if len(similar) > 0:
            print(f"\n👥 Similar Players:")
            for _, sim in similar.iterrows():
                print(f"   • {sim['player']}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 🔟 SENTIMENT & PSYCHOLOGICAL FACTORS (Estimated)
    # ═══════════════════════════════════════════════════════════════════
    
    print(f"\n{'='*70}")
    print("🔟 PSYCHOLOGICAL PROFILE")
    print('='*70)
    
    if len(player_batting) > 0:
        if bat_stats['avg_strike_rate'] > 140:
            mindset = "Aggressive - Risk Taker"
        elif bat_stats['avg_strike_rate'] > 120:
            mindset = "Balanced - Smart Aggression"
        else:
            mindset = "Conservative - Builds Innings"
        
        print(f"\n🧠 Playing Mindset: {mindset}")
        
        if bat_stats['consistency_score'] > 70:
            pressure = "Handles pressure well - Consistent performer"
        else:
            pressure = "Fluctuates under pressure"
        
        print(f"   Pressure Handling: {pressure}")

        # ═══════════════════════════════════════════════════════════════════
        # 1️⃣3️⃣ AUGMENTED PLAYER INSIGHTS (if available)
        # ═══════════════════════════════════════════════════════════════════

        def _print_insights(insights, indent=3):
            if not insights:
                print(' ' * indent + 'No augmented insights available for this player')
                return
            for k, v in insights.items():
                if isinstance(v, dict):
                    print(' ' * indent + f"{k}:")
                    for kk, vv in v.items():
                        print(' ' * (indent+3) + f"{kk}: {vv}")
                else:
                    print(' ' * indent + f"{k}: {v}")

        # try to find augmented record (exact match first, then case-insensitive)
        insights_record = None
        if exact_name in augmented_players:
            insights_record = augmented_players.get(exact_name)
        else:
            # case-insensitive search
            for k, v in augmented_players.items():
                if k and k.lower() == exact_name.lower():
                    insights_record = v
                    break

        print(f"\n{'='*70}")
        print("1️⃣3️⃣ AUGMENTED PLAYER INSIGHTS (Merged)")
        print('='*70)

        if insights_record is None:
            print("   No augmented insights found for this player in the augmented dataset.")
        else:
            # if the record contains a nested `player_insights` block, print it; otherwise print the whole record
            player_insights = insights_record.get('player_insights') if isinstance(insights_record, dict) else None
            if player_insights:
                _print_insights(player_insights, indent=4)
            else:
                # print top-level keys of the augmented record (excluding player)
                print('    Augmented record:')
                to_show = {k: v for k, v in insights_record.items() if k != 'player'}
                _print_insights(to_show, indent=6)
    
    # ═══════════════════════════════════════════════════════════════════
    # 1️⃣1️⃣ VISUALIZATION SUMMARY
    # ═══════════════════════════════════════════════════════════════════
    
    print(f"\n{'='*70}")
    print("1️⃣1️⃣ PERFORMANCE VISUALIZATION")
    print('='*70)
    
    if len(player_batting) > 0:
        recent_10 = batting_performances[batting_performances['player'] == exact_name].tail(10)
        
        print(f"\n📈 Last 10 Innings Trend:")
        print(f"   Innings: ", end="")
        for i in range(1, 11):
            print(f"{i:3d}", end=" ")
        print(f"\n   Runs:    ", end="")
        
        for _, row in recent_10.iterrows():
            runs = int(row['runs'])
            print(f"{runs:3d}", end=" ")
        
        print(f"\n   Form:    ", end="")
        for _, row in recent_10.iterrows():
            runs = int(row['runs'])
            if runs >= 50:
                print(" 🔥 ", end=" ")
            elif runs >= 30:
                print(" ✅ ", end=" ")
            elif runs >= 15:
                print(" 📊 ", end=" ")
            else:
                print(" ⚠️ ", end=" ")
        print()
    
    # ═══════════════════════════════════════════════════════════════════
    # 1️⃣2️⃣ OVERALL PLAYER SCORE
    # ═══════════════════════════════════════════════════════════════════
    
    print(f"\n{'='*70}")
    print("1️⃣2️⃣ OVERALL PLAYER PERFORMANCE SCORE")
    print('='*70)
    
    overall_score = 0
    score_breakdown = []
    
    if len(player_batting) > 0:
        bat_component = min((bat_stats['total_runs'] / 2000) * 40, 40)
        sr_component = min((bat_stats['avg_strike_rate'] / 150) * 20, 20)
        avg_component = min((bat_stats['batting_average'] / 50) * 20, 20)
        
        overall_score += bat_component + sr_component + avg_component
        score_breakdown.append(f"Batting: {bat_component + sr_component + avg_component:.1f}/80")
    
    if len(player_bowling) > 0:
        bowl_component = min((bowl_stats['total_wickets'] / 100) * 30, 30)
        econ_component = max(0, (8 - bowl_stats['avg_economy']) * 3)
        
        overall_score += bowl_component + econ_component
        score_breakdown.append(f"Bowling: {bowl_component + econ_component:.1f}/40")
    
    print(f"\n🏆 COMPOSITE PERFORMANCE INDEX: {overall_score:.1f}/100")
    
    for breakdown in score_breakdown:
        print(f"   • {breakdown}")
    
    # Final rating
    if overall_score >= 85:
        final_rating = "⭐⭐⭐⭐⭐ WORLD CLASS"
    elif overall_score >= 70:
        final_rating = "⭐⭐⭐⭐ INTERNATIONAL QUALITY"
    elif overall_score >= 55:
        final_rating = "⭐⭐⭐ SOLID PLAYER"
    elif overall_score >= 40:
        final_rating = "⭐⭐ DEVELOPING PLAYER"
    else:
        final_rating = "⭐ SQUAD MEMBER"
    
    print(f"\n   Final Rating: {final_rating}")
    
    # Recommendation
    print(f"\n📝 TEAM SELECTION RECOMMENDATION:")
    
    if overall_score >= 70:
        print(f"   ✅ MUST PICK - Core team member")
        print(f"   Should bat at position: {batting_position}")
    elif overall_score >= 55:
        print(f"   ✅ REGULAR SELECTION - Reliable option")
        print(f"   Best position: {batting_position}")
    elif overall_score >= 40:
        print(f"   ⚠️ SITUATIONAL PICK - Based on conditions")
    else:
        print(f"   ❌ RESERVE - Needs improvement")
    
    print("\n" + "="*70)
    
    result = {
        'player': exact_name,
        'role': role,
        'overall_score': overall_score,
        'special_shot': special_shot
    }

    # include augmented insights in return payload when available
    if insights_record is not None:
        result['augmented_record'] = insights_record

    return result

def search_player():
    """Interactive player search"""
    
    print("\n🔍 PLAYER SEARCH")
    print("="*70)
    
    print(f"\n📊 Database: {len(batting_stats)} batsmen, {len(bowling_stats)} bowlers")
    
    # Show some top players
    print(f"\n🌟 Top 10 Run Scorers:")
    top_batsmen = batting_stats.nlargest(10, 'total_runs')
    for i, row in top_batsmen.iterrows():
        print(f"   {i+1:2d}. {row['player']:30s} ({int(row['total_runs'])} runs)")
    
    print(f"\n🎯 Top 10 Wicket Takers:")
    top_bowlers = bowling_stats.nlargest(10, 'total_wickets')
    for i, row in top_bowlers.iterrows():
        print(f"   {i+1:2d}. {row['player']:30s} ({int(row['total_wickets'])} wickets)")
    
    print(f"\n💡 Enter player name (or part of name):")
    player_input = input("   → ").strip()
    
    # Search
    matching_bat = batting_stats[batting_stats['player'].str.contains(player_input, case=False, na=False)]
    matching_bowl = bowling_stats[bowling_stats['player'].str.contains(player_input, case=False, na=False)]
    
    all_matches = pd.concat([
        matching_bat[['player']],
        matching_bowl[['player']]
    ]).drop_duplicates()
    
    if len(all_matches) == 0:
        print(f"\n❌ No players found matching '{player_input}'")
        return
    
    if len(all_matches) == 1:
        player_name = all_matches.iloc[0]['player']
        analyze_player_complete(player_name)
    else:
        print(f"\n✅ Found {len(all_matches)} players:")
        for i, row in all_matches.iterrows():
            print(f"   {i+1}. {row['player']}")
        
        print(f"\n   Select player number: ", end="")
        try:
            choice = int(input()) - 1
            if 0 <= choice < len(all_matches):
                player_name = all_matches.iloc[choice]['player']
                analyze_player_complete(player_name)
        except:
            print("   Invalid selection")
    
    # Another search?
    print(f"\n\n🔄 Analyze another player? (y/n): ", end="")
    if input().strip().lower() == 'y':
        search_player()

# Run
if __name__ == "__main__":
    try:
        search_player()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")