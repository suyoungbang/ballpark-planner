
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# [작성하기]
# 메뉴를 찾지 못했을 때 MenuService가 던지는 사용자 정의 예외
# (Spring 프로젝트의 NotFoundException)
# 메시지는 Spring 프로젝트의 MenuService가 던지는 메시지와 동일하게 맞췄다.
class GameNotFoundError(Exception):

    def __init__(self, game_id: int):
        super().__init__(f"해당 경기가 존재하지 않습니다. gameId={game_id}")
        self.game_id = game_id

class PlanNotFoundError(Exception):

    def __init__(self, plan_id: int):
        super().__init__(f"해당 일정이 존재하지 않습니다. planId={plan_id}")
        self.plan_id = plan_id


# OpenAI 호출이 실패했을 때 LLM 클라이언트가 던지는 예외 (Spring 프로젝트의 AiRequestException)
# 키가 잘못되었거나, 요청 한도를 넘었거나, 응답이 제한 시간 안에 오지 않았을 때 발생한다.
# 추가할 필드가 없으므로 본문은 pass다. 메시지는 예외를 만들 때 전달한다. 예: AiRequestError("OpenAI 서버에 연결할 수 없습니다.")
class AiRequestError(Exception):
    pass


# main.py에서 app을 전달인자로 전달하며 호출되는 함수다.
# 그러면 이 함수 내부에 정의한 예외 처리기(exception_handler)가 app에 등록된다.
def register_exception_handlers(app: FastAPI) -> None:

    # MenuService가 MenuNotFoundError 예외를 던지면
    # FastAPI가 이 함수를 호출하고, 반환한 응답을 보낸다.
    # 핸들러(라우터의 함수)는 예외를 잡지 않아도 된다.
    # (Spring의 @ExceptionHandler와 동일)
    @app.exception_handler(GameNotFoundError)
    def handle_menu_not_found(request: Request, e: GameNotFoundError):

        # FastAPI의 JSONResponse는 Spring의 ResponseEntity<T>와 역할이 동일하다
        return JSONResponse(
            status_code=404,
            content={
                "code": "ERROR_CODE_00001",
                "description": "조회 실패",
                # str(e)는 예외를 만들 때 전달한 메시지다. (Java의 e.getMessage())
                "detail": str(e),
            },
        )

    
    @app.exception_handler(PlanNotFoundError)
    def handle_menu_not_found(request: Request, e: PlanNotFoundError):

        # FastAPI의 JSONResponse는 Spring의 ResponseEntity<T>와 역할이 동일하다
        return JSONResponse(
            status_code=404,
            content={
                "code": "ERROR_CODE_00002",
                "description": "조회 실패",
                # str(e)는 예외를 만들 때 전달한 메시지다. (Java의 e.getMessage())
                "detail": str(e),
            },
        )


    # OpenAI 호출이 실패하면 502 Bad Gateway로 응답한다.
    # 502는 "우리 서버가 호출한 다른쪽 서버가 실패했다"는 뜻이다.
    # 즉, 서버의 잘못이 맞기 때문에 5xx 에러는 맞지만 우리 FastAPI 서버의 잘못이 아니라
    # OpenAI 서버의 잘못인 것이다.
    @app.exception_handler(AiRequestError)
    def handle_ai_request_error(request, e):
        return JSONResponse(
            status_code=502,
            content={
                "code": "ERROR_CODE_00011",
                "description": "AI 응답 실패",
                "detail": str(e)
            }
        )
