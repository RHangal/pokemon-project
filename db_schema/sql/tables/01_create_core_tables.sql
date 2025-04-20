-- Drop and recreate core reference tables
DROP TABLE IF EXISTS pokemon_catch_rate CASCADE;
CREATE TABLE pokemon_catch_rate (
    id SERIAL PRIMARY KEY,
    catch_rate INT UNIQUE
);

DROP TABLE IF EXISTS pokemon_happiness CASCADE;
CREATE TABLE pokemon_happiness (
    id SERIAL PRIMARY KEY,
    base_happiness INT UNIQUE
);

DROP TABLE IF EXISTS pokemon_experience_growth CASCADE;
CREATE TABLE pokemon_experience_growth (
    id SERIAL PRIMARY KEY,
    description TEXT UNIQUE,
    growth_total INT
);

DROP TABLE IF EXISTS pokemon_gender_ratio CASCADE;
CREATE TABLE pokemon_gender_ratio (
    id SERIAL PRIMARY KEY,
    label TEXT UNIQUE,          -- e.g., '87.5 / 12.5'
    male_percent FLOAT,
    female_percent FLOAT
);

DROP TABLE IF EXISTS pokemon_egg_groups CASCADE;
CREATE TABLE pokemon_egg_groups (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE
);

DROP TABLE IF EXISTS pokemon_ability CASCADE;
CREATE TABLE pokemon_ability (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    description TEXT
);

DROP TABLE IF EXISTS pokemon_types CASCADE;
CREATE TABLE pokemon_types (
    id SERIAL PRIMARY KEY,
    type TEXT UNIQUE
);

DROP TABLE IF EXISTS pokemon_games CASCADE;
CREATE TABLE pokemon_games (
    id SERIAL PRIMARY KEY,
    game_name TEXT UNIQUE,
    game_release_year INT,
    details TEXT,
    release_years_by_system TEXT
);
