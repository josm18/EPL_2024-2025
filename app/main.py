import streamlit as st
from components.sidebar import sidebar
from components.overview import overview
from components.player_analysis import player_analysis
from components.team_analysis import team_analysis
from components.advanced_metrics import advanced_metrics
import utils.data_loader as data_loader


# Page configuration
st.set_page_config(
    page_title="Premier League Analytics 24/25",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('app/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = data_loader.load_data()

def main():
    # Sidebar
    page = sidebar()
    
    # Main content
    if page == "Overview":
        overview()
    elif page == "Player Analysis":
        player_analysis()
    elif page == "Team Analysis":
        team_analysis()
    elif page == "Advanced Metrics":
        advanced_metrics()

if __name__ == "__main__":
    main()
