# Ballpark Planner ⚾

야구 경기와 직관 계획을 관리하고, 저장된 계획을 바탕으로 AI가 직관 미션 카드와 친구 초대장을 만들어 주는 FastAPI 프로젝트다. AI 기능은 LangChain과 LangGraph로 만들었다.

## 주요 기능

- 경기 일정 조회 및 등록
- 직관 계획 조회·등록·수정·삭제
- 저장된 경기와 직관 계획을 활용한 미션 카드 생성 (초안 → 검토 → 재작성 그래프)
- 친구 이름과 직관 계획을 활용한 초대장 생성 (초안 → 검토 → 재작성 그래프)
- 초대장 스트리밍 (SSE로 글자가 써지는 대로 전송)
- 초대장 수정 요청 (직전 초대장을 기억해 두었다가 요청대로 고쳐 씀)

## 실행 방법

Python 3.14와 uv가 필요하다.

```bash
uv sync
cp .env.example .env
uv run fastapi dev
```

서버가 실행되면 `http://127.0.0.1:8000/docs`에서 API를 호출할 수 있다.

`.env`에 `OPENAI_API_KEY`를 넣거나 사용자 환경 변수로 등록한다. 키가 없으면 서버가 시작되지 않는다. LangSmith로 실행 과정을 추적하려면 `.env`에서 `LANGSMITH_TRACING=true`로 바꾸고 `LANGSMITH_API_KEY`를 넣는다. **`.env`는 Git에 올리지 않는다.**

## API

| 메서드 | 경로 | 기능 |
| --- | --- | --- |
| GET | `/api/games` | 경기 전체 조회 |
| GET | `/api/games/{game_id}` | 경기 상세 조회 |
| POST | `/api/games` | 경기 등록 |
| GET | `/api/visitplans` | 직관 계획 전체 조회 |
| GET | `/api/visitplans/{plan_id}` | 직관 계획 상세 조회 |
| POST | `/api/visitplans` | 직관 계획 등록 |
| PUT | `/api/visitplans/{plan_id}` | 직관 계획 수정 |
| DELETE | `/api/visitplans/{plan_id}` | 직관 계획 삭제 |
| POST | `/api/visitplans/{plan_id}/mission-card` | AI 미션 카드 생성 |
| POST | `/api/visitplans/{plan_id}/invitation` | AI 친구 초대장 생성 |
| POST | `/api/visitplans/{plan_id}/invitation/stream` | AI 친구 초대장 스트리밍 (SSE) |
| POST | `/api/visitplans/{plan_id}/invitation/revise` | AI 친구 초대장 수정 |

친구 초대장 생성·스트리밍 요청 예시:

```json
{
  "friendName": "민지"
}
```

친구 초대장 수정 요청 예시 (같은 `plan_id`로 초대장을 먼저 만든 뒤 호출한다):

```json
{
  "instruction": "네 문장으로 늘려줘"
}
```

## 요청 흐름

```text
일반 API: 요청 → 라우터 → 서비스 → 저장소 → 응답
AI API:   요청 → 라우터 → 서비스 → 저장소에서 계획·경기 조회
                                → LangGraph 그래프 (draft → review → 통과 못 하면 draft) → 응답
```

- 검토를 통과하지 못하면 다시 쓰되, 최대 2번까지만 쓴다.
- 초대장 그래프는 `plan_id`별로 마지막 상태를 메모리(InMemorySaver)에 저장한다. 수정 요청은 이 상태를 이어받아 고쳐 쓴다.

경기, 직관 계획, 초대장 상태는 모두 메모리에 저장된다. 서버를 다시 실행하면 등록·수정한 내용과 초대장 상태는 초기화되고 예시 데이터가 다시 준비된다. 예시 경기 일정은 실제 경기 일정이 아니다.

## 응답 확인

- 등록 성공: `201`
- 잘못된 요청값: `422`
- 없는 경기·직관 계획 조회: `404`
- 초대장 없이 수정 요청: `404`
- 직관 계획 삭제 성공: `204`
- OpenAI 호출 실패: `502` (스트리밍은 `event: error`로 전달)
- 비동기 AI 핸들러 실행 스레드: `MainThread`