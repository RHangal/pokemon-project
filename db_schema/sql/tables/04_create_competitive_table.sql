DROP TABLE IF EXISTS pokemon_competitive_usage CASCADE
CREATE TABLE pokemon_competitive_usage (
    id SERIAL PRIMARY KEY,
    pokemon_id INT NOT NULL REFERENCES pokemon(id),
    smogon_vgc_usage_2022 FLOAT,
    smogon_vgc_usage_2023 FLOAT,
    smogon_vgc_usage_2024 FLOAT,
    worlds_vgc_usage_2022 FLOAT,
    worlds_vgc_usage_2023 FLOAT,
    worlds_vgc_usage_2024 FLOAT,
    UNIQUE (pokemon_id)
);
