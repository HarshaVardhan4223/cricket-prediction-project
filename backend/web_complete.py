from flask import Flask, render_template, request, jsonify
from flask import make_response
from flask_cors import CORS
import pickle
import pandas as pd
import json
import os
import logging
import numpy as np

# Get the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Initialize Flask with correct paths
app = Flask(__name__,
            template_folder=os.path.join(PROJECT_ROOT, 'frontend', 'templates'),
            static_folder=os.path.join(PROJECT_ROOT, 'frontend', 'static'))
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

print("="*70)
print("🌐 LOADING ENHANCED CRICKET ANALYSIS SYSTEM...")
print("="*70)
print(f"📁 Base Directory: {BASE_DIR}")
print(f"📁 Project Root: {PROJECT_ROOT}")
print(f"📁 Templates: {app.template_folder}")
print("="*70)

# Load all models and data
try:
    model_path = os.path.join(PROJECT_ROOT, 'models', 'ultimate_ensemble_model.pkl')
    team_stats_path = os.path.join(PROJECT_ROOT, 'models', 'team_statistics.pkl')
    venue_path = os.path.join(PROJECT_ROOT, 'data', 'processed', 'venue_statistics_complete.csv')
    players_path = os.path.join(PROJECT_ROOT, 'data', 'global_cricket_players_fixed.json')
    batting_stats_path = os.path.join(PROJECT_ROOT, 'data', 'processed', 'players', 'batting_statistics.csv')
    bowling_stats_path = os.path.join(PROJECT_ROOT, 'data', 'processed', 'players', 'bowling_statistics.csv')
    augmented_players_path = os.path.join(PROJECT_ROOT, 'data', 'global_cricket_players_fixed_augmented_rich_v2.json')

    print(f"📂 Loading model from: {model_path}")
    with open(model_path, 'rb') as f:
        match_model = pickle.load(f)
    print("✅ Match Predictor Model Loaded")

    print(f"📂 Loading team stats from: {team_stats_path}")
    with open(team_stats_path, 'rb') as f:
        team_stats = pickle.load(f)
    print("✅ Team Statistics Loaded")

    print(f"📂 Loading venue stats from: {venue_path}")
    venue_stats = pd.read_csv(venue_path)
    print(f"✅ Venue Statistics Loaded ({len(venue_stats)} venues)")

    print(f"📂 Loading players from: {players_path}")
    with open(players_path, 'r') as f:
        players_data = json.load(f)
    players_df = pd.DataFrame(players_data)
    print(f"✅ Players Database Loaded ({len(players_df)} players)")

    print(f"📂 Loading batting stats from: {batting_stats_path}")
    batting_stats = pd.read_csv(batting_stats_path) if os.path.exists(batting_stats_path) else pd.DataFrame()
    print(f"✅ Batting Statistics Loaded ({len(batting_stats)} records)")

    print(f"📂 Loading bowling stats from: {bowling_stats_path}")
    bowling_stats = pd.read_csv(bowling_stats_path) if os.path.exists(bowling_stats_path) else pd.DataFrame()
    print(f"✅ Bowling Statistics Loaded ({len(bowling_stats)} records)")

    # Load augmented players with physiological insights
    augmented_players_data = {}
    if os.path.exists(augmented_players_path):
        print(f"📂 Loading augmented players with insights from: {augmented_players_path}")
        with open(augmented_players_path, 'r', encoding='utf-8') as f:
            augmented_list = json.load(f)
        if isinstance(augmented_list, list):
            for player_rec in augmented_list:
                name = player_rec.get('player_name') or player_rec.get('name')
                if name:
                    augmented_players_data[name] = player_rec
        print(f"✅ Augmented Players with Insights Loaded ({len(augmented_players_data)} players)")
    else:
        print(f"⚠️  Augmented players file not found: {augmented_players_path}")
        augmented_players_data = {}

except Exception as e:
    print(f"❌ Error loading data: {e}")
    match_model = None
    team_stats = {}
    venue_stats = pd.DataFrame()
    players_df = pd.DataFrame()
    batting_stats = pd.DataFrame()
    bowling_stats = pd.DataFrame()
    augmented_players_data = {}

# Comprehensive teams list (including IPL)
INTERNATIONAL_TEAMS = [
    "India", "Australia", "England", "Pakistan", "South Africa",
    "New Zealand", "West Indies", "Sri Lanka", "Bangladesh",
    "Afghanistan", "Zimbabwe", "Ireland", "Netherlands", "Scotland"
]

IPL_TEAMS = [
    "Mumbai Indians", "Chennai Super Kings", "Royal Challengers Bangalore",
    "Kolkata Knight Riders", "Delhi Capitals", "Punjab Kings",
    "Rajasthan Royals", "Sunrisers Hyderabad", "Gujarat Titans",
    "Lucknow Super Giants"
]

ALL_TEAMS = sorted(INTERNATIONAL_TEAMS + IPL_TEAMS)

# Comprehensive venues list
VENUES = sorted([
    # India
    "Wankhede Stadium, Mumbai", "Eden Gardens, Kolkata",
    "M. Chinnaswamy Stadium, Bangalore", "Feroz Shah Kotla, Delhi",
    "MA Chidambaram Stadium, Chennai", "Rajiv Gandhi International Stadium, Hyderabad",
    "Punjab Cricket Association Stadium, Mohali", "Narendra Modi Stadium, Ahmedabad",
    "Sawai Mansingh Stadium, Jaipur", "Holkar Cricket Stadium, Indore",
    "Green Park, Kanpur", "Vidarbha Cricket Association Stadium, Nagpur",
    "JSCA International Stadium Complex, Ranchi", "Himachal Pradesh Cricket Association Stadium, Dharamsala",
    "Barabati Stadium, Cuttack", "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam",
    # Australia, England, Pakistan/UAE, South Africa, New Zealand, Sri Lanka, West Indies, Bangladesh, Others
    "Melbourne Cricket Ground, Melbourne", "Sydney Cricket Ground, Sydney", "Adelaide Oval, Adelaide",
    "The Gabba, Brisbane", "Perth Stadium, Perth", "Bellerive Oval, Hobart", "Manuka Oval, Canberra",
    "Lord's, London", "The Oval, London", "Old Trafford, Manchester", "Edgbaston, Birmingham",
    "Headingley, Leeds", "Trent Bridge, Nottingham", "The Rose Bowl, Southampton", "County Ground, Bristol",
    "National Stadium, Karachi", "Gaddafi Stadium, Lahore", "Rawalpindi Cricket Stadium, Rawalpindi",
    "Dubai International Cricket Stadium, Dubai", "Sharjah Cricket Stadium, Sharjah",
    "Sheikh Zayed Stadium, Abu Dhabi", "The Wanderers Stadium, Johannesburg", "SuperSport Park, Centurion",
    "Newlands, Cape Town", "Kingsmead, Durban", "St George's Park, Port Elizabeth", "Eden Park, Auckland",
    "Hagley Oval, Christchurch", "Basin Reserve, Wellington", "University Oval, Dunedin",
    "R. Premadasa Stadium, Colombo", "Pallekele International Cricket Stadium, Pallekele",
    "Galle International Stadium, Galle", "Kensington Oval, Barbados", "Queen's Park Oval, Trinidad",
    "Sabina Park, Jamaica", "Sir Vivian Richards Stadium, Antigua", "Shere Bangla National Stadium, Dhaka",
    "Zahur Ahmed Chowdhury Stadium, Chittagong", "Harare Sports Club, Zimbabwe",
    "Bulawayo Athletic Club, Zimbabwe", "Village, Dublin"
])

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/match-predictor')
def match_predictor_page():
    return render_template('match_predictor.html')

@app.route('/player-analysis')
def player_analysis_page():
    return render_template('player_analysis.html')

@app.route('/player-insights')
def player_insights_page():
    return render_template('player_insights.html')

@app.route('/team-selector')
def team_selector_page():
    return render_template('team_selector.html')

@app.route('/coach-dashboard')
def coach_dashboard_page():
    return render_template('coach_dashboard.html')

@app.route('/performance-analysis')
def performance_analysis_page():
    return render_template('performance_analysis.html')

# API Endpoints
@app.route('/api/teams', methods=['GET'])
def get_teams():
    return jsonify({'success': True, 'teams': ALL_TEAMS, 'international': INTERNATIONAL_TEAMS, 'ipl': IPL_TEAMS})

@app.route('/api/venues', methods=['GET'])
def get_venues():
    return jsonify({'success': True, 'venues': VENUES})

@app.route('/api/search-teams', methods=['GET'])
def search_teams():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({'success': True, 'teams': ALL_TEAMS})
    filtered = [t for t in ALL_TEAMS if query in t.lower()]
    return jsonify({'success': True, 'teams': filtered})

@app.route('/api/search-venues', methods=['GET'])
def search_venues():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({'success': True, 'venues': VENUES})
    filtered = [v for v in VENUES if query in v.lower()]
    return jsonify({'success': True, 'venues': filtered})

@app.route('/api/search-players', methods=['GET'])
def search_players():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({'success': True, 'players': []})
    try:
        matching_players = players_df[players_df['player_name'].str.lower().str.contains(query, na=False)]
        suggestions = [{'name': row['player_name'], 'country': row['country']} for _, row in matching_players.iterrows()][:10]
        return jsonify({'success': True, 'players': suggestions})
    except Exception as e:
        logger.error(f"Error in search_players: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/predict-match', methods=['POST'])
def predict_match():
    try:
        data = request.json
        team1 = data['team1']
        team2 = data['team2']
        venue = data['venue']
        runs = int(data['runs'])
        wickets = int(data['wickets'])
        run_rate = float(data['run_rate'])

        t1_stats = team_stats.get(team1, {'wr': 0.5, 'bat_wr': 0.5, 'chase_wr': 0.5, 'avg_score': 150})
        t2_stats = team_stats.get(team2, {'wr': 0.5, 'bat_wr': 0.5, 'chase_wr': 0.5, 'avg_score': 150})

        venue_row = venue_stats[venue_stats['venue'].str.contains(venue.split(',')[0], case=False, na=False)]
        if len(venue_row) > 0:
            v_avg = venue_row['v_avg'].values[0]
            v_std = venue_row['v_std'].values[0]
            v_bat_adv = venue_row['v_bat_adv'].values[0]
            v_rr = venue_row['v_rr'].values[0]
        else:
            v_avg, v_std, v_bat_adv, v_rr = 165, 25, 0.5, 7.5

        score_above_venue = (runs - v_avg) / v_std if v_std > 0 else 0
        team_strength = t1_stats['wr'] - t2_stats['wr']
        situation_advantage = t1_stats['bat_wr'] - t2_stats['chase_wr']
        wickets_remaining = 10 - wickets
        wicket_quality = (wickets_remaining / 10) * (runs / 150)
        big_score = 1 if runs >= (v_avg + 15) else 0
        low_wickets = 1 if wickets <= 5 else 0
        dominant_performance = big_score * low_wickets
        balanced_match = 1 if abs(team_strength) < 0.15 else 0
        score_normalized = runs / v_avg if v_avg > 0 else 1
        overall_strength = (score_above_venue * 0.4 + team_strength * 0.3 + wicket_quality * 0.2 + situation_advantage * 0.1)

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

        if match_model:
            prediction = match_model.predict(user_input)[0]
            probability = match_model.predict_proba(user_input)[0]
            winner = team1 if prediction == 1 else team2
            team1_prob = round(probability[1] * 100, 1)
            team2_prob = round(probability[0] * 100, 1)
        else:
            winner = team1
            team1_prob = 65.0
            team2_prob = 35.0

        max_prob = max(team1_prob, team2_prob)
        if max_prob >= 80:
            confidence = "VERY HIGH"
            confidence_desc = "Strong prediction - Clear favorite"
        elif max_prob >= 70:
            confidence = "HIGH"
            confidence_desc = "Good prediction with solid evidence"
        elif max_prob >= 60:
            confidence = "MODERATE"
            confidence_desc = "Slight edge - Could be competitive"
        else:
            confidence = "LOW"
            confidence_desc = "Very close match - High uncertainty"

        if runs > v_avg + 20:
            score_analysis = "EXCELLENT SCORE - Well above venue average"
        elif runs > v_avg:
            score_analysis = "GOOD SCORE - Above venue average"
        elif runs > v_avg - 15:
            score_analysis = "PAR SCORE - Around venue average"
        else:
            score_analysis = "BELOW PAR - Below venue average"

        prob_diff = abs(team1_prob - team2_prob)
        if prob_diff < 10:
            match_situation = "VERY CLOSE - Could go either way"
        elif prob_diff < 20:
            match_situation = "COMPETITIVE - Slight edge"
        elif prob_diff < 40:
            match_situation = "CLEAR FAVORITE - Strong advantage"
        else:
            match_situation = "DOMINANT - Overwhelming favorite"

        return jsonify({
            'success': True,
            'prediction': {
                'winner': winner, 'team1': team1, 'team2': team2,
                'team1_probability': team1_prob, 'team2_probability': team2_prob,
                'confidence': confidence, 'confidence_description': confidence_desc
            },
            'match_details': {
                'venue': venue, 'score': f"{runs}/{wickets}",
                'run_rate': run_rate, 'wickets_remaining': wickets_remaining
            },
            'venue_analysis': {
                'average_score': round(v_avg, 0),
                'batting_first_advantage': round(v_bat_adv * 100, 0),
                'average_run_rate': round(v_rr, 1),
                'score_vs_average': round(runs - v_avg, 0),
                'score_analysis': score_analysis
            },
            'team_analysis': {
                'team1_win_rate': round(t1_stats['wr'] * 100, 1),
                'team2_win_rate': round(t2_stats['wr'] * 100, 1),
                'team1_batting_wr': round(t1_stats['bat_wr'] * 100, 1),
                'team2_chase_wr': round(t2_stats['chase_wr'] * 100, 1),
                'match_situation': match_situation
            }
        })
    except Exception as e:
        logger.error(f"Error in predict_match: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/players', methods=['GET'])
def get_all_players():
    try:
        if len(players_df) == 0:
            return jsonify({'success': False, 'error': 'No players loaded'}), 500
        return jsonify({'success': True, 'players': players_df.to_dict('records'), 'count': len(players_df)})
    except Exception as e:
        logger.error(f"Error in get_all_players: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/players/<country>', methods=['GET'])
def get_players_by_country(country):
    try:
        players = players_df[players_df['country'] == country]
        if len(players) == 0:
            return jsonify({'success': False, 'error': f'No players found for {country}'}), 404
        return jsonify({'success': True, 'players': players.to_dict('records'), 'count': len(players)})
    except Exception as e:
        logger.error(f"Error in get_players_by_country: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/performance-analysis', methods=['POST'])
def performance_analysis():
    try:
        data = request.json
        player1_name = data['player1']
        player2_name = data.get('player2', None)
        period = data.get('period', 'career')
        analysis_type = data.get('analysis_type', 'complete')

        # Find player in database
        player1_data = players_df[players_df['player_name'].str.contains(player1_name, case=False, na=False)]
        if len(player1_data) == 0:
            return jsonify({'success': False, 'error': f'Player {player1_name} not found'}), 404

        player1 = player1_data.iloc[0].to_dict()
        
        # Calculate comprehensive metrics
        player1_metrics = calculate_comprehensive_metrics(player1, batting_stats, bowling_stats, period)

        result = {
            'success': True,
            'player1': {
                'name': player1['player_name'],
                'country': player1['country'],
                'role': player1['role'],
                'age': player1.get('age', 'N/A'),
                'batting_style': player1.get('batting_style', 'N/A'),
                'bowling_style': player1.get('bowling_style', 'N/A'),
                'special_shot': player1.get('special_shot', 'N/A'),
                'teams': player1.get('teams', 'N/A'),
                'batting_position': player1.get('batting_position', 'N/A'),
                'is_young_star': player1.get('is_young_star', 'No'),
                'metrics': player1_metrics
            }
        }
        # Attach augmented insights for player1 if available
        try:
            aug1 = None
            key1 = player1.get('player_name')
            if key1:
                # exact match
                aug1 = augmented_players_data.get(key1)
                if not aug1:
                    # case-insensitive match
                    for aname, arec in augmented_players_data.items():
                        if aname and aname.lower() == key1.lower():
                            aug1 = arec
                            break
            if aug1:
                result['player1']['augmented'] = aug1
            # create highlight for player1
            try:
                highlight1 = create_player_highlight(player1, player1_metrics, aug1 if 'aug1' in locals() else None)
                if highlight1 and highlight1.get('main'):
                    result['player1']['highlight'] = highlight1
            except Exception:
                logger.debug('Could not compute highlight for player1')
        except Exception:
            logger.debug('Could not attach augmented insights for player1')

        if player2_name:
            player2_data = players_df[players_df['player_name'].str.contains(player2_name, case=False, na=False)]
            if len(player2_data) > 0:
                player2 = player2_data.iloc[0].to_dict()
                player2_metrics = calculate_comprehensive_metrics(player2, batting_stats, bowling_stats, period)

                result['player2'] = {
                    'name': player2['player_name'],
                    'country': player2['country'],
                    'role': player2['role'],
                    'metrics': player2_metrics
                }
                # Attach augmented insights for player2 if available
                try:
                    aug2 = None
                    key2 = player2.get('player_name')
                    if key2:
                        aug2 = augmented_players_data.get(key2)
                        if not aug2:
                            for aname, arec in augmented_players_data.items():
                                if aname and aname.lower() == key2.lower():
                                    aug2 = arec
                                    break
                    if aug2:
                        result['player2']['augmented'] = aug2
                    # create highlight for player2
                    try:
                        highlight2 = create_player_highlight(player2, player2_metrics, aug2 if 'aug2' in locals() else None)
                        if highlight2 and highlight2.get('main'):
                            result['player2']['highlight'] = highlight2
                    except Exception:
                        logger.debug('Could not compute highlight for player2')
                except Exception:
                    logger.debug('Could not attach augmented insights for player2')

                result['comparison'] = compare_players(player1_metrics, player2_metrics)

        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in performance_analysis: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/select-xi', methods=['POST'])
def select_playing_xi():
    try:
        data = request.json
        country = data['country']
        opposition = data.get('opposition', 'Unknown')
        venue = data.get('venue', 'Generic Stadium')
        match_format = data.get('format', 'T20')

        logger.info(f"Selecting XI for: {country} vs {opposition} at {venue} ({match_format})")

        # List of retired players to exclude (update this list as needed)
        RETIRED_PLAYERS = [
            'R Ashwin', 'Ashwin', 'Ravichandran Ashwin',
            'MS Dhoni',  # Retired from internationals
            'Yuvraj Singh',
            'Harbhajan Singh',
            'Virender Sehwag',
            'Gautam Gambhir',
            'Zaheer Khan',
            'Irfan Pathan',
            'Yusuf Pathan',
            'Suresh Raina',  # Retired from internationals
            'Ambati Rayudu',
            'Dinesh Karthik',  # Retired from internationals
        ]

        # Handle IPL teams differently - map to country players
        ipl_to_country_map = {
            'Mumbai Indians': 'India',
            'Chennai Super Kings': 'India',
            'Royal Challengers Bangalore': 'India',
            'Kolkata Knight Riders': 'India',
            'Delhi Capitals': 'India',
            'Punjab Kings': 'India',
            'Rajasthan Royals': 'India',
            'Sunrisers Hyderabad': 'India',
            'Gujarat Titans': 'India',
            'Lucknow Super Giants': 'India'
        }
        
        # Check if it's an IPL team
        is_ipl_team = country in ipl_to_country_map
        
        if is_ipl_team:
            # For IPL teams, get players who have IPL experience
            team_players = players_df[
                (players_df['ipl_matches'].notna()) & 
                (players_df['ipl_matches'] > 0)
            ].copy()
            logger.info(f"Found {len(team_players)} IPL players")
        else:
            # For international teams
            team_players = players_df[players_df['country'] == country].copy()
            logger.info(f"Found {len(team_players)} players for {country}")
            
            # Filter out retired players for INTERNATIONAL matches (ODI/T20I)
            if match_format in ['ODI', 'T20']:
                team_players = team_players[
                    ~team_players['player_name'].isin(RETIRED_PLAYERS)
                ].copy()
                logger.info(f"After filtering retired players: {len(team_players)} active players")

        if len(team_players) == 0:
            logger.error(f"No players found for {country}")
            return jsonify({
                'success': False, 
                'error': f'No players found for {country}. Please check the team name or try an international team.'
            }), 404

        # Get venue statistics
        venue_name = venue.split(',')[0]
        venue_row = venue_stats[venue_stats['venue'].str.contains(venue_name, case=False, na=False)]
        
        if len(venue_row) > 0:
            v_avg = venue_row['v_avg'].values[0]
            v_std = venue_row['v_std'].values[0]
            v_bat_adv = venue_row['v_bat_adv'].values[0]
            v_rr = venue_row['v_rr'].values[0]
        else:
            v_avg, v_std, v_bat_adv, v_rr = 165, 25, 0.5, 7.5

        logger.info(f"Venue stats - Avg: {v_avg}, Bat advantage: {v_bat_adv}")

        # Calculate player scores based on format
        player_scores = []
        for idx, player in team_players.iterrows():
            score = 0
            
            # Get format-specific stats
            if match_format == 'ODI':
                runs = player.get('odi_runs', 0)
                avg = player.get('odi_average', 0)
                sr = player.get('odi_strike_rate', 0)
                wickets = player.get('odi_wickets', 0)
                economy = player.get('odi_economy', 10)
                matches = player.get('odi_matches', 0)
            elif is_ipl_team or match_format == 'IPL':
                # For IPL teams, prioritize IPL stats
                runs = player.get('ipl_runs', 0) if pd.notna(player.get('ipl_runs')) else player.get('t20i_runs', 0)
                avg = player.get('ipl_average', 0) if pd.notna(player.get('ipl_average')) else player.get('t20i_average', 0)
                sr = player.get('ipl_strike_rate', 0) if pd.notna(player.get('ipl_strike_rate')) else player.get('t20i_strike_rate', 0)
                wickets = player.get('ipl_wickets', 0) if pd.notna(player.get('ipl_wickets')) else player.get('t20i_wickets', 0)
                economy = player.get('ipl_economy', 10) if pd.notna(player.get('ipl_economy')) else player.get('t20i_economy', 10)
                matches = player.get('ipl_matches', 0) if pd.notna(player.get('ipl_matches')) else player.get('t20i_matches', 0)
            else:  # T20
                runs = player.get('t20i_runs', 0) if pd.notna(player.get('t20i_runs')) else player.get('ipl_runs', 0)
                avg = player.get('t20i_average', 0) if pd.notna(player.get('t20i_average')) else player.get('ipl_average', 0)
                sr = player.get('t20i_strike_rate', 0) if pd.notna(player.get('t20i_strike_rate')) else player.get('ipl_strike_rate', 0)
                wickets = player.get('t20i_wickets', 0) if pd.notna(player.get('t20i_wickets')) else player.get('ipl_wickets', 0)
                economy = player.get('t20i_economy', 10) if pd.notna(player.get('t20i_economy')) else player.get('ipl_economy', 10)
                matches = player.get('t20i_matches', 0) if pd.notna(player.get('t20i_matches')) else player.get('ipl_matches', 0)

            # Clean data
            runs = 0 if pd.isna(runs) else float(runs)
            avg = 0 if pd.isna(avg) else float(avg)
            sr = 0 if pd.isna(sr) else float(sr)
            wickets = 0 if pd.isna(wickets) else float(wickets)
            economy = 10 if pd.isna(economy) else float(economy)
            matches = 0 if pd.isna(matches) else float(matches)

            # Skip players with no experience in this format
            if matches == 0:
                continue

            # Calculate batting score
            if 'Batsman' in player['role'] or 'Keeper' in player['role'] or 'All-Rounder' in player['role']:
                # Base batting score
                batting_score = (runs / 100) + (avg / 10) + (sr / 30)
                
                # Recent form bonus (if young star or good stats)
                if player.get('is_young_star') == 'Yes':
                    batting_score *= 1.08
                
                # Venue-based adjustments
                if v_avg > 180:  # High-scoring venue
                    if sr > 140:
                        batting_score *= 1.2  # Aggressive batsmen preferred
                    elif avg < 30:
                        batting_score *= 0.9  # Penalize inconsistent players
                elif v_avg < 150:  # Low-scoring venue
                    if avg > 35:
                        batting_score *= 1.15  # Consistent batsmen preferred
                    if sr < 100:
                        batting_score *= 0.95  # Penalize slow scorers in T20
                
                score += batting_score * 10

            # Calculate bowling score
            if 'Bowler' in player['role'] or 'All-Rounder' in player['role']:
                # Base bowling score
                bowling_score = (wickets / 20) + ((10 - economy) / 2)
                
                # Experience bonus
                if matches > 50:
                    bowling_score *= 1.05
                
                # Venue-based adjustments
                if v_avg < 150:  # Bowling-friendly venue
                    bowling_score *= 1.3
                elif v_avg > 180:  # Batting-friendly venue
                    if economy < 7.5:  # Economical bowlers valued
                        bowling_score *= 1.15
                
                score += bowling_score * 10

            # Role bonuses
            if 'All-Rounder' in player['role']:
                score *= 1.15  # All-rounder bonus
            
            # Experience bonus
            if matches > 100:
                score *= 1.05
            elif matches < 10:
                score *= 0.95

            # Apply fatigue/readiness penalty from augmented data
            pkey = player.get('player_name')
            if pkey and pkey in augmented_players_data:
                aug = augmented_players_data[pkey]
                ins = aug.get('player_insights') or {}
                perf = ins.get('performance_prediction', {}) if isinstance(ins, dict) else {}
                if 'high' in str(perf.get('fatigue_risk','')).lower():
                    score *= 0.85
                phys = ins.get('physiological_profile', {}) if isinstance(ins, dict) else {}
                if 'low' in str(phys.get('hrv_readiness_level','')).lower():
                    score *= 0.90

            player_scores.append({
                'name': player['player_name'],
                'role': player['role'],
                'batting_position': player.get('batting_position', '5-6'),
                'score': score,
                'runs': runs,
                'avg': avg,
                'sr': sr,
                'wickets': wickets,
                'economy': economy,
                'matches': matches
            })

        # Sort by score
        player_scores_df = pd.DataFrame(player_scores).sort_values('score', ascending=False)
        
        logger.info(f"Calculated scores for {len(player_scores_df)} players")

        if len(player_scores_df) < 11:
            return jsonify({
                'success': False,
                'error': f'Not enough active players found. Only {len(player_scores_df)} players available.'
            }), 400

        # Build balanced team with proper selection logic
        selected_xi = []

        # 1. Select openers (2 players) - Best aggressive batsmen for top order
        openers = player_scores_df[
            player_scores_df['batting_position'].str.contains('1-2|1-3', na=False, regex=True)
        ].head(2)
        
        if len(openers) < 2:
            # If not enough specialist openers, get best batsmen
            openers = player_scores_df[
                player_scores_df['role'].str.contains('Batsman|Keeper', na=False, regex=True)
            ].head(2)
        
        selected_xi.extend(openers.to_dict('records'))
        remaining = player_scores_df[~player_scores_df['name'].isin([p['name'] for p in selected_xi])]

        # 2. Select middle order (3 players) - Mix of aggression and stability
        middle = remaining[
            remaining['batting_position'].str.contains('3|4|5', na=False, regex=True)
        ].head(3)
        
        if len(middle) < 3:
            middle = remaining[
                remaining['role'].str.contains('Batsman|Keeper|All-Rounder', na=False, regex=True)
            ].head(3)
        
        selected_xi.extend(middle.to_dict('records'))
        remaining = remaining[~remaining['name'].isin([p['name'] for p in selected_xi])]

        # 3. Select all-rounders (2 players) - Critical for balance
        all_rounders = remaining[
            remaining['role'].str.contains('All-Rounder', na=False)
        ].head(2)
        
        selected_xi.extend(all_rounders.to_dict('records'))
        remaining = remaining[~remaining['name'].isin([p['name'] for p in selected_xi])]

        # 4. Select wicket-keeper if not already selected
        has_keeper = any('Keeper' in p['role'] for p in selected_xi)
        if not has_keeper:
            keeper = remaining[
                remaining['role'].str.contains('Keeper', na=False)
            ].head(1)
            if len(keeper) > 0:
                # Replace the lowest scoring batsman with keeper
                if len(selected_xi) >= 5:
                    selected_xi.pop()  # Remove last middle order player
                selected_xi.extend(keeper.to_dict('records'))
                remaining = remaining[~remaining['name'].isin([p['name'] for p in selected_xi])]

        # 5. Select pace bowlers (2-3 players depending on venue)
        pace_needed = 3 if v_avg < 160 else 2  # More pace on bowling-friendly tracks
        pace = remaining[
            remaining['role'].str.contains('Fast', na=False)
        ].head(pace_needed)
        selected_xi.extend(pace.to_dict('records'))
        remaining = remaining[~remaining['name'].isin([p['name'] for p in selected_xi])]

        # 6. Select spin bowlers (1-2 players)
        spin_needed = 2 if len(pace) < 3 else 1
        spin = remaining[
            remaining['role'].str.contains('Spin', na=False)
        ].head(spin_needed)
        selected_xi.extend(spin.to_dict('records'))
        remaining = remaining[~remaining['name'].isin([p['name'] for p in selected_xi])]

        # 7. Fill remaining spots with best available players
        while len(selected_xi) < 11 and len(remaining) > 0:
            selected_xi.append(remaining.iloc[0].to_dict())
            remaining = remaining.iloc[1:]

        logger.info(f"Selected {len(selected_xi)} players")

        # Final validation
        if len(selected_xi) < 11:
            return jsonify({
                'success': False,
                'error': f'Could not select full team. Only {len(selected_xi)} suitable players available.'
            }), 400

        # Sort by batting position for display
        batting_order_map = {
            '1-2': 1, '1-3': 1, '3': 3, '3-4': 3, '4': 4, '4-5': 4,
            '5': 5, '5-6': 5, '6': 6, '6-7': 6, '7': 7, '7-8': 7,
            '8': 8, '8-9': 8, '9': 9, '9-11': 9, '10': 10, '11': 11
        }
        
        for player in selected_xi:
            pos = player.get('batting_position', '5-6')
            player['order'] = batting_order_map.get(pos, 6)
        
        selected_xi = sorted(selected_xi, key=lambda x: x['order'])

        # Calculate team composition
        batsmen = len([p for p in selected_xi if 'Batsman' in p['role'] or 'Keeper' in p['role']])
        all_rounders_count = len([p for p in selected_xi if 'All-Rounder' in p['role']])
        bowlers = len([p for p in selected_xi if 'Bowler' in p['role'] and 'All-Rounder' not in p['role']])
        pace_count = len([p for p in selected_xi if 'Fast' in p['role']])
        spin_count = len([p for p in selected_xi if 'Spin' in p['role']])

        # Calculate average strike rate
        avg_sr = sum([p['sr'] for p in selected_xi if p['sr'] > 0]) / len([p for p in selected_xi if p['sr'] > 0]) if any(p['sr'] > 0 for p in selected_xi) else 0

        # Generate strengths
        strengths = []
        
        if avg_sr > 135:
            strengths.append(f"⚡ EXPLOSIVE batting lineup (Avg SR: {avg_sr:.1f})")
        elif avg_sr > 120:
            strengths.append(f"✅ BALANCED batting lineup (Avg SR: {avg_sr:.1f})")
        
        total_bowling = bowlers + all_rounders_count
        if total_bowling >= 6:
            strengths.append(f"🎯 EXCELLENT bowling depth ({total_bowling} bowlers)")
        elif total_bowling >= 5:
            strengths.append(f"🎯 GOOD bowling depth ({total_bowling} bowlers)")
        
        if all_rounders_count >= 2:
            strengths.append("⚡ STRONG balance with all-rounders")
        
        if v_avg > 180 and avg_sr > 135:
            strengths.append("🎯 PERFECT for HIGH-SCORING venue")
        elif v_avg < 150 and total_bowling >= 6:
            strengths.append("🎯 IDEAL for LOW-SCORING venue")
        
        if pace_count >= 3:
            strengths.append(f"💨 STRONG pace attack ({pace_count} pacers)")
        
        if spin_count >= 2:
            strengths.append(f"🌀 BALANCED spin options ({spin_count} spinners)")
        
        # Opposition-specific strength
        strengths.append(f"🆚 Optimized against {opposition}")

        return jsonify({
            'success': True,
            'players': selected_xi[:11],  # Ensure only 11 players
            'composition': {
                'batsmen': batsmen,
                'all_rounders': all_rounders_count,
                'bowlers': bowlers,
                'pace': pace_count,
                'spin': spin_count
            },
            'venue_info': {
                'avg_score': round(v_avg, 0),
                'type': 'High-Scoring' if v_avg > 180 else 'Moderate' if v_avg > 160 else 'Low-Scoring'
            },
            'strengths': strengths
        })
        
    except Exception as e:
        logger.error(f"Error in select_playing_xi: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 400

def calculate_comprehensive_metrics(player, batting_stats, bowling_stats, period='career'):
    """
    Calculate comprehensive player metrics including format-wise breakdown
    """
    logger.debug(f"Calculating comprehensive metrics for {player.get('player_name', 'Unknown')}")
    
    exact_name = player['player_name']
    
    # Helper function to safely get numeric values
    def safe_float(value, default=0.0):
        try:
            if pd.isna(value) or value is None or value == '':
                return default
            return float(value)
        except:
            return default
    
    def safe_int(value, default=0):
        try:
            if pd.isna(value) or value is None or value == '':
                return default
            return int(float(value))
        except:
            return default
    
    metrics = {
        'total_matches': 0,
        'batting': {
            'total_runs': 0,
            'average': 0.0,
            'strike_rate': 0.0,
            'hundreds': 0,
            'fifties': 0,
            'highest_score': 0,
            'total_fours': 0,
            'total_sixes': 0,
            'boundary_pct': 0.0,
            'dot_ball_pct': 0.0
        },
        'bowling': {
            'total_wickets': 0,
            'average': 0.0,
            'economy': 0.0,
            'strike_rate': 0.0,
            'best_bowling': 'N/A',
            'five_wickets': 0
        },
        'format_breakdown': {
            'odi': {
                'matches': 0, 'runs': 0, 'avg': 0.0, 'sr': 0.0, 'highest_score': 0,
                'hundreds': 0, 'fifties': 0, 'sixes': 0,
                'wickets': 0, 'economy': 0.0, 'bowling_avg': 0.0, 
                'bowling_sr': 0.0, 'best_bowling': 'N/A', 'five_wickets': 0
            },
            't20i': {
                'matches': 0, 'runs': 0, 'avg': 0.0, 'sr': 0.0, 'highest_score': 0,
                'hundreds': 0, 'fifties': 0, 'sixes': 0,
                'wickets': 0, 'economy': 0.0, 'bowling_avg': 0.0, 
                'bowling_sr': 0.0, 'best_bowling': 'N/A'
            },
            'ipl': {
                'matches': 0, 'runs': 0, 'avg': 0.0, 'sr': 0.0, 'highest_score': 0,
                'hundreds': 0, 'fifties': 0, 'sixes': 0,
                'wickets': 0, 'economy': 0.0, 'bowling_avg': 0.0, 
                'best_bowling': 'N/A'
            }
        },
        'overall_rating': 0.0,
        'batting_rating': 0.0,
        'bowling_rating': 0.0,
        'consistency_score': 0.0
    }

    # Calculate total matches
    odi_matches = safe_int(player.get('odi_matches'))
    t20i_matches = safe_int(player.get('t20i_matches'))
    ipl_matches = safe_int(player.get('ipl_matches'))
    metrics['total_matches'] = odi_matches + t20i_matches + ipl_matches

    # ODI FORMAT BREAKDOWN
    if odi_matches > 0:
        metrics['format_breakdown']['odi'] = {
            'matches': odi_matches,
            'runs': safe_int(player.get('odi_runs')),
            'avg': safe_float(player.get('odi_average')),
            'sr': safe_float(player.get('odi_strike_rate')),
            'highest_score': safe_int(player.get('odi_highest_score')),
            'hundreds': safe_int(player.get('odi_hundreds')),
            'fifties': safe_int(player.get('odi_fifties')),
            'sixes': safe_int(player.get('odi_sixes')),
            'wickets': safe_int(player.get('odi_wickets')),
            'economy': safe_float(player.get('odi_economy')),
            'bowling_avg': safe_float(player.get('odi_bowling_average')),
            'bowling_sr': safe_float(player.get('odi_bowling_sr')),
            'best_bowling': str(player.get('odi_best_bowling', 'N/A')),
            'five_wickets': safe_int(player.get('odi_five_wickets'))
        }

    # T20I FORMAT BREAKDOWN
    if t20i_matches > 0:
        metrics['format_breakdown']['t20i'] = {
            'matches': t20i_matches,
            'runs': safe_int(player.get('t20i_runs')),
            'avg': safe_float(player.get('t20i_average')),
            'sr': safe_float(player.get('t20i_strike_rate')),
            'highest_score': safe_int(player.get('t20i_highest_score')),
            'hundreds': safe_int(player.get('t20i_hundreds')),
            'fifties': safe_int(player.get('t20i_fifties')),
            'sixes': safe_int(player.get('t20i_sixes')),
            'wickets': safe_int(player.get('t20i_wickets')),
            'economy': safe_float(player.get('t20i_economy')),
            'bowling_avg': safe_float(player.get('t20i_bowling_average')),
            'bowling_sr': safe_float(player.get('t20i_bowling_sr')),
            'best_bowling': str(player.get('t20i_best_bowling', 'N/A'))
        }

    # IPL FORMAT BREAKDOWN
    if ipl_matches > 0:
        metrics['format_breakdown']['ipl'] = {
            'matches': ipl_matches,
            'runs': safe_int(player.get('ipl_runs')),
            'avg': safe_float(player.get('ipl_average')),
            'sr': safe_float(player.get('ipl_strike_rate')),
            'highest_score': safe_int(player.get('ipl_highest_score')),
            'hundreds': safe_int(player.get('ipl_hundreds')),
            'fifties': safe_int(player.get('ipl_fifties')),
            'sixes': safe_int(player.get('ipl_sixes')),
            'wickets': safe_int(player.get('ipl_wickets')),
            'economy': safe_float(player.get('ipl_economy')),
            'bowling_avg': safe_float(player.get('ipl_bowling_average')),
            'best_bowling': str(player.get('ipl_best_bowling', 'N/A'))
        }

    is_batsman = 'Batsman' in player['role'] or 'Keeper' in player['role'] or 'All-Rounder' in player['role']
    is_bowler = 'Bowler' in player['role'] or 'All-Rounder' in player['role']

    # BATTING ANALYSIS - Aggregate from all formats
    if is_batsman:
        # Calculate total career batting stats
        total_runs = (metrics['format_breakdown']['odi']['runs'] + 
                     metrics['format_breakdown']['t20i']['runs'] + 
                     metrics['format_breakdown']['ipl']['runs'])
        
        total_hundreds = (metrics['format_breakdown']['odi']['hundreds'] + 
                         metrics['format_breakdown']['t20i']['hundreds'] + 
                         metrics['format_breakdown']['ipl']['hundreds'])
        
        total_fifties = (metrics['format_breakdown']['odi']['fifties'] + 
                        metrics['format_breakdown']['t20i']['fifties'] + 
                        metrics['format_breakdown']['ipl']['fifties'])
        
        total_sixes = (metrics['format_breakdown']['odi']['sixes'] + 
                      metrics['format_breakdown']['t20i']['sixes'] + 
                      metrics['format_breakdown']['ipl']['sixes'])
        
        highest_score = max(
            metrics['format_breakdown']['odi']['highest_score'],
            metrics['format_breakdown']['t20i']['highest_score'],
            metrics['format_breakdown']['ipl']['highest_score']
        )
        
        # Calculate weighted average and strike rate
        total_innings = metrics['total_matches'] * 0.8  # Assume 80% batting innings
        avg_batting_avg = total_runs / total_innings if total_innings > 0 else 0.0
        
        # Weighted strike rate (T20 formats weighted higher)
        weighted_sr = 0.0
        sr_count = 0
        if metrics['format_breakdown']['odi']['matches'] > 0:
            weighted_sr += metrics['format_breakdown']['odi']['sr'] * 0.3
            sr_count += 0.3
        if metrics['format_breakdown']['t20i']['matches'] > 0:
            weighted_sr += metrics['format_breakdown']['t20i']['sr'] * 0.35
            sr_count += 0.35
        if metrics['format_breakdown']['ipl']['matches'] > 0:
            weighted_sr += metrics['format_breakdown']['ipl']['sr'] * 0.35
            sr_count += 0.35
        
        avg_strike_rate = weighted_sr / sr_count if sr_count > 0 else 0.0
        
        metrics['batting'] = {
            'total_runs': total_runs,
            'average': round(avg_batting_avg, 2),
            'strike_rate': round(avg_strike_rate, 2),
            'hundreds': total_hundreds,
            'fifties': total_fifties,
            'highest_score': highest_score,
            'total_fours': 0,  # Not available in master DB
            'total_sixes': total_sixes,
            'boundary_pct': 0.0,  # Not available in master DB
            'dot_ball_pct': 0.0   # Not available in master DB
        }
        
        # Calculate batting rating
        sr_score = min(avg_strike_rate / 140 * 100, 100)
        avg_score = min(avg_batting_avg / 45 * 100, 100)
        metrics['batting_rating'] = (sr_score * 0.5 + avg_score * 0.5)
        metrics['consistency_score'] = 70.0  # Default

    # BOWLING ANALYSIS - Aggregate from all formats
    if is_bowler:
        total_wickets = (metrics['format_breakdown']['odi']['wickets'] + 
                        metrics['format_breakdown']['t20i']['wickets'] + 
                        metrics['format_breakdown']['ipl']['wickets'])
        
        # Weighted economy rate
        weighted_econ = 0.0
        econ_count = 0
        if metrics['format_breakdown']['odi']['matches'] > 0 and metrics['format_breakdown']['odi']['economy'] > 0:
            weighted_econ += metrics['format_breakdown']['odi']['economy'] * 0.3
            econ_count += 0.3
        if metrics['format_breakdown']['t20i']['matches'] > 0 and metrics['format_breakdown']['t20i']['economy'] > 0:
            weighted_econ += metrics['format_breakdown']['t20i']['economy'] * 0.35
            econ_count += 0.35
        if metrics['format_breakdown']['ipl']['matches'] > 0 and metrics['format_breakdown']['ipl']['economy'] > 0:
            weighted_econ += metrics['format_breakdown']['ipl']['economy'] * 0.35
            econ_count += 0.35
        
        avg_economy = weighted_econ / econ_count if econ_count > 0 else 0.0
        
        # Get best bowling figures
        best_bowling = 'N/A'
        if metrics['format_breakdown']['odi']['best_bowling'] != 'N/A':
            best_bowling = metrics['format_breakdown']['odi']['best_bowling']
        elif metrics['format_breakdown']['t20i']['best_bowling'] != 'N/A':
            best_bowling = metrics['format_breakdown']['t20i']['best_bowling']
        elif metrics['format_breakdown']['ipl']['best_bowling'] != 'N/A':
            best_bowling = metrics['format_breakdown']['ipl']['best_bowling']
        
        metrics['bowling'] = {
            'total_wickets': total_wickets,
            'average': round(metrics['format_breakdown']['odi']['bowling_avg'], 2) if metrics['format_breakdown']['odi']['bowling_avg'] > 0 else 0.0,
            'economy': round(avg_economy, 2),
            'strike_rate': round(metrics['format_breakdown']['odi']['bowling_sr'], 2) if metrics['format_breakdown']['odi']['bowling_sr'] > 0 else 0.0,
            'best_bowling': best_bowling,
            'five_wickets': metrics['format_breakdown']['odi']['five_wickets']
        }
        
        # Calculate bowling rating
        econ_score = max(100 - (avg_economy - 6) * 10, 0) if avg_economy > 0 else 0
        wicket_score = min(total_wickets / 80 * 100, 100)
        metrics['bowling_rating'] = (econ_score * 0.5 + wicket_score * 0.5)

    # OVERALL RATING
    if is_batsman and is_bowler:  # All-rounder
        metrics['overall_rating'] = (metrics['batting_rating'] * 0.6 + metrics['bowling_rating'] * 0.4)
    elif is_batsman:
        metrics['overall_rating'] = metrics['batting_rating']
    elif is_bowler:
        metrics['overall_rating'] = metrics['bowling_rating']

    logger.debug(f"Comprehensive metrics calculated successfully")
    return metrics

def compare_players(metrics1, metrics2):
    comparison = {
        'batting': {
            'runs': 'player1' if metrics1['batting']['total_runs'] > metrics2['batting']['total_runs'] else 'player2',
            'average': 'player1' if metrics1['batting']['average'] > metrics2['batting']['average'] else 'player2',
            'strike_rate': 'player1' if metrics1['batting']['strike_rate'] > metrics2['batting']['strike_rate'] else 'player2'
        },
        'bowling': {
            'wickets': 'player1' if metrics1['bowling']['total_wickets'] > metrics2['bowling']['total_wickets'] else 'player2',
            'economy': 'player1' if (metrics1['bowling']['economy'] < metrics2['bowling']['economy'] and metrics1['bowling']['economy'] > 0) else 'player2'
        },
        'overall': {
            'rating': 'player1' if metrics1['overall_rating'] > metrics2['overall_rating'] else 'player2',
            'matches': 'player1' if metrics1['total_matches'] > metrics2['total_matches'] else 'player2'
        }
    }

    player1_wins = sum([1 for key in comparison['batting'].values() if key == 'player1'])
    player1_wins += sum([1 for key in comparison['bowling'].values() if key == 'player1'])
    player1_wins += sum([1 for key in comparison['overall'].values() if key == 'player1'])

    total_comparisons = len(comparison['batting']) + len(comparison['bowling']) + len(comparison['overall'])

    comparison['summary'] = {
        'player1_advantages': player1_wins,
        'player2_advantages': total_comparisons - player1_wins,
        'total_categories': total_comparisons
    }

    return comparison


def create_player_highlight(player, metrics, augmented=None):
    """Create a short main takeaway and supporting bullets for coaches.
    Prefers `augmented` insights when available, otherwise falls back to metrics.
    Returns dict: {'main': str, 'details': [str,...]}.
    """
    details = []
    main = ''

    # Try using augmented insights first (most human-friendly)
    try:
        if augmented and isinstance(augmented, dict):
            ins = augmented.get('player_insights') or augmented
            perf = ins.get('performance_prediction', {}) if isinstance(ins, dict) else {}
            pressure = ins.get('pressure_handling_mechanics', {}) if isinstance(ins, dict) else {}
            phys = ins.get('physiological_profile', {}) if isinstance(ins, dict) else {}

            # Big-game / knockout ability
            big = perf.get('big_game_probability') or pressure.get('big_game_probability') or perf.get('predicted_impact')
            if big:
                main = f"Strong big-game performer — {big}."
                details.append(f"Big-game probability: {big}")

            # Mental toughness
            mtr = pressure.get('mental_toughness_rating')
            if mtr:
                details.append(f"Mental Toughness: {mtr}")

            # Physiological readiness
            readiness = phys.get('hrv_readiness_level') or phys.get('readiness')
            if readiness:
                details.append(f"Readiness: {readiness}")

            # Coach note (short)
            coach = ins.get('coach_note')
            if coach:
                details.append(f"Coach: {coach[:140]}{('...' if len(coach) > 140 else '')}")

            if not main:
                # fallback to a concise summary from pressure/phys
                if mtr and isinstance(mtr, (int, float)) and float(mtr) >= 8:
                    main = "Handles pressure exceptionally well — recommended for high-leverage roles."
                elif readiness and ('low' in str(readiness).lower() or 'high' in str(readiness).lower()):
                    main = f"Readiness flagged: {readiness}. Consider workload adjustments." 
                else:
                    # keep empty to let metric-based fallback fill
                    main = ''
    except Exception:
        main = ''

    # Metric-based fallbacks
    try:
        if not main:
            # Use batting/bowling ratings + consistency
            br = metrics.get('batting_rating', 0)
            wor = metrics.get('overall_rating', 0)
            cons = metrics.get('consistency_score', 0)

            if wor >= 80 or br >= 80:
                main = 'High-impact player — frequent match-winner in preferred formats.'
            elif cons >= 70 and wor >= 65:
                main = 'Consistent high-performer — reliable under pressure.'
            elif wor >= 60:
                main = 'Solid performer — effective in most situations.'
            else:
                main = 'Developing player — may need situational deployment.'

            # Add format preference hints
            fmt = metrics.get('format_breakdown', {})
            try:
                t20_avg = fmt.get('t20i', {}).get('avg', 0)
                odi_avg = fmt.get('odi', {}).get('avg', 0)
                ipl_avg = fmt.get('ipl', {}).get('avg', 0)
                # prefer the format with highest average
                fav_fmt = None
                if t20_avg and (t20_avg >= odi_avg and t20_avg >= ipl_avg):
                    fav_fmt = 'T20/ IPL'
                elif ipl_avg and (ipl_avg >= odi_avg and ipl_avg >= t20_avg):
                    fav_fmt = 'IPL'
                elif odi_avg:
                    fav_fmt = 'ODI'
                if fav_fmt:
                    details.append(f"Performs comparatively better in: {fav_fmt}")
            except Exception:
                pass
    except Exception:
        pass

    # Trim duplicates and limit details
    seen = set()
    filtered = []
    for d in details:
        if d not in seen:
            filtered.append(d)
            seen.add(d)
        if len(filtered) >= 6:
            break

    return {'main': main, 'details': filtered}

@app.route('/api/player-insights/<player_name>', methods=['GET'])
def get_player_insights(player_name):
    """Get detailed player insights including physiological profile and performance prediction."""
    try:
        # Search in augmented data first
        player_rec = None
        
        # Try exact match
        if player_name in augmented_players_data:
            player_rec = augmented_players_data[player_name]
        else:
            # Try case-insensitive match
            for name, data in augmented_players_data.items():
                if name.lower() == player_name.lower():
                    player_rec = data
                    break
        
        if not player_rec:
            return jsonify({'success': False, 'error': f'Player {player_name} not found'}), 404
        
        # Return complete augmented player data
        return jsonify({
            'success': True,
            'player': player_rec  # Return the complete augmented record with all data
        })
    except Exception as e:
        logger.error(f"Error in get_player_insights: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/players-with-insights', methods=['GET'])
def get_players_with_insights():
    """Get all players with their insights summary for listing/search."""
    try:
        limit = request.args.get('limit', 100, type=int)
        country = request.args.get('country', None)
        
        result = []
        count = 0
        for name, data in augmented_players_data.items():
            if country and data.get('country', '').lower() != country.lower():
                continue
            insights = data.get('player_insights', {})
            result.append({
                'name': data.get('player_name'),
                'country': data.get('country'),
                'age': data.get('age'),
                'role': data.get('role'),
                'is_young_star': data.get('is_young_star'),
                'insights_summary': {
                    'mental_toughness_rating': insights.get('pressure_handling_mechanics', {}).get('mental_toughness_rating'),
                    'big_game_probability': insights.get('performance_prediction', {}).get('big_game_probability'),
                    'recovery_speed': insights.get('physiological_profile', {}).get('recovery_speed'),
                    'hrv_readiness_level': insights.get('physiological_profile', {}).get('hrv_readiness_level'),
                    'fatigue_risk': insights.get('performance_prediction', {}).get('fatigue_risk')
                }
            })
            count += 1
            if count >= limit:
                break
        
        return jsonify({
            'success': True,
            'count': len(result),
            'players': result
        })
    except Exception as e:
        logger.error(f"Error in get_players_with_insights: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/top-knockout-candidates', methods=['GET'])
def get_top_knockout_candidates():
    """Return a short report of players with high big-game probability (prefers augmented insights).
    Query params: limit=int, format=(json|csv)
    """
    try:
        limit = int(request.args.get('limit', 50))
        out_format = request.args.get('format', 'json')

        candidates = []
        for name, rec in augmented_players_data.items():
            ins = rec.get('player_insights') or {}
            perf = ins.get('performance_prediction', {}) if isinstance(ins, dict) else {}
            pressure = ins.get('pressure_handling_mechanics', {}) if isinstance(ins, dict) else {}

            big = perf.get('big_game_probability') or pressure.get('big_game_probability') or ''
            if not big:
                # also accept strings like 'Elite (80%...)' inside other fields
                big = perf.get('predicted_impact') or ''

            # simple matching for elite/high markers
            score_flag = False
            big_lowtext = str(big).lower()
            if 'elite' in big_lowtext or 'high' in big_lowtext or '%' in big_lowtext:
                score_flag = True

            if score_flag:
                candidates.append({
                    'name': rec.get('player_name') or name,
                    'country': rec.get('country'),
                    'role': rec.get('role'),
                    'big_game_probability': big,
                    'fatigue_risk': perf.get('fatigue_risk') or '',
                    'mental_toughness': pressure.get('mental_toughness_rating') or '',
                    'readiness': (ins.get('physiological_profile') or {}).get('hrv_readiness_level') if isinstance(ins, dict) else '',
                    'coach_note': (ins.get('coach_note') or '')[:160]
                })

        # sort by presence of 'elite' then by length of big_game_probability
        candidates = sorted(candidates, key=lambda x: (0 if 'elite' in str(x.get('big_game_probability','')).lower() else 1, -len(str(x.get('big_game_probability','')))))
        candidates = candidates[:limit]

        if out_format == 'csv':
            # build CSV
            import io, csv
            si = io.StringIO()
            writer = csv.writer(si)
            writer.writerow(['name','country','role','big_game_probability','mental_toughness','readiness','fatigue_risk','coach_note'])
            for c in candidates:
                writer.writerow([c.get('name',''), c.get('country',''), c.get('role',''), c.get('big_game_probability',''), c.get('mental_toughness',''), c.get('readiness',''), c.get('fatigue_risk',''), c.get('coach_note','')])
            output = make_response(si.getvalue())
            output.headers['Content-Type'] = 'text/csv'
            output.headers['Content-Disposition'] = 'attachment; filename=top_knockout_candidates.csv'
            return output

        return jsonify({'success': True, 'count': len(candidates), 'candidates': candidates})
    except Exception as e:
        logger.error(f"Error in get_top_knockout_candidates: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/coach-reports', methods=['GET'])
def get_coach_reports():
    """Reports for coaches: knockouts, fatigue-risk, readiness-status."""
    try:
        report_type = request.args.get('type', 'knockouts')
        limit = int(request.args.get('limit', 30))
        candidates = []
        if report_type == 'fatigue':
            for name, rec in augmented_players_data.items():
                ins = rec.get('player_insights') or {}
                perf = ins.get('performance_prediction', {}) if isinstance(ins, dict) else {}
                fatigue = perf.get('fatigue_risk', '')
                if fatigue and 'high' in str(fatigue).lower():
                    candidates.append({'name': rec.get('player_name') or name, 'country': rec.get('country'), 'role': rec.get('role'), 'fatigue_risk': fatigue})
            return jsonify({'success': True, 'type': 'fatigue', 'count': len(candidates), 'candidates': candidates[:limit]})
        elif report_type == 'readiness':
            high_r, low_r = [], []
            for name, rec in augmented_players_data.items():
                ins = rec.get('player_insights') or {}
                phys = ins.get('physiological_profile', {}) if isinstance(ins, dict) else {}
                readiness = phys.get('hrv_readiness_level') or ''
                rec_st = {'name': rec.get('player_name') or name, 'country': rec.get('country'), 'readiness': readiness}
                if 'high' in str(readiness).lower():
                    high_r.append(rec_st)
                elif 'low' in str(readiness).lower():
                    low_r.append(rec_st)
            return jsonify({'success': True, 'high': high_r[:limit], 'low': low_r[:limit]})
        else:
            for name, rec in augmented_players_data.items():
                ins = rec.get('player_insights') or {}
                perf = ins.get('performance_prediction', {}) if isinstance(ins, dict) else {}
                big = perf.get('big_game_probability') or ''
                if 'elite' in str(big).lower():
                    candidates.append({'name': rec.get('player_name') or name, 'country': rec.get('country'), 'big_game_probability': big})
            return jsonify({'success': True, 'count': len(candidates), 'candidates': candidates[:limit]})
    except Exception as e:
        logger.error(f"Error in get_coach_reports: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🌐 ENHANCED CRICKET ANALYSIS SYSTEM")
    print("="*70)
    print("🔗 Open: http://localhost:5000")
    print("="*70)
    print(f"\n📊 Loaded:")
    print(f"   Teams: {len(ALL_TEAMS)} (Int + IPL)")
    print(f"   Venues: {len(VENUES)}")
    print(f"   Players: {len(players_df)}")
    print("="*70 + "\n")

    app.run(debug=True, port=5000, host='0.0.0.0')