
import json
import pandas as pd
import numpy as np
import os

print("🏏 PROFESSIONAL CRICKET PLAYER ANALYSIS SYSTEM")
print("="*70)
print("Final Year Project - Complete Player Database")
print("="*70)

# Load master database
try:
    with open(r'E:\cricket-prediction-project\data\global_cricket_players_fixed.json', 'r') as f:
        players_data = json.load(f)
    master_db = pd.DataFrame(players_data)
    print(f"✅ Master Database Loaded: {len(master_db)} players across {master_db['country'].nunique()} countries")
except Exception as e:
    print(f"❌ ERROR: Could not load 'E:\\cricket-prediction-project\\data\\global_cricket_players_fixed.json'. Error: {e}")
    print("💡 Ensure 'fix_json_format.py' ran successfully or the file exists.")
    exit()

# Load match statistics
batting_stats = pd.DataFrame()
bowling_stats = pd.DataFrame()
batting_perf = pd.DataFrame()
bowling_perf = pd.DataFrame()

try:
    batting_stats = pd.read_csv(r'E:\cricket-prediction-project\data\processed\players\batting_statistics.csv')
    bowling_stats = pd.read_csv(r'E:\cricket-prediction-project\data\processed\players\bowling_statistics.csv')
    batting_perf = pd.read_csv(r'E:\cricket-prediction-project\data\processed\players\batting_performances.csv')
    bowling_perf = pd.read_csv(r'E:\cricket-prediction-project\data\processed\players\bowling_performances.csv')
    print(f"✅ Match Data: {len(batting_stats)} batsmen, {len(bowling_stats)} bowlers")
except Exception as e:
    print(f"⚠️ Warning: Match statistics not found. Using master database only. Error: {e}")

def export_player_ratings(output_file=r'E:\cricket-prediction-project\data\player_ratings.csv'):
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
    Get complete player profile with ACCURATE information
    """
    player_master = master_db[master_db['player_name'].str.contains(player_name, case=False, na=False)]
    
    if len(player_master) == 0:
        print(f"❌ Player '{player_name}' not found in master database")
        return None
    
    if len(player_master) > 1:
        print(f"\n✅ Found {len(player_master)} players:")
        for i, row in player_master.iterrows():
            print(f"   {i+1}. {row['player_name']} ({row['country']})")
        
        try:
            choice = int(input("\n   Select player number: ")) - 1
            player_info = player_master.iloc[choice]
        except (ValueError, IndexError):
            print("❌ Invalid selection. Exiting.")
            return None
    else:
        player_info = player_master.iloc[0]
    
    exact_name = player_info['player_name']
    
    print("\n" + "="*70)
    print(f"🏏 COMPLETE PLAYER ANALYSIS: {exact_name}")
    print("="*70)
    
    # BASIC PROFILE
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
    
    # BATTING ANALYSIS
    is_batsman = 'Batsman' in player_info['role'] or 'Keeper' in player_info['role'] or 'All-Rounder' in player_info['role']
    
    if is_batsman:
        print(f"\n{'='*70}")
        print("🏏 BATTING ANALYSIS")
        print('='*70)
        
        print(f"\n🎯 SIGNATURE SHOT (Speciality):")
        print(f"   {player_info['special_shot']}")
        print(f"   Batting Style: {player_info['batting_style']}")
        
        player_bat_stats = batting_stats[batting_stats['player'].str.contains(exact_name, case=False, na=False)] if not batting_stats.empty else pd.DataFrame()
        
        if len(player_bat_stats) > 0:
            stats = player_bat_stats.iloc[0]
            
            print(f"\n📊 CAREER STATISTICS (All Formats Combined):")
            print(f"   Innings Played: {int(stats['innings_played'])}")
            print(f"   Total Runs: {int(stats['total_runs'])}")
            print(f"   Batting Average: {stats['batting_average']:.2f}")
            print(f"   Strike Rate: {stats['avg_strike_rate']:.2f}")
            print(f"   Highest Score: {int(stats['highest_score'])}")
            
            print(f"\n🎯 BOUNDARY STATISTICS:")
            print(f"   Total Fours: {int(stats['total_fours'])}")
            print(f"   Total Sixes: {int(stats['total_sixes'])}")
            print(f"   Total Boundaries: {int(stats['total_fours'] + stats['total_sixes'])}")
            print(f"   Boundary %: {stats['avg_boundary_pct']:.1f}%")
            
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"   Runs per Innings: {stats['avg_runs_per_innings']:.2f}")
            print(f"   Consistency Score: {stats['consistency_score']:.1f}/100")
            print(f"   Dot Ball %: {stats['avg_dot_pct']:.1f}%")
            
            if not batting_perf.empty:
                player_formats = batting_perf[batting_perf['player'].str.contains(exact_name, case=False, na=False)]
                
                if len(player_formats) > 0:
                    print(f"\n📈 FORMAT-WISE BREAKDOWN:")
                    for fmt in ['ODI', 'T20', 'IPL']:
                        fmt_data = player_formats[player_formats['format'] == fmt]
                        if len(fmt_data) > 0:
                            fmt_runs = fmt_data['runs'].sum()
                            fmt_innings = len(fmt_data)
                            fmt_avg = fmt_data['runs'].mean()
                            fmt_sr = fmt_data['strike_rate'].mean()
                            
                            print(f"\n   {fmt}:")
                            print(f"      Innings: {fmt_innings} | Runs: {int(fmt_runs)}")
                            print(f"      Average: {fmt_avg:.1f} | SR: {fmt_sr:.1f}")
            
            sr_score = min(stats['avg_strike_rate'] / 140 * 100, 100)
            avg_score = min(stats['batting_average'] / 45 * 100, 100)
            consistency_score = stats['consistency_score']
            overall_rating = (sr_score * 0.3 + avg_score * 0.4 + consistency_score * 0.3)
            
            print(f"\n⭐ OVERALL BATTING RATING: {overall_rating:.1f}/100")
            
            if overall_rating >= 85:
                grade = "⭐⭐⭐⭐⭐ WORLD CLASS"
            elif overall_rating >= 75:
                grade = "⭐⭐⭐⭐ INTERNATIONAL CLASS"
            elif overall_rating >= 65:
                grade = "⭐⭐⭐ VERY GOOD"
            elif overall_rating >= 50:
                grade = "⭐⭐ GOOD"
            else:
                grade = "⭐ DEVELOPING"
            
            print(f"   Grade: {grade}")
        else:
            print(f"\n   ⚠️ No match statistics available. Using master database stats.")
            has_odi = pd.notna(player_info.get('odi_matches')) and player_info.get('odi_matches', 0) > 0
            has_t20i = pd.notna(player_info.get('t20i_matches')) and player_info.get('t20i_matches', 0) > 0
            has_ipl = pd.notna(player_info.get('ipl_matches')) and player_info.get('ipl_matches', 0) > 0
            
            if has_odi:
                print(f"\n📊 ODI STATISTICS:")
                print(f"   Matches: {int(player_info['odi_matches'])}")
                print(f"   Runs: {int(player_info['odi_runs'])}")
                print(f"   Average: {player_info['odi_average']:.2f}")
                print(f"   Strike Rate: {player_info['odi_strike_rate']:.2f}")
                print(f"   Highest Score: {int(player_info['odi_highest_score'])}")
                if pd.notna(player_info.get('odi_hundreds')):
                    print(f"   Hundreds: {int(player_info['odi_hundreds'])}")
                    print(f"   Fifties: {int(player_info['odi_fifties'])}")
                print(f"   Sixes: {int(player_info['odi_sixes']) if pd.notna(player_info.get('odi_sixes')) else 'N/A'}")
            
            if has_t20i:
                print(f"\n📊 T20I STATISTICS:")
                print(f"   Matches: {int(player_info['t20i_matches'])}")
                print(f"   Runs: {int(player_info['t20i_runs'])}")
                print(f"   Average: {player_info['t20i_average']:.2f}")
                print(f"   Strike Rate: {player_info['t20i_strike_rate']:.2f}")
                print(f"   Highest Score: {int(player_info['t20i_highest_score'])}")
                if pd.notna(player_info.get('t20i_hundreds')):
                    print(f"   Hundreds: {int(player_info['t20i_hundreds'])}")
                    print(f"   Fifties: {int(player_info['t20i_fifties'])}")
                print(f"   Sixes: {int(player_info['t20i_sixes']) if pd.notna(player_info.get('t20i_sixes')) else 'N/A'}")
            
            if has_ipl:
                print(f"\n📊 IPL STATISTICS:")
                print(f"   Matches: {int(player_info['ipl_matches'])}")
                print(f"   Runs: {int(player_info['ipl_runs'])}")
                print(f"   Average: {player_info['ipl_average']:.2f}")
                print(f"   Strike Rate: {player_info['ipl_strike_rate']:.2f}")
                print(f"   Highest Score: {int(player_info['ipl_highest_score'])}")
                if pd.notna(player_info.get('ipl_hundreds')):
                    print(f"   Hundreds: {int(player_info['ipl_hundreds'])}")
                    print(f"   Fifties: {int(player_info['ipl_fifties'])}")
                print(f"   Sixes: {int(player_info['ipl_sixes']) if pd.notna(player_info.get('ipl_sixes')) else 'N/A'}")
            
            total_runs = sum([
                player_info['odi_runs'] if has_odi else 0,
                player_info['t20i_runs'] if has_t20i else 0,
                player_info['ipl_runs'] if has_ipl else 0
            ])
            total_matches = sum([
                player_info['odi_matches'] if has_odi else 0,
                player_info['t20i_matches'] if has_t20i else 0,
                player_info['ipl_matches'] if has_ipl else 0
            ])
            if total_matches > 0:
                print(f"\n💯 OVERALL CAREER:")
                print(f"   Total Matches: {int(total_matches)}")
                print(f"   Total Runs: {int(total_runs)}")
                print(f"   Average per Match: {total_runs/total_matches:.2f}")
                
                overall_rating = (min(player_info.get('odi_average', 0) / 50 * 40, 40) +
                               min(player_info.get('t20i_strike_rate', 0) / 150 * 30, 30) +
                               min(player_info.get('ipl_average', 0) / 40 * 30, 30))
                print(f"\n⭐ OVERALL BATTING RATING: {overall_rating:.1f}/100")
                
                if overall_rating >= 85:
                    grade = "⭐⭐⭐⭐⭐ WORLD CLASS"
                elif overall_rating >= 75:
                    grade = "⭐⭐⭐⭐ INTERNATIONAL CLASS"
                elif overall_rating >= 65:
                    grade = "⭐⭐⭐ VERY GOOD"
                elif overall_rating >= 50:
                    grade = "⭐⭐ GOOD"
                else:
                    grade = "⭐ DEVELOPING"
                
                print(f"   Grade: {grade}")
    
    # BOWLING ANALYSIS
    is_bowler = 'Bowler' in player_info['role'] or 'All-Rounder' in player_info['role']
    
    if is_bowler:
        print(f"\n{'='*70}")
        print("🎯 BOWLING ANALYSIS")
        print('='*70)
        
        print(f"\n🎯 BOWLING SPECIALITY:")
        print(f"   {player_info['bowling_style']}")
        
        player_bowl_stats = bowling_stats[bowling_stats['player'].str.contains(exact_name, case=False, na=False)] if not bowling_stats.empty else pd.DataFrame()
        
        if len(player_bowl_stats) > 0:
            bowl = player_bowl_stats.iloc[0]
            
            print(f"\n📊 CAREER BOWLING STATISTICS:")
            print(f"   Spells Bowled: {int(bowl['spells_bowled'])}")
            print(f"   Total Wickets: {int(bowl['total_wickets'])}")
            print(f"   Bowling Average: {bowl['bowling_average']:.2f}")
            print(f"   Economy Rate: {bowl['avg_economy']:.2f}")
            print(f"   Strike Rate: {bowl['avg_bowling_sr']:.2f} balls/wicket")
            
            print(f"\n🎯 CONTROL & EFFECTIVENESS:")
            print(f"   Dot Ball %: {bowl['avg_dot_pct']:.1f}%")
            print(f"   Wickets per Spell: {bowl['avg_wickets_per_spell']:.2f}")
            print(f"   Runs Conceded per Spell: {bowl['avg_runs_per_spell']:.2f}")
            
            if not bowling_perf.empty:
                player_bowl_formats = bowling_perf[bowling_perf['player'].str.contains(exact_name, case=False, na=False)]
                
                if len(player_bowl_formats) > 0:
                    print(f"\n📈 FORMAT-WISE BOWLING:")
                    for fmt in ['ODI', 'T20', 'IPL']:
                        fmt_bowl = player_bowl_formats[player_bowl_formats['format'] == fmt]
                        if len(fmt_bowl) > 0:
                            fmt_wickets = fmt_bowl['wickets'].sum()
                            fmt_spells = len(fmt_bowl)
                            fmt_econ = fmt_bowl['economy'].mean()
                            
                            print(f"\n   {fmt}:")
                            print(f"      Spells: {fmt_spells} | Wickets: {int(fmt_wickets)}")
                            print(f"      Economy: {fmt_econ:.2f}")
            
            econ_score = max(100 - (bowl['avg_economy'] - 6) * 10, 0)
            wicket_score = min(bowl['total_wickets'] / 80 * 100, 100)
            dot_score = bowl['avg_dot_pct']
            bowling_rating = (econ_score * 0.4 + wicket_score * 0.3 + dot_score * 0.3)
            
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
        else:
            print(f"\n   ⚠️ No bowling statistics available. Using master database stats.")
            has_odi_bowl = pd.notna(player_info.get('odi_wickets')) and player_info.get('odi_wickets', 0) > 0
            has_t20i_bowl = pd.notna(player_info.get('t20i_wickets')) and player_info.get('t20i_wickets', 0) > 0
            has_ipl_bowl = pd.notna(player_info.get('ipl_wickets')) and player_info.get('ipl_wickets', 0) > 0
            
            if has_odi_bowl:
                print(f"\n📊 ODI BOWLING:")
                print(f"   Matches: {int(player_info['odi_matches'])}")
                print(f"   Wickets: {int(player_info['odi_wickets'])}")
                print(f"   Bowling Average: {player_info['odi_bowling_average']:.2f}")
                print(f"   Economy Rate: {player_info['odi_economy']:.2f}")
                print(f"   Strike Rate: {player_info['odi_bowling_sr']:.1f} balls/wicket")
                if pd.notna(player_info.get('odi_best_bowling')):
                    print(f"   Best Bowling: {player_info['odi_best_bowling']}")
                if pd.notna(player_info.get('odi_five_wickets')):
                    print(f"   Five-wicket Hauls: {int(player_info['odi_five_wickets'])}")
            
            if has_t20i_bowl:
                print(f"\n📊 T20I BOWLING:")
                print(f"   Matches: {int(player_info['t20i_matches'])}")
                print(f"   Wickets: {int(player_info['t20i_wickets'])}")
                print(f"   Bowling Average: {player_info['t20i_bowling_average']:.2f}")
                print(f"   Economy Rate: {player_info['t20i_economy']:.2f}")
                print(f"   Strike Rate: {player_info['t20i_bowling_sr']:.1f} balls/wicket")
                if pd.notna(player_info.get('t20i_best_bowling')):
                    print(f"   Best Bowling: {player_info['t20i_best_bowling']}")
            
            if has_ipl_bowl:
                print(f"\n📊 IPL BOWLING:")
                print(f"   Matches: {int(player_info['ipl_matches'])}")
                print(f"   Wickets: {int(player_info['ipl_wickets'])}")
                print(f"   Bowling Average: {player_info['ipl_bowling_average']:.2f}")
                print(f"   Economy Rate: {player_info['ipl_economy']:.2f}")
                if pd.notna(player_info.get('ipl_best_bowling')):
                    print(f"   Best Bowling: {player_info['ipl_best_bowling']}")
            
            if has_odi_bowl or has_t20i_bowl or has_ipl_bowl:
                total_wickets = sum([
                    player_info['odi_wickets'] if has_odi_bowl else 0,
                    player_info['t20i_wickets'] if has_t20i_bowl else 0,
                    player_info['ipl_wickets'] if has_ipl_bowl else 0
                ])
                print(f"\n💯 OVERALL BOWLING CAREER:")
                print(f"   Total Wickets: {int(total_wickets)}")
                
                bowling_rating = 0
                if has_odi_bowl:
                    bowling_rating += max(100 - (player_info['odi_economy'] - 6) * 10, 0) * 0.4
                    bowling_rating += min(player_info['odi_wickets'] / 80 * 100, 100) * 0.3
                if has_t20i_bowl:
                    bowling_rating += max(100 - (player_info['t20i_economy'] - 6) * 10, 0) * 0.3
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
    
    # TEAM RECOMMENDATION
    print(f"\n{'='*70}")
    print("📝 TEAM SELECTION RECOMMENDATION")
    print('='*70)
    
    print(f"\n✅ RECOMMENDED POSITION: {player_info['batting_position']}")
    print(f"✅ ROLE IN TEAM: {player_info['role']}")
    
    if 'All-Rounder' in player_info['role']:
        print(f"\n💪 ALL-ROUNDER ADVANTAGE:")
        print(f"   • Can contribute with both bat and ball")
        print(f"   • Provides balance to team composition")
        print(f"   • High-value player for any format")
    
    if player_info['is_young_star'] == 'Yes':
        print(f"\n🌟 YOUNG STAR STATUS:")
        print(f"   • Future of cricket")
        print(f"   • Invest in long-term development")
        print(f"   • High potential for growth")
    
    print("\n" + "="*70)
    
    return {
        'name': exact_name,
        'role': player_info['role'],
        'special_shot': player_info['special_shot'] if is_batsman else player_info['bowling_style']
    }

def list_all_players():
    """List all players by category"""
    print("\n" + "="*70)
    print("🏏 COMPLETE PLAYER DATABASE")
    print("="*70)
    
    print(f"\n📊 Total Players: {len(master_db)}")
    
    print(f"\n👥 BY ROLE:")
    role_counts = master_db['role'].value_counts()
    for role, count in role_counts.items():
        print(f"   {role}: {count}")
    
    young_stars = master_db[master_db['is_young_star'] == 'Yes']
    print(f"\n🌟 YOUNG STARS ({len(young_stars)} players):")
    for _, player in young_stars.iterrows():
        print(f"   • {player['player_name']} ({player['age']}) - {player['role']}")
    
    print(f"\n🌍 BY COUNTRY:")
    country_counts = master_db['country'].value_counts().head(10)
    for country, count in country_counts.items():
        print(f"   {country}: {count} players")
    
    print(f"\n🏏 SEARCH OPTIONS:")
    print(f"   1. Search by player name")
    print(f"   2. View all young stars")
    print(f"   3. View all-rounders")
    print(f"   4. View bowlers")
    print(f"   5. View batsmen")
    
    try:
        choice = input(f"\n   Enter choice (1-5): ").strip()
        
        if choice == '1':
            name = input("   Enter player name: ").strip()
            get_player_complete_profile(name)
        elif choice == '2':
            print(f"\n🌟 YOUNG STARS:")
            for i, row in young_stars.iterrows():
                print(f"   {i+1}. {row['player_name']}")
            num = int(input("\n   Select player number: ")) - 1
            get_player_complete_profile(young_stars.iloc[num]['player_name'])
        elif choice == '3':
            all_rounders = master_db[master_db['role'].str.contains('All-Rounder', na=False)]
            print(f"\n💪 ALL-ROUNDERS ({len(all_rounders)}):")
            for i, row in all_rounders.iterrows():
                print(f"   {i+1}. {row['player_name']} - {row['role']}")
            num = int(input("\n   Select player number: ")) - 1
            get_player_complete_profile(all_rounders.iloc[num]['player_name'])
        elif choice == '4':
            bowlers = master_db[master_db['role'].str.contains('Bowler', na=False) & 
                               ~master_db['role'].str.contains('All-Rounder', na=False)]
            print(f"\n🎯 PURE BOWLERS ({len(bowlers)}):")
            for i, row in bowlers.iterrows():
                print(f"   {i+1}. {row['player_name']} - {row['bowling_style']}")
            num = int(input("\n   Select player number: ")) - 1
            get_player_complete_profile(bowlers.iloc[num]['player_name'])
        elif choice == '5':
            batsmen = master_db[master_db['role'].str.contains('Batsman', na=False) & 
                               ~master_db['role'].str.contains('All-Rounder', na=False)]
            print(f"\n🏏 PURE BATSMEN ({len(batsmen)}):")
            for i, row in batsmen.iterrows():
                print(f"   {i+1}. {row['player_name']} - {row['special_shot']}")
            num = int(input("\n   Select player number: ")) - 1
            get_player_complete_profile(batsmen.iloc[num]['player_name'])
        
        print(f"\n\n🔄 Search another player? (y/n): ", end="")
        if input().strip().lower() == 'y':
            list_all_players()
    except (ValueError, IndexError):
        print("❌ Invalid input. Returning to main menu.")

# Run
if __name__ == "__main__":
    print("\n🎮 WELCOME TO PROFESSIONAL PLAYER ANALYSIS SYSTEM")
    print("="*70)
    
    try:
        export_player_ratings()
        list_all_players()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting... Thank you!")
    except Exception as e:
        print(f"\n❌ Error: {e}")