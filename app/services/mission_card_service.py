from app.core.exceptions import PlanNotFoundError
from app.core.exceptions import GameNotFoundError
from app.schemas.mission_card import MissionCardResponse
from app.repositories.game_repository import GameRepository
from app.repositories.visit_plan_repository import VisitPlanRepository
from app.clients.llm_client import LlmClient

INSTRUCTIONS = (
    "너는 야구 직관 미션 제작자이다. 사용자는 야구 경기를 직접 관람하러 간다. "
    "제공된 경기와 직관 일정을 기반으로 "
    "재미있고 실천 가능하고 중복되지 않는 미션 3개를 한 줄씩 작성한다. "
    "단, 일정을 절셩하거나 일반적인 관람 팁을 주는 것이 아닌 현장에서 직접 수행할 행동을 제시한다. "
    "각 미션에는 짧은 제목, 구체적인 행동, 성공 여부를 확인할 수 있는 조건을 넣는다. "
    "각 미션 처음에 숫자를 부여하여 구분할 수 있게 하고, "
    "'[제목] 행동 - 성공조건: ..' 형식을 따라 한 줄씩 작성한다. "
    "제공되지 않은 경기 관련 정보 또는 결과, 선수 정보는 지어내지 않는다."
)

class MissionCardService:
    def __init__(self, llm_client: LlmClient, 
                visit_plan_repo: VisitPlanRepository, 
                game_repo: GameRepository):
        self.llm_client = llm_client
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

        question = (
             f"경기: {game.home_team} vs {game.away_team}\n"
            f"장소: {game.stadium}\n"
            f"시작: {game.starts_at:%Y-%m-%d %H:%M}\n"
            f"좌석 구역: {visit_plan.seat_section}\n"
            f"음식 계획: {visit_plan.food_plan or '미정'}\n"
            f"유니폼: {visit_plan.uniform or '미정'}\n"
            f"메모: {visit_plan.memo or '없음'}"
        )

        mission_card = await self.llm_client.ask_async(INSTRUCTIONS, question)

        return MissionCardResponse(
            plan_id=plan_id,
            mission_card=mission_card,
            model=self.llm_client.model
        )
