from pydantic import Field

from app.schemas.base import CamelModel

# 친구 초대장 생성 요청 DTO
# 초대할 친구의 이름 받음
class FriendInvitationRequest(CamelModel):
    friend_name: str = Field(min_length=1, max_length=20)

# 친구 초대장 생성 응담 DTO
class FriendInvitationResponse(CamelModel):
    plan_id: int
    invitation: str
    model: str
