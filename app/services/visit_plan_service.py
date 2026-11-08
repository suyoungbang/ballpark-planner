
from app.repositories.game_repository import GameRepository
from app.schemas.visit_plan import VisitPlanRequest
from app.core.exceptions import PlanNotFoundError, GameNotFoundError
from app.schemas.visit_plan import VisitPlanResponse
from app.repositories.visit_plan_repository import VisitPlanRepository
from app.domains.visit_plan import VisitPlan

class VisitPlanService:

    # 생성자
    def __init__(self, repository: VisitPlanRepository, game_repository: GameRepository):
        self.repository = repository
        self.game_repository = game_repository

    # 1. 직관 일정 전체 조회
    def find_visit_plans(self) -> list[VisitPlanResponse]:
        
        visit_plans = self.repository.find_all()

        return [VisitPlanResponse.from_visit_plan(visit_plan) for visit_plan in visit_plans]

    # 2. 직관 일정 상세 조회
    def find_visit_plan(self, plan_id: int) -> VisitPlanResponse:

        visit_plan = self.repository.find_by_id(plan_id)

        if visit_plan is None:
            raise PlanNotFoundError(plan_id)

        return VisitPlanResponse.from_visit_plan(visit_plan)

    # 3. 직관 일정 등록
    def register_visit_plan(self, request: VisitPlanRequest) -> VisitPlanResponse:

        if self.game_repository.find_by_id(request.game_id) is None:
            raise GameNotFoundError(request.game_id)


        visit_plan = VisitPlan(
            plan_id= 0,
            game_id=request.game_id,
            seat_section = request.seat_section,
            seat_number = request.seat_number,
            transport = request.transport,
            food_plan = request.food_plan,
            uniform = request.uniform,
            memo = request.memo
        )

        saved = self.repository.save(visit_plan)

        return VisitPlanResponse.from_visit_plan(saved)


    # 4. 직관 일정 수정
    def update_visit_plan(self, plan_id: int, request:  VisitPlanRequest) -> VisitPlanResponse:

        if self.repository.find_by_id(plan_id) is None:
            raise PlanNotFoundError(plan_id)

        if self.game_repository.find_by_id(request.game_id) is None:
            raise GameNotFoundError(request.game_id)
          
        visit_plan = VisitPlan(
            plan_id = plan_id,
            game_id=request.game_id,
            seat_section = request.seat_section,
            seat_number = request.seat_number,
            transport = request.transport,
            food_plan = request.food_plan,
            uniform = request.uniform,
            memo = request.memo
        )
    
        updated = self.repository.update(visit_plan)

        if updated is None:
            raise PlanNotFoundError(plan_id)

        return VisitPlanResponse.from_visit_plan(updated)


    # 5. 직관 일정 삭제
    def delete_visit_plan(self, plan_id: int) -> None:
        if self.repository.find_by_id(plan_id) is None:
            raise PlanNotFoundError(plan_id)

        self.repository.delete(plan_id)
