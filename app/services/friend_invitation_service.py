from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.core.exceptions import GameNotFoundError
from app.core.exceptions import PlanNotFoundError
from app.schemas.friend_invitation import FriendInvitationResponse
from app.schemas.friend_invitation import FriendInvitationRequest
from app.repositories.game_repository import GameRepository
from app.repositories.visit_plan_repository import VisitPlanRepository
from app.clients.llm_client import LlmClient, to_ai_request_error
import openai
from app.core.config import get_settings



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

INVITATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", INSTRUCTIONS),
    ("human",
    "초대할 친구 이름: {friend_name}\n"
    "경기:{home_team} vs {away_team}\n"
    "장소:{stadium}\n"
    "시작:{starts_at}\n"
    "좌석구역:{seat_section}\n"
    "음식 계획:{food_plan}\n"
    "위 정보를 바탕으로 친구에게 보낼 초대 메시지를 작성해 줘."
    )
])

def build_invitation_chain(llm: ChatOpenAI) -> Runnable:
    return INVITATION_PROMPT | llm | StrOutputParser()

class FriendInvitationService:
    def __init__(self, chain: Runnable, 
                visit_plan_repo: VisitPlanRepository, game_repo: GameRepository):
        
        self.chain= chain
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
       }
        try:
            invitation = await self.chain.ainvoke(values)
        except openai.OpenAIError as e:
            raise to_ai_request_error(e) from e

        return FriendInvitationResponse(
            plan_id=plan_id,
            invitation=invitation,
            model=get_settings().openai_model
        )


