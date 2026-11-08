from pydantic import Field

from app.schemas.base import CamelModel
from app.domains.visit_plan import VisitPlan

class VisitPlanResponse(CamelModel):
    """ 직관 일정 응답 DTO """

    plan_id: int
    game_id: int
    seat_section: str 
    seat_number: str | None
    transport: str | None
    food_plan: str | None
    uniform: str | None
    memo: str | None

    @classmethod
    def from_visit_plan(cls, visit_plan:VisitPlan) -> VisitPlanResponse:
        return cls(
            plan_id = visit_plan.plan_id,
            game_id = visit_plan.game_id,
            seat_section = visit_plan.seat_section,
            seat_number = visit_plan.seat_number,
            transport = visit_plan.transport,
            food_plan = visit_plan.food_plan,
            uniform = visit_plan.uniform,
            memo = visit_plan.memo
        )

class VisitPlanRequest(CamelModel):
    """ 직관 일정 요청 DTO """
    game_id: int = Field(gt=0)
    seat_section: str = Field(min_length=1, max_length=30)
    seat_number: str | None = Field(default=None, min_length=1, max_length=20)
    transport: str | None = Field(default=None, min_length=1, max_length=50)
    food_plan: str | None = Field(default=None, min_length=1, max_length=100)
    uniform: str | None = Field(default=None, min_length=1, max_length=50)
    memo: str | None = Field(default=None, min_length=1, max_length=300)
