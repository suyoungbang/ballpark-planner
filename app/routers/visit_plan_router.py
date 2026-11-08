from app.schemas.visit_plan import VisitPlanRequest
from app.schemas.visit_plan import VisitPlanResponse
from fastapi import APIRouter

from app.dependencies import VisitPlanServiceDep

router = APIRouter(prefix="/api/visitplans", tags = ["visit plans"])

# 1. 직관 일정 전체 조회
@router.get("", summary="전체 직관 일정을 조회")
def find_visit_plans(service: VisitPlanServiceDep)  -> list[VisitPlanResponse]:
    return service.find_visit_plans()

# 2. 직관 일정 상세 조회
@router.get("/{plan_id}", summary="직관 일정 상세 조회")
def find_visit_plan(plan_id: int, service: VisitPlanServiceDep) -> VisitPlanResponse:
    return service.find_visit_plan(plan_id)

# 3. 새로운 직관 일정 등록
@router.post("", status_code=201, summary="직관 일정 등록")
def register_visit_plan(request: VisitPlanRequest, service: VisitPlanServiceDep,) -> VisitPlanResponse:
    return service.register_visit_plan(request)

# 4. 직관 일정 수정
@router.put("/{plan_id}", summary = "기존의 직관 일정을 변경")
def update_visit_plan(plan_id: int, request: VisitPlanRequest, service: VisitPlanServiceDep) -> VisitPlanResponse:
    return service.update_visit_plan(plan_id, request)

# 5. 직관 일정 삭제
@router.delete("/{plan_id}", status_code=204, summary = "직관 일정을 삭제")
def delete_visit_plan(plan_id: int, service: VisitPlanServiceDep) -> None:
    service.delete_visit_plan(plan_id)
    