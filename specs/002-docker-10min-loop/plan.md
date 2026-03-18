# Implementation Plan: Docker Persistent 10-Minute Scheduler

**Branch**: `002-docker-10min-loop` | **Date**: 2026-03-17 | **Spec**: `/Users/lukael/Develop/notion-gcal-slack/specs/002-docker-10min-loop/spec.md`
**Input**: Feature specification from `/specs/002-docker-10min-loop/spec.md`

## Summary

기존 1회 실행형 동기화 워커에 루프 실행 계층을 추가해, `docker run` 시 컨테이너가
지속 실행되며 10분 간격으로 동기화를 반복 수행하도록 확장한다. 단일 주기 실패는
프로세스 종료로 이어지지 않으며, 종료 신호 수신 시 안전 종료를 보장한다.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: pydantic-settings, notion-client, google-api-python-client, google-auth-oauthlib, python-dateutil  
**Storage**: 환경 변수(`.env`), 파일 자격증명(`token.json`, `contact.json`), 런타임 메모리 상태  
**Testing**: pytest, pytest-cov, unittest.mock  
**Target Platform**: Docker 컨테이너 기반 Linux 서버  
**Project Type**: 장기 실행형 백엔드 워커(주기 실행 루프 포함)  
**Performance Goals**: 주기 실행 간격 10분(±30초), 루프 실행 30분 기준 3회 이상 수행  
**Constraints**: 기존 `--once` 호환 유지, loop 기본 간격 600초, 실패 후 루프 지속, SIGTERM 안전 종료  
**Scale/Scope**: 단일 프로세스 루프 실행, 소규모 운영 환경, 외부 오케스트레이터 없이 단독 동작

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
- 코드 품질: 루프 계층을 `scheduler` 모듈로 분리하고 `black/pylint` 검증 유지
- 테스트 기준: 루프 간격, 실패 지속성, 종료 처리 통합 테스트 추가 예정
- 보안: 비밀정보는 기존과 동일하게 외부 파일/환경변수 주입 유지
- 문서 정비: README에 loop 모드 실행 및 운영 절차 한국어 갱신 예정

결과(Phase 1 설계 후 재검증): PASS
- `data-model.md`: 루프 상태/종료 상태 모델 정의 완료
- `contracts/runtime-loop-contract.md`: 실행/종료/로그/SLO 계약 정의 완료
- `quickstart.md`: loop/once 실행 절차와 검증 시나리오 문서화 완료

## Project Structure

### Documentation (this feature)

```text
specs/002-docker-10min-loop/
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
├── scheduler.py          # loop interval/signal handling
└── sync/
    ├── orchestrator.py
    ├── notion_client.py
    ├── calendar_client.py
    └── mapper.py

tests/
├── unit/
│   └── test_scheduler.py
├── contract/
│   └── test_runtime_loop_contract.py
└── integration/
    ├── test_loop_interval.py
    ├── test_loop_failure_continue.py
    └── test_signal_shutdown.py

ops/
├── Dockerfile
└── cron.sample
```

**Structure Decision**: 기존 단일 프로젝트를 유지하고, 스케줄링 책임을 `src/scheduler.py`
로 분리해 기존 동기화 모듈(`src/sync/*`)과 결합도를 낮춘다.

## Complexity Tracking

헌장 위반 없음. 복잡성 예외 없음.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 없음 | N/A | N/A |
