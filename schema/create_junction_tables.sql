CREATE TABLE pokemon_types_junction (
    id SERIAL PRIMARY KEY,
    pokemon_id INT REFERENCES pokemon(pokemon_id),
    type_id INT REFERENCES pokemon_types(id),
    slot TEXT CHECK (slot IN ('primary', 'secondary'))
);

CREATE TABLE pokemon_abilities_junction (
    id SERIAL PRIMARY KEY,
    pokemon_id INT NOT NULL REFERENCES pokemon(pokemon_id),
    ability_id INT NOT NULL REFERENCES pokemon_ability(id),
    slot TEXT NOT NULL CHECK (slot IN ('primary', 'secondary', 'hidden', 'event')),
    UNIQUE (pokemon_id, slot)
);

CREATE TABLE pokemon_egg_groups_junction (
    id SERIAL PRIMARY KEY,
    pokemon_id INT NOT NULL REFERENCES pokemon(pokemon_id),
    egg_group_id INT NOT NULL REFERENCES pokemon_egg_groups(id),
    slot TEXT NOT NULL CHECK (slot IN ('primary', 'secondary')),
    UNIQUE (pokemon_id, slot)
);
