from dataclasses import dataclass

@dataclass
class VisitPlan:
    plan_id: int 
    game_id: int 
    seat_section: str
    seat_number: str | None = None
    transport: str | None = None
    food_plan: str | None = None 
    uniform: str | None = None 
    memo: str | None = None