from app.core.exceptions import PlanNotFoundError
from app.core.exceptions import GameNotFoundError
from app.schemas.mission_card import MissionCardResponse
from app.repositories.game_repository import GameRepository
from app.repositories.visit_plan_repository import VisitPlanRepository
from app.clients.llm_client import to_ai_request_error
from app.core.config import get_settings
import openai

from pydantic import ValidationError
from langchain_core.runnables import Runnable
from app.core.exceptions import AiRequestError

class MissionCardService:
    def __init__(self, graph: Runnable,
                    visit_plan_repo: VisitPlanRepository,
                    game_repo: GameRepository):
            self.graph = graph
            self.visit_plan_repo = visit_plan_repo
            self.game_repo = game_repo
    
    async def create_mission_card(self, plan_id: int) -> MissionCardResponse:
        # 선택한 직관 일정을 찾는다. 
        visit_plan = self.visit_plan_repo.find_by_id(plan_id)

        if visit_plan is None:
            raise PlanNotFoundError(plan_id)

        # 계획에 저장된 game_id로 경기 정보를 찾는다.
        game = self.game_repo.find_by_id(visit_plan.game_id)
        if game is None:
            raise GameNotFoundError(visit_plan.game_id)

        values = {
            "home_team": game.home_team,
            "away_team": game.away_team,
            "stadium": game.stadium,
            "starts_at": f"{game.starts_at:%Y-%m-%d %H:%M}",
            "seat_section": visit_plan.seat_section,
            "food_plan": visit_plan.food_plan or "미정",
            "uniform": visit_plan.uniform or "미정",
            "memo": visit_plan.memo  or "없음",
            "attempts": 0
        }

       # 그래프를 비동기로 호출한다. OpenAI 오류와 응답 형식 오류는 502로 처리한다.
        try:
            result = await self.graph.ainvoke(values)
        except openai.OpenAIError as e:
            raise to_ai_request_error(e) from e
        except ValidationError as e:
            raise AiRequestError("AI 응답 형식이 올바르지 않습니다.") from e

        # 그래프의 최종 상태에서 미션 카드만 꺼낸다.
        mission_card = result["mission_card"]

        return MissionCardResponse(
            plan_id=plan_id,
            mission_card=mission_card,
            model=get_settings().openai_model
        )