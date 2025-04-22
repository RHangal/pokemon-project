# api/models/competitive.py
from typing import Optional
from pydantic import BaseModel

class CompetitiveFactors(BaseModel):
    pokemon_id: int
    true_pokemon_id: int
    pokemon_name: str
    alternate_form_name: Optional[str] = None
    label: str
    sprite_path: Optional[str] = None

    # Base Stats
    health_stat: int
    attack_stat: int
    defense_stat: int
    special_attack_stat: int
    special_defense_stat: int
    speed_stat: int
    base_stat_total: int

    # Competitive Usage
    smogon_vgc_usage_2022: Optional[float] = None
    smogon_vgc_usage_2023: Optional[float] = None
    smogon_vgc_usage_2024: Optional[float] = None
    worlds_vgc_usage_2022: Optional[float] = None
    worlds_vgc_usage_2023: Optional[float] = None
    worlds_vgc_usage_2024: Optional[float] = None

    # Typing
    primary_type: Optional[str] = None
    secondary_type: Optional[str] = None

    # Abilities
    primary_ability: Optional[str] = None
    secondary_ability: Optional[str] = None
    hidden_ability: Optional[str] = None
    event_ability: Optional[str] = None

    class Config:
        from_attributes = True
