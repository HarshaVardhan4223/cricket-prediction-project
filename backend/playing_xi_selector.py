
import json
import pandas as pd
import numpy as np
import os

print("🏏 PLAYING XI SELECTOR SYSTEM")
print("="*70)
print("Select best 11 players based on venue & opposition")
print("="*70)

# Load player database
try:
    with open(r'E:\cricket-prediction-project\data\global_cricket_players_fixed.json', 'r') as f:
        players_data = json.load(f)
    df = pd.DataFrame(players_data)
    print(f"✅ Loaded {len(df)} players")
except Exception as e:
    print(f"❌ Error loading database: {e}")
    print("💡 Ensure 'fix_json_format.py' ran successfully.")
    exit()

# Load venue statistics
try:
    venue_stats = pd.read_csv(r'E:\cricket-prediction-project\data\processed\venue_statistics_complete.csv')
    print(f"✅ Loaded {len(venue_stats)} venues")
except Exception as e:
    print(f"⚠️ No venue stats found - using defaults. Error: {e}")
    venue_stats = pd.DataFrame({
        'venue': ['Generic Stadium', 'Wankhede', 'Eden Gardens'],
        'v_avg': [165, 180, 170],
        'v_std': [25, 30, 28],
        'v_bat_adv': [0.5, 0.6, 0.55],
        'v_rr': [7.0, 7.5, 7.2]
    })

def export_team_xi(selected_df, country, venue, opposition, match_format, output_file=r'E:\cricket-prediction-project\data\selected_xi.csv'):
    """Export selected XI to CSV"""
    selected_df['country'] = country
    selected_df['venue'] = venue
    selected_df['opposition'] = opposition
    selected_df['format'] = match_format
    selected_df.to_csv(output_file, index=False)
    print(f"💾 Playing XI exported to {output_file}")

def select_best_xi(country, venue, opposition, match_format='T20'):
    """
    Select best Playing XI based on:
    - Country (which team)
    - Venue (ground characteristics)
    - Opposition (head-to-head consideration)
    - Format (ODI/T20)
    """
    print("\n" + "="*70)
    print(f"🏏 SELECTING PLAYING XI")
    print("="*70)
    print(f"   Team: {country}")
    print(f"   Venue: {venue}")
    print(f"   Opposition: {opposition}")
    print(f"   Format: {match_format}")
    
    team_players = df[df['country'] == country].copy()
    
    if len(team_players) == 0:
        print(f"\n❌ No players found for {country}")
        return None
    
    print(f"\n📊 Squad Size: {len(team_players)} players available")
    
    # Analyze venue
    venue_info = venue_stats[venue_stats['venue'].str.contains(venue, case=False, na=False)]
    
    if len(venue_info) > 0:
        venue_avg_score = venue_info['v_avg'].values[0]
        venue_bat_first_adv = venue_info['v_bat_adv'].values[0]
        venue_type = ("High-Scoring (Batting Friendly)" if venue_avg_score > 180 else
                      "Moderate-Scoring (Balanced)" if venue_avg_score > 160 else
                      "Low-Scoring (Bowling Friendly)")
    else:
        venue_avg_score = 165
        venue_bat_first_adv = 0.5
        venue_type = "Unknown (Using defaults)"
    
    print(f"\n🏟️ VENUE ANALYSIS:")
    print(f"   Type: {venue_type}")
    print(f"   Average Score: {venue_avg_score:.0f}")
    print(f"   Batting First Win %: {venue_bat_first_adv*100:.0f}%")
    
    # Calculate player scores
    player_scores = []
    for idx, player in team_players.iterrows():
        score = 0
        if match_format == 'ODI':
            runs = player.get('odi_runs', 0)
            avg = player.get('odi_average', 0)
            sr = player.get('odi_strike_rate', 0)
            wickets = player.get('odi_wickets', 0)
            economy = player.get('odi_economy', 10)
        else:  # T20
            runs = player.get('t20i_runs', 0) if pd.notna(player.get('t20i_runs')) else player.get('ipl_runs', 0)
            avg = player.get('t20i_average', 0) if pd.notna(player.get('t20i_average')) else player.get('ipl_average', 0)
            sr = player.get('t20i_strike_rate', 0) if pd.notna(player.get('t20i_strike_rate')) else player.get('ipl_strike_rate', 0)
            wickets = player.get('t20i_wickets', 0) if pd.notna(player.get('t20i_wickets')) else player.get('ipl_wickets', 0)
            economy = player.get('t20i_economy', 10) if pd.notna(player.get('t20i_economy')) else player.get('ipl_economy', 10)
        
        runs = 0 if pd.isna(runs) else runs
        avg = 0 if pd.isna(avg) else avg
        sr = 0 if pd.isna(sr) else sr
        wickets = 0 if pd.isna(wickets) else wickets
        economy = 10 if pd.isna(economy) else economy
        
        if 'Batsman' in player['role'] or 'Keeper' in player['role'] or 'All-Rounder' in player['role']:
            batting_score = (runs / 100) + (avg / 10) + (sr / 30)
            if venue_avg_score > 180 and sr > 140:
                batting_score *= 1.2
            elif venue_avg_score < 150 and avg > 35:
                batting_score *= 1.1
            score += batting_score * 10
        
        if 'Bowler' in player['role'] or 'All-Rounder' in player['role']:
            bowling_score = (wickets / 20) + ((10 - economy) / 2)
            if venue_avg_score < 150:
                bowling_score *= 1.3
            score += bowling_score * 10
        
        if 'All-Rounder' in player['role']:
            score *= 1.15
        if player['is_young_star'] == 'Yes':
            score *= 1.05
        
        player_scores.append({
            'name': player['player_name'],
            'role': player['role'],
            'batting_position': player['batting_position'],
            'score': score,
            'runs': runs,
            'avg': avg,
            'sr': sr,
            'wickets': wickets,
            'economy': economy
        })
    
    player_scores_df = pd.DataFrame(player_scores).sort_values('score', ascending=False)
    
    # Select balanced team
    selected_xi = []
    openers = player_scores_df[player_scores_df['batting_position'].str.contains('1-2|1-3', na=False)].head(2)
    selected_xi.extend(openers.to_dict('records'))
    remaining = player_scores_df[~player_scores_df['name'].isin([p['name'] for p in selected_xi])]
    
    middle_order = remaining[remaining['batting_position'].str.contains('3|4|5', na=False)].head(3)
    selected_xi.extend(middle_order.to_dict('records'))
    remaining = remaining[~remaining['name'].isin([p['name'] for p in selected_xi])]
    
    all_rounders = remaining[remaining['role'].str.contains('All-Rounder', na=False)].head(2)
    selected_xi.extend(all_rounders.to_dict('records'))
    remaining = remaining[~remaining['name'].isin([p['name'] for p in selected_xi])]
    
    pace_bowlers = remaining[remaining['role'].str.contains('Fast Bowler', na=False)].head(2)
    selected_xi.extend(pace_bowlers.to_dict('records'))
    remaining = remaining[~remaining['name'].isin([p['name'] for p in selected_xi])]
    
    spin_bowlers = remaining[remaining['role'].str.contains('Spin Bowler', na=False)].head(2)
    selected_xi.extend(spin_bowlers.to_dict('records'))
    remaining = remaining[~remaining['name'].isin([p['name'] for p in selected_xi])]
    
    while len(selected_xi) < 11 and len(remaining) > 0:
        selected_xi.append(remaining.iloc[0].to_dict())
        remaining = remaining.iloc[1:]
    
    selected_df = pd.DataFrame(selected_xi)
    batting_positions = {
        '1-2': 1, '1-3': 1, '3-4': 3, '4-5': 4, '5-6': 5, '5-7': 6,
        '6-7': 6, '7-8': 7, '8-9': 8, '9-11': 9, '10-11': 10, '11': 11
    }
    selected_df['sort_order'] = selected_df['batting_position'].map(
        lambda x: min([batting_positions.get(p.strip(), 10) for p in str(x).split('-')])
    )
    selected_df = selected_df.sort_values('sort_order')
    
    print(f"\n{'='*70}")
    print(f"🏆 SELECTED PLAYING XI FOR {country}")
    print('='*70)
    print(f"\n🏏 BATTING ORDER:")
    for i, player in enumerate(selected_df.to_dict('records'), 1):
        position_info = f"({player['batting_position']})"
        stats = (f"Wickets: {int(player['wickets'])} | Econ: {player['economy']:.2f}" if 'Bowler' in player['role'] and 'All-Rounder' not in player['role']
                 else f"Runs: {int(player['runs'])} @ {player['avg']:.1f} | Wickets: {int(player['wickets'])}" if 'All-Rounder' in player['role']
                 else f"Runs: {int(player['runs'])} @ {player['avg']:.1f} | SR: {player['sr']:.1f}")
        print(f"   {i:2d}. {player['name']:30s} {position_info:8s} - {player['role']}")
        print(f"       {stats}")
    
    print(f"\n📊 TEAM COMPOSITION:")
    batsmen = len([p for p in selected_xi if 'Batsman' in p['role'] or 'Keeper' in p['role']])
    all_rounders_count = len([p for p in selected_xi if 'All-Rounder' in p['role']])
    bowlers = len([p for p in selected_xi if 'Bowler' in p['role'] and 'All-Rounder' not in p['role']])
    print(f"   Batsmen/Keepers: {batsmen}")
    print(f"   All-Rounders: {all_rounders_count}")
    print(f"   Pure Bowlers: {bowlers}")
    
    print(f"\n🎯 BOWLING ATTACK:")
    pace = len([p for p in selected_xi if 'Fast' in p['role']])
    spin = len([p for p in selected_xi if 'Spin' in p['role']])
    print(f"   Pace Bowlers: {pace}")
    print(f"   Spin Bowlers: {spin}")
    
    print(f"\n💪 TEAM STRENGTHS:")
    avg_sr = selected_df['sr'].mean()
    if avg_sr > 135:
        print(f"   ⚡ EXPLOSIVE batting lineup (Avg SR: {avg_sr:.1f})")
    elif avg_sr > 120:
        print(f"   ✅ BALANCED batting lineup (Avg SR: {avg_sr:.1f})")
    else:
        print(f"   📊 SOLID batting lineup (Avg SR: {avg_sr:.1f})")
    
    if venue_avg_score > 180 and avg_sr > 135:
        print(f"   🎯 Well-suited for HIGH-SCORING venue")
    elif venue_avg_score < 150 and bowlers >= 5:
        print(f"   🎯 Strong BOWLING attack for LOW-SCORING venue")
    
    print("\n" + "="*70)
    
    export_team_xi(selected_df, country, venue, opposition, match_format)
    return selected_df

def team_selection_menu():
    while True:
        print("\n" + "="*70)
        print("🏏 TEAM SELECTION MENU")
        print("="*70)
        
        countries = sorted(df['country'].unique())
        print(f"\n🌍 AVAILABLE TEAMS:")
        for i, country in enumerate(countries, 1):
            player_count = len(df[df['country'] == country])
            print(f"   {i:2d}. {country:20s} ({player_count} players)")
        
        print(f"\n   0. Exit")
        
        try:
            choice = input("\n   Select team number: ").strip()
            if choice == '0':
                print("\n👋 Thank you!")
                break
            
            team_idx = int(choice) - 1
            if team_idx < 0 or team_idx >= len(countries):
                print("❌ Invalid selection!")
                continue
            
            selected_team = countries[team_idx]
            print(f"\n🆚 SELECT OPPOSITION:")
            for i, country in enumerate(countries, 1):
                if country != selected_team:
                    print(f"   {i:2d}. {country}")
            
            opp_choice = int(input("\n   Opposition number: ")) - 1
            opposition = [c for c in countries if c != selected_team][opp_choice]
            
            print(f"\n🏟️ ENTER VENUE:")
            print("   Examples: Wankhede, Eden Gardens, MCG, Lord's, etc.")
            venue = input("   Venue: ").strip() or "Generic Stadium"
            
            print(f"\n🏏 SELECT FORMAT:")
            print("   1. T20")
            print("   2. ODI")
            format_choice = input("   Format: ").strip()
            match_format = 'ODI' if format_choice == '2' else 'T20'
            
            select_best_xi(selected_team, venue, opposition, match_format)
            
            print(f"\n🔄 Select another team? (y/n): ", end="")
            if input().strip().lower() != 'y':
                break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue

if __name__ == "__main__":
    try:
        team_selection_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")