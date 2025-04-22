# graphql/types/competitive.py
import strawberry
from typing import Optional

@strawberry.type
class GQLCompetitiveFactors:
    pokemon_id: int
    true_pokemon_id: int
    pokemon_name: str
    alternate_form_name: Optional[str]

    label: str
    health_stat: int
    attack_stat: int
    defense_stat: int
    special_attack_stat: int
    special_defense_stat: int
    speed_stat: int
    base_stat_total: int

    smogon_vgc_usage_2022: Optional[float]
    smogon_vgc_usage_2023: Optional[float]
    smogon_vgc_usage_2024: Optional[float]
    worlds_vgc_usage_2022: Optional[float]
    worlds_vgc_usage_2023: Optional[float]
    worlds_vgc_usage_2024: Optional[float]

    primary_type: Optional[str]
    secondary_type: Optional[str]

    primary_ability: Optional[str]
    secondary_ability: Optional[str]
    hidden_ability: Optional[str]
    event_ability: Optional[str]

