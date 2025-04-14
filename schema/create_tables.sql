CREATE TABLE pokemon_catch_rate (
    id SERIAL PRIMARY KEY,
    catch_rate INT UNIQUE
);

CREATE TABLE pokemon_happiness (
    id SERIAL PRIMARY KEY,
    base_happiness INT UNIQUE
);

CREATE TABLE pokemon_experience_growth (
    id SERIAL PRIMARY KEY,
    description TEXT UNIQUE,
    growth_total INT
);

CREATE TABLE pokemon_gender_ratio (
    id SERIAL PRIMARY KEY,
    label TEXT UNIQUE,         -- e.g., '87.5 / 12.5'
    male_percent FLOAT,
    female_percent FLOAT
);

CREATE TABLE pokemon_egg_groups (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE pokemon_ability (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    description TEXT
);

CREATE TABLE pokemon_types (
    id SERIAL PRIMARY KEY,
    type TEXT UNIQUE
);

CREATE TABLE pokemon_games (
    id SERIAL PRIMARY KEY,
    game_name TEXT UNIQUE,
    game_release_year INT,
    details TEXT,
    release_years_by_system TEXT
);



