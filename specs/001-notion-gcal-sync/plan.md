# Implementation Plan: Notion-GCal Todo Sync

**Branch**: `001-notion-gcal-sync` | **Date**: 2026-03-17 | **Spec**: `/Users/lukael/Develop/notion-gcal-slack/specs/001-notion-gcal-sync/spec.md`
**Input**: Feature specification from `/specs/001-notion-gcal-sync/spec.md`

## Summary

Notion Todo 데이터를 주기적으로 조회해 Google Calendar 이벤트를 생성/갱신하는
단방향 동기화 서비스를 구현한다. `Google ID` 기반 멱등 처리로 중복 생성을 방지하고,
항목 단위 실패 격리 및 다음 주기 자동 복구를 통해 운영 안정성을 확보한다.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: notion-client, google-api-python-client, google-auth-oauthlib, python-dateutil, pydantic-settings  
**Storage**: 파일 기반 상태/자격증명(`token.json`, `contact.json`), 원천 상태는 Notion Database  
**Testing**: pytest, pytest-cov, unittest.mock  
**Target Platform**: Docker 컨테이너 기반 Linux 서버(주기 실행)  
**Project Type**: 백엔드 동기화 워커(배치성 서비스)  
**Performance Goals**: 단일 실행 기준 동기화 대상 500건을 60초 이내 처리, 신규 생성 95% 1분 내 반영  
**Constraints**: all-day 이벤트 정책, 기본 timezone Asia/Seoul, Notion API rate limit 준수, 단방향 동기화만 지원  
**Scale/Scope**: 단일 Notion DB -> 단일 Google Calendar 동기화, 5분 주기 실행, 소규모 팀 운영

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- 코드 품질: 린팅 규칙/코드 스타일 준수 전략과 리뷰 계획이 정의되어 있는가?
- 테스트 기준: 단위 테스트(edge case 포함), 통합 테스트 범위, 코어 모듈 85% 커버리지
  달성 방법이 정의되어 있는가?
- 보안: 의존성 취약점 스캔, 기밀정보 관리 방식, OWASP Top 10 기반 점검 계획이
  포함되어 있는가?
- 문서 정비: 한국어 문서 업데이트 대상(`README`, 설정 절차, API 사양, 사용자 가이드)
  과 릴리스 동기화 계획이 정의되어 있는가?

결과(초기): PASS
- 코드 품질: `black` + `pylint`를 CI/로컬 게이트로 사용하고 PR 리뷰 체크리스트에 포함
- 테스트 기준: `pytest` 단위/통합 테스트와 `pytest-cov` 85% 이상 게이트 적용
- 보안: `.env` 기반 비밀 주입, `token.json`/`contact.json` 비커밋, 의존성 취약점 점검 절차 반영
- 문서 정비: 릴리스 시 README/설정/API/운영 가이드를 한국어 기준으로 동기화

결과(Phase 1 설계 후 재검증): PASS
- `data-model.md`: 상태 전이/검증 규칙 정의로 테스트 가능성 확보
- `contracts/sync-service-contract.md`: 보안/멱등성/오류 격리 계약 명시
- `quickstart.md`: 린트/테스트/커버리지/운영 실행 절차 명시

## Project Structure

### Documentation (this feature)

```text
specs/001-notion-gcal-sync/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── main.py
├── config.py
├── sync/
│   ├── notion_client.py
│   ├── calendar_client.py
│   ├── mapper.py
│   └── orchestrator.py
└── domain/
    ├── models.py
    └── validators.py

tests/
├── unit/
│   ├── test_mapper.py
│   ├── test_timezone.py
│   └── test_done_prefix.py
├── integration/
│   ├── test_sync_create_flow.py
│   ├── test_sync_update_flow.py
│   ├── test_retry_isolation.py
│   ├── test_rate_limit_recovery.py
│   ├── test_no_reverse_sync.py
│   ├── test_sync_latency.py
│   └── test_sync_performance.py
└── contract/
    └── test_sync_contract.py

ops/
├── Dockerfile
└── cron.sample
```

**Structure Decision**: 단일 Python 프로젝트 구조를 채택한다. API 서버가 아닌 주기 실행형
백엔드 워커이므로 `src/sync` 중심의 오케스트레이션 구조와 `tests/{unit,integration,contract}`
분리 구조를 사용한다.

## Complexity Tracking

헌장 위반 없음. 복잡성 예외 없음.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 없음 | N/A | N/A |
