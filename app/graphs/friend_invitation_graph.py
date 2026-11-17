from typing import NotRequired, TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from pydantic import BaseModel, Field


INSTRUCTIONS = (
    "너는 야구 직관 도우미다. 친구에게 보낼 야구 직관 초대 메시지를 작성한다. "
    "친근하고 자연스러운 말투로 4~5문장을 쓴다. "
    "친구가 함께 직관에 가고싶어지도록 함께 즐길 만한 계획을 자연스럽게 전한다. "
    "하지만 과장된 약속은 하지 않는다. "
    "제공된 경기 날짜와 장소를 정확히 사용한다. "
    "경기 날짜와 장소는 초대 문장 다음줄에 '[날짜] ..', '[장소] ..' 형식을 따라 작성한다. "
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
    "검토 의견:{feedback}\n"
    "이전 초안:{invitation}\n"
    "수정 요청:{instruction}\n"
    "수정 요청이 '없음'이면 위 정보로 새 초대 메시지를 작성해 줘. "
    "수정 요청이 있으면 이전 초안을 그 요청대로 고쳐 써 줘. "
    "어떤 경우에도 [날짜], [장소] 줄은 그대로 남겨 줘."
    )
])

class InvitationState(TypedDict):
    # 1. 입력 필드
    friend_name: str
    home_team: str
    away_team: str
    stadium: str
    starts_at: str
    seat_section: str
    food_plan: str

    # 2. 초안 검사 결과 필드
    invitation: NotRequired[str]   # draft 노드가 쓴 초대장
    passed: NotRequired[bool]      # review 노드의 통과 여부
    feedback: NotRequired[str]     # review 노드가 준 수정 이유

    # 사용자의 수정 요청
    instruction: NotRequired[str]

    # 3. 반복 제어 필드
    attempts: int 

MAX_ATTEMPTS = 2

# review 노드가 LLM에게 받을 검토 판정 형식
class ReviewResult(BaseModel):
    """친구 초대장 초안을 검토한 판정 결과"""
    passed: bool = Field(description="초대장이 모든 작성 규칙을 지켰으면 True, 하나라도 어겼으면 False")
    reason: str = Field(description="통과하지 못한 경우 어긴 규칙과 고칠 방법을 한두 문장으로 구체적으로 쓴다. 통과한 경우 빈 문자열로 둔다.")

# 검토자 LLM에게 줄 지시문: 역할 + 검토 기준
REVIEW_INSTRUCTIONS = (
    "너는 친구 초대장 검토자다. 아래 기준을 모두 지켰는지 확인한다. "
    "1. 초대 문장 다음 줄에 '[날짜] ..', '[장소] ..' 형식의 줄이 있어야 한다. "
    "2. 초대장의 경기 날짜와 장소가 제공된 경기 정보와 정확히 같아야 한다. "
    "3. 친구의 좌석이나 티켓이 확보됐다고 단정하는 표현이 없어야 한다. "
    "4. 제공되지 않은 선수 정보, 경기 결과 등을 지어내지 않아야 한다."
    # "5. 초대장은 영어로만 작성되어야 한다."    # 상한 횟수 테스트용. 절대 통과할 수 없는 기준
)

REVIEW_PROMPT = ChatPromptTemplate.from_messages([
    ("system", REVIEW_INSTRUCTIONS),
    ("human",
     "경기:{home_team} vs {away_team}\n"
     "장소:{stadium}\n"
     "시작:{starts_at}\n"
     "검토할 초대장:\n{invitation}"
    )
])

def build_invitation_graph(llm: ChatOpenAI):
    draft_chain = INVITATION_PROMPT | llm | StrOutputParser()
    review_chain = REVIEW_PROMPT | llm.with_structured_output(ReviewResult)

    # [노드] 초안을 쓰고, 시도 횟수를 1 증가
    async def draft(state: InvitationState) -> dict:
        values = dict(state)                              # 상태를 복사한 새 dict
        values["feedback"] = state.get("feedback", "없음")  # feedback 키만 넣기
        invitation = await draft_chain.ainvoke(values)

        return {"invitation": invitation, "attempts": state["attempts"]+1}

    # [노드] 초안 검토 후 판정 결과를 state에 저장
    async def review(state: InvitationState) -> dict:
        result = await review_chain.ainvoke(state)

        print(f"[review] {state['attempts']}번째 초안: passed={result.passed}, reason={result.reason}")

        return {"passed":result.passed, "feedback": result.reason}

    # [라우팅 함수] 
    def route_after_review(state: InvitationState) -> str:
        # 1. 통과 
        if state["passed"]:
            print("[route] 통과 → 종료")
            return END

        # 2. 미통과인데 상한 도달
        if state["attempts"] >= MAX_ATTEMPTS:
            print("[route] 상한 도달 → 마지막 초안으로 종료")
            return END

        print("[route] 미통과 → 다시 쓰기")
        return "draft"
        
    builder = StateGraph(InvitationState)

    # 1. 노드 등록
    builder.add_node("draft", draft)
    builder.add_node("review", review)

    # 2. 고정 엣지
    builder.add_edge(START, "draft")
    builder.add_edge("draft", "review")

    # 3. 조건부 엣지
    builder.add_conditional_edges("review", route_after_review, ["draft", END])

    # 4. 컴파일
    return builder.compile(checkpointer=InMemorySaver())

