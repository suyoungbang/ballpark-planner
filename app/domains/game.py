from datetime import datetime
from dataclasses import dataclass

@dataclass
class Game:
    game_id: int
    home_team: str
    away_team: str
    stadium: str
    starts_at: datetime
