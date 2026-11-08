
from pydantic import Field
from datetime import datetime

from app.schemas.base import CamelModel
from app.domains.game import Game


class GameResponse(CamelModel):
    """ 경기 응답 DTO """

    game_id: int
    home_team: str
    away_team: str
    stadium: str
    starts_at: datetime

    @classmethod
    def from_game(cls, game:Game) -> GameResponse:
        return cls(
            game_id = game.game_id,
            home_team = game.home_team,
            away_team = game.away_team,
            stadium = game.stadium,
            starts_at = game.starts_at
        )

class GameCreateRequest(CamelModel):
    """ 경기 등록 요청 DTO """
    home_team: str = Field(min_length=1, max_length=20)
    away_team: str = Field(min_length=1, max_length=20)
    stadium: str = Field(min_length=1, max_length=20)
    starts_at: datetime
