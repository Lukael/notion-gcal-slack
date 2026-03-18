# Data Model: Docker Persistent 10-Minute Scheduler

## 1) LoopConfig
- **Description**: 주기 실행 루프의 런타임 설정
- **Fields**:
  - `mode` (enum: `once` | `loop`, required)
  - `interval_seconds` (int, required, default: 600)
  - `shutdown_timeout_seconds` (int, required, default: 30)
  - `max_consecutive_failures` (int, optional)
- **Validation Rules**:
  - `interval_seconds >= 1`
  - `shutdown_timeout_seconds >= 1`

## 2) LoopRunRecord
- **Description**: 각 주기 실행의 결과 메타데이터
- **Fields**:
  - `run_id` (string, unique)
  - `started_at` (datetime, required)
  - `finished_at` (datetime, required)
  - `duration_seconds` (float, required)
  - `status` (enum: `success` | `failed`, required)
  - `created_count` (int)
  - `updated_count` (int)
  - `failed_count` (int)
  - `next_run_at` (datetime, optional)
- **Validation Rules**:
  - `finished_at >= started_at`
  - `duration_seconds >= 0`

## 3) ShutdownState
- **Description**: 종료 신호 수신 및 루프 중지 상태
- **Fields**:
  - `signal_received` (bool, default: false)
  - `signal_name` (string, optional)
  - `received_at` (datetime, optional)
  - `safe_to_exit` (bool, default: false)
- **Validation Rules**:
  - `signal_received=true`일 때 `received_at` 존재

## Relationships
- `LoopConfig(1)` -> `LoopRunRecord(0..*)`
- `LoopRunRecord(1)` -> 기존 SyncRun 요약 값(created/updated/failed) 포함
- `ShutdownState(1)`은 루프 생명주기 전체에 공유

## State Transitions
- `INIT` -> `RUNNING_LOOP` (mode=loop)
- `RUNNING_LOOP` -> `RUN_CYCLE` -> `SLEEP_UNTIL_NEXT` 반복
- `RUN_CYCLE` 실패 -> `SLEEP_UNTIL_NEXT` (루프 지속)
- 종료 신호 수신 -> `SHUTDOWN_PENDING` -> `EXIT`
