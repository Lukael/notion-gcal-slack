# Notion-GCal Sync

Notion Todo를 Google Calendar 일정으로 동기화하는 Python 백엔드 워커입니다.

## 개요

- 동기화 방향: **Notion -> Google Calendar** (역방향 미지원)
- 동기화 기준: Notion 항목 중 `Due Date`가 있는 항목
- 멱등성 기준: `Google ID` 비어있음=create, 존재=update
- 실행 모델: 기본 loop 모드(10분 주기) + 필요 시 1회 실행(`--once`)

## 설정

필수 환경 변수:

- `NOTION_TOKEN`
- `NOTION_DATABASE_ID`
- `GCAL_CALENDAR_ID` (기본값: `primary`)
- `TIMEZONE` (기본값: `Asia/Seoul`)

예시:

```bash
NOTION_TOKEN=secret_xxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxx
GCAL_CALENDAR_ID=primary
TIMEZONE=Asia/Seoul
CONTACT_FILE=contact.json
TOKEN_FILE=token.json
CREDENTIALS_FILE=credentials.json
DRY_RUN=false
PAGE_SIZE=100
MAX_RETRIES=3
RETRY_BASE_SECONDS=0.3
SYNC_INTERVAL_SECONDS=600
SHUTDOWN_TIMEOUT_SECONDS=30
DRIFT_WARNING_SECONDS=30
```

## 실행 방법

```bash
poetry install
poetry run python -m src.main
```

단일 실행 모드:

```bash
poetry run python -m src.main --once
```

## Docker 실행

```bash
docker build -t notion-gcal-sync -f ops/Dockerfile .
docker run --rm --env-file .env \
  -v "$PWD/token.json:/app/token.json" \
  -v "$PWD/contact.json:/app/contact.json" \
  notion-gcal-sync
```

cron 샘플은 `ops/cron.sample` 참고.

## Loop 운영 로그 필드

- `cycle_started`: `run_id`, `started_at`
- `cycle_finished`: `run_id`, `started_at`, `finished_at`, `next_run_at`, `created_count`, `updated_count`, `failed_count`
- `drift_warning`: `drift_seconds`, `threshold_seconds`
- `loop_stopped`: `cycles`, `failures`, `successful_after_failure`, `recovery_rate`, `safe_to_exit`

## 품질 게이트

- 포맷: `poetry run black --check src tests`
- 린트: `poetry run pylint src`
- 테스트: `poetry run pytest`
- 커버리지: `pytest-cov`로 `src` 기준 최소 85%

## 의존성 취약점 점검

- 최소 주기: **월 1회 + 릴리스 전 1회**
- 권장 명령:

```bash
poetry export -f requirements.txt --without-hashes -o /tmp/requirements.txt
pip-audit -r /tmp/requirements.txt
```

- 발견된 취약점은 CVSS와 영향 범위를 기록 후 패치 또는 예외 승인 처리.

## OWASP Top 10 운영 체크리스트

- A01 Broken Access Control: 토큰/권한 범위 최소화 확인
- A02 Cryptographic Failures: 비밀정보 평문 커밋 금지, 저장소 외부 관리
- A03 Injection: 외부 입력 로깅/전달 시 검증
- A05 Security Misconfiguration: Docker 이미지/환경변수 권한 최소화
- A06 Vulnerable and Outdated Components: 월 1회 + 릴리스 전 `pip-audit` 실행
- A09 Security Logging and Monitoring Failures: 실패 로그 필드 표준화

## 운영 Runbook (한국어)

1. 장애 확인: 실패 로그의 `notion_page_id`, `operation`, `error_message` 확인
2. 외부 API 장애: 다음 주기 자동 재시도 확인
3. 인증 문제: `token.json` 갱신 후 재실행
4. 매핑 문제: `contact.json` 수정 후 재실행
5. 복구 확인: `loop_stopped` 로그의 `recovery_rate`와 `successful_after_failure` 확인

## 성능/지연 검증

- 지연 SLO: 생성/수정 반영 1분 이내
- 처리량 목표: 500건 60초 이내
- 드리프트 경고: 주기 지연이 `DRIFT_WARNING_SECONDS`를 넘으면 경고 로그 출력
- 장애 복구율: 실패 발생 후 다음 주기 성공 비율(`recovery_rate`) 기록
- 관련 테스트:
  - `tests/integration/test_sync_latency.py`
  - `tests/integration/test_sync_performance.py`

## 최종 검증 기록

아래 명령 결과를 릴리스 전 갱신:

```bash
poetry run black --check src tests
poetry run pylint src
poetry run pytest
```

최근 로컬 검증 결과(2026-03-17):

- `poetry run black --check src tests` -> PASS
- `poetry run pylint src` -> PASS (10.00/10)
- `poetry run pytest` -> PASS (34 passed, coverage 90.29%)