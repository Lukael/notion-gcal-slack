# Contract: Sync Service Interface

## Purpose
Notion Todo -> Google Calendar 동기화 서비스의 외부 실행/운영 계약을 정의한다.

## 1) Runtime Command Contract

### Command
`python -m src.main --once`

### Inputs
- Environment variables:
  - `NOTION_TOKEN` (required)
  - `NOTION_DATABASE_ID` (required)
  - `GCAL_CALENDAR_ID` (optional, default: `primary`)
  - `TZ` (optional, default: `Asia/Seoul`)
- Files:
  - `token.json` (required after first OAuth login)
  - `contact.json` (optional; attendees mapping)

### Behavior
- 정상 종료 시 exit code `0`
- 설정 오류/치명적 초기화 실패 시 exit code `1`
- 항목 단위 처리 실패가 있더라도 실행 자체는 완료 가능하며, 실패 건수는 로그로 보고

## 2) Data Mapping Contract

| Notion Property | Type | Required | Calendar Field | Rule |
|-----------------|------|----------|----------------|------|
| Task Name | Title | Yes | `summary` | Status가 Done이면 `✓ ` 접두 반영 |
| Due Date | Date | Yes (for sync) | `start.date`/`end.date` | all-day 이벤트로 변환 |
| Status | Select | Yes | `summary` | Done일 때 완료 표시 규칙 적용 |
| Assignees | Select | No | `attendees[].email` | `contact.json` 이름->이메일 매핑 |
| Google ID | Text | No | `event.id` | 없으면 생성, 있으면 업데이트 |

## 3) Idempotency Contract
- `Google ID`가 비어 있으면 create
- `Google ID`가 있으면 patch update
- 동일 `notion_page_id` 처리 시 중복 create를 금지

## 4) Error Handling Contract
- 외부 API 오류는 항목 단위로 격리
- 실패 항목은 다음 주기에서 재시도 대상
- 실패 로그는 최소 다음 필드를 포함:
  - notion_page_id
  - operation(create/update/map_attendees)
  - error_message
  - retry_eligible

## 5) Security Contract
- 비밀정보(`NOTION_TOKEN`, OAuth credential, `token.json`)는 저장소에 커밋 금지
- `contact.json` 내 개인정보는 최소 수집 원칙 적용
- OWASP Top 10 점검 체크리스트에 운영 절차 포함
