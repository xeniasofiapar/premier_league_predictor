import sqlite3
import pandas as pd

# Load CSV
df = pd.read_csv("football_data_2025_26.csv")

# Rename columns to match DB schema
df = df.rename(columns={
    "Round": "matchweek",    
    "Date": "date",
    "HomeTeam": "home_team",
    "AwayTeam": "away_team",
    "FTHG": "home_goals",
    "FTAG": "away_goals",
    "FTR": "result",
})

# Fix date format (removes time and keeps only YYYY-MM-DD)
df["date"] = pd.to_datetime(df["date"], dayfirst=True).dt.date

# Remove rows without goals (future fixtures)
df_matches = df.dropna(subset=["home_goals", "away_goals", "result"])

# Connect to SQLite
conn = sqlite3.connect("premier_league_project.db")
cur = conn.cursor()

# Insert teams
teams = set(df_matches["home_team"]).union(set(df_matches["away_team"]))

for team in teams:
    cur.execute("INSERT OR IGNORE INTO teams (name) VALUES (?)", (team,))

conn.commit()

# Create odds table
cur.execute("""
    CREATE TABLE IF NOT EXISTS odds (
        odds_id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER UNIQUE,
        odds_home REAL,
        odds_draw REAL,
        odds_away REAL,
        FOREIGN KEY (match_id) REFERENCES matches(match_id)
    )
""")
conn.commit()

# Insert matches
for _, row in df_matches.iterrows():
    cur.execute("""
    INSERT OR IGNORE INTO matches (date, matchweek, home_team_id, away_team_id,
        home_goals, away_goals, result
    )
    VALUES (
        ?, ?, 
        (SELECT team_id FROM teams WHERE name = ?),
        (SELECT team_id FROM teams WHERE name = ?),
        ?, ?, ?
    )
""", (
    row["date"].strftime("%Y-%m-%d"),
    int(row["matchweek"]),
    row["home_team"],
    row["away_team"],
    int(row["home_goals"]),
    int(row["away_goals"]),
    row["result"]
))

# Compute match features (league table stats)
# Initialize dictionary for all teams

stats = {
    team: {
        "played": 0,
        "won": 0,
        "drawn": 0,
        "lost": 0,
        "goals_for": 0,
        "goals_against": 0
    }
    for team in teams
}

# Process each match
for _, row in df_matches.iterrows():
    home = row["home_team"]
    away = row["away_team"]
    hg = int(row["home_goals"])
    ag = int(row["away_goals"])
    result = row["result"]

    # Played
    stats[home]["played"] += 1
    stats[away]["played"] += 1

    # Goals
    stats[home]["goals_for"] += hg
    stats[home]["goals_against"] += ag
    stats[away]["goals_for"] += ag
    stats[away]["goals_against"] += hg

    # Results
    if result == "H":
        stats[home]["won"] += 1
        stats[away]["lost"] += 1
    elif result == "A":
        stats[away]["won"] += 1
        stats[home]["lost"] += 1
    else:
        stats[home]["drawn"] += 1
        stats[away]["drawn"] += 1

# Insert into standings

for team, s in stats.items():
    goal_diff = s["goals_for"] - s["goals_against"]
    points = s["won"] * 3 + s["drawn"] * 1

    cur.execute("""
        INSERT OR REPLACE INTO standings (
            team_id, played, won, drawn, lost,
            goals_for, goals_against, goal_difference, points
        )
        VALUES (
            (SELECT team_id FROM teams WHERE name = ?),
            ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, (
        team,
        s["played"], s["won"], s["drawn"], s["lost"],
        s["goals_for"], s["goals_against"], goal_diff, points
    ))

conn.commit()

# Insert betting odds (sample data based on result)
import random
random.seed(42)

for _, row in df_matches.iterrows():
    match_id_val = None
    cur.execute(
        "SELECT match_id FROM matches WHERE date = ? AND home_team_id = (SELECT team_id FROM teams WHERE name = ?) AND away_team_id = (SELECT team_id FROM teams WHERE name = ?)",
        (row["date"].strftime("%Y-%m-%d"), row["home_team"], row["away_team"])
    )
    result = cur.fetchone()
    if result:
        match_id_val = result[0]
        
        # Generate realistic odds based on result
        hg = int(row["home_goals"])
        ag = int(row["away_goals"])
        
        if hg > ag:  # Home win
            odds_home = round(random.uniform(1.5, 2.5), 2)
            odds_away = round(random.uniform(2.5, 4.5), 2)
            odds_draw = round(random.uniform(2.8, 3.8), 2)
        elif ag > hg:  # Away win
            odds_home = round(random.uniform(2.5, 4.5), 2)
            odds_away = round(random.uniform(1.5, 2.5), 2)
            odds_draw = round(random.uniform(2.8, 3.8), 2)
        else:  # Draw
            odds_home = round(random.uniform(2.2, 3.2), 2)
            odds_away = round(random.uniform(2.2, 3.2), 2)
            odds_draw = round(random.uniform(1.8, 2.5), 2)
        
        cur.execute(
            "INSERT OR REPLACE INTO odds (match_id, odds_home, odds_draw, odds_away) VALUES (?, ?, ?, ?)",
            (match_id_val, odds_home, odds_draw, odds_away)
        )

conn.commit()
print("Database successfully populated!")