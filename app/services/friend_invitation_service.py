from app.core.exceptions import InvitationNotFoundError
from app.schemas.friend_invitation import InvitationRevisionRequest
from app.core.exceptions import AiRequestError
from pydantic import ValidationError
import openai
from langchain_core.runnables import Runnable
from fastapi.sse import ServerSentEvent

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
        
    def build_values(self, plan_id:int, request: FriendInvitationRequest) -> dict:
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
        "invitation": "없음" ,
        "instruction": "없음",
        "feedback": "없음",
        "attempts": 0,
       }

        return values
    
    def build_config(self, plan_id: int) -> dict:
        return {"configurable": {"thread_id": str(plan_id)}}

    async def create_invitation(self, plan_id: int, 
                                request: FriendInvitationRequest) -> FriendInvitationResponse:
        
        values = self.build_values(plan_id, request)

        try:
            result = await self.graph.ainvoke(values, self.build_config(plan_id))
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

    # 초안이 써지는대로 글자 조각을 SSE 이벤트로 흘려보낸다
    async def stream_invitation(self, plan_id: int, values: dict):
        try:
            async for chunk, metadata in self.graph.astream(values, self.build_config(plan_id), stream_mode="messages"):
                if metadata.get("langgraph_node") == "draft" and chunk.text:
                    yield ServerSentEvent(data={"text": chunk.text}, event="delta")
        except openai.OpenAIError as e:
            yield ServerSentEvent(data={"message": str(to_ai_request_error(e))}, event="error")
        except ValidationError:
            yield ServerSentEvent(data={"message": "AI 응답 형식이 올바르지 않습니다."}, event="error")


        # 체크포인터에 저장된 직전 초대장을 수정 요청 한 줄로 고친다
    async def revise_invitation(self, plan_id: int,
                                request: InvitationRevisionRequest) -> FriendInvitationResponse:
        config = self.build_config(plan_id)

        # 1. 이 방에 저장된 상태가 없으면 = 초대장을 만든 적 없음 → 404
        snapshot = await self.graph.aget_state(config)        
        if not snapshot.values:
            raise InvitationNotFoundError(plan_id)                      

        # 2. 수정 요청 한 줄 + 시도 횟수만 넣는다. 나머지는 체크포인터가 채운다
        values = {"instruction": request.instruction, "attempts": 0}

        # 3. 그래프 실행 (에러 처리는 create_invitation과 같다)
        try:
            result = await self.graph.ainvoke(values, config)
        except openai.OpenAIError as e:
            raise to_ai_request_error(e) from e
        except ValidationError as e:
            raise AiRequestError("AI 응답 형식이 올바르지 않습니다.") from e

        return FriendInvitationResponse(
            plan_id=plan_id,
            invitation=result["invitation"],
            model=get_settings().openai_model,
        )