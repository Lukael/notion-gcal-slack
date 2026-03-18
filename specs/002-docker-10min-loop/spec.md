# Feature Specification: Docker Persistent 10-Minute Scheduler

**Feature Branch**: `002-docker-10min-loop`  
**Created**: 2026-03-17  
**Status**: Draft  
**Input**: User description: "docker run을 하면 docker는 지속적으로 켜져있고 10분마다 코드가 동작하도록 해줘"

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

### User Story 1 - 컨테이너 상시 실행 + 10분 주기 자동 동기화 (Priority: P1)

운영자는 `docker run` 한 번으로 컨테이너가 계속 실행되고, Notion -> Google Calendar
동기화가 10분 간격으로 자동 반복되기를 원한다.

**Why this priority**: 수동 재실행 없이 자동 반복 실행이 이 기능의 핵심 요구사항이다.

**Independent Test**: 컨테이너를 25분 이상 실행해 최소 3회 실행 로그가 기록되고, 각 실행 간격이
10분(허용 오차 ±30초)인지 확인하면 독립 검증 가능하다.

**Acceptance Scenarios**:

1. **Given** 유효한 환경 변수와 인증 파일이 준비된 상태에서,
   **When** 사용자가 `docker run`을 실행하면,
   **Then** 컨테이너는 종료되지 않고 백그라운드 루프를 유지한다.
2. **Given** 컨테이너가 실행 중일 때,
   **When** 10분이 경과할 때마다,
   **Then** 동기화 코드가 자동으로 1회 실행된다.

---

### User Story 2 - 주기 실행 상태 가시성 확보 (Priority: P2)

운영자는 주기 실행 여부를 로그로 즉시 확인하고, 마지막 실행 시간/다음 실행 예정 시간을 파악하길 원한다.

**Why this priority**: 자동 실행이 동작하더라도 운영자가 상태를 확인할 수 없으면 장애 대응이 어렵다.

**Independent Test**: 컨테이너 로그에서 실행 시작/종료 타임스탬프와 다음 실행 대기 로그를 확인하면
독립 검증 가능하다.

**Acceptance Scenarios**:

1. **Given** 주기 실행 루프가 활성화된 상태에서,
   **When** 동기화가 완료되면,
   **Then** 실행 결과 요약과 다음 실행 예정 대기 정보가 로그에 기록된다.

---

### User Story 3 - 장애 복구와 안전 종료 (Priority: P3)

운영자는 단일 실행 실패가 컨테이너 종료로 이어지지 않기를 원하며, 컨테이너 종료 신호 시 안전하게 중단되길 원한다.

**Why this priority**: 장시간 실행 워커는 실패 내성이 없으면 운영 안정성이 떨어진다.

**Independent Test**: 한 주기에서 실패를 유도해도 다음 주기가 계속 수행되고, 종료 신호 시 정상 종료 로그가
남는지 확인하면 독립 검증 가능하다.

**Acceptance Scenarios**:

1. **Given** 특정 주기 실행이 실패하더라도,
   **When** 다음 10분 주기가 도래하면,
   **Then** 동기화 루프는 계속 실행된다.
2. **Given** 컨테이너가 실행 중일 때,
   **When** 종료 신호를 수신하면,
   **Then** 현재 실행 상태를 정리하고 정상 종료한다.

---

### Edge Cases

- 시스템 시간이 변경되거나 지연이 누적될 때도 10분 기준 실행 간격이 크게 드리프트되지 않아야 한다.
- 한 주기 실행 시간이 10분을 초과하면 다음 실행을 즉시 시작할지 건너뛸지 정책을 일관되게 적용해야 한다.
- 인증 토큰 만료로 단일 실행이 실패해도 프로세스 자체는 종료되지 않아야 한다.
- 컨테이너 재시작 후에도 동일 설정으로 주기 루프가 자동 재개되어야 한다.
- 종료 신호(SIGTERM) 수신 시 무한 대기 없이 제한 시간 내 종료해야 한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 컨테이너 시작 후 단일 실행이 아닌 지속 실행 루프를 MUST 시작한다.
- **FR-002**: 시스템은 기본 600초(10분) 주기로 동기화를 MUST 반복 실행하며,
  주기 오차 정책(±30초)을 적용해 운영 기준과 일치해야 한다.
- **FR-003**: 시스템은 각 주기 실행 시작/종료 시각과 결과 요약을 MUST 로그로 기록한다.
- **FR-004**: 시스템은 단일 주기 실패가 발생해도 다음 주기 실행을 MUST 지속한다.
- **FR-005**: 시스템은 종료 신호를 수신하면 루프를 안전하게 종료하고 종료 상태를 MUST 기록한다.
- **FR-006**: 시스템은 기존 `--once` 실행 모드를 MUST 유지해 수동 단일 실행을 지원한다.
- **FR-007**: 시스템은 기본 실행 모드에서 루프 모드를 사용하고, 실행 간격(기본 600초)을 MUST 설정 가능하게 한다.
- **FR-008**: 시스템은 컨테이너 환경에서 추가 스케줄러 없이 자체적으로 주기 실행을 MUST 수행한다.

### Non-Functional Requirements

- **NFR-TEST-001**: 루프 스케줄링/에러 지속성/종료 처리에 대한 단위 및 통합 테스트를 MUST 제공해야 한다.
- **NFR-TEST-002**: 코어 모듈 테스트 커버리지는 85% 이상을 MUST 유지해야 한다.
- **NFR-REL-001**: 24시간 연속 실행 기준으로 메모리 누수나 반복 크래시 없이 안정 동작해야 한다.
- **NFR-REL-002**: 10분 주기 오차는 정상 환경에서 ±30초 이내를 SHOULD 만족해야 하며, 초과 시 로그 경고를 남겨야 한다.
- **NFR-SEC-001**: 토큰/자격증명은 코드베이스 외부 주입 원칙을 MUST 준수해야 한다.
- **NFR-DOC-001**: README 및 운영 가이드는 루프 모드 실행법과 종료 정책을 한국어로 MUST 문서화해야 한다.

### Key Entities *(include if feature involves data)*

- **LoopConfig**: 실행 간격, 모드(`once`/`loop`), 종료 대기 시간 등 런타임 설정값.
- **LoopRunRecord**: 각 주기 실행의 시작 시각, 종료 시각, 성공/실패 상태, 요약 통계.
- **ShutdownState**: 종료 신호 수신 여부와 현재 실행 종료 준비 상태.

## Assumptions

- 컨테이너는 장기 실행 가능한 환경에서 구동되며 외부 오케스트레이터가 강제 종료를 반복하지 않는다.
- 10분 주기 요구는 wall-clock 기준이며 초 단위 정밀 스케줄러 수준은 요구하지 않는다.
- 기존 동기화 로직은 재사용하고 스케줄링 레이어만 확장하는 범위로 본다.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 컨테이너 1회 기동 후 30분 동안 최소 3회 이상 주기 실행이 자동 수행된다.
- **SC-002**: 주기 실행 간격은 90% 이상이 10분 ±30초 범위를 만족한다.
- **SC-003**: 개별 주기 실패가 발생해도 다음 주기 실행 성공률이 95% 이상 유지된다.
- **SC-004**: 종료 신호 수신 후 30초 이내 정상 종료 비율이 100%를 달성한다.
- **SC-005**: 변경 모듈 테스트 커버리지는 릴리스 시점 85% 이상을 유지한다.
- **SC-006**: 루프 모드 운영 문서 최신화 완료율 100%를 달성한다.
