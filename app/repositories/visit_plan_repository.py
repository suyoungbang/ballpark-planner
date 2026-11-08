from app.domains.visit_plan import VisitPlan

def init_visit_plans() -> list[VisitPlan]:
    return [
         VisitPlan(0, 1, "1루 내야", "3열 12번", "지하철", "허갈닭강정", "홈 유니폼", "친구랑 정문에서 만나기"),
        VisitPlan(0, 2, "그린존", None, "5번 버스", "마라샹궈&허니콤보", "깜자니폼", "가챠 뽑기 하고 오기"),
        VisitPlan(0, 3, "3루 내야", "7열 4번", "KTX", "심바다 후토마키&컵물회", "원정 유니폼", "집 오는 기차시간 맞춰서 나오기"),
        VisitPlan(0, 4, "중앙 테이블석", None, "친구 차", "경기 전 저녁 먹기", "원정 유니폼", "주차 시간 넉넉히 잡기"),
        VisitPlan(0, 5, "1루 내야", "2열 8번", "1호선(구일역 하차)", "지지고 라이스& 불고기 누들", None, "좌석 예매 후 번호 적기"),
    ]

class VisitPlanRepository:

    def __init__(self):
        self._visit_plans: dict[int, VisitPlan] = {}
        self._next_code = 1

        for visit_plan in init_visit_plans():
            self.save(visit_plan)


    
    # 전체 직관 일정 조회
    def find_all(self) -> list[VisitPlan]:
        return list(self._visit_plans.values())

    # 일정 상세 조회
    def find_by_id(self, plan_id: int) -> VisitPlan | None:
        return self._visit_plans.get(plan_id)

    # 직관 일정 등록
    def save(self, visit_plan: VisitPlan) -> VisitPlan:
        if visit_plan.plan_id == 0:
            visit_plan.plan_id = self._next_code
            self._next_code += 1

        self._visit_plans[visit_plan.plan_id] = visit_plan

        return visit_plan

    # 직관 일정 수정
    def update(self,visit_plan: VisitPlan) -> VisitPlan | None :

        if visit_plan.plan_id  not in self._visit_plans:
            return None

        self._visit_plans[visit_plan.plan_id] = visit_plan

        return visit_plan
        

    # 직관 일정 삭제
    def delete(self, plan_id: int) -> None:
        self._visit_plans.pop(plan_id, None)
