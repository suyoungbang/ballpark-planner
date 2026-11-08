from fastapi import FastAPI

from app.core.exceptions import register_exception_handlers
from app.routers import game_router, visit_plan_router

app = FastAPI(
    title="야구 직관 도우미",
    version="0.1.0",
)

register_exception_handlers(app)
app.include_router(game_router.router)
app.include_router(visit_plan_router.router)

