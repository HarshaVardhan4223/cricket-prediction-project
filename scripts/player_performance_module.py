import pickle
import sys
import os
import pandas as pd

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("🏏 CRICKET PLAYER PERFORMANCE ANALYZER")
print("="*70)
print("Comprehensive Player Analysis | 12+ Feature Categories")
print("="*70)

# Load player database
print("\n⏳ Loading player database...")

try:
    db_path = os.path.join(project_root, 'models', 'player_database_enhanced.pkl')
    
    with open(db_path, 'rb') as f:
        player_database = pickle.load(f)
    
    print(f"✅ Database loaded: {len(player_database)} players available")
    
except FileNotFoundError:
    print("❌ Error: Player database not found!")
    print("\n💡 Run: python scripts/build_player_database_enhanced.py")
    sys.exit(1)

def show_all_players():
    """Display all available players"""
    players = sorted(player_database.keys())
    print(f"\n👥 AVAILABLE PLAYERS ({len(players)} players):")
    print("="*70)
    print("💡 Tip: Type player number or search by name")
    print("-"*70)
    
    # Display in 3 columns
    for i in range(0, len(players), 3):
        row = players[i:i+3]
        line = ""
        for j, player in enumerate(row):
            line += f"{i+j+1:3d}. {player:22s} "
        print(line)
    
    return players

def show_top_performers():
    """Show top 10 performers by overall score"""
    print("\n🏆 TOP 10 PERFORMERS:")
    print("="*70)
    
    # Sort by overall score
    sorted_players = sorted(
        player_database.items(),
        key=lambda x: x[1]['overall_score'],
        reverse=True
    )[:10]
    
    for i, (player, profile) in enumerate(sorted_players, 1):
        role = profile['classification']['primary_role']
        score = profile['overall_score']
        print(f"{i:2d}. {player:30s} {role:20s} Score: {score}/100")
    
    print("="*70)

def display_player_profile(player_name):
    """Display comprehensive player profile"""
    
    if player_name not in player_database:
        print(f"\n❌ Player '{player_name}' not found in database!")
        return
    
    profile = player_database[player_name]
    
    # Header
    print("\n" + "="*70)
    print(f"🌟 PLAYER PROFILE: {player_name.upper()}")
    print("="*70)
    
    # Overall Score
    score = profile['overall_score']
    rating = "⭐⭐⭐⭐⭐" if score >= 80 else "⭐⭐⭐⭐" if score >= 60 else "⭐⭐⭐"
    print(f"\n🎯 OVERALL PERFORMANCE SCORE: {score}/100 {rating}")
    
    # Classification
    print(f"\n📋 PLAYER CLASSIFICATION:")
    print(f"   Primary Role: {profile['classification']['primary_role']}")
    print(f"   Category: {profile['classification']['category']}")
    print(f"   Playing Style: {profile['classification']['playing_style']}")
    print(f"   🎯 Ideal Team Position: {profile['classification']['ideal_team_position']}")
    
    # Batting Performance
    print(f"\n🏏 BATTING PERFORMANCE:")
    bat = profile['batting']
    if bat['matches'] > 0:
        print(f"   Matches: {bat['matches']} | Innings: {bat['innings']}")
        print(f"   Total Runs: {bat['total_runs']} | Highest: {bat['highest_score']}")
        print(f"   Average: {bat['average']} | Strike Rate: {bat['strike_rate']}")
        print(f"   Centuries: {bat['hundreds']} | Half-Centuries: {bat['fifties']}")
        print(f"   Boundaries: {bat['boundaries']['fours']} Fours, {bat['boundaries']['sixes']} Sixes")
        print(f"   🎯 Signature Shots: {', '.join(bat['signature_shots'])}")
        print(f"   💪 Power Hitting: {bat['power_hitting_ability']} sixes/match")
        print(f"   📊 Best Position: {bat['best_position']}")
    else:
        print("   No batting records available")
    
    # Bowling Performance
    print(f"\n🎯 BOWLING PERFORMANCE:")
    bowl = profile['bowling']
    if bowl['matches'] > 0:
        print(f"   Matches: {bowl['matches']} | Wickets: {bowl['total_wickets']}")
        print(f"   Best Figures: {bowl['best_figures']}")
        print(f"   Average: {bowl['average']} | Economy: {bowl['economy']}")
        print(f"   Strike Rate: {bowl['strike_rate']} balls/wicket")
        print(f"   5-Wicket Hauls: {bowl['five_wickets']}")
        print(f"   🎾 Bowling Type: {bowl['bowling_type']}")
        print(f"   ⚡ Special Deliveries: {', '.join(bowl['special_deliveries'])}")
        print(f"   💀 Death Bowling: {bowl['death_bowling_skill']*100:.0f}% effectiveness")
        print(f"   ⚡ Powerplay Skill: {bowl['powerplay_skill']*100:.0f}% effectiveness")
    else:
        print("   No bowling records available")
    
    # Fielding
    print(f"\n🧤 FIELDING PERFORMANCE:")
    field = profile['fielding']
    print(f"   Catches: {field['catches']} | Run Outs: {field['run_outs']}")
    print(f"   Stumpings: {field['stumpings']}")
    print(f"   Efficiency: {field['fielding_efficiency']*100:.0f}%")
    print(f"   Preferred Position: {field['preferred_position']}")
    
    # Form & Consistency
    print(f"\n⚡ CURRENT FORM & CONSISTENCY:")
    form = profile['form']
    print(f"   Current Form Score: {form['current_form']}/100")
    print(f"   Last 10 Matches (Batting): {form['last_10_matches']['batting_avg']} avg")
    print(f"   Last 10 Matches (Bowling): {form['last_10_matches']['bowling_avg']} wkts/match")
    print(f"   Form Trend: {form['form_trend']}")
    print(f"   Confidence Level: {form['confidence_level']*100:.0f}%")
    
    # Impact Index
    print(f"\n🧠 PLAYER IMPACT & CONTRIBUTION:")
    impact = profile['impact']
    print(f"   Overall Impact Index: {impact['overall_impact']:.2f}")
    print(f"   Batting Contribution: {impact['batting_contribution']}%")
    print(f"   Bowling Contribution: {impact['bowling_contribution']}%")
    print(f"   Match Winner Rating: {impact['match_winner_rating']*100:.0f}%")
    print(f"   🔥 Clutch Performance: {impact['clutch_performance']*100:.0f}%")
    
    # Venue Performance
    print(f"\n📈 VENUE & ADAPTABILITY:")
    venue = profile['venue_performance']
    print(f"   Home Advantage: {venue['home_advantage']*100:.0f}%")
    print(f"   Best Venues: {', '.join(venue['best_venues'][:3])}")
    print(f"   Venue Adaptability: {venue['venue_adaptability']*100:.0f}%")
    
    # Match Conditions
    print(f"\n🌦 MATCH CONDITIONS PERFORMANCE:")
    cond = profile['conditions']
    print(f"   Day Matches: {cond['day_performance']*100:.0f}%")
    print(f"   Night Matches: {cond['night_performance']*100:.0f}%")
    print(f"   Pressure Handling: {cond['pressure_handling']*100:.0f}%")
    print(f"   Chase Master: {'YES ✅' if cond['chase_master'] else 'NO'}")
    
    # Predictive Analytics
    print(f"\n🤖 AI PREDICTIVE ANALYTICS:")
    pred = profile['predictions']
    print(f"   Next Match Prediction:")
    print(f"      Expected Runs: {pred['next_match_prediction']['expected_runs']}")
    print(f"      Expected Wickets: {pred['next_match_prediction']['expected_wickets']}")
    print(f"      Confidence: {pred['next_match_prediction']['confidence']*100:.0f}%")
    print(f"   Peak Performance Probability: {pred['peak_performance_probability']*100:.0f}%")
    print(f"   Injury Risk: {pred['injury_risk']*100:.0f}%")
    
    print("\n" + "="*70)

def compare_players(player1, player2):
    """Compare two players side by side"""
    
    if player1 not in player_database or player2 not in player_database:
        print("\n❌ One or both players not found!")
        return
    
    p1 = player_database[player1]
    p2 = player_database[player2]
    
    print("\n" + "="*70)
    print(f"🆚 PLAYER COMPARISON")
    print("="*70)
    print(f"\n{player1:35s} vs {player2}")
    print("-"*70)
    
    # Overall Scores
    print(f"\n🎯 OVERALL PERFORMANCE SCORE:")
    print(f"   {player1}: {p1['overall_score']}/100")
    print(f"   {player2}: {p2['overall_score']}/100")
    winner = player1 if p1['overall_score'] > p2['overall_score'] else player2
    print(f"   🏆 Edge: {winner}")
    
    # Batting Comparison
    print(f"\n🏏 BATTING COMPARISON:")
    print(f"   {'Metric':<25s} {player1[:20]:>20s} {player2[:20]:>20s}")
    print(f"   {'-'*25} {'-'*20} {'-'*20}")
    print(f"   {'Matches':<25s} {p1['batting']['matches']:>20d} {p2['batting']['matches']:>20d}")
    print(f"   {'Total Runs':<25s} {p1['batting']['total_runs']:>20d} {p2['batting']['total_runs']:>20d}")
    print(f"   {'Average':<25s} {p1['batting']['average']:>20.2f} {p2['batting']['average']:>20.2f}")
    print(f"   {'Strike Rate':<25s} {p1['batting']['strike_rate']:>20.2f} {p2['batting']['strike_rate']:>20.2f}")
    print(f"   {'Centuries':<25s} {p1['batting']['hundreds']:>20d} {p2['batting']['hundreds']:>20d}")
    print(f"   {'Half-Centuries':<25s} {p1['batting']['fifties']:>20d} {p2['batting']['fifties']:>20d}")
    
    # Bowling Comparison
    print(f"\n🎯 BOWLING COMPARISON:")
    print(f"   {'Metric':<25s} {player1[:20]:>20s} {player2[:20]:>20s}")
    print(f"   {'-'*25} {'-'*20} {'-'*20}")
    print(f"   {'Wickets':<25s} {p1['bowling']['total_wickets']:>20d} {p2['bowling']['total_wickets']:>20d}")
    print(f"   {'Average':<25s} {p1['bowling']['average']:>20.2f} {p2['bowling']['average']:>20.2f}")
    print(f"   {'Economy':<25s} {p1['bowling']['economy']:>20.2f} {p2['bowling']['economy']:>20.2f}")
    print(f"   {'5-Wicket Hauls':<25s} {p1['bowling']['five_wickets']:>20d} {p2['bowling']['five_wickets']:>20d}")
    
    # Impact Comparison
    print(f"\n🧠 IMPACT COMPARISON:")
    print(f"   {'Metric':<25s} {player1[:20]:>20s} {player2[:20]:>20s}")
    print(f"   {'-'*25} {'-'*20} {'-'*20}")
    print(f"   {'Impact Index':<25s} {p1['impact']['overall_impact']:>20.2f} {p2['impact']['overall_impact']:>20.2f}")
    print(f"   {'Match Winner Rating':<25s} {p1['impact']['match_winner_rating']*100:>19.1f}% {p2['impact']['match_winner_rating']*100:>19.1f}%")
    print(f"   {'Clutch Performance':<25s} {p1['impact']['clutch_performance']*100:>19.1f}% {p2['impact']['clutch_performance']*100:>19.1f}%")
    
    # Form Comparison
    print(f"\n⚡ CURRENT FORM:")
    print(f"   {player1}: {p1['form']['current_form']}/100 ({p1['form']['form_trend']})")
    print(f"   {player2}: {p2['form']['current_form']}/100 ({p2['form']['form_trend']})")
    
    print("\n" + "="*70)

def search_players_by_role(role):
    """Find players by role"""
    matching = []
    for player, profile in player_database.items():
        if role.lower() in profile['classification']['primary_role'].lower():
            matching.append((player, profile['overall_score']))
    
    matching.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n🔍 PLAYERS WITH ROLE: {role}")
    print("="*70)
    
    if matching:
        for i, (player, score) in enumerate(matching[:20], 1):
            print(f"{i:2d}. {player:35s} Score: {score}/100")
    else:
        print("   No players found with this role")
    
    print("="*70)

def interactive_menu():
    """Main interactive menu"""
    
    while True:
        print("\n" + "="*70)
        print("🏏 PLAYER PERFORMANCE ANALYZER - MAIN MENU")
        print("="*70)
        print("\n1. 👤 View Player Profile")
        print("2. 🏆 Top 10 Performers")
        print("3. 🆚 Compare Two Players")
        print("4. 🔍 Search Players by Role")
        print("5. 👥 Show All Players")
        print("6. 📊 Quick Stats")
        print("7. ❌ Exit")
        
        choice = input("\n👉 Enter your choice (1-7): ").strip()
        
        if choice == '1':
            view_player_profile()
        
        elif choice == '2':
            show_top_performers()
        
        elif choice == '3':
            compare_two_players()
        
        elif choice == '4':
            search_by_role()
        
        elif choice == '5':
            show_all_players()
        
        elif choice == '6':
            show_quick_stats()
        
        elif choice == '7':
            print("\n👋 Thank you for using Player Performance Analyzer!")
            print("="*70)
            break
        
        else:
            print("\n❌ Invalid choice! Please enter 1-7")

def view_player_profile():
    """View individual player profile"""
    players = show_all_players()
    
    print("\n👤 Enter Player Name or Number:")
    player_input = input("   → ").strip()
    
    # Check if number
    if player_input.isdigit() and int(player_input) <= len(players):
        player_name = players[int(player_input) - 1]
    else:
        # Search by name
        matching = [p for p in players if player_input.lower() in p.lower()]
        if matching:
            player_name = matching[0]
            if len(matching) > 1:
                print(f"\n   Found {len(matching)} matches:")
                for i, p in enumerate(matching[:5], 1):
                    print(f"      {i}. {p}")
                print(f"   Selected: {player_name}")
        else:
            print(f"\n❌ Player '{player_input}' not found!")
            return
    
    display_player_profile(player_name)

def compare_two_players():
    """Compare two players interface"""
    players = show_all_players()
    
    print("\n👤 Enter First Player (Name or Number):")
    player1_input = input("   → ").strip()
    
    if player1_input.isdigit() and int(player1_input) <= len(players):
        player1 = players[int(player1_input) - 1]
    else:
        matching = [p for p in players if player1_input.lower() in p.lower()]
        if matching:
            player1 = matching[0]
        else:
            print(f"❌ Player '{player1_input}' not found!")
            return
    
    print(f"   ✅ Selected: {player1}")
    
    print("\n👤 Enter Second Player (Name or Number):")
    player2_input = input("   → ").strip()
    
    if player2_input.isdigit() and int(player2_input) <= len(players):
        player2 = players[int(player2_input) - 1]
    else:
        matching = [p for p in players if player2_input.lower() in p.lower()]
        if matching:
            player2 = matching[0]
        else:
            print(f"❌ Player '{player2_input}' not found!")
            return
    
    print(f"   ✅ Selected: {player2}")
    
    compare_players(player1, player2)

def search_by_role():
    """Search players by role interface"""
    print("\n🔍 SEARCH BY ROLE:")
    print("="*70)
    print("Available roles:")
    print("   1. Specialist Batsman")
    print("   2. Specialist Bowler")
    print("   3. All-Rounder")
    print("   4. Wicket-Keeper")
    
    role_input = input("\n👉 Enter role name or number: ").strip()
    
    role_map = {
        '1': 'Batsman',
        '2': 'Bowler',
        '3': 'All-Rounder',
        '4': 'Keeper'
    }
    
    role = role_map.get(role_input, role_input)
    search_players_by_role(role)

def show_quick_stats():
    """Show quick database statistics"""
    print("\n📊 QUICK STATISTICS:")
    print("="*70)
    
    total_players = len(player_database)
    
    # Count by role
    batsmen = sum(1 for p in player_database.values() if 'Batsman' in p['classification']['primary_role'])
    bowlers = sum(1 for p in player_database.values() if 'Bowler' in p['classification']['primary_role'])
    allrounders = sum(1 for p in player_database.values() if 'All-Rounder' in p['classification']['primary_role'])
    
    print(f"\n👥 Total Players: {total_players}")
    print(f"   Batsmen: {batsmen}")
    print(f"   Bowlers: {bowlers}")
    print(f"   All-Rounders: {allrounders}")
    
    # Average scores
    avg_score = sum(p['overall_score'] for p in player_database.values()) / total_players
    print(f"\n🎯 Average Performance Score: {avg_score:.1f}/100")
    
    # Top scorer
    top_scorer = max(player_database.items(), key=lambda x: x[1]['overall_score'])
    print(f"\n🏆 Highest Rated Player:")
    print(f"   {top_scorer[0]} - {top_scorer[1]['overall_score']}/100")
    
    # Most runs
    most_runs = max(player_database.items(), key=lambda x: x[1]['batting']['total_runs'])
    print(f"\n🏏 Most Runs:")
    print(f"   {most_runs[0]} - {most_runs[1]['batting']['total_runs']} runs")
    
    # Most wickets
    most_wickets = max(player_database.items(), key=lambda x: x[1]['bowling']['total_wickets'])
    print(f"\n🎯 Most Wickets:")
    print(f"   {most_wickets[0]} - {most_wickets[1]['bowling']['total_wickets']} wickets")
    
    print("\n" + "="*70)

# Run the interactive menu
if __name__ == "__main__":
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting... Thank you!")