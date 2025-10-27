import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import filter_data, get_team_colors
import utils.group_stats as gs

def player_analysis():
    """
    Player analysis component with detailed player statistics and comparisons
    """
    st.title("Player Analysis")
    
    # Get filtered data and team colors
    df = st.session_state.data
    team_colors = get_team_colors()
    
    # Filtering options
    st.sidebar.write("### Filters")
    
    # Position filter
    positions = sorted(df['Position'].unique())
    selected_positions = st.sidebar.multiselect("Filter by Position", positions)
    
    # Team filter
    teams = sorted(df['Club'].unique())
    selected_teams = st.sidebar.multiselect("Filter by Team", teams)
    
    # Minutes filter
    min_minutes = st.sidebar.slider("Minimum Minutes Played", 0, 3000, 300)
    
    # Apply filters
    filtered_df = df.copy()

    if selected_positions:
        filtered_df = filtered_df[filtered_df['Position'].isin(selected_positions)]
    if selected_teams:
        filtered_df = filtered_df[filtered_df['Club'].isin(selected_teams)]
    filtered_df = filtered_df[filtered_df['Minutes'] >= min_minutes]

    

    # Player selection from filtered data
    players = sorted(filtered_df['Player Name'].unique())
    selected_players = st.multiselect(
        "Select Players to Compare",
        players,
        max_selections=5
    )
    
    if not selected_players:
        st.info("Please select players to analyze")
        return
    
    # Player comparison
    player_stats = df[df['Player Name'].isin(selected_players)]
    
    # Create a color mapping for the selected players based on their teams
    player_team_colors = {
        player: team_colors[player_stats[player_stats['Player Name'] == player]['Club'].iloc[0]]
        for player in selected_players
    }
    
    # Display Analysis Type Selection
    analysis_type = st.radio(
        "Select Analysis Type",
        ["Offensive Metrics", "Defensive Metrics", "Possession Metrics"]
    )
    
    # Radar Chart
    st.subheader("Player Comparison - Key Metrics")
    
    if analysis_type == "Offensive Metrics":
        metrics = ['Goals', 'Assists', 'Shots On Target', 'Conversion %',
                  'Big Chances Missed', 'Through Balls']
    elif analysis_type == "Defensive Metrics":
        metrics = ['Tackles', 'Interceptions', 'Blocks', 'Possession Won',
                  'gDuels Won', 'aDuels Won']
    else:  # Possession Metrics
        metrics = ['Passes %', 'Progressive Carries',
                  'fThird Passes %', 'Possession Won', 'Dispossessed']

    fig = go.Figure()
    for player in selected_players:
        player_data = player_stats[player_stats['Player Name'] == player]
        #values = [player[f'{metric}_norm'] for metric in metrics]
        #values.append(values[0])  # Complete the circle
        
        fig.add_trace(go.Scatterpolar(
            r=[player_data[f'{metric}_norm'].iloc[0] for metric in metrics],
            theta=metrics,
            name=player,
            hoverinfo='text',
            hovertext=[
                f"{metric}: {player_data[metric].iloc[0]:.1f}<br>Relative: {player_data[f'{metric}_norm'].iloc[0]:.1%}"
                for metric in metrics
            ],
            line=dict(color=player_team_colors[player], width=0),
            fillcolor=player_team_colors[player],
            opacity=0.6,
            fill='toself'
        ))
    
    fig.update_layout(
        polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 1],
            showticklabels=False,
            showline=False,
            showgrid=True,
            gridcolor='rgba(211, 211, 211, 0.5)',  # Light gray with transparency
            tickvals=[0.2, 0.4, 0.6, 0.8, 1.0],
            ticktext=['20%', '40%', '60%', '80%', '100%']
        ),
        angularaxis=dict(
            showline=True,
            linewidth=2,
            linecolor='rgba(211, 211, 211, 0.5)',
            gridcolor='rgba(211, 211, 211, 0.5)'
        ),
        bgcolor='rgba(0,0,0,0)'  # Transparent background
    ),
    showlegend=True,
    height=600,
    width=800,
    paper_bgcolor='white',
    plot_bgcolor='white'
    )
    st.plotly_chart(fig)
    
    # Detailed Statistics based on analysis type
    st.subheader("Detailed Statistics")
    
    if analysis_type == "Offensive Metrics":
        cols = ['Player Name', 'Club', 'Position', 'Minutes', 'Goals', 'Assists',
                'Shots', 'Shots On Target', 'Conversion %', 'Big Chances Missed',
                'Through Balls', 'Carries Ended with Shot']
    elif analysis_type == "Defensive Metrics":
        cols = ['Player Name', 'Club', 'Position', 'Minutes', 'Tackles', 
                'Interceptions', 'Blocks', 'Possession Won', 'Clean Sheets',
                'Ground Duels', 'gDuels Won', 'gDuels %',
                'Aerial Duels', 'aDuels Won', 'aDuels %']
    else:  # Possession Metrics
        cols = ['Player Name', 'Club', 'Position', 'Minutes', 'Passes',
                'Successful Passes', 'Passes %', 'Progressive Carries',
                'fThird Passes', 'fThird Passes %', 'Through Balls',
                'Dispossessed']
    
    st.dataframe(player_stats[cols].set_index('Player Name'))
    
    # Detailed Analysis based on type
    if analysis_type == "Offensive Metrics":
        # Offensive Performance
        st.subheader("Offensive Performance")
        off_metrics = pd.melt(
            player_stats,
            id_vars=['Player Name'],
            value_vars=['Goals', 'Assists', 'Shots On Target', 'Big Chances Missed'],
            var_name='Metric',
            value_name='Value'
        )
        
        fig_off = px.bar(
            off_metrics,
            x='Player Name',
            y='Value',
            color='Metric',
            title="Offensive Metrics Comparison",
            barmode='group'
        )
        st.plotly_chart(fig_off)
        
        # Shot Efficiency
        st.subheader("Shot Efficiency Analysis")
        fig_efficiency = px.scatter(
            player_stats,
            x='Shots',
            y='Goals',
            size='Minutes',
            color='Club',
            color_discrete_map=team_colors,
            hover_data=['Player Name', 'Conversion %'],
            text='Player Name',
            title="Goals vs Shots"
        )
        st.plotly_chart(fig_efficiency)
        
    elif analysis_type == "Defensive Metrics":
        # Defensive Actions
        st.subheader("Defensive Actions")
        def_metrics = pd.melt(
            player_stats,
            id_vars=['Player Name'],
            value_vars=['Tackles', 'Interceptions', 'Blocks', 'Possession Won'],
            var_name='Metric',
            value_name='Value'
        )
        
        fig_def = px.bar(
            def_metrics,
            x='Player Name',
            y='Value',
            color='Metric',
            title="Defensive Actions Comparison",
            barmode='group'
        )
        st.plotly_chart(fig_def)
        
        # Duels Analysis
        st.subheader("Duels Analysis")
        cols = st.columns(2)
        
        with cols[0]:
            fig_ground = px.bar(
                player_stats,
                x='Player Name',
                y=['Ground Duels', 'gDuels Won'],
                title="Ground Duels",
                barmode='group'
            )
            st.plotly_chart(fig_ground)
            
        with cols[1]:
            fig_aerial = px.bar(
                player_stats,
                x='Player Name',
                y=['Aerial Duels', 'aDuels Won'],
                title="Aerial Duels",
                barmode='group'
            )
            st.plotly_chart(fig_aerial)
        
        # Cards Analysis
        st.subheader("Cards Analysis")
        fig_cards = px.scatter(
            player_stats,
            x='Appearances',    
            y='Card Score',
            title="Card Impact Analysis",
            size='Minutes',
            color='Club',
            color_discrete_map=team_colors,
            hover_data=['Player Name', 'Yellow Cards', 'Red Cards'],
        )
        st.plotly_chart(fig_cards)

    else:  # Possession Metrics
        # Passing Analysis
        st.subheader("Passing Analysis")
        fig_passing = px.bar(
            player_stats,
            x='Player Name',
            y=['Passes', 'Successful Passes'],
            title="Passing Accuracy",
            barmode='group'
        )
        st.plotly_chart(fig_passing)
        
        # Progressive Play
        st.subheader("Progressive Play Analysis")
        prog_metrics = pd.melt(
            player_stats,
            id_vars=['Player Name'],
            value_vars=['Progressive Carries', 'fThird Passes', 'Through Balls'],
            var_name='Metric',
            value_name='Value'
        )
        
        fig_prog = px.bar(
            prog_metrics,
            x='Player Name',
            y='Value',
            color='Metric',
            title="Progressive Play Metrics",
            barmode='group'
        )
        st.plotly_chart(fig_prog)

        fig_runVSpassing = px.scatter(
            player_stats,
            x='Progressive Carries',
            y='fThird Passes',
            size='Minutes',
            color='Club',
            color_discrete_map=team_colors,
            hover_data=['Player Name'],
            text='Player Name',
            title="Progressive Carries vs fThird Passes"
        )
        st.plotly_chart(fig_runVSpassing)
