import pandas as pd
import numpy as np
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
    
    df = create_performance_metrics(df)

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


def create_performance_metrics(df):
    """Creates advanced performance metrics"""
    # Offensive efficiency metrics

    # Avoid division by zero and handle missing columns gracefully
    df = df.copy()

    # Set to 0 if Minutes is zero or missing for any per 90 calculation
    df['Goals_per_90'] = np.where(df['Minutes'] > 0, (df['Goals'] / df['Minutes']) * 90, 0)
    df['Assists_per_90'] = np.where(df['Minutes'] > 0, (df['Assists'] / df['Minutes']) * 90, 0)
    df['Goal_Contributions'] = df['Goals'] + df['Assists']
    df['G+A_per_90'] = df['Goals_per_90'] + df['Assists_per_90']
    df['Shot_Accuracy'] = np.where(df['Shots'] > 0, 
                                   (df['Shots On Target'] / df['Shots']) * 100, 0)
    
    # Playmaking metrics
    df['Key_Passes_per_90'] = np.where(df['Minutes'] > 0, (df['Through Balls'] / df['Minutes']) * 90, 0)
    df['Progressive_Actions'] = df['Progressive Carries'] + df['Successful fThird Passes']
    df['Progressive_per_90'] = np.where(df['Minutes'] > 0, (df['Progressive_Actions'] / df['Minutes']) * 90, 0)

    # Defensive metrics
    df['Defensive_Actions'] = df['Tackles'] + df['Interceptions'] + df['Clearances']
    df['Defensive_per_90'] = np.where(df['Minutes'] > 0, (df['Defensive_Actions'] / df['Minutes']) * 90, 0)
    df['Duel_Success_Rate'] = np.where(
        (df['Ground Duels'] + df['Aerial Duels']) > 0,
        ((df['gDuels Won'] + df['aDuels Won']) / (df['Ground Duels'] + df['Aerial Duels'])) * 100,
        0
    )

    # Goalkeeper metrics
    df['Clean_Sheet_Rate'] = np.where(
        df['Appearances'] > 0,
        (df['Clean Sheets'] / df['Appearances']) * 100,
        0
    )

    return df
