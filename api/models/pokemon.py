from typing import Optional
from pydantic import BaseModel


class Pokemon(BaseModel):
    id: int
    pokemon_id: int
    pokedex_number: int
    pokemon_name: str
    classification: str
    alternate_form_name: Optional[str]
    pre_evolution_pokemon_id: Optional[int]
    evolution_details: Optional[str]

    game_id: Optional[int]
    catch_rate_id: Optional[int]
    base_happiness_id: Optional[int]
    experience_growth_id: Optional[int]
    gender_ratio_id: Optional[int]

    # Base Stats
    health_stat: int
    attack_stat: int
    defense_stat: int
    special_attack_stat: int
    special_defense_stat: int
    speed_stat: int
    base_stat_total: int

    # EV Yields
    health_ev: int
    attack_ev: int
    defense_ev: int
    special_attack_ev: int
    special_defense_ev: int
    speed_ev: int
    ev_yield_total: int

    sprite_path: Optional[str]

    class Config:
        orm_mode = True  # Ensures compatibility with raw SQL query rows or ORM results

