# ⚽ Premier League Match Predictor

A machine learning-powered web application for predicting Premier League football match outcomes with beautiful data visualizations and detailed team statistics.

## 🎯 Features

- **Advanced Prediction Model**: Uses ensemble methods (RandomForest & ExtraTrees) to predict match outcomes
- **Comprehensive Feature Engineering**: 
  - Recent form metrics (5-match rolling windows)
  - Team performance indicators (goals, clean sheets, win rates)
  - Venue-specific form analysis
  - Rest days impact
  - Betting odds integration
  
- **Beautiful Interactive UI** powered by Streamlit:
  - Team statistics buttons with detailed metrics
  - Probability visualization for all outcomes
  - Head-to-head match history
  - Recent performance trends
  - Feature importance analysis

## 📊 Project Structure

```
├── load_data.py              # Load CSV data into SQLite database
├── feature_engineering.py    # Generate features from match data
├── model_train.py            # Train and evaluate ML models
├── app.py                    # Original Gradio interface
├── app_advanced.py           # Advanced Streamlit interface (RECOMMENDED)
├── football_data_2025_26.csv # Input match data
└── premier_league_project.db # SQLite database (auto-created)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pandas numpy scikit-learn joblib sqlite3 streamlit plotly
```

### 2. Prepare Data

```bash
python load_data.py
```
This script:
- Reads `football_data_2025_26.csv`
- Creates SQLite database with teams, matches, and standings
- Generates realistic betting odds

### 3. Engineer Features

```bash
python feature_engineering.py
```
Creates features table with:
- Historical form metrics
- Win rates and clean sheets
- Goal scoring/conceding averages
- Calculated differential features

### 4. Train Model

```bash
python model_train.py
```
Evaluates multiple models and saves the best one:
- RandomForest vs ExtraTrees comparison
- Shows accuracy, F1 score, confusion matrix
- Saves `match_predictor.pkl`

### 5. Launch the Predictor

**Recommended - Advanced UI:**
```bash
streamlit run app_advanced.py
```

Or use the original Gradio interface:
```bash
python app.py
```

## 📈 Feature Engineering Details

### Core Statistics (5-Match Rolling Window)
- **Form**: Average points earned (0-1 scale)
- **Win Rate**: Percentage of wins in recent matches
- **Avg Goals**: Average goals scored
- **Avg Conceded**: Average goals conceded
- **Clean Sheets**: Number of matches without conceding
- **Failed to Score**: Number of matches without scoring

### Venue-Specific Metrics
- Home form for home team
- Away form for away team
- Home win rate for home team
- Away win rate for away team

### Differential Features
- Form difference
- Venue form difference
- Goals difference
- Points difference
- Goal difference
- Rest days difference

### Additional Features
- Days since last match (rest advantage)
- Total points and goal difference
- Matches played
- Betting odds (home, draw, away)

## 🤖 Model Performance

The system trains two models:
- **RandomForest**: 800 trees, max_depth=12, balanced classes
- **ExtraTrees**: 800 trees, max_depth=12

Best model is selected based on accuracy on test set (25% holdout).

### Key Metrics
- Accuracy: Measures correct predictions
- F1 Score (weighted): Handles class imbalance
- Confusion Matrix: Shows prediction distribution

## 💡 Model Insights

### What Makes a Good Prediction?
1. **Recent Form**: Teams in good form tend to win more
2. **Venue Advantage**: Home teams have inherent advantage
3. **Goals Scoring**: Teams scoring more in recent matches continue
4. **Rest**: Teams with more rest days tend to perform better
5. **Betting Odds**: Market odds reflect collective wisdom

### Prediction Interpretation
- **Probability > 50%**: Strong prediction for that outcome
- **Probabilities Close**: Uncertain outcome, more competitive
- **Odds**: Market assessment of match outcome

## ⚠️ Important Notes

1. **Data Quality**: Predictions depend on accurate historical data
2. **Sample Size**: First few matches of season have limited historical data
3. **Injuries/Suspensions**: Not currently factored in
4. **Recent Changes**: Recent team composition changes not captured
5. **Betting**: For entertainment only - not financial advice

## 🔄 Database Schema

### Teams Table
```sql
CREATE TABLE teams (
    team_id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);
```

### Matches Table
```sql
CREATE TABLE matches (
    match_id INTEGER PRIMARY KEY,
    date DATE,
    matchweek INTEGER,
    home_team_id INTEGER,
    away_team_id INTEGER,
    home_goals INTEGER,
    away_goals INTEGER,
    result TEXT,
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id)
);
```

### Match Features Table
```sql
CREATE TABLE match_features (
    match_id INTEGER PRIMARY KEY,
    home_form REAL,
    away_form REAL,
    ...
);
```

### Odds Table
```sql
CREATE TABLE odds (
    odds_id INTEGER PRIMARY KEY,
    match_id INTEGER UNIQUE,
    odds_home REAL,
    odds_draw REAL,
    odds_away REAL,
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);
```

## 🛠️ Troubleshooting

### "Model not found" Error
- Ensure `model_train.py` has been run successfully
- Check `match_predictor.pkl` exists in the project directory

### "Database not found" Error
- Run `load_data.py` first to create the database
- Ensure `football_data_2025_26.csv` is in the project directory

### "No teams found" Error
- CSV might be empty or have wrong column names
- Check columns: Round, Date, HomeTeam, AwayTeam, FTHG, FTAG, FTR

### Predictions seem off
- Limited training data for early season matches
- Model trained on historical patterns - anomalies may not be predicted
- Consider team news, injuries, transfers

## 📚 Technologies Used

- **pandas**: Data manipulation and analysis
- **scikit-learn**: Machine learning models
- **sqlite3**: Local database
- **streamlit**: Web interface
- **plotly**: Interactive visualizations
- **joblib**: Model serialization

## 🎨 UI Features

- 🏠 **Team Selection**: Dropdown menus for home and away teams
- 📊 **Prediction Dashboard**: Clear probability display with odds
- 📈 **Statistics Tabs**: 
  - Individual team stats with recent matches
  - Head-to-head history
- 🎯 **Feature Analysis**: Bar chart showing important features
- ♿ **Responsive Design**: Works on desktop and mobile

## 🔮 Future Enhancements

- [ ] Add player injury/suspension data
- [ ] Include historical head-to-head records
- [ ] Implement live odds integration
- [ ] Add team transfer analysis
- [ ] Real-time updates
- [ ] Betting strategy recommendations
- [ ] Player performance metrics
- [ ] Manager tactics analysis

## 📧 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Ensure database is properly initialized
4. Check data format in CSV

---

**Made with ❤️ for football fans and ML enthusiasts**
