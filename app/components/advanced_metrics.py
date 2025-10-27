import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats
from utils.data_loader import filter_data
import utils.group_stats as gs

def advanced_metrics():
    """
    Advanced metrics component showing correlations and advanced statistics
    """
    st.title("Advanced Metrics")
    
    # Get filtered data
    df = st.session_state.data
    
    # Correlation Analysis
    st.subheader("Performance Metrics Correlation")
    
    # Select metrics for correlation
    numeric_cols = ['Goals', 'Assists', 'Shots', 'Shots On Target', 
                   'Passes', 'Successful Passes', 'Progressive Carries',
                   'Possession Won', 'Minutes']
    
    correlation_matrix = df[numeric_cols].corr()
    
    fig_corr = px.imshow(
        correlation_matrix,
        labels=dict(color="Correlation"),
        x=numeric_cols,
        y=numeric_cols,
        color_continuous_scale="RdBu",
        aspect="auto"
    )
    st.plotly_chart(fig_corr)
    
    # Performance Indices
    st.subheader("Player Performance Index")
    
    # Calculate performance index
    df['Attack_Index'] = (
        stats.zscore(df['Goals']) + 
        stats.zscore(df['Assists']) + 
        stats.zscore(df['Shots On Target'])
    ) / 3
    
    df['Possession_Index'] = (
        stats.zscore(df['Successful Passes']) + 
        stats.zscore(df['Progressive Carries']) + 
        stats.zscore(df['Possession Won'])
    ) / 3
    
    # Show top performers
    st.write("Top 10 Players by Attack Index")
    attack_leaders = df.nlargest(10, 'Attack_Index')[
        ['Player Name', 'Club', 'Position', 'Attack_Index']
    ]
    st.dataframe(attack_leaders)
    
    st.write("Top 10 Players by Possession Index")
    possession_leaders = df.nlargest(10, 'Possession_Index')[
        ['Player Name', 'Club', 'Position', 'Possession_Index']
    ]
    st.dataframe(possession_leaders)
    
    # Scatter plot of indices
    fig_indices = px.scatter(
        df,
        x='Attack_Index',
        y='Possession_Index',
        color='Position',
        hover_data=['Player Name', 'Club'],
        title="Attack vs Possession Index"
    )
    st.plotly_chart(fig_indices)
    
    # Advanced Team Analysis
    st.subheader("Team Style Analysis")
    
    team_style = df.groupby('Club').agg({
        'Passes': 'mean',
        'Progressive Carries': 'mean',
        'Possession Won': 'mean',
        'Goals': 'mean',
        'Shots': 'mean'
    }).reset_index()
    
    # Normalize metrics
    style_metrics = ['Passes', 'Progressive Carries', 'Possession Won', 'Goals', 'Shots']
    team_style[style_metrics] = team_style[style_metrics].apply(stats.zscore)
    
    # Create radar chart for team styles
    fig_style = go.Figure()
    
    for team in team_style['Club']:
        team_data = team_style[team_style['Club'] == team]
        values = team_data[style_metrics].values.flatten().tolist()
        values.append(values[0])  # Complete the circle
        
        fig_style.add_trace(go.Scatterpolar(
            r=values,
            theta=style_metrics + [style_metrics[0]],
            name=team
        ))
    
    fig_style.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=True
    )
    st.plotly_chart(fig_style)
