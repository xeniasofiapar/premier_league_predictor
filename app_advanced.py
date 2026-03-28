import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

N_RECENT = 5

# Load model
try:
    bundle = joblib.load("match_predictor.pkl")
    model = bundle["model"]
    feature_cols = bundle["feature_cols"]
except:
    st.error("Model not found. Please train the model first using model_train.py")
    st.stop()

# Page config
st.set_page_config(
    page_title="🏆 Premier League Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with vibrant colors
st.markdown("""
    <style>
    /* Main background */
    .main {
        padding: 20px;
        background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
    }
    
    /* Page background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #16213e 0%, #0f3460 100%);
    }
    
    /* Metric cards with gradient backgrounds */
    .stMetric {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0, 212, 255, 0.2);
        border: 2px solid rgba(0, 212, 255, 0.3);
    }
    
    /* Team cards - distinctive colors */
    .team-card {
        background: linear-gradient(135deg, #ff006e 0%, #d62828 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(255, 0, 110, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.2);
        font-weight: bold;
        font-size: 20px;
    }
    
    /* Prediction box */
    .prediction-box {
        background: linear-gradient(135deg, #1abc9c 0%, #16a085 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 8px solid #00d4ff;
        box-shadow: 0 8px 16px rgba(26, 188, 156, 0.3);
        color: white;
    }
    
    /* Section headers */
    .stat-header {
        font-size: 28px;
        font-weight: bold;
        margin: 25px 0;
        background: linear-gradient(90deg, #00d4ff 0%, #ff006e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Tab styling */
    .stTabs [role="tablist"] {
        background-color: rgba(15, 15, 30, 0.8);
        border-bottom: 3px solid #00d4ff;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #00d4ff, #ff006e);
        color: white;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #ff006e 100%);
        color: white;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0, 212, 255, 0.4);
    }
    
    /* Selectbox styling */
    .stSelectbox {
        background-color: rgba(30, 40, 60, 0.9);
        color: white;
    }
    
    /* Text color */
    .stMarkdown, .stText {
        color: #e0e0e0;
    }
    
    /* Divider line */
    hr {
        border-color: #00d4ff;
        opacity: 0.3;
    }
    
    /* Card-like containers */
    .stInfo, .stSuccess, .stWarning, .stError {
        border-radius: 10px;
        border-left: 5px solid #00d4ff;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def get_teams():
    conn = sqlite3.connect("premier_league_project.db")
    teams = pd.read_sql_query(
        "SELECT name FROM teams ORDER BY name", conn
    )["name"].tolist()
    conn.close()
    return teams

@st.cache_data
def load_played_matches():
    conn = sqlite3.connect("premier_league_project.db")
    query = """
    SELECT
        m.match_id,
        m.date,
        t1.name AS home_team,
        t2.name AS away_team,
        m.home_goals,
        m.away_goals,
        m.result
    FROM matches m
    JOIN teams t1 ON m.home_team_id = t1.team_id
    JOIN teams t2 ON m.away_team_id = t2.team_id
    WHERE m.result IN ('H', 'D', 'A')
    ORDER BY m.date, m.match_id;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values(["date", "match_id"]).reset_index(drop=True)

def summarize_team(matches, team, venue=None, n=None):
    team_matches = matches[
        (matches["home_team"] == team) | (matches["away_team"] == team)
    ].copy()

    if venue == "home":
        team_matches = team_matches[team_matches["home_team"] == team].copy()
    elif venue == "away":
        team_matches = team_matches[team_matches["away_team"] == team].copy()

    team_matches = team_matches.sort_values(["date", "match_id"])

    recent_points = []
    recent_gf = []
    recent_ga = []
    clean_sheets = []
    failed_to_score = []
    total_points = 0
    gf_total = 0
    ga_total = 0

    for _, row in team_matches.iterrows():
        if row["home_team"] == team:
            gf = int(row["home_goals"])
            ga = int(row["away_goals"])
        else:
            gf = int(row["away_goals"])
            ga = int(row["home_goals"])

        if gf > ga:
            pts = 3
        elif gf == ga:
            pts = 1
        else:
            pts = 0

        total_points += pts
        gf_total += gf
        ga_total += ga

        recent_points.append(pts)
        recent_gf.append(gf)
        recent_ga.append(ga)
        clean_sheets.append(1 if ga == 0 else 0)
        failed_to_score.append(1 if gf == 0 else 0)

    # Use all matches if n is None, otherwise use last n matches
    if n is None:
        vals_for_form = recent_points
        vals_for_goals = recent_gf
        vals_for_conceded = recent_ga
        form_denominator = len(recent_points) * 3 if recent_points else 1
        clean_sheets_recent = clean_sheets[-N_RECENT:]
        failed_score_recent = failed_to_score[-N_RECENT:]
        recent_matches_list = team_matches[-N_RECENT:]
    else:
        vals_for_form = recent_points[-n:]
        vals_for_goals = recent_gf[-n:]
        vals_for_conceded = recent_ga[-n:]
        form_denominator = n * 3
        clean_sheets_recent = clean_sheets[-n:]
        failed_score_recent = failed_to_score[-n:]
        recent_matches_list = team_matches[-n:]
    
    win_rate = sum(1 for v in vals_for_form if v == 3) / len(vals_for_form) if vals_for_form else 0

    return {
        "played": len(team_matches),
        "points": total_points,
        "gd": gf_total - ga_total,
        "form": sum(vals_for_form) / form_denominator if vals_for_form else 0.0,
        "win_rate": win_rate,
        "avg_goals": sum(vals_for_goals) / len(vals_for_goals) if vals_for_goals else 0.0,
        "avg_conceded": sum(vals_for_conceded) / len(vals_for_conceded) if vals_for_conceded else 0.0,
        "clean_sheets_5": sum(clean_sheets_recent) if clean_sheets_recent else 0,
        "failed_to_score_5": sum(failed_score_recent) if failed_score_recent else 0,
        "recent_matches": recent_matches_list.sort_values(["date", "match_id"], ascending=False)
    }

def get_last_play_date(matches, team):
    tm = matches[(matches["home_team"] == team) | (matches["away_team"] == team)].copy()
    if tm.empty:
        return None
    return tm.sort_values(["date", "match_id"]).iloc[-1]["date"]

def get_head_to_head(matches, home_team, away_team):
    h2h = matches[
        ((matches["home_team"] == home_team) & (matches["away_team"] == away_team)) |
        ((matches["home_team"] == away_team) & (matches["away_team"] == home_team))
    ].sort_values("date", ascending=False).head(5)
    return h2h

def get_latest_odds_for_teams(home_team, away_team):
    conn = sqlite3.connect("premier_league_project.db")
    query = """
    SELECT o.odds_home, o.odds_draw, o.odds_away
    FROM odds o
    JOIN matches m ON o.match_id = m.match_id
    JOIN teams th ON m.home_team_id = th.team_id
    JOIN teams ta ON m.away_team_id = ta.team_id
    WHERE th.name = ? AND ta.name = ?
    ORDER BY m.date DESC, m.match_id DESC
    LIMIT 1;
    """
    row = pd.read_sql_query(query, conn, params=[home_team, away_team])
    conn.close()

    if row.empty:
        return {"odds_home": 2.5, "odds_draw": 3.2, "odds_away": 2.8}

    return {
        "odds_home": float(row.iloc[0]["odds_home"]) if pd.notna(row.iloc[0]["odds_home"]) else 2.5,
        "odds_draw": float(row.iloc[0]["odds_draw"]) if pd.notna(row.iloc[0]["odds_draw"]) else 3.2,
        "odds_away": float(row.iloc[0]["odds_away"]) if pd.notna(row.iloc[0]["odds_away"]) else 2.8,
    }

# Title and header
st.markdown("""
<div style="text-align: center; margin-bottom: 30px; padding: 30px; background: linear-gradient(135deg, #ff006e 0%, #00d4ff 100%); border-radius: 15px; box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);">
    <h1 style="color: white; font-size: 50px; margin: 0;">⚽ Premier League Predictor</h1>
    <p style="color: #e0e0e0; font-size: 16px; margin-top: 10px;">AI-Powered Match Predictions with Advanced Analytics</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Team selection
st.sidebar.header("🎯 Select Match")
teams = get_teams()

col1, col2 = st.sidebar.columns(2)
with col1:
    home_team = st.selectbox("🏠 Home Team", teams, key="home")
with col2:
    away_team = st.selectbox("✈️ Away Team", teams, key="away")

st.sidebar.markdown("---")

# Load match data
matches = load_played_matches()

# Check if teams are different
if home_team == away_team:
    st.error("❌ Please select different teams!")
    st.stop()

# Get team data
home_all = summarize_team(matches, home_team, venue=None)
away_all = summarize_team(matches, away_team, venue=None)
home_home = summarize_team(matches, home_team, venue="home")
away_away = summarize_team(matches, away_team, venue="away")

# Get rest days
latest_date = matches["date"].max()
home_last = get_last_play_date(matches, home_team)
away_last = get_last_play_date(matches, away_team)
home_days_rest = int((latest_date - home_last).days) if home_last is not None else 7
away_days_rest = int((latest_date - away_last).days) if away_last is not None else 7

# Get odds
odds = get_latest_odds_for_teams(home_team, away_team)

# Prepare prediction features
X = pd.DataFrame([{
    "home_form": home_all["form"],
    "away_form": away_all["form"],
    "home_home_form": home_home["form"],
    "away_away_form": away_away["form"],
    "home_avg_goals": home_all["avg_goals"],
    "away_avg_goals": away_all["avg_goals"],
    "home_avg_conceded": home_all["avg_conceded"],
    "away_avg_conceded": away_all["avg_conceded"],
    "home_clean_sheets_5": home_all["clean_sheets_5"],
    "away_clean_sheets_5": away_all["clean_sheets_5"],
    "home_failed_to_score_5": home_all["failed_to_score_5"],
    "away_failed_to_score_5": away_all["failed_to_score_5"],
    "home_points": home_all["points"],
    "away_points": away_all["points"],
    "home_gd": home_all["gd"],
    "away_gd": away_all["gd"],
    "home_played": home_all["played"],
    "away_played": away_all["played"],
    "home_days_rest": home_days_rest,
    "away_days_rest": away_days_rest,
    "home_win_rate": home_all["win_rate"],
    "away_win_rate": away_all["win_rate"],
    "home_home_win_rate": home_home["win_rate"],
    "away_away_win_rate": away_away["win_rate"],
    "form_diff": home_all["form"] - away_all["form"],
    "venue_form_diff": home_home["form"] - away_away["form"],
    "avg_goals_diff": home_all["avg_goals"] - away_all["avg_goals"],
    "avg_conceded_diff": home_all["avg_conceded"] - away_all["avg_conceded"],
    "points_diff": home_all["points"] - away_all["points"],
    "gd_diff": home_all["gd"] - away_all["gd"],
    "played_diff": home_all["played"] - away_all["played"],
    "rest_diff": home_days_rest - away_days_rest,
    "clean_sheet_diff": home_all["clean_sheets_5"] - away_all["clean_sheets_5"],
    "failed_score_diff": home_all["failed_to_score_5"] - away_all["failed_to_score_5"],
    "win_rate_diff": home_all["win_rate"] - away_all["win_rate"],
    "venue_win_rate_diff": home_home["win_rate"] - away_away["win_rate"],
    "odds_home": odds["odds_home"],
    "odds_draw": odds["odds_draw"],
    "odds_away": odds["odds_away"],
}])

# Add missing columns
for col in feature_cols:
    if col not in X.columns:
        X[col] = 0.0

X = X[feature_cols]

# Make prediction
proba = model.predict_proba(X)[0]
classes = model.classes_.tolist()

prob_home = float(proba[classes.index("H")])
prob_draw = float(proba[classes.index("D")])
prob_away = float(proba[classes.index("A")])

pred = model.predict(X)[0]
pred_text = {"H": "🏠 Home Win", "D": "🤝 Draw", "A": "✈️ Away Win"}[pred]

# Main prediction box
st.markdown('<div class="stat-header">📊 Match Prediction</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f'<div class="team-card"><h3>{home_team}</h3></div>', unsafe_allow_html=True)
    
with col2:
    st.markdown(f"""
    <div class="prediction-box">
    <h2 style="text-align: center; color: #667eea;">{pred_text}</h2>
    <p style="text-align: center; font-size: 18px;">vs</p>
    </div>
    """, unsafe_allow_html=True)
    
with col3:
    st.markdown(f'<div class="team-card"><h3>{away_team}</h3></div>', unsafe_allow_html=True)

# Probability display
st.markdown('<div class="stat-header">🎯 Win Probabilities</div>', unsafe_allow_html=True)
prob_col1, prob_col2, prob_col3 = st.columns(3)

with prob_col1:
    st.metric(f"🏠 {home_team} Win", f"{prob_home*100:.1f}%", 
              delta=f"Odds: {odds['odds_home']:.2f}x")
    
with prob_col2:
    st.metric("🤝 Draw", f"{prob_draw*100:.1f}%", 
              delta=f"Odds: {odds['odds_draw']:.2f}x")
    
with prob_col3:
    st.metric(f"✈️ {away_team} Win", f"{prob_away*100:.1f}%", 
              delta=f"Odds: {odds['odds_away']:.2f}x")

# Visualization
prob_data = pd.DataFrame({
    'Outcome': ['Home Win', 'Draw', 'Away Win'],
    'Probability': [prob_home*100, prob_draw*100, prob_away*100]
})

fig = go.Figure(data=[
    go.Bar(x=prob_data['Outcome'], y=prob_data['Probability'], 
           marker_color=['#ff006e', '#1abc9c', '#00d4ff'],
           text=prob_data['Probability'].round(1).astype(str) + '%',
           textposition='auto',
           textfont=dict(color='white', size=14, family='Arial Black'))
])
fig.update_layout(
    title="<b>Prediction Confidence</b>",
    xaxis_title="Match Outcome",
    yaxis_title="Probability (%)",
    height=350,
    showlegend=False,
    plot_bgcolor='rgba(15, 15, 30, 0.9)',
    paper_bgcolor='rgba(15, 15, 30, 0.9)',
    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0, 212, 255, 0.1)', color='#e0e0e0'),
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0, 212, 255, 0.1)', color='#e0e0e0'),
    title_font=dict(size=20, color='#00d4ff'),
    font=dict(family='Arial', size=12, color='#e0e0e0')
)
st.plotly_chart(fig, use_container_width=True)

# Team statistics tabs
st.markdown("---")
st.markdown('<div class="stat-header">📈 Team Statistics</div>', unsafe_allow_html=True)

tabs = st.tabs([
    f"🏠 {home_team} Stats",
    f"✈️ {away_team} Stats",
    "⚔️ Head to Head"
])

with tabs[0]:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Matches Played", home_all["played"])
    with col2:
        st.metric("⭐ Form (5 matches)", f"{home_all['form']:.3f}")
    with col3:
        st.metric("🎯 Win Rate (5)", f"{home_all['win_rate']*100:.0f}%")
    with col4:
        st.metric("🏠 Home Form", f"{home_home['form']:.3f}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⚽ Avg Goals Scored", f"{home_all['avg_goals']:.2f}")
    with col2:
        st.metric("🛡️ Avg Goals Conceded", f"{home_all['avg_conceded']:.2f}")
    with col3:
        st.metric("🚫 Clean Sheets (5)", home_all["clean_sheets_5"])
    with col4:
        st.metric("😴 Days Rest", home_days_rest)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📈 Points Total", home_all["points"])
    with col2:
        st.metric("🆚 Goal Difference", home_all["gd"])
    
    # Recent matches
    st.markdown("**Recent Matches:**")
    recent = home_all["recent_matches"].copy()
    recent_display = []
    for _, row in recent.iterrows():
        if row["home_team"] == home_team:
            result = f"{row['home_goals']} - {row['away_goals']} vs {row['away_team']}"
        else:
            result = f"{row['away_goals']} - {row['home_goals']} vs {row['home_team']}"
        recent_display.append({"Date": row["date"].strftime("%Y-%m-%d"), "Result": result})
    
    if recent_display:
        st.dataframe(pd.DataFrame(recent_display), use_container_width=True, hide_index=True)

with tabs[1]:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Matches Played", away_all["played"])
    with col2:
        st.metric("⭐ Form (5 matches)", f"{away_all['form']:.3f}")
    with col3:
        st.metric("🎯 Win Rate (5)", f"{away_all['win_rate']*100:.0f}%")
    with col4:
        st.metric("✈️ Away Form", f"{away_away['form']:.3f}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⚽ Avg Goals Scored", f"{away_all['avg_goals']:.2f}")
    with col2:
        st.metric("🛡️ Avg Goals Conceded", f"{away_all['avg_conceded']:.2f}")
    with col3:
        st.metric("🚫 Clean Sheets (5)", away_all["clean_sheets_5"])
    with col4:
        st.metric("😴 Days Rest", away_days_rest)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📈 Points Total", away_all["points"])
    with col2:
        st.metric("🆚 Goal Difference", away_all["gd"])
    
    # Recent matches
    st.markdown("**Recent Matches:**")
    recent = away_all["recent_matches"].copy()
    recent_display = []
    for _, row in recent.iterrows():
        if row["home_team"] == away_team:
            result = f"{row['home_goals']} - {row['away_goals']} vs {row['away_team']}"
        else:
            result = f"{row['away_goals']} - {row['home_goals']} vs {row['home_team']}"
        recent_display.append({"Date": row["date"].strftime("%Y-%m-%d"), "Result": result})
    
    if recent_display:
        st.dataframe(pd.DataFrame(recent_display), use_container_width=True, hide_index=True)

with tabs[2]:
    h2h = get_head_to_head(matches, home_team, away_team)
    
    if not h2h.empty:
        h2h_display = []
        for _, row in h2h.iterrows():
            h2h_display.append({
                "Date": row["date"].strftime("%Y-%m-%d"),
                "Home": row["home_team"],
                "Score": f"{row['home_goals']} - {row['away_goals']}",
                "Away": row["away_team"],
                "Result": row["result"]
            })
        
        st.dataframe(pd.DataFrame(h2h_display), use_container_width=True, hide_index=True)
    else:
        st.info("No head-to-head matches found.")

# Feature importance section
st.markdown("---")
st.markdown('<div class="stat-header">🔍 Key Features Used</div>', unsafe_allow_html=True)

feature_importance_df = pd.DataFrame({
    'Feature': feature_cols,
    'Value': X.iloc[0][feature_cols].values
})

fig = px.bar(feature_importance_df.sort_values('Value', key=abs, ascending=True).tail(15), 
             x='Value', y='Feature', orientation='h',
             title="<b>Top 15 Features</b>",
             color='Value',
             color_continuous_scale=['#00d4ff', '#ff006e'])

fig.update_layout(
    height=500,
    plot_bgcolor='rgba(15, 15, 30, 0.9)',
    paper_bgcolor='rgba(15, 15, 30, 0.9)',
    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0, 212, 255, 0.1)', color='#e0e0e0'),
    yaxis=dict(color='#e0e0e0'),
    title_font=dict(size=20, color='#00d4ff'),
    font=dict(family='Arial', size=12, color='#e0e0e0'),
    coloraxis_colorbar=dict(thickness=15, len=0.7)
)
st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; background: linear-gradient(90deg, rgba(0, 212, 255, 0.1), rgba(255, 0, 110, 0.1)); border-radius: 10px; border: 2px solid rgba(0, 212, 255, 0.2);">
    <p style="color: #e0e0e0; font-size: 14px;"><b>⚠️ Disclaimer:</b> This predictor is for entertainment purposes only. Predictions are based on historical data and machine learning models, which may not always be accurate. Do not bet based solely on these predictions.</p>
</div>
""", unsafe_allow_html=True)
