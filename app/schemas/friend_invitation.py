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

# 초대장 수정 요청 DTO
# 수정 지시 한 줄만 받는다. 나머지 정보는 체크포인터가 기억한다.
class InvitationRevisionRequest(CamelModel):
    instruction: str = Field(min_length=1, max_length=20)