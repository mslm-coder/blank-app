import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
import streamlit as st
from datetime import datetime

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
    h1 {
        color: white !important;
    }
    h2, h3 {
        color: #0a4d0a;
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
</style>
""", unsafe_allow_html=True)

def get_sample_data():
    """Sample tournament data"""
    return {
        'tournament': {
            'tournamentName': 'WM Phoenix Open (Demo)',
            'currentRound': '2',
        },
        'pairings': {
            'rnds': [{
                'roundNum': '2',
                'groups': [
                    {
                        'teeTime': '7:40 AM',
                        'course': 'TPC Scottsdale (Stadium)',
                        'players': [
                            {'playerName': 'Scottie Scheffler', 'currentPosition': 'T1', 'score': '-12', 'scoreNum': -12, 'thru': '15', 'status': 'active'},
                            {'playerName': 'Rory McIlroy', 'currentPosition': 'T3', 'score': '-10', 'scoreNum': -10, 'thru': '15', 'status': 'active'},
                            {'playerName': 'Jordan Spieth', 'currentPosition': 'T8', 'score': '-7', 'scoreNum': -7, 'thru': '15', 'status': 'active'}
                        ]
                    },
                    {
                        'teeTime': '7:51 AM',
                        'course': 'TPC Scottsdale (Stadium)',
                        'players': [
                            {'playerName': 'Patrick Cantlay', 'currentPosition': 'T1', 'score': '-12', 'scoreNum': -12, 'thru': '14', 'status': 'active'},
                            {'playerName': 'Xander Schauffele', 'currentPosition': 'T5', 'score': '-9', 'scoreNum': -9, 'thru': '14', 'status': 'active'},
                            {'playerName': 'Viktor Hovland', 'currentPosition': 'T12', 'score': '-6', 'scoreNum': -6, 'thru': '14', 'status': 'active'}
                        ]
                    },
                    {
                        'teeTime': '8:02 AM',
                        'course': 'TPC Scottsdale (Stadium)',
                        'players': [
                            {'playerName': 'Jon Rahm', 'currentPosition': 'T3', 'score': '-10', 'scoreNum': -10, 'thru': '13', 'status': 'active'},
                            {'playerName': 'Collin Morikawa', 'currentPosition': 'T8', 'score': '-7', 'scoreNum': -7, 'thru': '13', 'status': 'active'},
                            {'playerName': 'Justin Thomas', 'currentPosition': 'T15', 'score': '-5', 'scoreNum': -5, 'thru': '13', 'status': 'active'}
                        ]
                    },
                    {
                        'teeTime': '8:13 AM',
                        'course': 'TPC Scottsdale (Stadium)',
                        'players': [
                            {'playerName': 'Max Homa', 'currentPosition': 'T5', 'score': '-9', 'scoreNum': -9, 'thru': '12', 'status': 'active'},
                            {'playerName': 'Tony Finau', 'currentPosition': 'T12', 'score': '-6', 'scoreNum': -6, 'thru': '12', 'status': 'active'},
                            {'playerName': 'Sam Burns', 'currentPosition': 'T20', 'score': '-4', 'scoreNum': -4, 'thru': '12', 'status': 'active'}
                        ]
                    },
                    {
                        'teeTime': '12:30 PM',
                        'course': 'TPC Scottsdale (Stadium)',
                        'players': [
                            {'playerName': 'Tommy Fleetwood', 'currentPosition': 'T8', 'score': '-7', 'scoreNum': -7, 'thru': 'F', 'status': 'complete'},
                            {'playerName': 'Hideki Matsuyama', 'currentPosition': 'T15', 'score': '-5', 'scoreNum': -5, 'thru': 'F', 'status': 'complete'},
                            {'playerName': 'Rickie Fowler', 'currentPosition': 'T25', 'score': '-3', 'scoreNum': -3, 'thru': 'F', 'status': 'complete'}
                        ]
                    },
                    {
                        'teeTime': '12:41 PM',
                        'course': 'TPC Scottsdale (Stadium)',
                        'players': [
                            {'playerName': 'Brooks Koepka', 'currentPosition': 'T12', 'score': '-6', 'scoreNum': -6, 'thru': 'F', 'status': 'complete'},
                            {'playerName': 'Cameron Smith', 'currentPosition': 'T20', 'score': '-4', 'scoreNum': -4, 'thru': 'F', 'status': 'complete'},
                            {'playerName': 'Will Zalatoris', 'currentPosition': 'T30', 'score': '-2', 'scoreNum': -2, 'thru': 'F', 'status': 'complete'}
                        ]
                    }
                ]
            }]
        },
        'dataSource': 'Demo Data (Browser Environment)'
    }

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
    st.title("⛳ PGA Tour 3-Ball Tracker")
    
    # Sidebar
    with st.sidebar:
        st.header("Controls")
        
        st.info("🌐 **Browser Demo Mode**\n\nThis is sample data. For live data:\n- Download index.html and open in browser\n- OR deploy to Streamlit Cloud")
        
        st.markdown("---")
        search_term = st.text_input("🔍 Search Player", "")
        
        st.markdown("---")
        st.caption(f"Demo updated: {datetime.now().strftime('%I:%M:%S %p')}")
    
    # Get sample data
    tournament_data = get_sample_data()
    
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
                display_threeball(group)

if __name__ == '__main__':
    main()
