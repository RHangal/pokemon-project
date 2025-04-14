CREATE TABLE pokemon (
    id SERIAL PRIMARY KEY,
    pokemon_id INT UNIQUE,
    pokedex_number INT,
    pokemon_name TEXT,
    classification TEXT,
    alternate_form_name TEXT,
    pre_evolution_pokemon_id INT,
    evolution_details TEXT,

    -- Foreign keys
    game_id INT REFERENCES pokemon_games(id),
    catch_rate_id INT REFERENCES pokemon_catch_rate(id),
    base_happiness_id INT REFERENCES pokemon_happiness(id),
    experience_growth_id INT REFERENCES pokemon_experience_growth(id),
    gender_ratio_id INT REFERENCES pokemon_gender_ratio(id),

    -- Base stats
    health_stat INT,
    attack_stat INT,
    defense_stat INT,
    special_attack_stat INT,
    special_defense_stat INT,
    speed_stat INT,
    base_stat_total INT,

    -- EV yields
    health_ev INT,
    attack_ev INT,
    defense_ev INT,
    special_attack_ev INT,
    special_defense_ev INT,
    speed_ev INT,
    ev_yield_total INT
);

ALTER TABLE pokemon ADD COLUMN sprite_path TEXT;




