from app.schemas.game import GameCreateRequest
from fastapi import APIRouter

from app.dependencies import GameServiceDep
from app.schemas.game import GameResponse

router = APIRouter(prefix="/api/games", tags=["games"])

# 경기 전체 조회
@router.get("", summary="야구 경기 전체 일정을 조회")
def find_games(service: GameServiceDep) -> list[GameResponse]:
    return service.find_games()

# 경기 상세 조회
@router.get("/{game_id}", summary="야구 경기 상세 일정을 조회")
def find_game(game_id: int, service: GameServiceDep) -> GameResponse:
    return service.find_game(game_id)   

# 새로운 경기 등록
@router.post("", status_code=201, summary="새로운 경기 등록")
def register_game(request: GameCreateRequest, service: GameServiceDep) -> GameResponse:
    return service.register_game(request)