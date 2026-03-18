# Contract: Runtime Loop Execution

## Purpose
`docker run` 시 컨테이너가 유지되고 10분마다 동기화가 반복 실행되는 런타임 계약을 정의한다.

## 1) CLI Contract

### Supported Modes
- `python -m src.main --once`
  - 1회 실행 후 종료
- `python -m src.main`
  - 기본 loop 모드로 지속 실행

### Optional Environment Inputs
- `SYNC_INTERVAL_SECONDS` (default: `600`)
- `SHUTDOWN_TIMEOUT_SECONDS` (default: `30`)

## 2) Loop Behavior Contract
- loop 모드에서는 다음 순서를 반복:
  1. cycle 시작 로그 출력
  2. 동기화 실행
  3. 결과 요약 로그 출력
  4. 다음 실행 예정 시각/대기시간 로그 출력
- cycle 실패 시에도 프로세스는 종료되지 않고 다음 cycle로 진행

## 3) Shutdown Contract
- SIGTERM/SIGINT 수신 시:
  - 수신 로그를 남긴다
  - 현재 cycle 안전 종료 후 루프를 종료한다
  - 종료 코드 `0` 또는 정의된 정상 종료 코드를 반환한다

## 4) Logging Contract
- 최소 로그 필드:
  - `mode` (`once`/`loop`)
  - `run_id`
  - `started_at`, `finished_at`
  - `created_count`, `updated_count`, `failed_count`
  - `next_run_at` (loop 모드에서)

## 5) SLO Contract
- 주기 실행 간격 목표: 600초 ±30초
- 30분 관측 구간에서 최소 3회 cycle 수행
- 단일 cycle 실패 후 다음 cycle 실행 성공률 목표: 95% 이상
