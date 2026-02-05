"""
PGA Tour 3-Ball Tracker - Streamlit Application
Real-time 3-ball groupings and scores from ESPN and PGA Tour APIs
"""

import streamlit as st
import requests
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="PGA Tour 3-Ball Tracker",
    page_icon="⛳",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0a4d0a 0%, #1a5c1a 100%);
    }
    .stApp {
        background: transparent;
    }
    .threeball-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .player-row {
        padding: 12px;
        border-bottom: 1px solid #f0f0f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .player-row.leader {
        background: #e8f5e9;
        border-radius: 8px;
    }
    .score-under {
        color: #c62828;
        font-weight: bold;
        font-size: 1.2em;
    }
    .score-over {
        color: #2e7d32;
        font-weight: bold;
        font-size: 1.2em;
    }
    .score-even {
        color: #333;
        font-weight: bold;
        font-size: 1.2em;
    }
    h1 {
        color: white !important;
    }
    h2, h3 {
        color: #0a4d0a;
    }
</style>
""", unsafe_allow_html=True)

class PGADataFetcher:
    """Handles fetching data from multiple golf APIs"""
    
    def __init__(self):
        self.espn_leaderboard_url = 'https://site.api.espn.com/apis/site/v2/sports/golf/pga/leaderboard'
        self.pga_schedule_url = 'https://statdata.pgatour.com/r/current/schedule-v2.json'
    
    @st.cache_data(ttl=120)  # Cache for 2 minutes
    def fetch_from_espn(_self):
        """Fetch tournament data from ESPN API"""
        try:
            response = requests.get(_self.espn_leaderboard_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('events') or len(data['events']) == 0:
                return None
                
            event = data['events'][0]
            competition = event.get('competitions', [{}])[0]
            
            return _self.transform_espn_data(event, competition)
        except Exception as e:
            st.warning(f"ESPN API failed: {str(e)}")
            return None
    
    def transform_espn_data(self, event, competition):
        """Transform ESPN data format"""
        competitors = competition.get('competitors', [])
        
        # Group players by tee time
        grouped_by_time = {}
        
        for comp in competitors:
            athlete = comp.get('athlete', {})
            tee_time = comp.get('teeTime', '12:00 PM')
            
            if tee_time not in grouped_by_time:
                grouped_by_time[tee_time] = []
            
            score_value = comp.get('score', {}).get('value', '0')
            try:
                score_num = int(score_value) if score_value else 0
            except:
                score_num = 0
            
            grouped_by_time[tee_time].append({
                'playerName': athlete.get('displayName', 'Unknown'),
                'currentPosition': comp.get('status', {}).get('position', {}).get('displayValue', 'T1'),
                'score': comp.get('score', {}).get('displayValue', 'E'),
                'scoreNum': score_num,
                'thru': comp.get('status', {}).get('thru', 'F'),
                'status': comp.get('status', {}).get('type', {}).get('name', 'active')
            })
        
        # Convert to 3-ball groups
        groups = []
        for tee_time, players in grouped_by_time.items():
            for i in range(0, len(players), 3):
                group = players[i:i+3]
                if group:
                    groups.append({
                        'teeTime': tee_time,
                        'course': competition.get('venue', {}).get('fullName', 'Course'),
                        'players': group
                    })
        
        return {
            'tournament': {
                'tournamentName': event.get('name', 'PGA Tour Event'),
                'currentRound': str(competition.get('status', {}).get('period', 1))
            },
            'pairings': {
                'rnds': [{
                    'roundNum': str(competition.get('status', {}).get('period', 1)),
                    'groups': groups
                }]
            },
            'dataSource': 'ESPN API'
        }
    
    @st.cache_data(ttl=120)
    def fetch_from_pga_tour(_self):
        """Fetch tournament data from PGA Tour API"""
        try:
            schedule_response = requests.get(_self.pga_schedule_url, timeout=10)
            schedule_response.raise_for_status()
            schedule_data = schedule_response.json()
            
            tournaments = schedule_data.get('tournaments', [])
            current_tournament = None
            
            for t in tournaments:
                if t.get('tournStatus') in ['In Progress', 'Upcoming']:
                    current_tournament = t
                    break
            
            if not current_tournament and tournaments:
                current_tournament = tournaments[0]
            
            if not current_tournament:
                return None
            
            perm_num = current_tournament.get('permNum')
            pairings_url = f'https://statdata.pgatour.com/r/{perm_num}/pairings.json'
            
            pairings_response = requests.get(pairings_url, timeout=10)
            pairings_response.raise_for_status()
            pairings_data = pairings_response.json()
            
            leaderboard_url = f'https://statdata.pgatour.com/r/{perm_num}/leaderboard-v2mini.json'
            try:
                leaderboard_response = requests.get(leaderboard_url, timeout=10)
                leaderboard_data = leaderboard_response.json() if leaderboard_response.ok else None
            except:
                leaderboard_data = None
            
            return _self.transform_pga_tour_data(current_tournament, pairings_data, leaderboard_data)
        except Exception as e:
            st.warning(f"PGA Tour API failed: {str(e)}")
            return None
    
    def transform_pga_tour_data(self, tournament, pairings, leaderboard):
        """Transform PGA Tour data format"""
        player_scores = {}
        if leaderboard and leaderboard.get('leaderboard', {}).get('players'):
            for p in leaderboard['leaderboard']['players']:
                player_scores[p.get('player_id')] = {
                    'score': p.get('total', 'E'),
                    'position': p.get('current_position', 'T1'),
                    'thru': p.get('thru', 'F')
                }
        
        current_round_num = tournament.get('currentRound', '1')
        rnds = pairings.get('rnds', [])
        current_round = None
        
        for r in rnds:
            if str(r.get('roundNum')) == str(current_round_num):
                current_round = r
                break
        
        if not current_round and rnds:
            current_round = rnds[0]
        
        if not current_round or not current_round.get('groups'):
            return None
        
        enriched_groups = []
        for group in current_round['groups']:
            players = []
            for p in group.get('players', []):
                pid = p.get('pid')
                score_data = player_scores.get(pid, {})
                
                first_name = p.get('firstName', '')
                last_name = p.get('lastName', '')
                player_name = p.get('playerName', f"{first_name} {last_name}".strip())
                
                score = score_data.get('score', 'E')
                try:
                    score_num = int(score) if score != 'E' else 0
                except:
                    score_num = 0
                
                players.append({
                    'playerName': player_name,
                    'currentPosition': score_data.get('position', 'T1'),
                    'score': score,
                    'scoreNum': score_num,
                    'thru': score_data.get('thru', 'F'),
                    'status': 'active'
                })
            
            enriched_groups.append({
                'teeTime': group.get('teeTime', '12:00 PM'),
                'course': group.get('course', 'Course'),
                'players': players
            })
        
        return {
            'tournament': {
                'tournamentName': tournament.get('tournamentName', 'PGA Tour Event'),
                'currentRound': str(current_round_num)
            },
            'pairings': {
                'rnds': [{
                    'roundNum': str(current_round_num),
                    'groups': enriched_groups
                }]
            },
            'dataSource': 'PGA Tour API'
        }
    
    def get_sample_data(self):
        """Return sample data for demonstration"""
        return {
            'tournament': {
                'tournamentName': 'WM Phoenix Open (Sample Data)',
                'currentRound': '1',
            },
            'pairings': {
                'rnds': [{
                    'roundNum': '1',
                    'groups': [
                        {
                            'teeTime': '7:40 AM',
                            'course': 'TPC Scottsdale (Stadium)',
                            'players': [
                                {'playerName': 'Scottie Scheffler', 'currentPosition': 'T1', 'score': '-5', 'scoreNum': -5, 'thru': '14', 'status': 'active'},
                                {'playerName': 'Rory McIlroy', 'currentPosition': 'T3', 'score': '-4', 'scoreNum': -4, 'thru': '14', 'status': 'active'},
                                {'playerName': 'Jordan Spieth', 'currentPosition': 'T8', 'score': '-2', 'scoreNum': -2, 'thru': '14', 'status': 'active'}
                            ]
                        },
                        {
                            'teeTime': '7:51 AM',
                            'course': 'TPC Scottsdale (Stadium)',
                            'players': [
                                {'playerName': 'Patrick Cantlay', 'currentPosition': 'T1', 'score': '-5', 'scoreNum': -5, 'thru': '13', 'status': 'active'},
                                {'playerName': 'Xander Schauffele', 'currentPosition': 'T5', 'score': '-3', 'scoreNum': -3, 'thru': '13', 'status': 'active'},
                                {'playerName': 'Viktor Hovland', 'currentPosition': 'T12', 'score': '-1', 'scoreNum': -1, 'thru': '13', 'status': 'active'}
                            ]
                        }
                    ]
                }]
            },
            'dataSource': 'Sample Data'
        }
    
    def fetch_tournament_data(self):
        """Fetch tournament data with fallback logic"""
        data = self.fetch_from_espn()
        if data:
            return data
        
        data = self.fetch_from_pga_tour()
        if data:
            return data
        
        return self.get_sample_data()

def format_score(score_num):
    """Format score display"""
    if score_num == 0:
        return 'E'
    elif score_num > 0:
        return f'+{score_num}'
    else:
        return str(score_num)

def get_score_class(score_num):
    """Get CSS class for score"""
    if score_num < 0:
        return 'score-under'
    elif score_num > 0:
        return 'score-over'
    else:
        return 'score-even'

def display_threeball(group):
    """Display a single 3-ball group"""
    # Find leading score
    scores = [p['scoreNum'] for p in group['players']]
    leading_score = min(scores)
    
    st.markdown(f"### 🕐 {group['teeTime']}")
    st.markdown(f"*{group['course']}*")
    
    for player in group['players']:
        is_leader = player['scoreNum'] == leading_score
        score_class = get_score_class(player['scoreNum'])
        formatted_score = format_score(player['scoreNum'])
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            if is_leader:
                st.markdown(f"**🏆 {player['playerName']}** *(Leading)*")
            else:
                st.markdown(f"**{player['playerName']}**")
            st.caption(player['currentPosition'])
        
        with col2:
            st.markdown(f"<span class='{score_class}'>{formatted_score}</span>", unsafe_allow_html=True)
        
        with col3:
            thru_text = 'F' if player['thru'] == 'F' else f"{player['thru']}*"
            st.markdown(thru_text)
    
    st.markdown("---")

# Main app
def main():
    # Header
    st.title("⛳ PGA Tour 3-Ball Tracker")
    
    # Initialize fetcher
    fetcher = PGADataFetcher()
    
    # Sidebar controls
    with st.sidebar:
        st.header("Controls")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        search_term = st.text_input("🔍 Search Player", "")
        
        st.markdown("---")
        st.info("**Auto-refresh:** Data cached for 2 minutes")
        st.caption(f"Last updated: {datetime.now().strftime('%I:%M:%S %p')}")
    
    # Fetch data
    with st.spinner("Loading PGA Tour data..."):
        tournament_data = fetcher.fetch_tournament_data()
    
    if not tournament_data:
        st.error("Unable to load tournament data")
        return
    
    # Display tournament info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader(tournament_data['tournament']['tournamentName'])
    with col2:
        st.metric("Round", tournament_data['tournament']['currentRound'])
    with col3:
        st.info(f"📡 {tournament_data['dataSource']}")
    
    st.markdown("---")
    
    # Get groups
    groups = tournament_data['pairings']['rnds'][0]['groups']
    
    # Filter by search
    if search_term:
        groups = [g for g in groups if any(
            search_term.lower() in p['playerName'].lower() 
            for p in g['players']
        )]
    
    if not groups:
        st.warning("No matches found. Try a different search term.")
        return
    
    # Display groups in columns
    cols = st.columns(2)
    for idx, group in enumerate(groups):
        with cols[idx % 2]:
            with st.container():
                st.markdown('<div class="threeball-card">', unsafe_allow_html=True)
                display_threeball(group)
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
