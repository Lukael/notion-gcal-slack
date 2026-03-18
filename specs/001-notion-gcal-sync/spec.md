# Feature Specification: Notion-GCal Todo Sync

**Feature Branch**: `001-notion-gcal-sync`  
**Created**: 2026-03-17  
**Status**: Draft  
**Input**: User description: "Notion Todo를 Google Calendar 일정으로 자동 동기화하는 백엔드 서비스"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - 신규 Todo 일정 자동 생성 (Priority: P1)

운영자는 Notion 데이터베이스에 일정 대상 Todo를 등록하면, 별도 수동 입력 없이 같은 내용이
Google Calendar에 자동 생성되기를 원한다.

**Why this priority**: 수동 일정 입력 제거와 누락 방지가 서비스의 핵심 가치이며, 최소 기능(MVP)이다.

**Independent Test**: 동기화 조건을 만족하는 신규 Todo 1건을 등록한 뒤, 1분 내 Calendar 이벤트가
1건 생성되고 Notion 항목에 이벤트 식별자가 기록되는지 확인하면 독립 검증 가능하다.

**Acceptance Scenarios**:

1. **Given** 동기화 대상 조건을 만족하고 이벤트 식별자가 없는 Todo가 존재할 때,
   **When** 동기화 주기가 실행되면, **Then** Calendar 이벤트가 생성되고 식별자가 저장된다.
2. **Given** 여러 페이지로 분할된 Todo 목록이 존재할 때,
   **When** 동기화 주기가 실행되면, **Then** pagination을 끝까지 처리해 대상 항목을 모두 반영한다.

---

### User Story 2 - 기존 일정 자동 갱신 및 상태 반영 (Priority: P2)

운영자는 Notion Todo가 수정되거나 완료 상태가 되면, 기존 Calendar 일정도 자동 갱신되어
일정 정보의 일관성이 유지되기를 원한다.

**Why this priority**: 생성 이후 변경사항이 반영되지 않으면 일정 신뢰도가 떨어져 운영 목적을 달성할 수 없다.

**Independent Test**: 기존 이벤트 식별자가 있는 Todo의 제목/날짜/상태를 수정하고 동기화 실행 시,
기존 이벤트가 갱신되며 완료 상태는 제목 접두 표시가 적용되는지 확인하면 독립 검증 가능하다.

**Acceptance Scenarios**:

1. **Given** 이벤트 식별자가 저장된 Todo가 있고 제목 또는 날짜가 변경되었을 때,
   **When** 동기화 주기가 실행되면, **Then** 기존 Calendar 이벤트가 업데이트된다.
2. **Given** 이벤트 식별자가 저장된 Todo의 상태가 Done일 때,
   **When** 동기화 주기가 실행되면, **Then** 이벤트 제목 앞에 완료 표시가 반영된다.

---

### User Story 3 - 안정적 운영 및 장애 복구 (Priority: P3)

운영자는 외부 API 오류나 일부 항목 실패가 발생하더라도 전체 동기화가 중단되지 않고, 다음 주기에서
자동 복구되기를 원한다.

**Why this priority**: 정기 동기화 서비스는 안정성이 핵심이며, 실패 격리와 재시도 가능성이 운영 효율을 좌우한다.

**Independent Test**: 일부 항목에서 외부 API 오류를 유도한 뒤 동기화를 실행해도 다른 항목은 계속 처리되고,
실패 항목이 다음 실행에서 재처리되는지 확인하면 독립 검증 가능하다.

**Acceptance Scenarios**:

1. **Given** 동기화 대상 항목 중 일부 요청이 실패할 때,
   **When** 동기화 주기가 실행되면, **Then** 실패는 항목 단위로 격리되고 다른 항목은 계속 처리된다.
2. **Given** 이전 실행에서 실패한 항목이 존재할 때,
   **When** 다음 동기화 주기가 실행되면, **Then** 해당 항목이 자동 재시도되어 복구될 수 있다.

---

### Edge Cases

- Due Date가 없거나 형식이 유효하지 않은 항목은 동기화 대상에서 제외하고 경고 로그를 남긴다.
- timezone이 없는 datetime은 Asia/Seoul 기준으로 해석한다.
- 동일 Todo가 반복 조회되어도 이미 식별자가 있으면 중복 이벤트를 생성하지 않는다.
- contact 매핑에 없는 참여자 이름은 해당 참여자만 제외하고 이벤트 생성/갱신은 계속한다.
- Notion 또는 Google API 일시 오류 발생 시 전체 작업을 중단하지 않고 항목 단위 실패로 기록한다.
- Notion API rate limit 징후가 있으면 다음 주기에 재시도할 수 있도록 실패 사유를 남긴다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 Notion 데이터베이스에서 Due Date가 있는 Todo 항목만 동기화 대상으로 MUST 선별한다.
- **FR-002**: 시스템은 페이지네이션을 처리하여 조회 가능한 모든 대상 항목을 MUST 수집한다.
- **FR-003**: 시스템은 이벤트 식별자가 비어 있는 대상 항목에 대해 Calendar 이벤트를 MUST 생성한다.
- **FR-004**: 시스템은 생성된 이벤트의 식별자를 원본 Todo 항목에 MUST 저장한다.
- **FR-005**: 시스템은 이벤트 식별자가 존재하는 항목 변경 시 기존 Calendar 이벤트를 MUST 갱신한다.
- **FR-006**: 시스템은 상태가 Done인 항목의 이벤트 제목에 완료 표시를 MUST 반영한다.
- **FR-007**: 시스템은 모든 동기화 이벤트를 all-day 일정으로 MUST 생성 또는 유지한다.
- **FR-008**: 시스템은 참여자 값이 존재하면 사전 정의된 이름-이메일 매핑을 조회해 참석자를 MUST 반영한다.
- **FR-009**: 시스템은 구성된 주기 실행 모델에 따라 사용자 개입 없이 동기화를 MUST 반복 수행한다.
- **FR-010**: 시스템은 항목 단위 오류 격리, 로그 기록, 다음 주기 재시도를 MUST 지원한다.
- **FR-011**: 시스템은 양방향 동기화 없이 Notion -> Calendar 단방향 동기화만 MUST 제공한다.
- **FR-012**: 시스템은 중복 생성 방지를 위해 Todo별 이벤트 식별자 기반 상태 관리를 MUST 수행한다.

### Non-Functional Requirements

- **NFR-TEST-001**: 변경 범위 기능별 단위 테스트는 edge case를 포함해 MUST 정의되어야 한다.
- **NFR-TEST-002**: 생성/갱신/재시도 핵심 플로우에 대한 통합 테스트 시나리오는 MUST 정의되어야 한다.
- **NFR-TEST-003**: 코어 모듈 테스트 커버리지는 최소 85% 이상을 MUST 유지해야 한다.
- **NFR-SEC-001**: 인증 토큰 및 민감 구성값은 코드 저장소 외부에서 안전하게 관리되어야 하며,
  평문 커밋을 MUST 금지한다.
- **NFR-SEC-002**: 의존성 취약점 점검 주기와 대응 정책은 릴리스 프로세스에 MUST 포함되어야 한다.
- **NFR-SEC-003**: OWASP Top 10 기준의 위협 점검 항목을 운영 체크리스트에 MUST 포함해야 한다.
- **NFR-REL-001**: 서비스는 개별 항목 실패가 전체 동기화 실패로 확장되지 않도록 MUST 설계되어야 한다.
- **NFR-REL-002**: 기본 시간대는 Asia/Seoul이며 누락 시간대 입력에 대해 일관된 fallback을 MUST 적용한다.
- **NFR-DOC-001**: 운영/개발 문서는 한국어를 기본으로 유지하고 릴리스 시점 최신 상태를 MUST 보장한다.

### Key Entities *(include if feature involves data)*

- **NotionTask**: Notion의 원본 Todo 항목. 주요 속성은 제목, 예정일, 상태, 참여자, 이벤트 식별자.
- **CalendarEventLink**: Todo와 Calendar 이벤트의 매핑 상태. 중복 생성 방지와 업데이트 대상 식별에 사용.
- **SyncRun**: 1회 동기화 실행 단위. 실행 시간, 처리 건수, 실패 건수, 재시도 대상 메타데이터를 포함.
- **ContactDirectory**: 참여자 이름과 이메일의 매핑 정보. 참석자 변환 기준 데이터.

## Assumptions

- 동기화 대상 Notion 데이터베이스는 서비스 접근 권한이 사전에 승인되어 있다.
- 일정은 all-day 이벤트 정책을 기본으로 하며 시간 단위 정밀 스케줄링은 이번 범위에서 제외한다.
- 주기 실행은 운영 환경 스케줄러(예: cron 또는 동등 기능)로 보장된다.
- 단방향 동기화 정책(Notion -> Calendar)은 비즈니스 범위로 확정되어 있다.
- 참여자 매핑 데이터는 운영자가 유지하며 미매핑 사용자는 경고 후 제외된다.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 신규 Todo 동기화 대상 항목의 95% 이상이 생성 후 1분 내 Calendar에 반영된다.
- **SC-002**: 이벤트 식별자가 있는 Todo 수정 건의 95% 이상이 다음 동기화 주기 내 반영된다.
- **SC-003**: 중복 이벤트 생성률은 월간 총 동기화 건수 대비 0.1% 이하를 유지한다.
- **SC-004**: 일시적 외부 API 오류 발생 시, 실패 항목의 90% 이상이 다음 실행에서 자동 복구된다.
- **SC-005**: 코어 모듈 테스트 커버리지는 릴리스 기준 85% 이상을 유지한다.
- **SC-006**: 릴리스 시점에 README/설정/API/사용자 가이드 문서 최신화 완료율 100%를 달성한다.
