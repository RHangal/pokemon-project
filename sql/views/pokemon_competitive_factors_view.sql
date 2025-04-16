CREATE OR REPLACE VIEW pokemon_competitive_factors_view AS
WITH type_data AS (
    SELECT 
        pokemon_id,
        MAX(CASE WHEN slot = 'primary' THEN pt.type END) AS primary_type,
        MAX(CASE WHEN slot = 'secondary' THEN pt.type END) AS secondary_type
    FROM pokemon_types_junction tj
    LEFT JOIN pokemon_types pt ON tj.type_id = pt.id
    GROUP BY pokemon_id
),
ability_data AS (
    SELECT 
        pokemon_id,
        MAX(CASE WHEN slot = 'primary' THEN pa.name END) AS primary_ability,
        MAX(CASE WHEN slot = 'secondary' THEN pa.name END) AS secondary_ability,
        MAX(CASE WHEN slot = 'hidden' THEN pa.name END) AS hidden_ability,
        MAX(CASE WHEN slot = 'event' THEN pa.name END) AS event_ability
    FROM pokemon_abilities_junction aj
    LEFT JOIN pokemon_ability pa ON aj.ability_id = pa.id
    GROUP BY pokemon_id
)

SELECT 
    u.pokemon_id,
    p.pokemon_id AS true_pokemon_id,
    p.pokemon_name,
    p.alternate_form_name,

    -- Label like "Charizard (Gmax)"
    CASE 
        WHEN p.alternate_form_name IS NOT NULL 
        THEN CONCAT(p.pokemon_name, ' (', p.alternate_form_name, ')')
        ELSE p.pokemon_name
    END AS label,

    -- Base Stats
    p.health_stat,
    p.attack_stat,
    p.defense_stat,
    p.special_attack_stat,
    p.special_defense_stat,
    p.speed_stat,
    p.base_stat_total,

    -- Competitive Usage
    u.smogon_vgc_usage_2022,
    u.smogon_vgc_usage_2023,
    u.smogon_vgc_usage_2024,
    u.worlds_vgc_usage_2022,
    u.worlds_vgc_usage_2023,
    u.worlds_vgc_usage_2024,

    -- Types and Abilities
    td.primary_type,
    td.secondary_type,
    ad.primary_ability,
    ad.secondary_ability,
    ad.hidden_ability,
    ad.event_ability

FROM pokemon_competitive_usage u
JOIN pokemon p ON u.pokemon_id = p.id
LEFT JOIN type_data td ON td.pokemon_id = p.pokemon_id
LEFT JOIN ability_data ad ON ad.pokemon_id = p.pokemon_id;




