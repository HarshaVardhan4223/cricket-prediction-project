import json
import pandas as pd
import numpy as np

print("🏏 COMPLETE CRICKET PLAYER ANALYSIS SYSTEM")
print("="*70)
print("Global Database: 234 Players | 10 Countries")
print("="*70)

# Load the global database
try:
    players_data = []
    with open('data/global_cricket_players.json', 'r') as f:
        for line in f:
            if line.strip():  # Skip empty lines
                players_data.append(json.loads(line))
    
    df = pd.DataFrame(players_data)
    print(f"\n✅ Loaded {len(df)} players successfully!")
except Exception as e:
    print(f"❌ Error loading database: {e}")
    exit()

# Display summary
print(f"\n📊 DATABASE SUMMARY:")
print(f"   Total Players: {len(df)}")
print(f"   Countries: {df['country'].nunique()}")

print(f"\n🌍 PLAYERS BY COUNTRY:")
country_counts = df['country'].value_counts()
for country, count in country_counts.items():
    print(f"   {country:20s}: {count:3d} players")

print(f"\n⭐ YOUNG STARS: {len(df[df['is_young_star'] == 'Yes'])} players")

print(f"\n👥 PLAYERS BY ROLE:")
role_counts = df['role'].value_counts()
for role, count in role_counts.items():
    print(f"   {role:30s}: {count:3d} players")

# ════════════════════════════════════════════════════════════════════
# COMPLETE PLAYER ANALYSIS FUNCTION
# ════════════════════════════════════════════════════════════════════

def analyze_player_complete(player_name):
    """
    Complete analysis with ALL statistics from verified database
    """
    
    # Search player
    matches = df[df['player_name'].str.contains(player_name, case=False, na=False)]
    
    if len(matches) == 0:
        print(f"\n❌ Player '{player_name}' not found")
        print("\n💡 Try searching by:")
        print("   - First name only")
        print("   - Last name only")
        print("   - Partial name")
        return None
    
    if len(matches) > 1:
        print(f"\n✅ Found {len(matches)} players:")
        for i, row in matches.iterrows():
            print(f"   {i+1}. {row['player_name']} ({row['country']}) - {row['role']}")
        
        choice = int(input("\n   Select player number: ")) - 1
        player = matches.iloc[choice]
    else:
        player = matches.iloc[0]
    
    name = player['player_name']
    
    # ═══════════════════════════════════════════════════════════════════
    # HEADER
    # ═══════════════════════════════════════════════════════════════════
    
    print("\n" + "="*70)
    print(f"🏏 COMPLETE PLAYER PROFILE: {name}")
    print("="*70)
    
    # ═══════════════════════════════════════════════════════════════════
    # BASIC INFORMATION
    # ═══════════════════════════════════════════════════════════════════
    
    print(f"\n👤 BASIC INFORMATION:")
    print(f"   Full Name: {name}")
    print(f"   Country: {player['country']}")
    print(f"   Age: {player['age']} years")
    print(f"   Role: {player['role']}")
    print(f"   Batting Position: {player['batting_position']}")
    
    if player['teams'] and player['teams'] != 'N/A':
        print(f"   Current Team: {player['teams']}")
    
    if player['is_young_star'] == 'Yes':
        print(f"   🌟 STATUS: YOUNG STAR - Rising Talent!")
    
    # ═══════════════════════════════════════════════════════════════════
    # BATTING ANALYSIS
    # ═══════════════════════════════════════════════════════════════════
    
    is_batsman = ('Batsman' in player['role'] or 
                  'Keeper' in player['role'] or 
                  'All-Rounder' in player['role'])
    
    if is_batsman:
        print(f"\n{'='*70}")
        print("🏏 BATTING ANALYSIS")
        print('='*70)
        
        print(f"\n🎯 SIGNATURE SHOT:")
        print(f"   {player['special_shot']}")
        print(f"   Batting Style: {player['batting_style']}")
        
        # Check which formats have data
        has_odi = pd.notna(player.get('odi_matches')) and player.get('odi_matches', 0) > 0
        has_t20i = pd.notna(player.get('t20i_matches')) and player.get('t20i_matches', 0) > 0
        has_ipl = pd.notna(player.get('ipl_matches')) and player.get('ipl_matches', 0) > 0
        has_test = pd.notna(player.get('test_matches')) and player.get('test_matches', 0) > 0
        
        # ODI STATS
        if has_odi:
            print(f"\n📊 ODI STATISTICS:")
            print(f"   Matches: {int(player['odi_matches'])}")
            print(f"   Runs: {int(player['odi_runs'])}")
            print(f"   Average: {player['odi_average']:.2f}")
            print(f"   Strike Rate: {player['odi_strike_rate']:.2f}")
            print(f"   Highest Score: {int(player['odi_highest_score'])}")
            
            if pd.notna(player.get('odi_hundreds')):
                print(f"   Hundreds: {int(player['odi_hundreds'])}")
                print(f"   Fifties: {int(player['odi_fifties'])}")
            
            if pd.notna(player.get('odi_sixes')):
                print(f"   Sixes: {int(player['odi_sixes'])}")
            
            # Rating
            odi_rating = (player['odi_average'] / 50 * 40) + (player['odi_strike_rate'] / 100 * 30)
            if player['odi_hundreds'] > 0:
                odi_rating += (player['odi_hundreds'] / 30 * 30)
            
            print(f"\n   ⭐ ODI Rating: {min(odi_rating, 100):.1f}/100")
        
        # T20I STATS
        if has_t20i:
            print(f"\n📊 T20 INTERNATIONAL STATISTICS:")
            print(f"   Matches: {int(player['t20i_matches'])}")
            print(f"   Runs: {int(player['t20i_runs'])}")
            print(f"   Average: {player['t20i_average']:.2f}")
            print(f"   Strike Rate: {player['t20i_strike_rate']:.2f}")
            print(f"   Highest Score: {int(player['t20i_highest_score'])}")
            
            if pd.notna(player.get('t20i_hundreds')):
                print(f"   Hundreds: {int(player['t20i_hundreds'])}")
                print(f"   Fifties: {int(player['t20i_fifties'])}")
            
            if pd.notna(player.get('t20i_sixes')):
                print(f"   Sixes: {int(player['t20i_sixes'])}")
            
            # Rating
            t20_rating = (player['t20i_average'] / 40 * 30) + (player['t20i_strike_rate'] / 150 * 50)
            if player.get('t20i_hundreds', 0) > 0:
                t20_rating += 20
            
            print(f"\n   ⭐ T20I Rating: {min(t20_rating, 100):.1f}/100")
        
        # IPL STATS
        if has_ipl:
            print(f"\n📊 IPL STATISTICS:")
            print(f"   Matches: {int(player['ipl_matches'])}")
            print(f"   Runs: {int(player['ipl_runs'])}")
            print(f"   Average: {player['ipl_average']:.2f}")
            print(f"   Strike Rate: {player['ipl_strike_rate']:.2f}")
            print(f"   Highest Score: {int(player['ipl_highest_score'])}")
            
            if pd.notna(player.get('ipl_hundreds')):
                print(f"   Hundreds: {int(player['ipl_hundreds'])}")
                print(f"   Fifties: {int(player['ipl_fifties'])}")
            
            if pd.notna(player.get('ipl_sixes')):
                print(f"   Sixes: {int(player['ipl_sixes'])}")
            
            # Rating
            ipl_rating = (player['ipl_average'] / 40 * 30) + (player['ipl_strike_rate'] / 140 * 50)
            if player.get('ipl_hundreds', 0) > 0:
                ipl_rating += 20
            
            print(f"\n   ⭐ IPL Rating: {min(ipl_rating, 100):.1f}/100")
        
        # TEST STATS (if available)
        if has_test:
            print(f"\n📊 TEST STATISTICS:")
            print(f"   Matches: {int(player['test_matches'])}")
            print(f"   Runs: {int(player['test_runs'])}")
            print(f"   Average: {player['test_average']:.2f}")
            print(f"   Highest Score: {int(player['test_highest_score'])}")
            if pd.notna(player.get('test_hundreds')):
                print(f"   Hundreds: {int(player['test_hundreds'])}")
        
        # OVERALL BATTING ASSESSMENT
        if has_odi or has_t20i or has_ipl:
            total_runs = 0
            total_matches = 0
            
            if has_odi:
                total_runs += player['odi_runs']
                total_matches += player['odi_matches']
            if has_t20i:
                total_runs += player['t20i_runs']
                total_matches += player['t20i_matches']
            if has_ipl:
                total_runs += player['ipl_runs']
                total_matches += player['ipl_matches']
            
            print(f"\n💯 OVERALL CAREER:")
            print(f"   Total Matches (All formats): {int(total_matches)}")
            print(f"   Total Runs: {int(total_runs)}")
            print(f"   Average per Match: {total_runs/total_matches:.2f}")
            
            # Final Grade
            if total_runs > 10000:
                grade = "⭐⭐⭐⭐⭐ LEGEND"
            elif total_runs > 7000:
                grade = "⭐⭐⭐⭐ WORLD CLASS"
            elif total_runs > 4000:
                grade = "⭐⭐⭐ INTERNATIONAL CLASS"
            elif total_runs > 2000:
                grade = "⭐⭐ ESTABLISHED PLAYER"
            else:
                grade = "⭐ RISING PLAYER"
            
            print(f"\n   🏆 Career Grade: {grade}")
    
    # ═══════════════════════════════════════════════════════════════════
    # BOWLING ANALYSIS (FOR BOWLERS)
    # ═══════════════════════════════════════════════════════════════════
    
    is_bowler = 'Bowler' in player['role']
    
    if is_bowler:
        print(f"\n{'='*70}")
        print("🎯 BOWLING ANALYSIS")
        print('='*70)
        
        print(f"\n🎯 BOWLING SPECIALITY:")
        print(f"   {player['bowling_style']}")
        
        # Check bowling formats
        has_odi_bowl = pd.notna(player.get('odi_wickets')) and player.get('odi_wickets', 0) > 0
        has_t20i_bowl = pd.notna(player.get('t20i_wickets')) and player.get('t20i_wickets', 0) > 0
        has_ipl_bowl = pd.notna(player.get('ipl_wickets')) and player.get('ipl_wickets', 0) > 0
        
        # ODI BOWLING
        if has_odi_bowl:
            print(f"\n📊 ODI BOWLING:")
            print(f"   Matches: {int(player['odi_matches'])}")
            print(f"   Wickets: {int(player['odi_wickets'])}")
            print(f"   Bowling Average: {player['odi_bowling_average']:.2f}")
            print(f"   Economy Rate: {player['odi_economy']:.2f}")
            print(f"   Strike Rate: {player['odi_bowling_sr']:.1f} balls/wicket")
            
            if pd.notna(player.get('odi_best_bowling')):
                print(f"   Best Bowling: {player['odi_best_bowling']}")
            
            if pd.notna(player.get('odi_five_wickets')):
                print(f"   Five-wicket Hauls: {int(player['odi_five_wickets'])}")
            
            # Rating
            odi_bowl_rating = 0
            if player['odi_economy'] < 5.0:
                odi_bowl_rating += 40
            elif player['odi_economy'] < 5.5:
                odi_bowl_rating += 30
            else:
                odi_bowl_rating += 20
            
            odi_bowl_rating += min((player['odi_wickets'] / 200) * 60, 60)
            
            print(f"\n   ⭐ ODI Bowling Rating: {odi_bowl_rating:.1f}/100")
        
        # T20I BOWLING
        if has_t20i_bowl:
            print(f"\n📊 T20I BOWLING:")
            print(f"   Matches: {int(player['t20i_matches'])}")
            print(f"   Wickets: {int(player['t20i_wickets'])}")
            print(f"   Bowling Average: {player['t20i_bowling_average']:.2f}")
            print(f"   Economy Rate: {player['t20i_economy']:.2f}")
            print(f"   Strike Rate: {player['t20i_bowling_sr']:.1f} balls/wicket")
            
            if pd.notna(player.get('t20i_best_bowling')):
                print(f"   Best Bowling: {player['t20i_best_bowling']}")
            
            # Rating
            t20_bowl_rating = 0
            if player['t20i_economy'] < 7.0:
                t20_bowl_rating += 40
            elif player['t20i_economy'] < 8.0:
                t20_bowl_rating += 30
            else:
                t20_bowl_rating += 20
            
            t20_bowl_rating += min((player['t20i_wickets'] / 100) * 60, 60)
            
            print(f"\n   ⭐ T20I Bowling Rating: {t20_bowl_rating:.1f}/100")
        
        # IPL BOWLING
        if has_ipl_bowl:
            print(f"\n📊 IPL BOWLING:")
            print(f"   Matches: {int(player['ipl_matches'])}")
            print(f"   Wickets: {int(player['ipl_wickets'])}")
            print(f"   Bowling Average: {player['ipl_bowling_average']:.2f}")
            print(f"   Economy Rate: {player['ipl_economy']:.2f}")
            
            if pd.notna(player.get('ipl_best_bowling')):
                print(f"   Best Bowling: {player['ipl_best_bowling']}")
            
            # Rating
            ipl_bowl_rating = 0
            if player['ipl_economy'] < 7.5:
                ipl_bowl_rating += 40
            elif player['ipl_economy'] < 8.5:
                ipl_bowl_rating += 30
            else:
                ipl_bowl_rating += 20
            
            ipl_bowl_rating += min((player['ipl_wickets'] / 150) * 60, 60)
            
            print(f"\n   ⭐ IPL Bowling Rating: {ipl_bowl_rating:.1f}/100")
        
        # OVERALL BOWLING
        if has_odi_bowl or has_t20i_bowl or has_ipl_bowl:
            total_wickets = 0
            
            if has_odi_bowl:
                total_wickets += player['odi_wickets']
            if has_t20i_bowl:
                total_wickets += player['t20i_wickets']
            if has_ipl_bowl:
                total_wickets += player['ipl_wickets']
            
            print(f"\n💯 OVERALL BOWLING CAREER:")
            print(f"   Total Wickets (All formats): {int(total_wickets)}")
            
            # Grade
            if total_wickets > 500:
                grade = "⭐⭐⭐⭐⭐ LEGEND"
            elif total_wickets > 350:
                grade = "⭐⭐⭐⭐ WORLD CLASS"
            elif total_wickets > 200:
                grade = "⭐⭐⭐ INTERNATIONAL CLASS"
            elif total_wickets > 100:
                grade = "⭐⭐ ESTABLISHED BOWLER"
            else:
                grade = "⭐ RISING BOWLER"
            
            print(f"\n   🏆 Bowling Grade: {grade}")
    
    # ═══════════════════════════════════════════════════════════════════
    # TEAM SELECTION RECOMMENDATION
    # ═══════════════════════════════════════════════════════════════════
    
    print(f"\n{'='*70}")
    print("📝 TEAM SELECTION RECOMMENDATION")
    print('='*70)
    
    print(f"\n✅ RECOMMENDED ROLE: {player['role']}")
    print(f"✅ BATTING POSITION: {player['batting_position']}")
    
    if 'All-Rounder' in player['role']:
        print(f"\n💪 ALL-ROUNDER VALUE:")
        print(f"   • Dual threat with bat and ball")
        print(f"   • Provides team balance")
        print(f"   • Can change game momentum")
    
    if player['is_young_star'] == 'Yes':
        print(f"\n🌟 YOUNG STAR POTENTIAL:")
        print(f"   • Age: {player['age']} - Peak years ahead")
        print(f"   • High growth potential")
        print(f"   • Long-term investment")
    
    # Format recommendation
    print(f"\n🎯 BEST FORMATS:")
    
    if has_odi and is_batsman:
        if player['odi_average'] > 45:
            print(f"   ⭐ ODI - Elite performer")
        elif player['odi_average'] > 35:
            print(f"   ✅ ODI - Strong option")
    
    if has_t20i and is_batsman:
        if player['t20i_strike_rate'] > 145:
            print(f"   ⭐ T20 - Explosive player")
        elif player['t20i_strike_rate'] > 130:
            print(f"   ✅ T20 - Good option")
    
    if has_odi_bowl:
        if player['odi_economy'] < 5.0:
            print(f"   ⭐ ODI - Economical bowler")
    
    if has_t20i_bowl:
        if player['t20i_economy'] < 7.5:
            print(f"   ⭐ T20 - Death overs specialist")
    
    print("\n" + "="*70)
    
    return player

# ════════════════════════════════════════════════════════════════════
# SEARCH MENU
# ════════════════════════════════════════════════════════════════════

def search_menu():
    """Interactive search menu"""
    
    while True:
        print("\n" + "="*70)
        print("🔍 PLAYER SEARCH MENU")
        print("="*70)
        
        print("\n📋 OPTIONS:")
        print("   1. Search by player name")
        print("   2. View top run scorers (ODI)")
        print("   3. View top run scorers (T20I)")
        print("   4. View top wicket takers (ODI)")
        print("   5. View top wicket takers (T20I)")
        print("   6. View all young stars")
        print("   7. View players by country")
        print("   8. Exit")
        
        choice = input("\n   Enter choice (1-8): ").strip()
        
        if choice == '1':
            name = input("\n   Enter player name: ").strip()
            if name:
                analyze_player_complete(name)
        
        elif choice == '2':
            print("\n🏏 TOP 10 ODI RUN SCORERS:")
            top_odi = df[df['odi_runs'].notna()].nlargest(10, 'odi_runs')
            for i, row in top_odi.iterrows():
                print(f"   {i+1:2d}. {row['player_name']:30s} - {int(row['odi_runs'])} runs @ {row['odi_average']:.2f}")
        
        elif choice == '3':
            print("\n🏏 TOP 10 T20I RUN SCORERS:")
            top_t20 = df[df['t20i_runs'].notna()].nlargest(10, 't20i_runs')
            for i, row in top_t20.iterrows():
                print(f"   {i+1:2d}. {row['player_name']:30s} - {int(row['t20i_runs'])} runs @ SR {row['t20i_strike_rate']:.2f}")
        
        elif choice == '4':
            print("\n🎯 TOP 10 ODI WICKET TAKERS:")
            top_odi_bowl = df[df['odi_wickets'].notna()].nlargest(10, 'odi_wickets')
            for i, row in top_odi_bowl.iterrows():
                print(f"   {i+1:2d}. {row['player_name']:30s} - {int(row['odi_wickets'])} wickets @ {row['odi_bowling_average']:.2f}")
        
        elif choice == '5':
            print("\n🎯 TOP 10 T20I WICKET TAKERS:")
            top_t20_bowl = df[df['t20i_wickets'].notna()].nlargest(10, 't20i_wickets')
            for i, row in top_t20_bowl.iterrows():
                print(f"   {i+1:2d}. {row['player_name']:30s} - {int(row['t20i_wickets'])} wickets @ Econ {row['t20i_economy']:.2f}")
        
        elif choice == '6':
            young = df[df['is_young_star'] == 'Yes'].sort_values('age')
            print(f"\n🌟 YOUNG STARS ({len(young)} players):")
            for i, row in young.iterrows():
                print(f"   {i+1:2d}. {row['player_name']:30s} ({row['age']}) - {row['country']:15s} - {row['role']}")
        
        elif choice == '7':
            print("\n🌍 SELECT COUNTRY:")
            countries = sorted(df['country'].unique())
            for i, country in enumerate(countries, 1):
                count = len(df[df['country'] == country])
                print(f"   {i}. {country} ({count} players)")
            
            c_choice = int(input("\n   Enter number: "))
            selected_country = countries[c_choice - 1]
            
            country_players = df[df['country'] == selected_country].sort_values('player_name')
            print(f"\n🏏 {selected_country} PLAYERS ({len(country_players)}):")
            for i, row in country_players.iterrows():
                print(f"   {i+1:2d}. {row['player_name']:30s} - {row['role']}")
        
        elif choice == '8':
            print("\n👋 Thank you for using Player Analysis System!")
            break
        
        else:
            print("\n❌ Invalid choice!")

# Run
if __name__ == "__main__":
    try:
        search_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")