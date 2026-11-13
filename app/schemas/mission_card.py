from typing import Literal
from pydantic import Field

from app.schemas.base import CamelModel


class Mission(CamelModel):
    """
    사용자가 수행해야 할 직관 미션 하나의 정보.
    사용자의 직관 일정 계획에 기반으로 작성한다.
    """
    title: str = Field(description="미션의 이름. 예) 짝짝이 인증사진 ")
    action: str = Field(description="사용자가 취해야 할 미션의 내용.")
    success_condition: str = Field(description="미션 성공 조건. 예) 셀카, 남이 찍어준 사진 포함 최소 사진 2장 남기기. ")
    difficulty: Literal["상", "중", "하"] = Field(description="미션의 난이도. "
                        "예) 하 = 자리에서 바로 할 수 있음 / 중 = 이동하거나 준비가 필요함 / 상 = 타이밍이나 운이 따라야 함. ")

class MissionCard(CamelModel):
    """한 경기에 수행해야 할 총 3가지의 미션이 들어가는 미션 카드"""
    card_title: str = Field(description="미션 카드의 이름")
    things_to_bring: list[str] = Field(description="미션들을 수행하기 위해 챙겨야 하는 준비물. 미션과 관련 없는 물건을 임의로 지어내지 않는다.")
    missions: list[Mission] = Field(description="총 3개. 미션들끼리 서로 겹치지 않기.")

class MissionCardResponse(CamelModel):
    plan_id:int
    mission_card: MissionCard   
    model: str