# Tasks: Docker Persistent 10-Minute Scheduler

**Input**: Design documents from `/specs/002-docker-10min-loop/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: 헌장에 따라 테스트는 REQUIRED이며, 루프 간격/실패 지속/종료 처리 검증을 포함한다.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: loop 모드 확장을 위한 공통 설정/운영 파일을 준비한다.

- [X] T001 Add loop-related env keys and defaults in `env.example`
- [X] T002 [P] Update Docker runtime command expectations in `ops/Dockerfile`
- [X] T003 [P] Add .dockerignore entries for runtime secret files in `.dockerignore`
- [X] T004 [P] Define scheduler runtime docs skeleton in `README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 루프 실행, 종료 신호, 실행 기록 모델 등 모든 스토리의 기반을 구축한다.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Extend settings model for loop mode options in `src/config.py`
- [X] T006 Add loop runtime domain records in `src/domain/models.py`
- [X] T007 Implement scheduler core loop and sleep policy in `src/scheduler.py`
- [X] T008 Implement signal handling utility for graceful shutdown in `src/scheduler.py`
- [X] T009 Refactor entrypoint mode selection (`once`/`loop`) in `src/main.py`
- [X] T010 [P] Add scheduler unit test scaffold in `tests/unit/test_scheduler.py`
- [X] T011 [P] Add loop integration fixture scaffold in `tests/integration/conftest_loop.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 컨테이너 상시 실행 + 10분 주기 자동 동기화 (Priority: P1) 🎯 MVP

**Goal**: 컨테이너가 종료되지 않고 10분 주기 loop로 동기화를 반복 수행한다.

**Independent Test**: 25분 실행 기준 최소 3회 cycle 로그가 기록되고 간격이 10분 ±30초 범위인지 검증.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T012 [P] [US1] Add loop interval unit tests in `tests/unit/test_scheduler.py`
- [X] T013 [P] [US1] Add integration test for repeated cycle execution in `tests/integration/test_loop_interval.py`
- [X] T014 [P] [US1] Add contract test for default loop mode behavior in `tests/contract/test_runtime_loop_contract.py`

### Implementation for User Story 1

- [X] T015 [US1] Implement default loop mode bootstrap in `src/main.py`
- [X] T016 [US1] Implement 600-second interval scheduling logic in `src/scheduler.py`
- [X] T017 [US1] Integrate one-cycle sync invocation inside scheduler in `src/scheduler.py`
- [X] T018 [US1] Ensure manual once mode remains functional in `src/main.py`

**Checkpoint**: User Story 1 is fully functional and independently testable

---

## Phase 4: User Story 2 - 주기 실행 상태 가시성 확보 (Priority: P2)

**Goal**: cycle 시작/종료/결과/다음 실행 대기 정보를 운영 로그로 확인 가능하게 한다.

**Independent Test**: 로그 출력에서 run_id, started_at, finished_at, next_run_at 필드 확인.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T019 [P] [US2] Add unit test for loop run record serialization in `tests/unit/test_scheduler.py`
- [X] T020 [P] [US2] Add integration test for cycle summary logging in `tests/integration/test_loop_logging.py`
- [X] T021 [P] [US2] Add contract test for log field set in `tests/contract/test_runtime_loop_contract.py`
- [X] T022 [P] [US2] Add integration test for drift warning log when interval exceeds threshold in `tests/integration/test_loop_drift_warning.py`

### Implementation for User Story 2

- [X] T023 [US2] Implement structured run start/end log output in `src/scheduler.py`
- [X] T024 [US2] Implement next run wait-time logging in `src/scheduler.py`
- [X] T025 [US2] Add mode/run_id metadata to loop logs in `src/scheduler.py`
- [X] T026 [US2] Implement drift threshold warning logging for interval outliers in `src/scheduler.py`

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: User Story 3 - 장애 복구와 안전 종료 (Priority: P3)

**Goal**: 단일 주기 실패 후 루프를 지속하고, 종료 신호 시 graceful shutdown을 수행한다.

**Independent Test**: 실패 유도 후 다음 cycle 재실행 확인 + SIGTERM 처리 후 30초 내 종료 확인.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T027 [P] [US3] Add integration test for failure-continue behavior in `tests/integration/test_loop_failure_continue.py`
- [X] T028 [P] [US3] Add integration test for signal shutdown behavior in `tests/integration/test_signal_shutdown.py`
- [X] T029 [P] [US3] Add unit test for shutdown state transitions in `tests/unit/test_scheduler.py`
- [X] T030 [P] [US3] Add integration test for failure-recovery success-rate measurement in `tests/integration/test_loop_recovery_rate.py`

### Implementation for User Story 3

- [X] T031 [US3] Implement cycle exception isolation and continue policy in `src/scheduler.py`
- [X] T032 [US3] Implement SIGTERM/SIGINT graceful shutdown flow in `src/scheduler.py`
- [X] T033 [US3] Implement shutdown timeout guard and final exit logging in `src/scheduler.py`
- [X] T034 [US3] Implement recovery-rate metric aggregation and logging in `src/scheduler.py`

**Checkpoint**: All user stories are independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 품질/보안/문서/SLO 검증을 마무리한다.

- [X] T035 [P] Raise and verify coverage gate (>=85%) for scheduler changes in `pyproject.toml` and `tests/`
- [X] T036 [P] Document loop mode runbook and troubleshooting in `README.md`
- [X] T037 Add OWASP Top 10 notes for long-running container operation in `README.md`
- [X] T038 Add quickstart verification updates for loop mode in `specs/002-docker-10min-loop/quickstart.md`
- [X] T039 Add latency/drift and recovery-rate verification scenario docs in `README.md`
- [X] T040 Run final lint/format/test and capture output summary in `README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on desired user stories completion

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational; no dependencies on other stories
- **User Story 2 (P2)**: Starts after Foundational; uses US1 scheduler execution path
- **User Story 3 (P3)**: Starts after Foundational; validates resilience on top of US1/US2

### Within Each User Story

- Tests first (unit/integration/contract), failing state 확인 후 구현
- Core scheduler logic before entrypoint wiring
- Logging and shutdown hooks after cycle execution is stable
- Story checkpoint validation 후 다음 우선순위로 이동

### Parallel Opportunities

- Setup: T002, T003, T004 parallel 가능
- Foundational: T010, T011 parallel 가능
- US1: T012, T013, T014 parallel 가능
- US2: T019, T020, T021, T022 parallel 가능
- US3: T027, T028, T029, T030 parallel 가능
- Polish: T035, T036 parallel 가능

---

## Parallel Example: User Story 1

```bash
Task: "T012 [US1] Add loop interval unit tests in tests/unit/test_scheduler.py"
Task: "T013 [US1] Add integration test for repeated cycle execution in tests/integration/test_loop_interval.py"
Task: "T014 [US1] Add contract test for default loop mode behavior in tests/contract/test_runtime_loop_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate container stays alive and cycles every 10 minutes
5. Demo MVP

### Incremental Delivery

1. Setup + Foundational 완료
2. US1 추가 후 주기 실행 검증
3. US2 추가 후 로그 가시성 검증
4. US3 추가 후 실패 지속/안전 종료 검증
5. Polish에서 문서/보안/커버리지 게이트 마감

### Parallel Team Strategy

1. 팀 공통으로 Phase 1-2 완료
2. 이후 분담:
   - 개발자 A: scheduler core + US1
   - 개발자 B: logging + US2
   - 개발자 C: signal/shutdown + US3

---

## Notes

- 모든 태스크는 체크박스 + Task ID + 파일 경로를 포함한다.
- 사용자 스토리 단계 태스크는 반드시 `[USx]` 라벨을 포함한다.
- 테스트 태스크는 각 사용자 스토리에서 구현 태스크보다 먼저 수행한다.
- 헌장 기준(코드 품질/테스트/보안/문서)을 Polish 단계에서 최종 확인한다.
