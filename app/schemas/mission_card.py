from app.schemas.base import CamelModel

class MissionCardResponse(CamelModel):
    plan_id:int
    mission_card: str       # llm이 생성해주는 미션 내용
    model: str