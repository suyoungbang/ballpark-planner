from typing import NotRequired, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph

from app.schemas.mission_card import MissionCard

class MissionCardState(TypedDict):
    home_team: str
    away_team: str
    stadium: str
    starts_at: str
    seat_section: str
    food_plan: str
    uniform: str
    memo: str

    mission_card: NotRequired[MissionCard]
    passed: NotRequired[bool]
    feedback: NotRequired[str]

    attempts: int

MAX_ATTEMPTS = 2


INSTRUCTIONS = (
    "너는 야구 직관 미션 제작자이다. 사용자는 야구 경기를 직접 관람하러 간다. "
    "제공된 경기와 직관 일정을 기반으로 "
    "재미있고 실천 가능하고 중복되지 않는 미션 3개를 작성한다. "
    "단, 일정을 설명하거나 일반적인 관람 팁을 주는 것이 아닌 현장에서 직접 수행할 행동을 제시한다. "
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
        "메모: {memo}\n"           
        "검토 의견: {feedback}"      
        )
    ]
)


# 검토 판정 형식 (설명만 미션 카드에 맞게)
class ReviewResult(BaseModel):
    """미션 카드 초안을 검토한 판정 결과"""
    passed: bool = Field(description="미션 카드가 모든 검토 기준을 지켰으면 True, 하나라도 어겼으면 False")
    reason: str = Field(description="통과하지 못한 경우 어긴 기준과 고칠 방법을 한두 문장으로 구체적으로 쓴다. 통과한 경우 빈 문자열로 둔다.")

# 검토자 지시문
REVIEW_INSTRUCTIONS = (
    "너는 야구 직관 미션 카드 검토자다. 아래 기준을 모두 지켰는지 확인한다. "
    "1. 미션이 정확히 3개여야 한다. "
    "2. 일정 설명이나 일반적인 관람 팁이 아니라 현장에서 직접 수행할 행동이어야 한다. "
    "3. 준비물은 미션 수행에 필요한 것만 있어야 하고, 미션과 관련 없는 물건을 지어내지 않아야 한다. "
    "4. 제공되지 않은 선수 정보, 경기 결과 등을 지어내지 않아야 한다."
)

REVIEW_PROMPT = ChatPromptTemplate.from_messages([
    ("system", REVIEW_INSTRUCTIONS),
    ("human",
     "경기: {home_team} vs {away_team}\n"
     "장소: {stadium}\n"
     "좌석구역: {seat_section}\n"
     "음식계획: {food_plan}\n"
     "유니폼: {uniform}\n"
     "메모: {memo}\n"
     "검토할 미션 카드:\n{mission_card}"
    )
])


def build_mission_card_graph(llm: ChatOpenAI):
    draft_chain = MISSION_CARD_PROMPT | llm.with_structured_output(MissionCard)
    review_chain = REVIEW_PROMPT | llm.with_structured_output(ReviewResult)

    # [노드] 미션 카드 초안을 만들고 시도 횟수를 1 늘린다.
    async def draft(state: MissionCardState) -> dict:
        values = dict(state)
        values["feedback"] = state.get("feedback", "없음")
        mission_card = await draft_chain.ainvoke(values)
 
        return {"mission_card": mission_card, "attempts": state["attempts"] + 1}

    # [노드] 미션 카드를 검토하고 판정 결과를 저장한다.
    async def review(state: MissionCardState) -> dict:
        values = dict(state)
        values["mission_card"] = state["mission_card"].model_dump_json()
        result = await review_chain.ainvoke(values)

        print(f"[mission review] {state['attempts']}번째 초안: passed={result.passed}, reason={result.reason}")

        return {"passed": result.passed, "feedback": result.reason}

    # [라우팅 함수]
    def route_after_review(state: MissionCardState) -> str: 
        # 1. 통과 
        if state["passed"]:
            print("[mission route] 통과 → 종료")
            return END

         # 2. 미통과인데 상한 도달
        if state["attempts"] >= MAX_ATTEMPTS:
            print("[mission route] 상한 도달 → 마지막 초안으로 종료")
            return END
        print("[mission route] 미통과 → 다시 쓰기")
        return "draft"

    builder = StateGraph(MissionCardState)                  

    # 1. 노드 등록
    builder.add_node("draft", draft)
    builder.add_node("review", review)

    # 2. 고정 엣지
    builder.add_edge(START, "draft")
    builder.add_edge("draft", "review")

    # 3. 조건부 엣지
    builder.add_conditional_edges("review", route_after_review, ["draft", END])

    return builder.compile()