# Ballpark Planner ⚾

야구 경기와 직관 계획을 관리하고, 저장된 계획을 바탕으로 AI가 직관 미션 카드와 친구 초대장을 만들어 주는 FastAPI 프로젝트다.

## 주요 기능

- 경기 일정 조회 및 등록
- 직관 계획 조회·등록·수정·삭제
- 저장된 경기와 직관 계획을 활용한 비동기 미션 카드 생성
- 친구 이름과 직관 계획을 활용한 비동기 초대장 생성

## 실행 방법

Python 3.14와 uv가 필요하다.

```bash
uv sync
cp .env.example .env
uv run fastapi dev
```

서버가 실행되면 `http://127.0.0.1:8000/docs`에서 API를 호출할 수 있다.

`.env`에 `FAKE_LLM=true`를 설정하면 실제 OpenAI 호출 없이 요청 흐름을 확인할 수 있다. 실제 AI 응답을 사용하려면 `.env`에 `OPENAI_API_KEY`를 추가하고 `FAKE_LLM=false`로 설정한다. **`.env`는 Git에 올리지 않는다.**

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

친구 초대장 요청 예시:

```json
{
  "friendName": "민지"
}
```

## 요청 흐름

```text
일반 API: 요청 → 라우터 → 서비스 → 저장소 → 응답
AI API:   요청 → 라우터 → 서비스 → 저장소에서 계획·경기 조회
                                → LLM 클라이언트 → 응답
```

경기와 직관 계획은 메모리의 딕셔너리에 저장된다. 서버를 다시 실행하면 등록·수정한 내용은 초기화되고 예시 데이터가 다시 준비된다. 예시 경기 일정은 실제 경기 일정이 아니다.

## 응답 확인

- 등록 성공: `201`
- 잘못된 요청값: `422`
- 없는 경기·직관 계획 조회: `404`
- 직관 계획 삭제 성공: `204`
- OpenAI 호출 실패: `502`
- 비동기 AI 핸들러 실행 스레드: `MainThread`