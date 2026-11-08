from fastapi import APIRouter
import threading

from app.schemas.mission_card import MissionCardResponse
from app.dependencies import MissionCardServiceDep


router = APIRouter(prefix="/api/visitplans", tags=["mission cards"])

@router.post("/{plan_id}/mission-card", summary="직관 미션 카드 생성")
async def create_mission_card(plan_id:int, service: MissionCardServiceDep) -> MissionCardResponse:

    print(f"[mission-card] thread={threading.current_thread().name}")

    return await service.create_mission_card(plan_id)