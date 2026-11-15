from app.routers import friend_invitation_router
from app.routers import mission_card_router
from app.clients.llm_client import create_chat_model
from app.core.config import get_settings
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.exceptions import register_exception_handlers
from app.routers import game_router, visit_plan_router
from app.graphs.friend_invitation_graph import build_invitation_graph
from app.graphs.mission_card_graph import build_mission_card_graph

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    llm = create_chat_model(settings)

    app.state.invitation_graph = build_invitation_graph(llm)
    print("[lifespan] 초대장 그래프를 만들었다.")

    app.state.mission_card_graph = build_mission_card_graph(llm)  
    print("[lifespan] 미션 카드 그래프를 만들었다.")

    # 서버가 요청 받음
    yield



app = FastAPI(
    title="야구 직관 도우미",
    version="0.1.0",
    lifespan= lifespan
)

register_exception_handlers(app)
app.include_router(game_router.router)
app.include_router(visit_plan_router.router)
app.include_router(mission_card_router.router)
app.include_router(friend_invitation_router.router)
