from fastapi import APIRouter
import threading

from app.schemas.friend_invitation import FriendInvitationResponse
from app.dependencies import FriendInvitationServiceDep
from app.schemas.friend_invitation import FriendInvitationRequest

router = APIRouter(prefix="/api/visitplans", tags=["friend invitaion"])

@router.post("/{plan_id}/invitation", summary="직관 친구 초대장 생성")
async def create_invitation(
    plan_id: int,
    request: FriendInvitationRequest,
    service: FriendInvitationServiceDep
    ) -> FriendInvitationResponse:
    print(f"[invitation] thread={threading.current_thread().name}")

    return await service.create_invitation(plan_id, request)