from app.clients.llm_client import LlmClient
from typing import Annotated

from fastapi import Depends, Request

from app.repositories.game_repository import GameRepository
from app.services.game_service import GameService
from app.repositories.visit_plan_repository import VisitPlanRepository
from app.services.visit_plan_service import VisitPlanService
from app.services.mission_card_service import MissionCardService
from app.services.friend_invitation_service import FriendInvitationService



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


# lifespan이 app.state에 저장한 LLM 클라이언트를 현재 요청에서 꺼낸다.
def get_llm_client(request: Request) -> LlmClient:
    return request.app.state.llm_client

# [LLM] 1. 직관 미션 카드
# LLM 클라이언트와 두 저장소를 주입해 미션 카드 서비스를 만든다.
def get_mission_card_service(llm_client:Annotated[LlmClient, Depends(get_llm_client)],
                            visit_plan_repo: Annotated[VisitPlanRepository, Depends(get_visit_plan_repository)],
                            game_repo: Annotated[GameRepository, Depends(get_game_repository)],
                            ) -> MissionCardService:
    return MissionCardService(llm_client, visit_plan_repo, game_repo)

# [LLM] 2. 친구 초대장 
def get_friend_invitation_service(
                            llm_client: Annotated[LlmClient, Depends(get_llm_client)],
                            visit_plan_repo: Annotated[VisitPlanRepository, Depends(get_visit_plan_repository)],
                            game_repo: Annotated[GameRepository, Depends(get_game_repository)]
                            ) -> FriendInvitationService:
    return FriendInvitationService(llm_client, visit_plan_repo, game_repo)
    

# 라우터에서 서비스 의존성을 간단히 선언하는 별칭이다.
GameServiceDep = Annotated[GameService, Depends(get_game_service)]
VisitPlanServiceDep = Annotated[VisitPlanService, Depends(get_visit_plan_service)]
MissionCardServiceDep = Annotated[MissionCardService, Depends(get_mission_card_service)]
FriendInvitationServiceDep = Annotated[FriendInvitationService, Depends(get_friend_invitation_service)]