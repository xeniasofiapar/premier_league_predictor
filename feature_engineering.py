import sqlite3
import pandas as pd
import numpy as np

N_RECENT = 5

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

matches = pd.read_sql_query(query, conn)
matches["date"] = pd.to_datetime(matches["date"])
matches = matches.sort_values(["date", "match_id"]).reset_index(drop=True)

teams = sorted(set(matches["home_team"]).union(set(matches["away_team"])))

def new_team_state():
    return {
        "played": 0,
        "points": 0,
        "gf": 0,
        "ga": 0,
        "gd": 0,
        "last_date": None,
        "recent_points_all": [],
        "recent_goals_for_all": [],
        "recent_goals_against_all": [],
        "recent_clean_sheets_all": [],
        "recent_failed_score_all": [],
        "recent_points_home": [],
        "recent_goals_for_home": [],
        "recent_goals_against_home": [],
        "recent_points_away": [],
        "recent_goals_for_away": [],
        "recent_goals_against_away": [],
    }

state = {team: new_team_state() for team in teams}
rows = []

def avg_last(lst, n=None):
    # If n is None, use all history; otherwise use last n matches
    vals = lst if n is None else lst[-n:]
    return float(sum(vals) / len(vals)) if vals else 0.0

def sum_last(lst, n=None):
    # If n is None, use all history; otherwise use last n matches
    vals = lst if n is None else lst[-n:]
    return int(sum(vals)) if vals else 0

def form_last(lst, n=None):
    # If n is None, use all history; otherwise use last n matches
    vals = lst if n is None else lst[-n:]
    max_points = len(vals) * 3 if n is None else n * 3
    return float(sum(vals) / max_points) if vals else 0.0

def win_rate_last(lst, n=None):
    # If n is None, use all history; otherwise use last n matches
    vals = lst if n is None else lst[-n:]
    if not vals:
        return 0.0
    wins = sum(1 for v in vals if v == 3)
    return float(wins / len(vals))

def days_since(last_date, current_date):
    if last_date is None:
        return 7
    return int((current_date - last_date).days)

for _, m in matches.iterrows():
    home = m["home_team"]
    away = m["away_team"]
    match_date = m["date"]

    hs = state[home]
    aws = state[away]

    home_form = form_last(hs["recent_points_all"], n=None)  # All-time form
    away_form = form_last(aws["recent_points_all"], n=None)  # All-time form

    home_home_form = form_last(hs["recent_points_home"], n=None)  # All-time home form
    away_away_form = form_last(aws["recent_points_away"], n=None)  # All-time away form

    home_avg_goals = avg_last(hs["recent_goals_for_all"], n=None)  # All-time average
    away_avg_goals = avg_last(aws["recent_goals_for_all"], n=None)  # All-time average

    home_avg_conceded = avg_last(hs["recent_goals_against_all"], n=None)  # All-time average
    away_avg_conceded = avg_last(aws["recent_goals_against_all"], n=None)  # All-time average

    home_clean_sheets_5 = sum_last(hs["recent_clean_sheets_all"], n=N_RECENT)  # Keep last 5
    away_clean_sheets_5 = sum_last(aws["recent_clean_sheets_all"], n=N_RECENT)  # Keep last 5

    home_failed_to_score_5 = sum_last(hs["recent_failed_score_all"], n=N_RECENT)  # Keep last 5
    away_failed_to_score_5 = sum_last(aws["recent_failed_score_all"], n=N_RECENT)  # Keep last 5

    home_days_rest = days_since(hs["last_date"], match_date)
    away_days_rest = days_since(aws["last_date"], match_date)

    home_win_rate = win_rate_last(hs["recent_points_all"], n=None)  # All-time win rate
    away_win_rate = win_rate_last(aws["recent_points_all"], n=None)  # All-time win rate
    home_home_win_rate = win_rate_last(hs["recent_points_home"], n=None)  # All-time home win rate
    away_away_win_rate = win_rate_last(aws["recent_points_away"], n=None)  # All-time away win rate

    row = {
        "match_id": int(m["match_id"]),
        "match_date": match_date.strftime("%Y-%m-%d"),
        "home_team": home,
        "away_team": away,
        "result": m["result"],

        "home_form": home_form,
        "away_form": away_form,
        "home_home_form": home_home_form,
        "away_away_form": away_away_form,

        "home_avg_goals": home_avg_goals,
        "away_avg_goals": away_avg_goals,
        "home_avg_conceded": home_avg_conceded,
        "away_avg_conceded": away_avg_conceded,

        "home_clean_sheets_5": home_clean_sheets_5,
        "away_clean_sheets_5": away_clean_sheets_5,
        "home_failed_to_score_5": home_failed_to_score_5,
        "away_failed_to_score_5": away_failed_to_score_5,

        "home_points": hs["points"],
        "away_points": aws["points"],
        "home_gd": hs["gd"],
        "away_gd": aws["gd"],
        "home_played": hs["played"],
        "away_played": aws["played"],

        "home_days_rest": home_days_rest,
        "away_days_rest": away_days_rest,
        
        "home_win_rate": home_win_rate,
        "away_win_rate": away_win_rate,
        "home_home_win_rate": home_home_win_rate,
        "away_away_win_rate": away_away_win_rate,
    }

    row["form_diff"] = row["home_form"] - row["away_form"]
    row["venue_form_diff"] = row["home_home_form"] - row["away_away_form"]
    row["avg_goals_diff"] = row["home_avg_goals"] - row["away_avg_goals"]
    row["avg_conceded_diff"] = row["home_avg_conceded"] - row["away_avg_conceded"]
    row["points_diff"] = row["home_points"] - row["away_points"]
    row["gd_diff"] = row["home_gd"] - row["away_gd"]
    row["played_diff"] = row["home_played"] - row["away_played"]
    row["rest_diff"] = row["home_days_rest"] - row["away_days_rest"]
    row["clean_sheet_diff"] = row["home_clean_sheets_5"] - row["away_clean_sheets_5"]
    row["failed_score_diff"] = row["home_failed_to_score_5"] - row["away_failed_to_score_5"]
    row["win_rate_diff"] = row["home_win_rate"] - row["away_win_rate"]
    row["venue_win_rate_diff"] = row["home_home_win_rate"] - row["away_away_win_rate"]

    rows.append(row)

    hg = int(m["home_goals"])
    ag = int(m["away_goals"])

    if hg > ag:
        home_pts, away_pts = 3, 0
    elif hg < ag:
        home_pts, away_pts = 0, 3
    else:
        home_pts, away_pts = 1, 1

    hs["played"] += 1
    aws["played"] += 1

    hs["points"] += home_pts
    aws["points"] += away_pts

    hs["gf"] += hg
    hs["ga"] += ag
    aws["gf"] += ag
    aws["ga"] += hg

    hs["gd"] = hs["gf"] - hs["ga"]
    aws["gd"] = aws["gf"] - aws["ga"]

    hs["last_date"] = match_date
    aws["last_date"] = match_date

    hs["recent_points_all"].append(home_pts)
    aws["recent_points_all"].append(away_pts)

    hs["recent_goals_for_all"].append(hg)
    aws["recent_goals_for_all"].append(ag)

    hs["recent_goals_against_all"].append(ag)
    aws["recent_goals_against_all"].append(hg)

    hs["recent_clean_sheets_all"].append(1 if ag == 0 else 0)
    aws["recent_clean_sheets_all"].append(1 if hg == 0 else 0)

    hs["recent_failed_score_all"].append(1 if hg == 0 else 0)
    aws["recent_failed_score_all"].append(1 if ag == 0 else 0)

    hs["recent_points_home"].append(home_pts)
    hs["recent_goals_for_home"].append(hg)
    hs["recent_goals_against_home"].append(ag)

    aws["recent_points_away"].append(away_pts)
    aws["recent_goals_for_away"].append(ag)
    aws["recent_goals_against_away"].append(hg)

features_df = pd.DataFrame(rows)
features_df.to_sql("match_features", conn, if_exists="replace", index=False)

conn.close()
print("Enhanced feature engineering completed successfully.")
