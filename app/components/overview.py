import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import filter_data, get_team_colors


def overview():
    """
    Overview section displaying key statistics and trends
    """
    st.title("Premier League Analytics 2024/25")
    
    # Get filtered data and team colors
    df = st.session_state.data
    team_colors = get_team_colors()
    if st.session_state.filters['team']:
        df = df[df['Club'].isin(st.session_state.filters['team'])]
    if st.session_state.filters['position']:
        df = df[df['Position'].isin(st.session_state.filters['position'])]
    
    # Layout with columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Goals",
            df['Goals'].sum(),
            f"{df['Goals'].mean():.2f} per player"
        )
    
    with col2:
        st.metric(
            "Total Assists",
            df['Assists'].sum(),
            f"{df['Assists'].mean():.2f} per player"
        )
    
    with col3:
        st.metric(
            "Average Minutes",
            f"{df['Minutes'].mean():.0f}",
            f"{df['Minutes'].std():.0f} std dev"
        )
    
    # Position Distribution
    st.subheader("Player Distribution by Position")
    pos_dist = df['Position'].value_counts()
    fig_pos = px.pie(
        values=pos_dist.values,
        names=pos_dist.index,
        title="Position Distribution"
    )
    st.plotly_chart(fig_pos)

    # Team Performance Overview
    st.subheader("Team Performance Overview")
    team_stats = df.groupby('Club').agg({
        'Goals': 'sum',
        'Assists': 'sum',
        'Goals Conceded': 'sum',
        'Shots': 'sum',
        'Shots On Target': 'sum',
        'Goals_per_90': 'mean',
        'Defensive_per_90': 'mean'
    }).reset_index()
    
    fig_team = px.bar(
        team_stats,
        x='Club',
        y=['Goals', 'Goals Conceded'],
        title="Goals and Assists by Team",
        barmode='group'
    )
    st.plotly_chart(fig_team)
    
    # Shot Efficiency Analysis
    st.subheader("Shot Efficiency Analysis")
    shot_efficiency = team_stats.copy()
    shot_efficiency['Conversion Rate'] = (shot_efficiency['Goals'] / shot_efficiency['Shots']) * 100
    
    fig_efficiency = px.scatter(
        shot_efficiency,
        x='Shots',
        y='Goals',
        size='Conversion Rate',
        hover_data=['Club'],
        color= 'Club',
        color_discrete_map=team_colors,
        text='Club',
        title="Shot Efficiency by Team"
    )
    st.plotly_chart(fig_efficiency)

    # Defensive Efficiency Analysis
    st.subheader("Defensive Efficiency Analysis")
    defensive_efficiency = team_stats.copy()
    defensive_efficiency['Defensive Efficiency'] = (
        defensive_efficiency['Shots On Target'] / defensive_efficiency['Goals Conceded']
    ) * 100
    fig_defensive = px.scatter(
        defensive_efficiency,
        x='Shots On Target',
        y='Goals Conceded',
        size='Defensive Efficiency',
        hover_data=['Club'],
        color= 'Club',
        color_discrete_map=team_colors,
        text='Club',
        title="Defensive Efficiency by Team"
    )
    st.plotly_chart(fig_defensive)
    
    # Scatter plot: Offense vs Defense
    st.subheader("Team Offensive and Defensive Balance")

    fig_offense_defense = px.scatter(
        team_stats,
        x='Goals_per_90',
        y='Defensive_per_90',
        color='Club',
        color_discrete_map=team_colors,
        text='Club'
    )
    fig_offense_defense.update_layout(
        title='Team Offensive-Defensive Balance',
        xaxis_title='Goals per 90min (team average)',
        yaxis_title='Defensive actions per 90min'
    )
    st.plotly_chart(fig_offense_defense)

    # Team buildup analysis
    st.subheader("Team Build-Up Analysis")
    team_buildup = df.groupby('Club').agg({
        'Passes': 'mean',
        'Passes %': 'mean',
        'Progressive Carries': 'mean',
        'Possession Won': 'mean',
        'Crosses %': 'mean',
        'fThird Passes': 'mean'
    }).reset_index()

    fig_buildup = px.scatter(
        team_buildup,
        x='Passes',
        y='Progressive Carries',
        size='Passes %',
        hover_data=['Club'],
        color= 'Club',
        color_discrete_map=team_colors,
        text='Club',
        title="Build-Up Play by Team"
    )
    st.plotly_chart(fig_buildup)

    fig_finalThird = px.scatter(
        team_buildup,
        x='fThird Passes',
        y='Crosses %',
        size='Possession Won',
        hover_data=['Club'],
        color= 'Club',
        color_discrete_map=team_colors,
        text='Club',
        title="Final Third Play by Team"
    )
    st.plotly_chart(fig_finalThird)


