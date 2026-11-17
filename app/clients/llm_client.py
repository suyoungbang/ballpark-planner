import openai
from langchain_openai import ChatOpenAI

from app.core.config import Settings
from app.core.exceptions import AiRequestError




def to_ai_request_error(e: openai.OpenAIError) -> AiRequestError:
    """OpenAI 오류를 우리 프로젝트의 AI 요청 오류로 변경"""

    if isinstance(e, openai.AuthenticationError):
        return AiRequestError("OpenAI API 키가 올바르지 않습니다.")

    if isinstance(e, openai.RateLimitError):
        return AiRequestError("OpenAI 요청 한도를 넘었거나 잔액이 부족합니다.")

    # 시간 초과는 연결 오류의 한 종류이므로 먼저 검사한다.
    if isinstance(e, openai.APITimeoutError):
        return AiRequestError("OpenAI 응답이 제한 시간 안에 오지 않았습니다.")

    if isinstance(e, openai.APIConnectionError):
        return AiRequestError("OpenAI 서버에 연결할 수 없습니다.")

    return AiRequestError(f"OpenAI 호출 실패: {e}")


def create_chat_model(settings: Settings) -> ChatOpenAI:
    """ 설정값으로 랭체인 채팅 모델 객체 만들어 반환 """
    return ChatOpenAI(
        model=settings.openai_model,
        reasoning={"effort": settings.openai_reasoning_effort},
        max_tokens=settings.openai_max_output_tokens,
        timeout=settings.openai_timeout_seconds,
        max_retries=1
    )
