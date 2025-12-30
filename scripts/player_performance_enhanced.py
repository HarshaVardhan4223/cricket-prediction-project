import pandas as pd
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("🏏 CRICKET PLAYER PERFORMANCE ANALYZER")
print("="*70)
print("Comprehensive Player Analysis | Based on Real Match Data")
print("="*70)

# Load player data
print("\n⏳ Loading player database...")

try:
    batting_stats_path = os.path.join(project_root, 'data', 'processed', 'players', 'batting_statistics.csv')
    bowling_stats_path = os.path.join(project_root, 'data', 'processed', 'players', 'bowling_statistics.csv')
    special_shots_path = os.path.join(project_root, 'data', 'processed', 'players', 'special_shots.csv')
    player_roles_path = os.path.join(project_root, 'data', 'processed', 'players', 'player_roles.csv')
    
    batting_df = pd.read_csv(batting_stats_path)
    bowling_df = pd.read_csv(bowling_stats_path)
    special_shots_df = pd.read_csv(special_shots_path)
    player_roles_df = pd.read_csv(player_roles_path)
    
    print(f"✅ Database loaded:")
    print(f"   Batsmen: {len(batting_df)} players")
    print(f"   Bowlers: {len(bowling_df)} players")
    print(f"   Special shots: {len(special_shots_df)} players")
    print(f"   Roles: {len(player_roles_df)} players")
    
except FileNotFoundError as e:
    print(f"❌ Error: {e}")
    print("\n💡 Run: python scripts/player_database_fixed.py")
    sys.exit(1)

def get_all_players():
    """Get list of all unique players"""
    all_players = set()
    all_players.update(batting_df['player'].tolist())
    all_players.update(bowling_df['player'].tolist())
    return sorted(list(all_players))

def calculate_overall_score(bat_stats, bowl_stats):
    """Calculate overall performance score (0-100)"""
    score = 50  # Base score
    
    if bat_stats is not None:
        # Batting contribution (max 40 points)
        avg_score = min(bat_stats['batting_average'] / 50 * 20, 20)
        sr_score = min(bat_stats['avg_strike_rate'] / 150 * 15, 15)
        consistency = min(bat_stats['consistency_score'] / 10, 5)
        score += avg_score + sr_score + consistency
    
    if bowl_stats is not None:
        # Bowling contribution (max 35 points)
        wicket_score = min(bowl_stats['total_wickets'] / 100 * 15, 15)
        economy_score = max(0, 15 - bowl_stats['avg_economy'])
        avg_score = max(0, 10 - bowl_stats['bowling_average'] / 5)
        score += wicket_score + economy_score + avg_score
    
    return round(min(score, 100), 1)

def display_player_profile(player_name):
    """Display comprehensive player profile"""
    
    # Get player data
    bat_stats = batting_df[batting_df['player'] == player_name]
    bowl_stats = bowling_df[bowling_df['player'] == player_name]
    special_shot = special_shots_df[special_shots_df['player'] == player_name]
    role = player_roles_df[player_roles_df['player'] == player_name]
    
    if bat_stats.empty and bowl_stats.empty:
        print(f"\n❌ Player '{player_name}' not found in database!")
        return
    
    # Convert to dict for easier access
    bat_dict = bat_stats.iloc[0].to_dict() if not bat_stats.empty else None
    bowl_dict = bowl_stats.iloc[0].to_dict() if not bowl_stats.empty else None
    shot_dict = special_shot.iloc[0].to_dict() if not special_shot.empty else None
    role_dict = role.iloc[0].to_dict() if not role.empty else None
    
    # Calculate overall score
    overall_score = calculate_overall_score(bat_dict, bowl_dict)
    
    # Header
    print("\n" + "="*70)
    print(f"🌟 PLAYER PROFILE: {player_name.upper()}")
    print("="*70)
    
    # Overall Score
    rating = "⭐⭐⭐⭐⭐" if overall_score >= 80 else "⭐⭐⭐⭐" if overall_score >= 60 else "⭐⭐⭐"
    print(f"\n🎯 OVERALL PERFORMANCE SCORE: {overall_score}/100 {rating}")
    
    # Classification
    if role_dict:
        print(f"\n📋 PLAYER CLASSIFICATION:")
        print(f"   Primary Role: {role_dict['role']}")
        print(f"   🎯 Ideal Batting Position: {role_dict['batting_position']}")
        if shot_dict:
            print(f"   Playing Style: {shot_dict['signature_style']}")
    
    # Batting Performance
    if bat_dict:
        print(f"\n🏏 BATTING PERFORMANCE:")
        print(f"   Matches: {int(bat_dict['innings_played'])}")
        print(f"   Total Runs: {int(bat_dict['total_runs'])} | Highest: {int(bat_dict['highest_score'])}")
        print(f"   Average: {bat_dict['batting_average']:.2f} | Strike Rate: {bat_dict['avg_strike_rate']:.2f}")
        
        # Milestones
        hundreds = len(batting_df[(batting_df['player'] == player_name)])  # Approximation
        print(f"   Boundaries: {int(bat_dict['total_fours'])} Fours, {int(bat_dict['total_sixes'])} Sixes")
        print(f"   Boundary %: {bat_dict['avg_boundary_pct']:.1f}%")
        
        if shot_dict:
            print(f"   🎯 Special Shot: {shot_dict['special_shot']}")
        
        print(f"   💪 Power Hitting: {bat_dict['total_sixes'] / bat_dict['innings_played']:.1f} sixes/match")
        print(f"   📊 Consistency Score: {bat_dict['consistency_score']:.1f}/100")
        
        # Performance rating
        if bat_dict['batting_average'] > 40:
            print(f"   ⭐ WORLD CLASS BATSMAN")
        elif bat_dict['batting_average'] > 30:
            print(f"   ✅ EXCELLENT BATSMAN")
        elif bat_dict['batting_average'] > 25:
            print(f"   ✔️  GOOD BATSMAN")
    else:
        print("\n🏏 BATTING: No significant batting records")
    
    # Bowling Performance
    if bowl_dict:
        print(f"\n🎯 BOWLING PERFORMANCE:")
        print(f"   Matches: {int(bowl_dict['spells_bowled'])}")
        print(f"   Total Wickets: {int(bowl_dict['total_wickets'])}")
        print(f"   Bowling Average: {bowl_dict['bowling_average']:.2f}")
        print(f"   Economy: {bowl_dict['avg_economy']:.2f} | Strike Rate: {bowl_dict['avg_bowling_sr']:.2f}")
        print(f"   Dot Ball %: {bowl_dict['avg_dot_pct']:.1f}%")
        print(f"   Wickets/Match: {bowl_dict['avg_wickets_per_spell']:.2f}")
        
        # Performance rating
        if bowl_dict['bowling_average'] < 20 and bowl_dict['avg_economy'] < 7:
            print(f"   ⭐ WORLD CLASS BOWLER")
        elif bowl_dict['bowling_average'] < 25 and bowl_dict['avg_economy'] < 8:
            print(f"   ✅ EXCELLENT BOWLER")
        elif bowl_dict['bowling_average'] < 30:
            print(f"   ✔️  GOOD BOWLER")
    else:
        print("\n🎯 BOWLING: No significant bowling records")
    
    # Stats Summary
    print(f"\n📊 CAREER SUMMARY:")
    if bat_dict:
        print(f"   Total Balls Faced: {int(bat_dict['total_balls'])}")
        print(f"   Total Boundaries: {int(bat_dict['total_fours'] + bat_dict['total_sixes'])}")
    if bowl_dict:
        print(f"   Total Balls Bowled: {int(bowl_dict['total_balls_bowled'])}")
        print(f"   Total Runs Conceded: {int(bowl_dict['total_runs_conceded'])}")
    
    print("\n" + "="*70)

def show_top_performers(category='overall', limit=10):
    """Show top performers"""
    print(f"\n🏆 TOP {limit} PERFORMERS - {category.upper()}")
    print("="*70)
    
    if category == 'batsman':
        top = batting_df.nlargest(limit, 'batting_average')
        for i, row in enumerate(top.itertuples(), 1):
            print(f"{i:2d}. {row.player:30s} Avg: {row.batting_average:.2f} | SR: {row.avg_strike_rate:.2f}")
    
    elif category == 'bowler':
        top = bowling_df.nsmallest(limit, 'bowling_average')
        for i, row in enumerate(top.itertuples(), 1):
            print(f"{i:2d}. {row.player:30s} Avg: {row.bowling_average:.2f} | Econ: {row.avg_economy:.2f}")
    
    elif category == 'overall':
        # Calculate scores for all players
        all_players_list = get_all_players()
        player_scores = []
        
        for player in all_players_list[:100]:  # Top 100 to save time
            bat = batting_df[batting_df['player'] == player]
            bowl = bowling_df[bowling_df['player'] == player]
            
            bat_dict = bat.iloc[0].to_dict() if not bat.empty else None
            bowl_dict = bowl.iloc[0].to_dict() if not bowl.empty else None
            
            score = calculate_overall_score(bat_dict, bowl_dict)
            player_scores.append((player, score))
        
        player_scores.sort(key=lambda x: x[1], reverse=True)
        
        for i, (player, score) in enumerate(player_scores[:limit], 1):
            role = player_roles_df[player_roles_df['player'] == player]['role'].values
            role_str = role[0] if len(role) > 0 else "Unknown"
            print(f"{i:2d}. {player:30s} {role_str:20s} Score: {score}/100")
    
    print("="*70)

def compare_players(player1, player2):
    """Compare two players"""
    print("\n" + "="*70)
    print(f"🆚 PLAYER COMPARISON")
    print("="*70)
    print(f"\n{player1:35s} vs {player2}")
    print("-"*70)
    
    # Get stats
    p1_bat = batting_df[batting_df['player'] == player1]
    p1_bowl = bowling_df[bowling_df['player'] == player1]
    p2_bat = batting_df[batting_df['player'] == player2]
    p2_bowl = bowling_df[bowling_df['player'] == player2]
    
    p1_bat_dict = p1_bat.iloc[0].to_dict() if not p1_bat.empty else None
    p1_bowl_dict = p1_bowl.iloc[0].to_dict() if not p1_bowl.empty else None
    p2_bat_dict = p2_bat.iloc[0].to_dict() if not p2_bat.empty else None
    p2_bowl_dict = p2_bowl.iloc[0].to_dict() if not p2_bowl.empty else None
    
    # Overall scores
    p1_score = calculate_overall_score(p1_bat_dict, p1_bowl_dict)
    p2_score = calculate_overall_score(p2_bat_dict, p2_bowl_dict)
    
    print(f"\n🎯 OVERALL SCORE:")
    print(f"   {player1}: {p1_score}/100")
    print(f"   {player2}: {p2_score}/100")
    print(f"   🏆 Edge: {player1 if p1_score > p2_score else player2}")
    
    # Batting comparison
    if p1_bat_dict and p2_bat_dict:
        print(f"\n🏏 BATTING COMPARISON:")
        print(f"   {'Metric':<25s} {player1[:20]:>20s} {player2[:20]:>20s}")
        print(f"   {'-'*25} {'-'*20} {'-'*20}")
        print(f"   {'Total Runs':<25s} {p1_bat_dict['total_runs']:>20.0f} {p2_bat_dict['total_runs']:>20.0f}")
        print(f"   {'Average':<25s} {p1_bat_dict['batting_average']:>20.2f} {p2_bat_dict['batting_average']:>20.2f}")
        print(f"   {'Strike Rate':<25s} {p1_bat_dict['avg_strike_rate']:>20.2f} {p2_bat_dict['avg_strike_rate']:>20.2f}")
        print(f"   {'Sixes':<25s} {p1_bat_dict['total_sixes']:>20.0f} {p2_bat_dict['total_sixes']:>20.0f}")
    
    # Bowling comparison
    if p1_bowl_dict and p2_bowl_dict:
        print(f"\n🎯 BOWLING COMPARISON:")
        print(f"   {'Metric':<25s} {player1[:20]:>20s} {player2[:20]:>20s}")
        print(f"   {'-'*25} {'-'*20} {'-'*20}")
        print(f"   {'Wickets':<25s} {p1_bowl_dict['total_wickets']:>20.0f} {p2_bowl_dict['total_wickets']:>20.0f}")
        print(f"   {'Average':<25s} {p1_bowl_dict['bowling_average']:>20.2f} {p2_bowl_dict['bowling_average']:>20.2f}")
        print(f"   {'Economy':<25s} {p1_bowl_dict['avg_economy']:>20.2f} {p2_bowl_dict['avg_economy']:>20.2f}")
    
    print("\n" + "="*70)

def search_players(search_term):
    """Search for players"""
    all_players = get_all_players()
    matching = [p for p in all_players if search_term.lower() in p.lower()]
    
    if matching:
        print(f"\n🔍 Found {len(matching)} matching players:")
        for i, player in enumerate(matching[:20], 1):
            print(f"   {i}. {player}")
        return matching
    else:
        print(f"\n❌ No players found matching '{search_term}'")
        return []

def interactive_menu():
    """Main interactive menu"""
    
    while True:
        print("\n" + "="*70)
        print("🏏 PLAYER PERFORMANCE ANALYZER - MAIN MENU")
        print("="*70)
        print("\n1. 👤 View Player Profile")
        print("2. 🏆 Top 10 Batsmen")
        print("3. 🎯 Top 10 Bowlers")
        print("4. ⭐ Top 10 Overall")
        print("5. 🆚 Compare Two Players")
        print("6. 🔍 Search Players")
        print("7. 👥 Show All Players")
        print("8. ❌ Exit")
        
        choice = input("\n👉 Enter your choice (1-8): ").strip()
        
        if choice == '1':
            player = input("\n👤 Enter player name: ").strip()
            if player:
                display_player_profile(player)
        
        elif choice == '2':
            show_top_performers('batsman')
        
        elif choice == '3':
            show_top_performers('bowler')
        
        elif choice == '4':
            show_top_performers('overall')
        
        elif choice == '5':
            p1 = input("\n👤 Enter first player: ").strip()
            p2 = input("👤 Enter second player: ").strip()
            if p1 and p2:
                compare_players(p1, p2)
        
        elif choice == '6':
            term = input("\n🔍 Enter search term: ").strip()
            if term:
                search_players(term)
        
        elif choice == '7':
            all_players = get_all_players()
            print(f"\n👥 ALL PLAYERS ({len(all_players)}):")
            for i, player in enumerate(all_players[:50], 1):
                print(f"   {i}. {player}")
            if len(all_players) > 50:
                print(f"   ... and {len(all_players) - 50} more")
        
        elif choice == '8':
            print("\n👋 Thank you for using Player Performance Analyzer!")
            print("="*70)
            break
        
        else:
            print("\n❌ Invalid choice! Please enter 1-8")

# Run
if __name__ == "__main__":
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting... Thank you!")