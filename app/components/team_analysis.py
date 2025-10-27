import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.data_loader  import filter_data
from utils.data_loader import get_team_colors


def team_analysis():
    """
    Team analysis component showing team performance and statistics
    """
    st.title("Team Analysis")
    
    # Get filtered data and team colors
    if 'data' not in st.session_state or st.session_state.data is None:
        st.warning("No data loaded. Please upload or load data to proceed.")
        return
    df = st.session_state.data
    team_colors = get_team_colors()
    
    # Team selection
    teams = sorted(df['Club'].unique())
    st.write("### Team Selection")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_teams = st.multiselect("Select Teams to Compare", teams, default=[teams[0]], max_selections=5)
    with col2:
        analysis_type = st.radio("Analysis Type", ["Single Team", "Team Comparison"])
    
    if not selected_teams:
        st.info("Please select at least one team to analyze")
        return
    
    # Filter data based on selection
    team_data = df[df['Club'].isin(selected_teams)]
    
    # Apply additional filters
    positions = st.multiselect("Filter by Position", sorted(df['Position'].unique()))
    min_minutes = st.slider("Minimum Minutes Played", 0, 3000, 0)
    
    if positions:
        team_data = team_data[team_data['Position'].isin(positions)]
    if min_minutes > 0:
        team_data = team_data[team_data['Minutes'] >= min_minutes]
    
    # Team Overview
    st.subheader("Team Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Squad Size",
            len(team_data),
            f"{len(team_data[team_data['Minutes'] > 0])} active players"
        )
    
    with col2:
        st.metric(
            "Total Goals",
            team_data['Goals'].sum(),
            f"{team_data['Goals'].mean():.2f} per player"
        )
    
    with col3:
        st.metric(
            "Total Assists",
            team_data['Assists'].sum(),
            f"{team_data['Assists'].mean():.2f} per player"
        )

    with col4:
        st.metric(
            "Total Goals Conceded",
            team_data['Goals Conceded'].sum(),
            f"{team_data['Goals Conceded'].mean():.2f} per player"
        )
    
    # Position Distribution
    st.subheader("Squad Composition")
    pos_dist = team_data['Position'].value_counts()
    fig_pos = px.pie(
        values=pos_dist.values,
        names=pos_dist.index,
        title="Position Distribution"
    )
    st.plotly_chart(fig_pos)

    # Playing Time Distribution
    st.subheader("Playing Time Distribution")
    fig_minutes = px.bar(
        team_data,
        x='Player Name',
        y='Minutes',
        color='Position',
        title="Minutes Played by Player"
    )
    st.plotly_chart(fig_minutes)
    
    # Player Performance
    st.subheader("Top Attack Performers")
    
    # Goals
    top_scorers = team_data.nlargest(5, 'Forward_Score')[['Player Name', 'Forward_Score', 'Goals', 'Minutes', 'Club']]
    fig_scorers = px.bar(
        top_scorers,
        x='Player Name',
        y='Forward_Score',
        color='Club',
        color_discrete_map=team_colors
    )
    st.plotly_chart(fig_scorers)

    st.subheader("Top Playmakers")

    top_assisters = team_data.nlargest(5, 'Midfielder_Score')[['Player Name', 'Midfielder_Score', 'Minutes', 'Club']]
    fig_assisters = px.bar(
        top_assisters,
        x='Player Name',
        y='Midfielder_Score',
        color='Club',
        color_discrete_map=team_colors
    )
    st.plotly_chart(fig_assisters)

    st.subheader("Top Defensive Players")

    top_defenders = team_data.nlargest(5, 'Defender_Score')[['Player Name', 'Defender_Score', 'Tackles', 'Minutes', 'Club']]
    fig_defenders = px.bar(
        top_defenders,
        x='Player Name',
        y='Defender_Score',
        color='Club',
        color_discrete_map=team_colors
    )
    st.plotly_chart(fig_defenders)

    if analysis_type == "Team Comparison":
        st.write("## Team Comparison Analysis")
        
        # Possession and Progressive Play Comparison
        st.subheader("Possession and Progressive Play")
        team_possession = team_data.groupby('Club').agg({
            'Passes': 'sum',
            'Passes %': 'mean',
            'Progressive Carries': 'sum',
            'fThird Passes': 'sum',
            'Through Balls': 'sum'
        }).reset_index()
        
        fig_possession = px.bar(
            team_possession,
            x='Club',
            y=['Passes', 'Progressive Carries'],
            barmode='group',
            title="Possession and Progressive Play Metrics"
        )
        st.plotly_chart(fig_possession)
        
        # Defensive Comparison
        st.subheader("Defensive Performance")
        team_defense = team_data.groupby('Club').agg({
            'Tackles_norm': 'mean',
            'Interceptions_norm': 'mean',
            'Blocks_norm': 'mean',
            'Clean Sheets_norm': 'mean',
            'Possession Won_norm': 'mean',
            'Tackles': 'mean',
            'Interceptions': 'mean',
            'Blocks': 'mean',
            'Clean Sheets': 'mean',
            'Possession Won': 'mean'
        }).reset_index()
        
        # Radar chart for defensive metrics
        fig_defense = go.Figure()
        metrics = ['Tackles', 'Interceptions', 'Blocks', 'Clean Sheets', 'Possession Won']
        team_colors_map = get_team_colors()
        
        for team in team_defense['Club']:
            team_def_data = team_defense[team_defense['Club'] == team]
            # values.append(values[0])  # Complete the circle
            
            fig_defense.add_trace(go.Scatterpolar(
                r=[team_def_data[f'{metric}_norm'].iloc[0] for metric in metrics],
                theta=metrics,
                name=team,
                hoverinfo='text',
                hovertext=[
                    f"{metric}: {team_def_data[metric].iloc[0]:.1f}<br>Relative: {team_def_data[f'{metric}_norm'].iloc[0]:.1%}"
                    for metric in metrics
                ],
                line=dict(color=team_colors_map[team], width=0),
                fill='toself'
            ))
        
        fig_defense.update_layout(  
            polar=dict(radialaxis=dict(visible=True, showticklabels=False, showline=False)),
            showlegend=True,
            title="Defensive Metrics Comparison"
        )
        st.plotly_chart(fig_defense)
        
        # Attacking Efficiency
        st.subheader("Attacking Efficiency")
        team_attack = team_data.groupby('Club').agg({
            'Goals': 'sum',
            'Shots': 'sum',
            'Shots On Target': 'sum',
            'Big Chances Missed': 'sum'
        }).reset_index()
        
        team_attack['Conversion Rate'] = (team_attack['Goals'] / team_attack['Shots'] * 100).round(2)
        team_attack['Shot Accuracy'] = (team_attack['Shots On Target'] / team_attack['Shots'] * 100).round(2)
        
        fig_attack = px.scatter(
            team_attack,
            x='Shot Accuracy',
            y='Conversion Rate',
            size='Goals',
            hover_data=['Club', 'Shots', 'Goals'],
            text='Club',
            color= 'Club',
            color_discrete_map=team_colors,
            title="Shot Efficiency Analysis"
        )
        st.plotly_chart(fig_attack)
        
    # Detailed Team Statistics
    st.subheader("Detailed Team Statistics")
    
    # Calculate advanced team stats
    team_stats = team_data.groupby('Club').agg({
        'Goals': 'sum',
        'Assists': 'sum',
        'Shots': 'sum',
        'Shots On Target': 'sum',
        'Passes': 'sum',
        'Passes %': 'mean',
        'Progressive Carries': 'sum',
        'Possession Won': 'sum',
        'Tackles': 'sum',
        'Interceptions': 'sum',
        'Blocks': 'sum',
        'Ground Duels': 'sum',
        'gDuels %': 'mean',
        'Aerial Duels': 'sum',
        'aDuels %': 'mean',
        'Dispossessed': 'sum',
        'Clean Sheets': lambda x: x[team_data['Position'] == 'GKP'].sum()
    }).reset_index()
    st.write("Below is a summary table of key statistics for the selected teams, including attacking, defensive, and passing metrics.")
    st.dataframe(team_stats)
