CREATE OR REPLACE VIEW pokemon_competitive_factors_view AS
SELECT
    p.pokemon_id,
    p.pokemon_name,
    p.alternate_form_name,

    -- Base stats
    p.health_stat,
    p.attack_stat,
    p.defense_stat,
    p.special_attack_stat,
    p.special_defense_stat,
    p.speed_stat,
    p.base_stat_total,

    -- Competitive usage
    u.smogon_vgc_usage_2022,
    u.smogon_vgc_usage_2023,
    u.smogon_vgc_usage_2024,
    u.worlds_vgc_usage_2022,
    u.worlds_vgc_usage_2023,
    u.worlds_vgc_usage_2024,

    -- Types
    pt_primary.type AS primary_type,
    pt_secondary.type AS secondary_type,

    -- Abilities
    pa_primary.name AS primary_ability,
    pa_secondary.name AS secondary_ability,
    pa_hidden.name AS hidden_ability,
    pa_event.name AS event_ability

FROM pokemon_competitive_usage u
JOIN pokemon p ON u.pokemon_id = p.pokemon_id

-- Join for types
LEFT JOIN pokemon_types_junction ptj1
    ON ptj1.pokemon_id = p.pokemon_id AND ptj1.slot = 'primary'
LEFT JOIN pokemon_types_junction ptj2
    ON ptj2.pokemon_id = p.pokemon_id AND ptj2.slot = 'secondary'
LEFT JOIN pokemon_types pt_primary ON pt_primary.id = ptj1.type_id
LEFT JOIN pokemon_types pt_secondary ON pt_secondary.id = ptj2.type_id

-- Join for abilities
LEFT JOIN pokemon_abilities_junction paj1
    ON paj1.pokemon_id = p.pokemon_id AND paj1.slot = 'primary'
LEFT JOIN pokemon_abilities_junction paj2
    ON paj2.pokemon_id = p.pokemon_id AND paj2.slot = 'secondary'
LEFT JOIN pokemon_abilities_junction paj3
    ON paj3.pokemon_id = p.pokemon_id AND paj3.slot = 'hidden'
LEFT JOIN pokemon_abilities_junction paj4
    ON paj4.pokemon_id = p.pokemon_id AND paj4.slot = 'event'

LEFT JOIN pokemon_ability pa_primary ON pa_primary.id = paj1.ability_id
LEFT JOIN pokemon_ability pa_secondary ON pa_secondary.id = paj2.ability_id
LEFT JOIN pokemon_ability pa_hidden ON pa_hidden.id = paj3.ability_id
LEFT JOIN pokemon_ability pa_event ON pa_event.id = paj4.ability_id

ORDER BY p.pokemon_id;
