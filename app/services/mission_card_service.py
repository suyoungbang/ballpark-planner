from app.core.exceptions import PlanNotFoundError
from app.core.exceptions import GameNotFoundError
from app.schemas.mission_card import MissionCardResponse
from app.repositories.game_repository import GameRepository
from app.repositories.visit_plan_repository import VisitPlanRepository
from app.clients.llm_client import to_ai_request_error
from app.core.config import get_settings
import openai

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

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

MISSION_CARD_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", INSTRUCTIONS),
        ("human",
        "경기: {home_team} vs {away_team}\n"
        "장소: {stadium}\n"
        "시작: {starts_at}\n"
        "좌석구역: {seat_section}\n"
        "음식계획: {food_plan}\n"
        "유니폼: {uniform}\n"
        "메모: {memo}"
        )
    ]
)

# 모델과 체인은 요청마다 만들지 말고 lifespan에서 한 번만 만들도록 클래스 밖에 선언
def build_mission_card_chain(llm: ChatOpenAI) -> Runnable:
    return MISSION_CARD_PROMPT | llm | StrOutputParser()


class MissionCardService:
    def __init__(self, chain: Runnable, 
                visit_plan_repo: VisitPlanRepository, 
                game_repo: GameRepository):
        self.chain = chain
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
        }

        # 체인을 비동기로 호출한다. OpenAI 오류는 502 에러로 처리.
        try:
            mission_card = await self.chain.ainvoke(values)

        except openai.OpenAIError as e:
            raise to_ai_request_error(e) from e

        return MissionCardResponse(
            plan_id=plan_id,
            mission_card=mission_card,
            model=get_settings().openai_model
        )
