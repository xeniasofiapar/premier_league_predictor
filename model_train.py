import sqlite3
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

conn = sqlite3.connect("premier_league_project.db")

query = """
SELECT
    f.match_id,
    f.match_date,
    f.result,
    f.home_form,
    f.away_form,
    f.home_home_form,
    f.away_away_form,
    f.home_avg_goals,
    f.away_avg_goals,
    f.home_avg_conceded,
    f.away_avg_conceded,
    f.home_clean_sheets_5,
    f.away_clean_sheets_5,
    f.home_failed_to_score_5,
    f.away_failed_to_score_5,
    f.home_points,
    f.away_points,
    f.home_gd,
    f.away_gd,
    f.home_played,
    f.away_played,
    f.home_days_rest,
    f.away_days_rest,
    f.form_diff,
    f.venue_form_diff,
    f.avg_goals_diff,
    f.avg_conceded_diff,
    f.points_diff,
    f.gd_diff,
    f.played_diff,
    f.rest_diff,
    f.clean_sheet_diff,
    f.failed_score_diff,
    o.odds_home,
    o.odds_draw,
    o.odds_away
FROM match_features f
LEFT JOIN odds o
    ON f.match_id = o.match_id
WHERE f.result IN ('H', 'D', 'A')
ORDER BY f.match_date, f.match_id;
"""

df = pd.read_sql_query(query, conn)
conn.close()

df["match_date"] = pd.to_datetime(df["match_date"])
df = df.sort_values(["match_date", "match_id"]).reset_index(drop=True)

odds_cols = ["odds_home", "odds_draw", "odds_away"]
for col in odds_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].median())

feature_cols = [
    "home_form", "away_form",
    "home_home_form", "away_away_form",
    "home_avg_goals", "away_avg_goals",
    "home_avg_conceded", "away_avg_conceded",
    "home_clean_sheets_5", "away_clean_sheets_5",
    "home_failed_to_score_5", "away_failed_to_score_5",
    "home_points", "away_points",
    "home_gd", "away_gd",
    "home_played", "away_played",
    "home_days_rest", "away_days_rest",
    "home_win_rate", "away_win_rate",
    "home_home_win_rate", "away_away_win_rate",
    "form_diff", "venue_form_diff",
    "avg_goals_diff", "avg_conceded_diff",
    "points_diff", "gd_diff", "played_diff",
    "rest_diff", "clean_sheet_diff", "failed_score_diff",
    "win_rate_diff", "venue_win_rate_diff",
    "odds_home", "odds_draw", "odds_away"
]

feature_cols = [c for c in feature_cols if c in df.columns]

split_idx = int(len(df) * 0.75)
train_df = df.iloc[:split_idx].copy()
test_df = df.iloc[split_idx:].copy()

X_train = train_df[feature_cols]
y_train = train_df["result"]
X_test = test_df[feature_cols]
y_test = test_df["result"]

models = {
    "RandomForest": RandomForestClassifier(
        n_estimators=800,
        max_depth=12,
        min_samples_split=8,
        min_samples_leaf=3,
        class_weight="balanced_subsample",
        random_state=42
    ),
    "ExtraTrees": ExtraTreesClassifier(
        n_estimators=800,
        max_depth=12,
        min_samples_split=8,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42
    )
}

best_name = None
best_model = None
best_pred = None
best_acc = -1

for name, model in models.items():
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    acc = accuracy_score(y_test, pred)

    print(f"\n{name}")
    print("Accuracy:", round(acc, 4))
    print("Weighted F1:", round(f1_score(y_test, pred, average="weighted"), 4))
    print(classification_report(y_test, pred))
    print(confusion_matrix(y_test, pred))

    if acc > best_acc:
        best_acc = acc
        best_name = name
        best_model = model
        best_pred = pred

joblib.dump(
    {
        "model": best_model,
        "model_name": best_name,
        "feature_cols": feature_cols
    },
    "match_predictor.pkl"
)

print("\nBest model:", best_name)
print("Best accuracy:", round(best_acc, 4))
print("Saved as match_predictor.pkl")
