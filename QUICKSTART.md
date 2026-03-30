# 🚀 Quick Start Guide

## Step-by-Step Setup

### 1️⃣ Install Dependencies
```bash
pip install pandas numpy scikit-learn joblib streamlit plotly
```

### 2️⃣ Prepare Your Data
`football_data_2025_26.csv` in the project folder with columns:
- Round
- Date
- HomeTeam
- AwayTeam
- FTHG (Full Time Home Goals)
- FTAG (Full Time Away Goals)
- FTR (Full Time Result: H/D/A)

### 3️⃣ Initialize Database
```bash
python load_data.py
```
✅ Creates `premier_league_project.db` with:
- Teams table
- Matches table  
- Odds table (with sample realistic odds)

### 4️⃣ Generate Features
```bash
python feature_engineering.py
```
✅ Creates match features table with:
- Form metrics
- Win rates
- Goal statistics
- Rest days
- Differential features

### 5️⃣ Train Model
```bash
python model_train.py
```
✅ Trains RandomForest and ExtraTrees models
✅ Saves best model as `match_predictor.pkl`
📊 Shows accuracy, F1 scores, confusion matrix

### 6️⃣ Launch Predictions! 🎉
```bash
streamlit run app_advanced.py
```

Opens UI at: http://localhost:8501

---

## 📱 Using the App

### Select Teams
1. Use dropdown menus on left sidebar to pick Home and Away teams
2. Predictions update automatically

### View Predictions
- **Main Cards**: Show the predicted outcome (Home Win/Draw/Away Win)
- **Probability Chart**: Visual display of all outcome chances
- **Bar Chart**: Win odds from betting market

### Explore Team Stats
Click on tabs to view:
- **Home Team Stats**: All metrics for home team
- **Away Team Stats**: All metrics for away team  
- **Head to Head**: Recent matches between these teams

### Team Statistics Include:
- ⭐ Form (5-match average)
- 🎯 Win Rate
- ⚽ Average Goals Scored
- 🛡️ Average Goals Conceded
- 🚫 Clean Sheets (last 5)
- 😴 Days Rest

### Interpret Features
- Higher form = better recent performance
- Higher win rate = more victories recently
- More rest usually = advantage
- Goal difference shows attacking/defensive strength

---

## 🔄 Workflow Summary

```
football_data_2025_26.csv
        ↓
   load_data.py
        ↓
premier_league_project.db (matches, teams, odds)
        ↓
   feature_engineering.py
        ↓
match_features table (with all engineered features)
        ↓
   model_train.py
        ↓
match_predictor.pkl (trained model)
        ↓
   app_advanced.py (Streamlit UI)
        ↓
🎉 Predictions!
```

---

## 💡 Tips for Better Predictions

### Factors That Matter Most:
1. **Recent Form** - Last 5 matches show current state
2. **Home Advantage** - Home teams win ~44% vs ~27% for away
3. **Goals Scored** - Teams that score more tend to win
4. **Rest Days** - Fresh teams perform better
5. **Clean Sheets** - Defensive strength correlates with wins

### When to Trust Predictions:
- ✅ Probabilities far from 50% (clear prediction)
- ✅ Teams with lots of match history
- ✅ Mid-season matches (more data available)
- ✅ Similar recent forms = uncertain result

### When to Be Cautious:
- ⚠️ Season start (limited history)
- ⚠️ New teams with few matches
- ⚠️ Close probabilities (50% chance either way)
- ⚠️ Recent major team changes (transfers, injuries)

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Model not found" | Run `python model_train.py` first |
| "Database error" | Run `python load_data.py` first |
| "No teams found" | Check CSV column names match specification |
| "Streamlit not found" | Run `pip install streamlit` |
| Predictions seem random | Need more match history for accuracy |

---

## 📊 Model Details

### What Data Is Used?
- Home team: form, win rate, goals, rest, points
- Away team: same metrics
- Betting odds: market consensus

### How Is It Trained?
- Ensemble of RandomForest and ExtraTrees
- 75% data for training, 25% for testing
- Balanced class weights (handles draw rarity)

### Accuracy Expectations
- ~50-55% on unseen data is typical for football
- Better than random (33.3%) shows prediction power
- Betting models need 52%+ to be profitable

---
