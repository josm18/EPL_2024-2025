import pandas as pd
from pathlib import Path
import utils.group_stats as gs
import os

def load_data():
    """
    Load and preprocess the EPL player statistics data
    """
    DATA_PATH = Path(__file__).parent.parent.parent / 'data' / 'epl_player_stats_24_25.csv'
    df = pd.read_csv(DATA_PATH)

    # brighton and hove albion and brighton are the same club
    df['Club'] = df['Club'].replace({'Brighton': 'Brighton & Hove Albion'})

    # Data preprocessing
    df['Minutes_Played'] = pd.to_numeric(df['Minutes'], errors='coerce')
    df['Goals_per_90'] = df['Goals'] * 90 / df['Minutes_Played']
    df['Assists_per_90'] = df['Assists'] * 90 / df['Minutes_Played']
    
    # Calculate additional metrics
    df['Goal_Contributions'] = df['Goals'] + df['Assists']
    df['Shot_Accuracy'] = df['Shots On Target'] / df['Shots'] * 100

    # State performance scores
    df['Forward_Score'] = df.apply(gs.calculate_forward_score, axis=1)
    df['Midfielder_Score'] = df.apply(gs.calculate_midfielder_score, axis=1)
    df['Defender_Score'] = df.apply(gs.calculate_defender_score, axis=1)
    df['Goalkeeper_Score'] = df.apply(gs.calculate_goalkeeper_score, axis=1)
    df['Card Score'] = df['Yellow Cards'] * 0.5 + df['Red Cards'] * 1

    df = gs.normalize_metrics(df)

    return df

def get_team_colors():
    """
    Return a dictionary of team colors for visualization
    """
    return {
        'Arsenal': '#EF0107',         # Red
        'Aston Villa': '#95BFE5',     # Light Blue
        'Bournemouth': '#DA291C',     # Red
        'Brentford': '#E30613',       # Red
        'Brighton & Hove Albion': '#0057B8',        # Blue
        'Chelsea': '#034694',         # Blue
        'Crystal Palace': '#1B458F',  # Blue
        'Everton': '#003399',         # Blue
        'Fulham': '#000000',          # Black
        'Ipswich Town': '#0000FF',     # Blue
        'Leicester City': '#003090',   # Blue
        'Liverpool': '#C8102E',       # Red
        'Manchester City': '#6CABDD', # Sky Blue
        'Manchester United': '#DA291C', # Red
        'Newcastle United': '#241F20', # Black
        'Nottingham Forest': '#DD1E2F', # Red
        'Southampton': '#D71920',     # Red
        'Tottenham Hotspur': '#132257', # Navy Blue
        'West Ham United': '#7A263A', # Claret
        'Wolverhampton Wanderers': '#FDB913'    # Gold
    }

def filter_data(df, team=None, position=None, min_minutes=0):
    """
    Filter dataset based on selected criteria
    """
    filtered_df = df.copy()
    
    if team:
        filtered_df = filtered_df[filtered_df['Club'] == team]
    if position:
        filtered_df = filtered_df[filtered_df['Position'] == position]
    if min_minutes > 0:
        filtered_df = filtered_df[filtered_df['Minutes'] >= min_minutes]
        
    return filtered_df
