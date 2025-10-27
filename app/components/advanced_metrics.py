import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats
from utils.data_loader import filter_data, get_team_colors
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
    
    df['Defense_Index'] = (
        stats.zscore(df['Tackles']) +
        stats.zscore(df['Interceptions']) +
        stats.zscore(df['Blocks']) +
        stats.zscore(df['Clean Sheets'])
    ) / 4

    # Show top performers
    st.write("Top 10 Players by Attack Index (Include Goals, Assists, Shots On Target)")
    attack_leaders = df.nlargest(10, 'Attack_Index')[
        ['Player Name', 'Club', 'Position', 'Attack_Index']
    ]
    st.dataframe(attack_leaders)
    
    st.write("Top 10 Players by Possession Index (Include Successful Passes, Progressive Carries, Possession Won)")
    possession_leaders = df.nlargest(10, 'Possession_Index')[
        ['Player Name', 'Club', 'Position', 'Possession_Index']
    ]
    st.dataframe(possession_leaders)

    st.write("Top 10 Players by Defense Index (Include Tackles, Interceptions, Blocks, Clean Sheets)")
    defense_leaders = df.nlargest(10, 'Defense_Index')[
        ['Player Name', 'Club', 'Position', 'Defense_Index']
    ]
    st.dataframe(defense_leaders)

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
    team_colors_map = get_team_colors()
    
    # Create radar chart for team styles
    fig_style = go.Figure()
    for team in team_style['Club']:
        team_data = team_style[team_style['Club'] == team]
        
        fig_style.add_trace(go.Scatterpolar(
            r=team_data[style_metrics].values.flatten().tolist(),
            theta=style_metrics,
            name=team,
            hoverinfo='text',
            hovertext=[
                f"{metric}: {team_data[metric].iloc[0]:.1f}"
                for metric in style_metrics
            ],
            line=dict(color=team_colors_map[team], width=0),
            fill='toself'
        ))
    
    fig_style.update_layout(
        polar=dict(radialaxis=dict(visible=True, showticklabels=False, showline=False)),
        showlegend=True,
    )
    st.plotly_chart(fig_style)

    def create_recruitment_analysis(df):
        """Recruitment analysis based on value-for-money ratio"""
        # Import required libraries
        for col in ['Goals_per_90', 'Assists_per_90', 'Shot_Accuracy', 'Passes %', 'Defensive_per_90', 'Duel_Success_Rate']:
            df[f'{col}_z'] = stats.zscore(df[col])
        # Weighted sum of standardized scores
        df['Performance_Score'] = (
        df['Goals_per_90_z'] * 3 +
        df['Assists_per_90_z'] * 2 +
        df['Shot_Accuracy_z'] * 1 +
        df['Passes %_z'] * 1 +
        df['Defensive_per_90_z'] * 1 +
        df['Duel_Success_Rate_z'] * 1)

        # Identify valued players (lots of playing time, high performance)
        undervalued_field_players = df[(df['Position'] != 'GKP') &
            (df['Minutes'] > df['Minutes'].quantile(0.3)) &
            (df['Performance_Score'] > df['Performance_Score'].quantile(0.7)) &
            (df['Appearances'] > 10)
        ].sort_values('Performance_Score', ascending=False)


        # Scatter plot: Performance vs Playing Time
        # Scatter plot with Plotly
        fig_talent = px.scatter(df[df['Position'] != 'GKP'], 
                                x='Minutes', 
                                y='Performance_Score',
                                color='Appearances',
                                hover_data=['Player Name', 'Club', 'Position'],
                                title='💎 Hidden Talent Identification',
                                labels={'Minutes': 'Minutes played',
                                        'Performance_Score': 'Performance Score',
                                        'Appearances': 'Number of Appearances'})

        # Top valued players plot with Plotly
        fig_top = px.bar(undervalued_field_players.head(15),
                            y='Player Name',
                            x='Performance_Score',
                            orientation='h',
                            title='🎯 Top 15 Valued Players',
                            labels={'Performance_Score': 'Performance Score',
                                'Player Name': ''})

        # Display plots
        st.plotly_chart(fig_talent)
        st.plotly_chart(fig_top)

        return undervalued_field_players[['Player Name', 'Club', 'Position', 'Performance_Score', 
                            'Minutes', 'G+A_per_90', 'Passes %']].head(20)

    st.subheader("Recruitment Analysis: Identifying Undervalued Field Players")
    undervalued_players = create_recruitment_analysis(df)
    st.subheader("Top 20 Field Players")
    st.dataframe(undervalued_players, height=400)