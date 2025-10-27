import streamlit as st
import plotly.express as px
from utils.data_loader import filter_data

def sidebar():
    """
    Create and manage the sidebar filters
    """
    st.sidebar.title("⚽ Navigation")
    
    # Page selection
    page = st.sidebar.selectbox(
        "Choose a section",
        ["Overview", "Player Analysis", "Team Analysis", "Advanced Metrics"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.title("🎯 Filters")
    
    # Common filters
    teams = sorted(st.session_state.data['Club'].unique())
    positions = sorted(st.session_state.data['Position'].unique())
    
    selected_team = st.sidebar.multiselect("Select Team(s)", teams)
    selected_position = st.sidebar.multiselect("Select Position(s)", positions)
    min_minutes = st.sidebar.slider("Minimum Minutes Played", 0, 3000, 0)
    
    # Store filter selections in session state
    st.session_state.filters = {
        'team': selected_team,
        'position': selected_position,
        'min_minutes': min_minutes
    }
    
    return page
