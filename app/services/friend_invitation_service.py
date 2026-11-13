from app.core.exceptions import AiRequestError
from pydantic import ValidationError
import openai
from langchain_core.runnables import Runnable

from app.core.exceptions import GameNotFoundError
from app.core.exceptions import PlanNotFoundError
from app.schemas.friend_invitation import FriendInvitationResponse
from app.schemas.friend_invitation import FriendInvitationRequest
from app.repositories.game_repository import GameRepository
from app.repositories.visit_plan_repository import VisitPlanRepository
from app.clients.llm_client import to_ai_request_error
from app.core.config import get_settings




class FriendInvitationService:
    def __init__(self, graph: Runnable, 
                visit_plan_repo: VisitPlanRepository, game_repo: GameRepository):
        
        self.graph= graph
        self.visit_plan_repo= visit_plan_repo
        self.game_repo = game_repo

    
    async def create_invitation(self, plan_id: int, 
                                request: FriendInvitationRequest) -> FriendInvitationResponse:
        # 초대장 만들 직관 일정 찾기
        visit_plan = self.visit_plan_repo.find_by_id(plan_id)

        if visit_plan is None:
            raise PlanNotFoundError(plan_id)
        
        # 직관 일정에 연결된 경기 정보 찾기
        game = self.game_repo.find_by_id(visit_plan.game_id)

        if game is None:
            raise GameNotFoundError(visit_plan.game_id)

        values = {
        "friend_name": request.friend_name,
        "home_team": game.home_team,
        "away_team": game.away_team,
        "stadium": game.stadium,
        "starts_at": f"{game.starts_at:%Y-%m-%d %H:%M}",
        "seat_section": visit_plan.seat_section,
        "food_plan": visit_plan.food_plan or "미정" ,
        "attempts": 0,
       }
        try:
            result = await self.graph.ainvoke(values)
        except openai.OpenAIError as e:
            raise to_ai_request_error(e) from e
        except ValidationError as e:
            raise AiRequestError("AI 응답 형식이 올바르지 않습니다.") from e

        invitation = result["invitation"]

        return FriendInvitationResponse(
            plan_id=plan_id,
            invitation=invitation,
            model=get_settings().openai_model
        )


