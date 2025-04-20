-- Create junction tables
DROP TABLE IF EXISTS pokemon_types_junction CASCADE;
CREATE TABLE pokemon_types_junction (
    id SERIAL PRIMARY KEY,
    pokemon_id INT REFERENCES pokemon(id),
    type_id INT REFERENCES pokemon_types(id),
    slot TEXT CHECK (slot IN ('primary', 'secondary'))
);

DROP TABLE IF EXISTS pokemon_abilities_junction CASCADE;
CREATE TABLE pokemon_abilities_junction (
    id SERIAL PRIMARY KEY,
    pokemon_id INT NOT NULL REFERENCES pokemon(id),
    ability_id INT NOT NULL REFERENCES pokemon_ability(id),
    slot TEXT NOT NULL CHECK (slot IN ('primary', 'secondary', 'hidden', 'event')),
    UNIQUE (pokemon_id, slot)
);

DROP TABLE IF EXISTS pokemon_egg_groups_junction CASCADE;
CREATE TABLE pokemon_egg_groups_junction (
    id SERIAL PRIMARY KEY,
    pokemon_id INT NOT NULL REFERENCES pokemon(id),
    egg_group_id INT NOT NULL REFERENCES pokemon_egg_groups(id),
    slot TEXT NOT NULL CHECK (slot IN ('primary', 'secondary')),
    UNIQUE (pokemon_id, slot)
);
