from app.core.exceptions import GameNotFoundError
from app.core.exceptions import PlanNotFoundError
from app.schemas.friend_invitation import FriendInvitationResponse
from app.schemas.friend_invitation import FriendInvitationRequest
from app.repositories.game_repository import GameRepository
from app.repositories.visit_plan_repository import VisitPlanRepository
from app.clients.llm_client import LlmClient


INSTRUCTIONS = (
    "너는 야구 직관 도우미다. 친구에게 보낼 야구 직관 초대 메시지를 작성한다. "
    "친근하고 자연스러운 말투로 3~4문장을 쓴다. "
    "친구가 함께 직관에 가고싶어지도록 함께 즐길 만한 계획을 자연스럽게 전한다. "
    "하지만 과장된 약속은 하지 않는다. "
    "제공된 경기 날짜와 장소를 정확히 사용한다. "
    "경기 날짜와 장소는 초대 문장 다음줄에 '[날짜] ..', '[장소] ..' 형식을 따라 작성한다."
    "친구의 좌석이나 티켓이 확보됐다고 단정하지 않는다. "
    "제공되지 않은 경기 관련 정보 또는 결과, 선수 정보는 지어내지 않는다."
)


class FriendInvitationService:
    def __init__(self, llm_client:LlmClient, 
                visit_plan_repo: VisitPlanRepository, game_repo: GameRepository):
        
        self.llm_client =llm_client
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

        question = (
            f"초대할 친구: {request.friend_name}\n"
            f"경기: {game.home_team} vs {game.away_team}\n"
            f"장소: {game.stadium}\n"
            f"시작: {game.starts_at:%Y-%m-%d %H:%M}\n"
            f"내 좌석 구역: {visit_plan.seat_section}\n"
            f"음식 계획: {visit_plan.food_plan or '미정'}\n"
            "위 정보를 바탕으로 친구에게 보낼 초대 메시지를 작성해 줘."
            )
        
        invitation = await self.llm_client.ask_async(INSTRUCTIONS, question)

        return FriendInvitationResponse(
            plan_id=plan_id,
            invitation=invitation,
            model=self.llm_client.model
        )


