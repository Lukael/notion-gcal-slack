# Data Model: Notion-GCal Todo Sync

## 1) NotionTask
- **Description**: Notion 데이터베이스에서 조회되는 원본 작업 항목
- **Fields**:
  - `notion_page_id` (string, required, unique): Notion 페이지 식별자
  - `task_name` (string, required): 일정 제목 원본
  - `due_date` (date, required for sync): 동기화 기준 날짜
  - `status` (enum: `Todo` | `Doing` | `Done`, required)
  - `assignees` (list[string], optional): 참여자 이름 목록
  - `google_id` (string, optional): Google Calendar 이벤트 ID
- **Validation Rules**:
  - `due_date`가 없으면 동기화 제외
  - `status=Done`이면 제목 렌더링 시 완료 표시 적용
  - `assignees`는 빈 목록 허용

## 2) CalendarEventPayload
- **Description**: Google Calendar 생성/갱신 요청에 사용되는 정규화 모델
- **Fields**:
  - `event_id` (string, optional): 업데이트 시 필요
  - `summary` (string, required): 최종 이벤트 제목
  - `start_date` (date, required)
  - `end_date` (date, required): all-day 정책에 따라 계산
  - `timezone` (string, required, default: `Asia/Seoul`)
  - `attendees` (list[email], optional)
  - `all_day` (boolean, required, fixed: true)
- **Validation Rules**:
  - `end_date >= start_date`
  - `timezone` 누락 시 기본값 대체
  - 중복 이메일 제거 후 전달

## 3) ContactDirectory
- **Description**: 참여자 이름 -> 이메일 매핑 사전
- **Fields**:
  - `name` (string, unique key)
  - `email` (string, RFC 형식)
- **Validation Rules**:
  - 매핑 실패 시 해당 참여자는 제외하고 경고 로그 기록
  - 잘못된 이메일 포맷은 무시하고 경고 로그 기록

## 4) SyncRun
- **Description**: 1회 동기화 실행 메타 정보
- **Fields**:
  - `run_id` (string, unique)
  - `started_at` (datetime, required)
  - `finished_at` (datetime, required)
  - `total_items` (int)
  - `created_count` (int)
  - `updated_count` (int)
  - `skipped_count` (int)
  - `failed_count` (int)
  - `failure_items` (list[FailureRecord])

## 5) FailureRecord
- **Description**: 항목 단위 실패 기록
- **Fields**:
  - `notion_page_id` (string, required)
  - `operation` (enum: `create` | `update` | `map_attendees`)
  - `error_code` (string, optional)
  - `error_message` (string, required)
  - `retry_eligible` (boolean, required)

## Relationships
- `NotionTask(1)` -> `CalendarEventPayload(0..1)` 변환
- `NotionTask.assignees(*)` -> `ContactDirectory(*)` 조회
- `SyncRun(1)` -> `FailureRecord(0..*)` 포함

## State Transitions
- `NotionTask.google_id == null` + valid due date -> `CREATE_EVENT`
- `NotionTask.google_id != null` -> `UPDATE_EVENT`
- any API error -> `FAILED_ITEM` (retry on next run)
- success -> `SYNCED`
