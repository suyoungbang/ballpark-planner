from typing import Annotated

from fastapi import Depends

from app.repositories.game_repository import GameRepository
from app.services.game_service import GameService
from app.repositories.visit_plan_repository import VisitPlanRepository
from app.services.visit_plan_service import VisitPlanService



# 데이터가 요청마다 초기화되지 않도록 저장소 하나를 재사용한다.
game_repository = GameRepository()
visit_plan_repository = VisitPlanRepository()


# 1. 경기 
def get_game_repository() -> GameRepository:
    return game_repository

# FastAPI가 저장소를 먼저 준비해 서비스에 넣어준다.
def get_game_service(
    repository: Annotated[GameRepository, Depends(get_game_repository)],
) -> GameService:
    return GameService(repository)


# 2. 직관 일정
def get_visit_plan_repository() -> VisitPlanRepository:
    return visit_plan_repository

def get_visit_plan_service(
    repository: Annotated[VisitPlanRepository, Depends(get_visit_plan_repository)],
    game_repository: Annotated[GameRepository, Depends(get_game_repository)],
) -> VisitPlanService:
    return VisitPlanService(repository, game_repository)

# 라우터에서 서비스 의존성을 간단히 선언하는 별칭이다.
GameServiceDep = Annotated[GameService, Depends(get_game_service)]
VisitPlanServiceDep = Annotated[VisitPlanService, Depends(get_visit_plan_service)]
