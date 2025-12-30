import pandas as pd
import json
import os

print("🏏 PROFESSIONAL CRICKET PLAYER ANALYSIS SYSTEM")
print("="*70)
print("Final Year Project - Complete Player Performance Module")
print("Sources: ESPNcricinfo, ICC, Official T20 Leagues")
print("Updated: January 2025")
print("="*70)

# Load master database from JSON
try:
    master_db = pd.read_json(r'E:\cricket-prediction-project\data\global_cricket_players.json')
    print(f"✅ Master Database Loaded: {len(master_db)} players across {master_db['country'].nunique()} countries")
except:
    print("❌ ERROR: 'E:\\cricket-prediction-project\\data\\global_cricket_players.json' not found! Ensure create_complete_global_database.py ran successfully.")
    exit()

def save_player_analysis(player_data, output_file='E:/cricket-prediction-project/data/player_analysis.json'):
    with open(output_file, 'a') as f:
        json.dump(player_data, f, indent=4)
        f.write('\n')
    print(f"💾 Player analysis saved to {output_file}")

def generate_summary_report():
    print("\n📊 GENERATING SUMMARY REPORT")
    summary = {
        'total_players': len(master_db),
        'countries': master_db['country'].nunique(),
        'young_stars': len(master_db[master_db['is_young_star'] == 'Yes']),
        'top_odi_batsmen': master_db[master_db['odi_runs'].notna()][['player_name', 'country', 'odi_runs', 'odi_average']].nlargest(10, 'odi_runs').to_dict('records'),
        'top_t20i_bowlers': master_db[master_db['t20i_wickets'].notna()][['player_name', 'country', 't20i_wickets', 't20i_bowling_average']].nlargest(10, 't20i_wickets').to_dict('records')
    }
    with open('E:/cricket-prediction-project/data/summary_report.json', 'w') as f:
        json.dump(summary, f, indent=4)
    print("💾 Summary report saved to E:/cricket-prediction-project/data/summary_report.json")

def export_player_ratings(output_file='E:/cricket-prediction-project/data/player_ratings.csv'):
    ratings = []
    for _, player in master_db.iterrows():
        batting_rating = 0
        bowling_rating = 0
        if 'Batsman' in player['role'] or 'Keeper' in player['role'] or 'All-Rounder' in player['role']:
            odi_avg = player['odi_average'] if pd.notna(player.get('odi_average')) else 0
            t20i_sr = player['t20i_strike_rate'] if pd.notna(player.get('t20i_strike_rate')) else 0
            ipl_avg = player['ipl_average'] if pd.notna(player.get('ipl_average')) else 0
            batting_rating = (min((odi_avg + ipl_avg) / 80 * 100, 100) * 0.5 + min(t20i_sr / 140 * 100, 100) * 0.5)
        if 'Bowler' in player['role'] or 'All-Rounder' in player['role']:
            odi_wickets = player['odi_wickets'] if pd.notna(player.get('odi_wickets')) else 0
            t20i_econ = player['t20i_economy'] if pd.notna(player.get('t20i_economy')) else 10
            ipl_wickets = player['ipl_wickets'] if pd.notna(player.get('ipl_wickets')) else 0
            bowling_rating = (min((odi_wickets + ipl_wickets) / 100 * 100, 100) * 0.5 + max(100 - (t20i_econ - 6) * 10, 0) * 0.5)
        ratings.append({
            'player_name': player['player_name'],
            'country': player['country'],
            'role': player['role'],
            'batting_rating': batting_rating,
            'bowling_rating': bowling_rating
        })
    pd.DataFrame(ratings).to_csv(output_file, index=False)
    print(f"💾 Player ratings exported to {output_file}")

def get_player_complete_profile(player_name):
    """
    Get complete player profile with accurate, role-specific information
    """
    player_master = master_db[master_db['player_name'].str.contains(player_name, case=False, na=False)]
    
    if len(player_master) == 0:
        print(f"❌ Player '{player_name}' not found in master database")
        return None
    
    if len(player_master) > 1:
        print(f"\n✅ Found {len(player_master)} players:")
        for i, row in player_master.iterrows():
            print(f"   {i+1}. {row['player_name']} ({row['country']})")
        
        choice = int(input("\n   Select player number: ")) - 1
        player_info = player_master.iloc[choice]
    else:
        player_info = player_master.iloc[0]
    
    exact_name = player_info['player_name']
    
    print("\n" + "="*70)
    print(f"🏏 COMPLETE PLAYER ANALYSIS: {exact_name}")
    print("="*70)
    
    print(f"\n👤 PLAYER PROFILE (Verified Information):")
    print(f"   Full Name: {exact_name}")
    print(f"   Country: {player_info['country']}")
    print(f"   Age: {player_info['age']} years")
    print(f"   Role: {player_info['role']}")
    print(f"   Batting Position: {player_info['batting_position']}")
    print(f"   Teams: {player_info['teams']}")
    print(f"   Formats: {player_info['formats']}")
    
    if player_info['is_young_star'] == 'Yes':
        print(f"   🌟 YOUNG STAR - Rising Talent!")
    
    is_batsman = 'Batsman' in player_info['role'] or 'Keeper' in player_info['role'] or 'All-Rounder' in player_info['role']
    
    if is_batsman:
        print(f"\n{'='*70}")
        print("🏏 BATTING ANALYSIS")
        print('='*70)
        
        print(f"\n🎯 SIGNATURE SHOT (Speciality):")
        print(f"   {player_info['special_shot']}")
        print(f"   Batting Style: {player_info['batting_style']}")
        
        if 'ODI' in player_info['formats']:
            print(f"\n📊 ODI BATTING STATISTICS:")
            print(f"   Matches: {int(player_info['odi_matches'])}")
            print(f"   Runs: {int(player_info['odi_runs'])}")
            print(f"   Average: {player_info['odi_average']:.2f}")
            print(f"   Strike Rate: {player_info['odi_strike_rate']:.2f}")
            print(f"   Hundreds: {int(player_info['odi_hundreds'])}")
            print(f"   Fifties: {int(player_info['odi_fifties'])}")
            print(f"   Highest Score: {int(player_info['odi_highest_score'])}")
        
        if 'T20I' in player_info['formats']:
            print(f"\n📊 T20I BATTING STATISTICS:")
            print(f"   Matches: {int(player_info['t20i_matches'])}")
            print(f"   Runs: {int(player_info['t20i_runs'])}")
            print(f"   Average: {player_info['t20i_average']:.2f}")
            print(f"   Strike Rate: {player_info['t20i_strike_rate']:.2f}")
            print(f"   Hundreds: {int(player_info['t20i_hundreds'])}")
            print(f"   Fifties: {int(player_info['t20i_fifties'])}")
            print(f"   Highest Score: {int(player_info['t20i_highest_score'])}")
        
        if 'IPL' in player_info['formats']:
            print(f"\n📊 IPL BATTING STATISTICS:")
            print(f"   Matches: {int(player_info['ipl_matches'])}")
            print(f"   Runs: {int(player_info['ipl_runs'])}")
            print(f"   Average: {player_info['ipl_average']:.2f}")
            print(f"   Strike Rate: {player_info['ipl_strike_rate']:.2f}")
            print(f"   Hundreds: {int(player_info['ipl_hundreds'])}")
            print(f"   Fifties: {int(player_info['ipl_fifties'])}")
            print(f"   Highest Score: {int(player_info['ipl_highest_score'])}")
        
        odi_avg = player_info['odi_average'] if 'ODI' in player_info['formats'] else 0
        t20i_sr = player_info['t20i_strike_rate'] if 'T20I' in player_info['formats'] else 0
        ipl_avg = player_info['ipl_average'] if 'IPL' in player_info['formats'] else 0
        avg_score = min((odi_avg + ipl_avg) / 80 * 100, 100)
        sr_score = min(t20i_sr / 140 * 100, 100)
        batting_rating = (avg_score * 0.5 + sr_score * 0.5)
        
        print(f"\n⭐ OVERALL BATTING RATING: {batting_rating:.1f}/100")
        if batting_rating >= 85:
            grade = "⭐⭐⭐⭐⭐ WORLD CLASS"
        elif batting_rating >= 75:
            grade = "⭐⭐⭐⭐ INTERNATIONAL CLASS"
        elif batting_rating >= 65:
            grade = "⭐⭐⭐ VERY GOOD"
        elif batting_rating >= 50:
            grade = "⭐⭐ GOOD"
        else:
            grade = "⭐ DEVELOPING"
        print(f"   Grade: {grade}")
    
    is_bowler = 'Bowler' in player_info['role'] or 'All-Rounder' in player_info['role']
    
    if is_bowler:
        print(f"\n{'='*70}")
        print("🎯 BOWLING ANALYSIS")
        print('='*70)
        
        print(f"\n🎯 BOWLING SPECIALITY:")
        print(f"   {player_info['bowling_style']}")
        
        if 'ODI' in player_info['formats'] and pd.notna(player_info.get('odi_wickets')):
            print(f"\n📊 ODI BOWLING STATISTICS:")
            print(f"   Matches: {int(player_info['odi_matches'])}")
            print(f"   Wickets: {int(player_info['odi_wickets'])}")
            print(f"   Bowling Average: {player_info['odi_bowling_average']:.2f}")
            print(f"   Economy Rate: {player_info['odi_economy']:.2f}")
            print(f"   Best Bowling: {player_info.get('odi_best_bowling', 'N/A')}")
        
        if 'T20I' in player_info['formats'] and pd.notna(player_info.get('t20i_wickets')):
            print(f"\n📊 T20I BOWLING STATISTICS:")
            print(f"   Matches: {int(player_info['t20i_matches'])}")
            print(f"   Wickets: {int(player_info['t20i_wickets'])}")
            print(f"   Bowling Average: {player_info['t20i_bowling_average']:.2f}")
            print(f"   Economy Rate: {player_info['t20i_economy']:.2f}")
            print(f"   Best Bowling: {player_info.get('t20i_best_bowling', 'N/A')}")
        
        if 'IPL' in player_info['formats'] and pd.notna(player_info.get('ipl_wickets')):
            print(f"\n📊 IPL BOWLING STATISTICS:")
            print(f"   Matches: {int(player_info['ipl_matches'])}")
            print(f"   Wickets: {int(player_info['ipl_wickets'])}")
            print(f"   Bowling Average: {player_info['ipl_bowling_average']:.2f}")
            print(f"   Economy Rate: {player_info['ipl_economy']:.2f}")
            print(f"   Best Bowling: {player_info.get('ipl_best_bowling', 'N/A')}")
        
        odi_wickets = player_info['odi_wickets'] if pd.notna(player_info.get('odi_wickets')) else 0
        t20i_econ = player_info['t20i_economy'] if pd.notna(player_info.get('t20i_economy')) else 10
        ipl_wickets = player_info['ipl_wickets'] if pd.notna(player_info.get('ipl_wickets')) else 0
        wicket_score = min((odi_wickets + ipl_wickets) / 100 * 100, 100)
        econ_score = max(100 - (t20i_econ - 6) * 10, 0)
        bowling_rating = (wicket_score * 0.5 + econ_score * 0.5)
        
        print(f"\n⭐ OVERALL BOWLING RATING: {bowling_rating:.1f}/100")
        if bowling_rating >= 85:
            grade = "⭐⭐⭐⭐⭐ WORLD CLASS"
        elif bowling_rating >= 75:
            grade = "⭐⭐⭐⭐ INTERNATIONAL CLASS"
        elif bowling_rating >= 65:
            grade = "⭐⭐⭐ VERY GOOD"
        elif bowling_rating >= 50:
            grade = "⭐⭐ GOOD"
        else:
            grade = "⭐ DEVELOPING"
        print(f"   Grade: {grade}")
    
    print(f"\n{'='*70}")
    print("📝 TEAM SELECTION RECOMMENDATION")
    print('='*70)
    
    print(f"\n✅ RECOMMENDED POSITION: {player_info['batting_position']}")
    print(f"✅ ROLE IN TEAM: {player_info['role']}")
    
    if 'All-Rounder' in player_info['role']:
        print(f"\n💪 ALL-ROUNDER ADVANTAGE:")
        print(f"   • Contributes with both bat and ball")
        print(f"   • Provides team balance in all formats")
        print(f"   • High-value player for strategic flexibility")
    
    if player_info['is_young_star'] == 'Yes':
        print(f"\n🌟 YOUNG STAR STATUS:")
        print(f"   • Future of cricket")
        print(f"   • High potential for growth")
        print(f"   • Ideal for long-term team investment")
    
    print("\n" + "="*70)
    
    result = {
        'name': exact_name,
        'role': player_info['role'],
        'special_skill': player_info['special_shot'] if is_batsman else player_info['bowling_style']
    }
    save_player_analysis(result)
    return result

def list_all_players():
    """List all players by category, country, or top performers"""
    
    print("\n" + "="*70)
    print("🏏 COMPLETE PLAYER DATABASE")
    print("="*70)
    
    print(f"\n📊 Total Players: {len(master_db)}")
    
    print(f"\n👥 BY ROLE:")
    role_counts = master_db['role'].value_counts()
    for role, count in role_counts.items():
        print(f"   {role}: {count}")
    
    print(f"\n🌍 BY COUNTRY:")
    country_counts = master_db['country'].value_counts()
    for country, count in country_counts.items():
        print(f"   {country}: {count} players")
    
    young_stars = master_db[master_db['is_young_star'] == 'Yes']
    print(f"\n🌟 YOUNG STARS ({len(young_stars)}):")
    for _, player in young_stars.iterrows():
        print(f"   • {player['player_name']} ({player['age']}) - {player['role']} ({player['country']})")
    
    print(f"\n🏏 SEARCH OPTIONS:")
    print(f"   1. Search by player name")
    print(f"   2. View all young stars")
    print(f"   3. View all-rounders")
    print(f"   4. View bowlers")
    print(f"   5. View batsmen")
    print(f"   6. View by country")
    print(f"   7. Top 5 ODI run scorers")
    print(f"   8. Top 5 T20I run scorers")
    print(f"   9. Top 5 ODI wicket-takers")
    print(f"   10. Top 5 T20I wicket-takers")
    
    choice = input(f"\n   Enter choice (1-10): ").strip()
    
    if choice == '1':
        name = input("   Enter player name: ").strip()
        get_player_complete_profile(name)
    
    elif choice == '2':
        print(f"\n🌟 YOUNG STARS:")
        for i, row in young_stars.iterrows():
            print(f"   {i+1}. {row['player_name']} ({row['country']})")
        num = int(input("\n   Select player number: ")) - 1
        get_player_complete_profile(young_stars.iloc[num]['player_name'])
    
    elif choice == '3':
        all_rounders = master_db[master_db['role'].str.contains('All-Rounder', na=False)]
        print(f"\n💪 ALL-ROUNDERS ({len(all_rounders)}):")
        for i, row in all_rounders.iterrows():
            print(f"   {i+1}. {row['player_name']} - {row['role']} ({row['country']})")
        num = int(input("\n   Select player number: ")) - 1
        get_player_complete_profile(all_rounders.iloc[num]['player_name'])
    
    elif choice == '4':
        bowlers = master_db[master_db['role'].str.contains('Bowler', na=False) & 
                           ~master_db['role'].str.contains('All-Rounder', na=False)]
        print(f"\n🎯 PURE BOWLERS ({len(bowlers)}):")
        for i, row in bowlers.iterrows():
            print(f"   {i+1}. {row['player_name']} - {row['bowling_style']} ({row['country']})")
        num = int(input("\n   Select player number: ")) - 1
        get_player_complete_profile(bowlers.iloc[num]['player_name'])
    
    elif choice == '5':
        batsmen = master_db[master_db['role'].str.contains('Batsman|Keeper', na=False) & 
                           ~master_db['role'].str.contains('All-Rounder', na=False)]
        print(f"\n🏏 PURE BATSMEN/WICKETKEEPERS ({len(batsmen)}):")
        for i, row in batsmen.iterrows():
            print(f"   {i+1}. {row['player_name']} - {row['special_shot']} ({row['country']})")
        num = int(input("\n   Select player number: ")) - 1
        get_player_complete_profile(batsmen.iloc[num]['player_name'])
    
    elif choice == '6':
        country = input("   Enter country name: ").strip()
        country_players = master_db[master_db['country'].str.contains(country, case=False, na=False)]
        if len(country_players) == 0:
            print(f"❌ No players found for {country}")
        else:
            print(f"\n🌍 PLAYERS FROM {country.upper()} ({len(country_players)}):")
            for i, row in country_players.iterrows():
                print(f"   {i+1}. {row['player_name']} - {row['role']}")
            num = int(input("\n   Select player number: ")) - 1
            get_player_complete_profile(country_players.iloc[num]['player_name'])
    
    elif choice == '7':
        print(f"\n🏏 TOP 5 ODI RUN SCORERS:")
        odi_batsmen = master_db[master_db['odi_runs'].notna()].nlargest(5, 'odi_runs')
        for i, row in odi_batsmen.iterrows():
            print(f"   {row['player_name']:20s}: {int(row['odi_runs'])} runs @ {row['odi_average']:.2f} avg")
        # Uncomment to include chart
        # generate_odi_runs_chart()
    
    elif choice == '8':
        print(f"\n🏏 TOP 5 T20I RUN SCORERS:")
        t20_batsmen = master_db[master_db['t20i_runs'].notna()].nlargest(5, 't20i_runs')
        for i, row in t20_batsmen.iterrows():
            print(f"   {row['player_name']:20s}: {int(row['t20i_runs'])} runs @ SR {row['t20i_strike_rate']:.2f}")
    
    elif choice == '9':
        print(f"\n🎯 TOP 5 ODI WICKET-TAKERS:")
        odi_bowlers = master_db[master_db['odi_wickets'].notna()].nlargest(5, 'odi_wickets')
        for i, row in odi_bowlers.iterrows():
            print(f"   {row['player_name']:20s}: {int(row['odi_wickets'])} wickets @ {row['odi_bowling_average']:.2f} avg")
    
    elif choice == '10':
        print(f"\n🎯 TOP 5 T20I WICKET-TAKERS:")
        t20_bowlers = master_db[master_db['t20i_wickets'].notna()].nlargest(5, 't20i_wickets')
        for i, row in t20_bowlers.iterrows():
            print(f"   {row['player_name']:20s}: {int(row['t20i_wickets'])} wickets @ {row['t20i_bowling_average']:.2f} avg")
    
    print(f"\n\n🔄 Search another player or category? (y/n): ", end="")
    if input().strip().lower() == 'y':
        list_all_players()

if __name__ == "__main__":
    print("\n🎮 WELCOME TO PROFESSIONAL PLAYER ANALYSIS SYSTEM")
    print("="*70)
    generate_summary_report()
    export_player_ratings()
    try:
        list_all_players()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting... Thank you!")
    except Exception as e:
        print(f"\n❌ Error: {e}")