from app.routers import mission_card_router
from app.clients.llm_client import OpenAiLlmClient
from app.clients.llm_client import FakeLlmClient
from app.core.config import get_settings
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.exceptions import register_exception_handlers
from app.routers import game_router, visit_plan_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    if settings.fake_llm or settings.openai_api_key is None:
        print(f"[lifespan] 가짜 LLM 클라이언트를 사용한다. (FAKE_LLM={settings.fake_llm}, "
              f"키 있음={settings.openai_api_key is not None}, 응답까지 {settings.fake_llm_delay_seconds}초)")
        app.state.llm_client = FakeLlmClient(settings)
    else:
        print(f"[lifespan] OpenAI 클라이언트를 사용한다. (model={settings.openai_model})")
        app.state.llm_client = OpenAiLlmClient(settings)
    
    # 서버가 요청 받음
    yield

    await app.state.llm_client.close()


app = FastAPI(
    title="야구 직관 도우미",
    version="0.1.0",
    lifespan= lifespan
)

register_exception_handlers(app)
app.include_router(game_router.router)
app.include_router(visit_plan_router.router)
app.include_router(mission_card_router.router)
