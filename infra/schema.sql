-- Football Analytics Platform — Full Schema
-- Compatible with Neon (Serverless PostgreSQL) and PostgreSQL 15+

-- 1. TEAMS
CREATE TABLE teams (
    id INTEGER PRIMARY KEY, -- API-Football Team ID
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    logo_url VARCHAR(500),
    founded INTEGER,
    venue_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. PLAYERS
CREATE TABLE players (
    id INTEGER PRIMARY KEY, -- API-Football Player ID
    team_id INTEGER REFERENCES teams(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    position VARCHAR(50),
    nationality VARCHAR(100),
    photo_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. FIXTURES
CREATE TABLE fixtures (
    id INTEGER PRIMARY KEY, -- API-Football Fixture ID
    league_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    home_team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
    away_team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
    venue VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    referee VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. RESULTS
CREATE TABLE results (
    fixture_id INTEGER PRIMARY KEY REFERENCES fixtures(id) ON DELETE CASCADE,
    home_goals INTEGER,
    away_goals INTEGER,
    home_xg DECIMAL(5,2),
    away_xg DECIMAL(5,2),
    home_possession INTEGER,
    away_possession INTEGER,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. STANDINGS
CREATE TABLE standings (
    id SERIAL PRIMARY KEY,
    league_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL,
    points INTEGER NOT NULL,
    form VARCHAR(20),
    goals_diff INTEGER,
    played INTEGER,
    won INTEGER,
    draw INTEGER,
    lose INTEGER,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(league_id, season, team_id)
);

-- 6. ODDS
CREATE TABLE odds (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER REFERENCES fixtures(id) ON DELETE CASCADE,
    bookmaker VARCHAR(100) NOT NULL,
    home_win DECIMAL(6,3) NOT NULL,
    draw DECIMAL(6,3) NOT NULL,
    away_win DECIMAL(6,3) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. INJURIES
CREATE TABLE injuries (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
    fixture_id INTEGER REFERENCES fixtures(id) ON DELETE CASCADE,
    team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
    type VARCHAR(255),
    reason VARCHAR(255),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. FEATURES
CREATE TABLE features (
    fixture_id INTEGER PRIMARY KEY REFERENCES fixtures(id) ON DELETE CASCADE,
    home_team_form_score DECIMAL(5,2),
    away_team_form_score DECIMAL(5,2),
    home_win_streak INTEGER,
    away_win_streak INTEGER,
    home_avg_goals_scored DECIMAL(5,2),
    away_avg_goals_scored DECIMAL(5,2),
    home_avg_goals_conceded DECIMAL(5,2),
    away_avg_goals_conceded DECIMAL(5,2),
    implied_home_prob DECIMAL(5,4),
    implied_away_prob DECIMAL(5,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. PREDICTIONS
CREATE TABLE predictions (
    fixture_id INTEGER PRIMARY KEY REFERENCES fixtures(id) ON DELETE CASCADE,
    prob_home_win DECIMAL(5,4) NOT NULL,
    prob_draw DECIMAL(5,4) NOT NULL,
    prob_away_win DECIMAL(5,4) NOT NULL,
    predicted_winner_id INTEGER REFERENCES teams(id) ON DELETE SET NULL,
    model_version VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES
CREATE INDEX idx_fixtures_date ON fixtures(date);
CREATE INDEX idx_odds_fixture_id ON odds(fixture_id);
CREATE INDEX idx_standings_league_season ON standings(league_id, season);
