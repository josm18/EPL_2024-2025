from matplotlib.pyplot import axes
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import filter_data, get_team_colors
import utils.group_stats as gs

def position_analysis():

    # Get filtered data and team colors
    df = st.session_state.data
    team_colors = get_team_colors()
    st.title("Position Analysis")

    # Performance by Position
    st.subheader("Performance by Position")

    position_stats = df.groupby('Position').agg({
        'Goals_per_90': 'mean',
        'Assists_per_90': 'mean',
        'G+A_per_90': 'mean',
        'Shot_Accuracy': 'mean',
        'Passes %': 'mean',
        'Defensive_per_90': 'mean',
        'Duel_Success_Rate': 'mean',
        'Minutes': 'mean'
    }).round(2)

    st.dataframe(position_stats)

    # Visualization

    def create_tactical_dashboard(df):
        
        # Correlation matrix of offensive metrics
        offensive_metrics = ['Goals_per_90', 'Assists_per_90', 'Shot_Accuracy', 
                            'Conversion %', 'Progressive_per_90']
        corr_matrix = df[offensive_metrics].corr()

        fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdYlBu_r')
        fig_corr.update_layout(title='Offensive Metrics Correlation')
        st.plotly_chart(fig_corr)

        # Distribution of goals per position
        position_goals = df.groupby('Position')['Goals_per_90'].mean().sort_values(ascending=True)
        fig_goals = px.bar(position_goals, x=position_goals.index, y=position_goals.values,
                           title='Goals per 90 Minutes by Position', labels={'x': 'Position', 'y': 'Goals per 90 Minutes'})
        st.plotly_chart(fig_goals)
              
        # Defensive efficiency by position
        defensive_by_pos = df.groupby('Position')['Defensive_per_90'].mean().sort_values(ascending=True)
        fig_defensive = px.bar(defensive_by_pos, orientation='h',
                             title='Defensive Actions per 90 Minutes by Position',
                             labels={'value': 'Defensive Actions per 90 Minutes', 'Position': 'Position'})
        fig_defensive.update_layout(showlegend=False)
        st.plotly_chart(fig_defensive)
        
        # Pass accuracy by position
        pass_accuracy = df.groupby('Position')['Passes %'].mean().sort_values(ascending=True)
        fig_passes = px.bar(pass_accuracy, orientation='h',
                          title='Pass Accuracy by Position',
                          labels={'value': 'Pass Success Percentage', 'Position': 'Position'})
        fig_passes.update_layout(showlegend=False)
        st.plotly_chart(fig_passes)

    create_tactical_dashboard(df)