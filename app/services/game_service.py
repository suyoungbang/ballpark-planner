from app.schemas.game import GameCreateRequest
from app.core.exceptions import GameNotFoundError
from app.schemas.game import GameResponse
from app.repositories.game_repository import GameRepository
from app.domains.game import Game

class GameService:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    # 1. 경기 전체 조회
    def find_games(self) -> list[GameResponse]:
        
        games = self.repository.find_all()

        return [GameResponse.from_game(game) for game in games]

    # 2. 경기 상세 조회
    def find_game(self, game_id: int) -> GameResponse:
        
        game = self.repository.find_by_id(game_id)

        if game is None:
            raise GameNotFoundError(game_id)

        return GameResponse.from_game(game)

    # 3. 새로운 경기 일정 등록
    def register_game(self, request: GameCreateRequest) -> GameResponse:

        game = Game (
            game_id=0,
            home_team=request.home_team,
            away_team=request.away_team,
            stadium=request.stadium,
            starts_at=request.starts_at
        )

        saved= self.repository.save(game)

        return GameResponse.from_game(saved)
