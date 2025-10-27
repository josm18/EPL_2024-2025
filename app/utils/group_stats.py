import pandas as pd
from pathlib import Path
import os

# Utility functions for performance metrics
def calculate_forward_score(player_data):
    weights = {
        'Goals': 0.35,
        'Shots On Target': 0.2,
        'Shots': 0.15,
        'Conversion %': 0.2,
        'Assists': 0.15,
        'Crosses %': 0.1,
        'fThird Passes %': 0.05,
        'Successful fThird Passes': 0.1,
        'Carries Ended with Goal': 0.15,
        'Carries Ended with Assist': 0.15,
        'Carries Ended with Shot': 0.1,
        'Hit Woodwork': 0.05,
        'Big Chances Missed': -0.1,
        'Offsides': -0.05,
        'Dispossessed': -0.05
    }
    
    score = sum(player_data[metric] * weight for metric, weight in weights.items())
    return score

def calculate_midfielder_score(player_data):
    weights = {
        'Goals': 0.25,
        'Shots On Target': 0.1,
        'Shots': 0.1,
        'Conversion %': 0.1,
        'Passes %': 0.1,
        'Assists': 0.15,
        'Crosses %': 0.1,
        'fThird Passes': 0.15,
        'Successful fThird Passes': 0.1,
        'Through Balls': 0.1,
        'Hit Woodwork': 0.005,
        'Big Chances Missed': -0.05,
        'Offsides': -0.05,
        'Tackles': 0.1,
        'Interceptions': 0.1,
        'Carries Ended with Goal': 0.15,
        'Carries Ended with Assist': 0.15,
        'Carries Ended with Shot': 0.1,
        'Clearances': 0.1,
        'aDuels %': 0.1,
        'gDuels %': 0.1,
        'Possession Won': 0.1,
        'Dispossessed': -0.1
    }
    
    score = sum(player_data[metric] * weight for metric, weight in weights.items())
    return score

def calculate_defender_score(player_data):
    weights = {
        'Tackles': 0.2,
        'Interceptions': 0.2,
        'Clean Sheets': 0.2,
        'Clearances': 0.1,
        'aDuels %': 0.1,
        'gDuels %': 0.1,
        'Possession Won': 0.1,
        'Dispossessed': -0.2,
        'Own Goals': -0.3,
        'Passes %': 0.1
    }
    
    score = sum(player_data[metric] * weight for metric, weight in weights.items())
    return score

def calculate_goalkeeper_score(player_data):
    weights = {
        'Saves %': 0.25,
        'Saves': 0.2,
        'Goals Prevented': 0.25,
        'High Claims': 0.15,
        'Passes %': 0.1,
        'Penalties Saved': 0.1,
        'Punches': 0.05,
        'Dispossessed': -0.1,
        'Goals Conceded': -0.2
    }
    
    score = sum(player_data[metric] * weight for metric, weight in weights.items())
    return score

# Normalize columns to 0-1 scale for scoring
def normalize_columns(df, columns):
    df_norm = df.copy()
    for col in columns:
        if col in df.columns:
            df_norm[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
    return df_norm

# Normalize metrics for radar chart
def normalize_metrics(df):
    """Normalize each metric relative to its maximum value"""
    df_norm = df.copy()
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            max_value = df[col].max()
            df_norm[f'{col}_norm'] = df[col] / max_value
        else:
            continue
    return df_norm