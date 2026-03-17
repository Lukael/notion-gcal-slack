# Tasks: Notion-GCal Todo Sync

**Input**: Design documents from `/specs/001-notion-gcal-sync/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: 헌장에 따라 테스트는 REQUIRED이며, 각 사용자 스토리에 대해 단위(edge case 포함) 및 통합 테스트를 포함한다.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 프로젝트 기본 골격, 의존성, 품질 도구를 준비한다.

- [X] T001 Initialize Poetry project metadata and dependencies in `pyproject.toml`
- [X] T002 Create environment sample and secrets policy in `env.example` and `.gitignore`
- [X] T003 [P] Configure formatting/linting rules for Python in `pyproject.toml`
- [X] T004 [P] Create Docker runtime skeleton in `ops/Dockerfile`
- [X] T005 [P] Add scheduler sample configuration in `ops/cron.sample`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 모든 사용자 스토리가 공통으로 사용하는 도메인/클라이언트/오케스트레이션 기반을 구축한다.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Implement settings loader and required env validation in `src/config.py`
- [X] T007 Create domain models and validation helpers in `src/domain/models.py` and `src/domain/validators.py`
- [X] T008 Implement Notion query client with pagination support in `src/sync/notion_client.py`
- [X] T009 Implement Google Calendar client wrapper (create/patch) in `src/sync/calendar_client.py`
- [X] T010 Implement mapping logic (all-day, done prefix, attendees) in `src/sync/mapper.py`
- [X] T011 Implement sync orchestrator skeleton with item-level isolation in `src/sync/orchestrator.py`
- [X] T012 Wire CLI entrypoint and one-shot execution flow in `src/main.py`
- [X] T013 [P] Add contract baseline test scaffold in `tests/contract/test_sync_contract.py`
- [X] T014 [P] Add shared integration test fixtures in `tests/integration/conftest.py`
- [X] T015 Implement Notion API rate-limit backoff/retry policy in `src/sync/notion_client.py`
- [X] T016 [P] Add integration test for Notion rate-limit recovery in `tests/integration/test_rate_limit_recovery.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 신규 Todo 일정 자동 생성 (Priority: P1) 🎯 MVP

**Goal**: `Google ID`가 없는 동기화 대상 Todo를 Calendar 이벤트로 생성하고 Notion에 이벤트 ID를 저장한다.

**Independent Test**: 신규 대상 Todo를 준비한 뒤 1회 실행 시 이벤트 생성 + Notion `Google ID` 저장이 완료되면 합격.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T017 [P] [US1] Add contract test for create-path I/O in `tests/contract/test_sync_contract.py`
- [X] T018 [P] [US1] Add integration test for new event creation flow in `tests/integration/test_sync_create_flow.py`
- [X] T019 [P] [US1] Add unit tests for create mapping edge cases in `tests/unit/test_mapper.py`

### Implementation for User Story 1

- [X] T020 [US1] Implement create candidate filtering (Due Date exists + no Google ID) in `src/sync/orchestrator.py`
- [X] T021 [US1] Implement create payload mapping and all-day conversion in `src/sync/mapper.py`
- [X] T022 [US1] Implement calendar event create call handling in `src/sync/calendar_client.py`
- [X] T023 [US1] Implement write-back of created event ID to Notion in `src/sync/notion_client.py`
- [X] T024 [US1] Integrate create flow in run pipeline and summary counters in `src/sync/orchestrator.py`

**Checkpoint**: User Story 1 is fully functional and independently testable

---

## Phase 4: User Story 2 - 기존 일정 자동 갱신 및 상태 반영 (Priority: P2)

**Goal**: `Google ID`가 있는 항목의 변경사항을 patch 업데이트하고 Done 상태를 제목에 반영한다.

**Independent Test**: 기존 이벤트가 연결된 Todo를 수정 후 실행 시 동일 이벤트가 갱신되고 Done 접두가 반영되면 합격.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T025 [P] [US2] Add contract test for update-path I/O in `tests/contract/test_sync_contract.py`
- [X] T026 [P] [US2] Add integration test for update flow in `tests/integration/test_sync_update_flow.py`
- [X] T027 [P] [US2] Add unit test for done-prefix rendering in `tests/unit/test_done_prefix.py`

### Implementation for User Story 2

- [X] T028 [US2] Implement update candidate selection (Google ID exists) in `src/sync/orchestrator.py`
- [X] T029 [US2] Implement patch payload generation with done-prefix rule in `src/sync/mapper.py`
- [X] T030 [US2] Implement calendar patch update execution in `src/sync/calendar_client.py`
- [X] T031 [US2] Integrate update branch metrics/logging into sync pipeline in `src/sync/orchestrator.py`

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: User Story 3 - 안정적 운영 및 장애 복구 (Priority: P3)

**Goal**: API 오류와 매핑 오류를 항목 단위로 격리하고 다음 실행에서 재시도 가능한 운영 동작을 제공한다.

**Independent Test**: 일부 항목 실패를 유도해도 실행이 지속되고, 수정 후 다음 실행에서 복구되면 합격.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T032 [P] [US3] Add contract test for error record schema in `tests/contract/test_sync_contract.py`
- [X] T033 [P] [US3] Add integration test for failure isolation and retry in `tests/integration/test_retry_isolation.py`
- [X] T034 [P] [US3] Add unit tests for timezone fallback and attendee mapping failures in `tests/unit/test_timezone.py`
- [X] T035 [P] [US3] Add integration test to assert no Calendar-to-Notion reverse sync behavior in `tests/integration/test_no_reverse_sync.py`

### Implementation for User Story 3

- [X] T036 [US3] Implement per-item exception boundary and retry eligibility tagging in `src/sync/orchestrator.py`
- [X] T037 [US3] Implement timezone fallback handling (Asia/Seoul default) in `src/sync/mapper.py`
- [X] T038 [US3] Implement attendee mapping fallback when contact lookup fails in `src/sync/mapper.py`
- [X] T039 [US3] Implement structured failure logging fields in `src/sync/orchestrator.py`

**Checkpoint**: All user stories are independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 품질, 보안, 문서, 배포 운영 기준을 최종 정리한다.

- [X] T040 [P] Raise and verify coverage gate (>=85%) in `pyproject.toml` and `tests/`
- [X] T041 [P] Add dependency vulnerability check task to workflow docs in `README.md`
- [X] T042 Add OWASP Top 10 security checklist section in `README.md`
- [X] T043 Add Korean runbook for setup/execution/troubleshooting in `README.md`
- [X] T044 Add latency SLO verification scenario (create/update <= 1 minute) in `tests/integration/test_sync_latency.py`
- [X] T045 Add performance validation scenario (500 items <= 60s) and report template in `tests/integration/test_sync_performance.py` and `README.md`
- [X] T046 Validate quickstart flow and update discrepancies in `specs/001-notion-gcal-sync/quickstart.md`
- [X] T047 Run final lint/format/test commands and record results in `README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on desired user stories completion

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational; no dependency on other stories
- **User Story 2 (P2)**: Starts after Foundational; reuses US1 entities/flows but independently testable
- **User Story 3 (P3)**: Starts after Foundational; validates resilience on top of US1/US2 behavior

### Within Each User Story

- Contract/integration/unit tests first, failing state 확인 후 구현
- Mapper/domain logic before orchestrator branch integration
- Client call handling before end-to-end pipeline wiring
- Story checkpoint validation 후 다음 우선순위로 이동

### Parallel Opportunities

- Setup: T003, T004, T005 parallel 가능
- Foundational: T013, T014, T016 parallel 가능
- US1: T017, T018, T019 parallel 가능
- US2: T025, T026, T027 parallel 가능
- US3: T032, T033, T034, T035 parallel 가능
- Polish: T040, T041 parallel 가능

---

## Parallel Example: User Story 1

```bash
Task: "T017 [US1] Add contract test for create-path I/O in tests/contract/test_sync_contract.py"
Task: "T018 [US1] Add integration test for new event creation flow in tests/integration/test_sync_create_flow.py"
Task: "T019 [US1] Add unit tests for create mapping edge cases in tests/unit/test_mapper.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate create flow end-to-end
5. Demo/deploy MVP

### Incremental Delivery

1. Setup + Foundational 완료
2. US1 추가 후 독립 검증
3. US2 추가 후 독립 검증
4. US3 추가 후 복구 시나리오 검증
5. Polish 단계에서 보안/문서/커버리지 게이트 마감

### Parallel Team Strategy

1. 공동으로 Phase 1-2 완료
2. 이후 담당 분리:
   - 개발자 A: US1 create path
   - 개발자 B: US2 update path
   - 개발자 C: US3 resilience path

---

## Notes

- 모든 태스크는 체크박스 + Task ID + 파일 경로를 포함한다.
- 사용자 스토리 단계 태스크는 반드시 `[USx]` 라벨을 포함한다.
- 테스트 태스크는 각 사용자 스토리에서 구현 태스크보다 먼저 수행한다.
- 헌장 기준(코드 품질/테스트/보안/문서)을 Polish에서 최종 게이트로 재확인한다.
