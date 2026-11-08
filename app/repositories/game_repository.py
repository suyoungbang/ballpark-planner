from app.domains.game import Game
from datetime import datetime

def init_games() -> list[Game]:
    return [
        Game(0, "SSG 랜더스", "두산 베어스", "인천SSG랜더스필드", datetime(2027, 4, 3, 18, 30)),
        Game(0, "SSG 랜더스", "한화 이글스", "인천SSG랜더스필드", datetime(2027, 4, 10, 18, 30)),
        Game(0, "롯데 자이언츠", "SSG 랜더스", "사직구장", datetime(2027, 4, 22, 18, 30)),
        Game(0, "기아 타이거즈", "LG 트윈스", "광주기아챔피언스필드", datetime(2027, 5, 10, 14, 0)),
        Game(0, "키움 히어로즈", "NC 다이노스", "고척스카이돔", datetime(2027, 6, 11, 14, 0)),
    ]

class GameRepository:

    def __init__(self):
        self._games: dict[int, Game] = {}
        self._next_code = 1

        for game in init_games():
            self.save(game)

    
    # 전체 경기 조회
    def find_all(self) -> list[Game]:
        return list(self._games.values())

    # 경기 상세 조회
    def find_by_id(self, game_id: int) -> Game | None:
        return self._games.get(game_id)

    # 경기 등록
    def save(self, game: Game) -> Game:
        if game.game_id == 0:
            game.game_id = self._next_code
            self._next_code += 1
        
        self._games[game.game_id] = game

        return game