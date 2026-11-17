from app.schemas.friend_invitation import InvitationRevisionRequest
from fastapi import APIRouter, Depends
from typing import Annotated
from fastapi.sse import EventSourceResponse
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


# 스트리밍이 시작되기 전에 일정과 경기를 찾아 입력 dict를 만든다. 없으면 여기서 404.
def get_invitation_values(plan_id: int,
                          request: FriendInvitationRequest,
                          service: FriendInvitationServiceDep) -> dict:
    return service.build_values(plan_id, request)


# 초안이 써지는 대로 글자 조각을 흘려보내는 엔드포인트
@router.post("/{plan_id}/invitation/stream",
             response_class=EventSourceResponse,
             summary="직관 친구 초대장 스트리밍")
async def stream_invitation(
    plan_id: int,
    values: Annotated[dict, Depends(get_invitation_values)],
    service: FriendInvitationServiceDep,
):
    print(f"[invitation stream] thread={threading.current_thread().name}")

    async for event in service.stream_invitation(plan_id, values):
        yield event


# 직전 초대장을 수정 요청 한 줄로 고치는 엔드포인트
@router.post("/{plan_id}/invitation/revise", summary="직관 친구 초대장 수정")  
async def revise_invitation(
    plan_id: int,
    request: InvitationRevisionRequest,                                
    service: FriendInvitationServiceDep,
) -> FriendInvitationResponse:
    print(f"[invitation revise] thread={threading.current_thread().name}")
    return await service.revise_invitation(plan_id, request)  