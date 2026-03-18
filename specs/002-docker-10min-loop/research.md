# Research: Docker Persistent 10-Minute Scheduler

## Decision 1: 컨테이너 내부 루프 스케줄러 채택
- **Decision**: `docker run` 시 단일 실행이 아니라 내부 루프를 시작하고, 매 주기마다 동기화를 호출한다.
- **Rationale**: 사용자 요구(컨테이너 상시 실행 + 10분 반복)를 가장 직접적으로 충족한다.
- **Alternatives considered**:
  - 외부 cron만 사용: 컨테이너가 종료되는 1회 실행 모델이라 요구와 불일치
  - host-level systemd timer: 운영 의존성이 커지고 “docker run 한 번” 요구에서 벗어남

## Decision 2: 간격 제어는 monotonic 기반 sleep 계산
- **Decision**: 각 사이클 완료 시점 기준으로 다음 실행 절대 시각을 계산해 drift를 줄인다.
- **Rationale**: 단순 `sleep(600)` 반복보다 실행시간 변동 시 누적 오차를 줄일 수 있다.
- **Alternatives considered**:
  - 고정 sleep: 실행 시간이 길어질수록 실제 주기가 밀림

## Decision 3: 실패 시 루프 지속
- **Decision**: 개별 주기 예외는 로그 기록 후 다음 주기로 진행한다.
- **Rationale**: 장기 실행 워커의 가용성을 보장하고 일시 장애에 강하다.
- **Alternatives considered**:
  - 예외 즉시 종료: 복구 자동화 요구(FR-004) 미충족

## Decision 4: 종료 신호 처리
- **Decision**: SIGTERM/SIGINT 수신 시 루프 플래그를 내려 다음 안전 지점에서 종료한다.
- **Rationale**: 컨테이너 종료 시 graceful shutdown을 보장해 데이터 정합성/로그 일관성을 지킨다.
- **Alternatives considered**:
  - 강제 종료 의존: 종료 상태 기록 누락 및 비정상 종료 가능성 증가

## Decision 5: 실행 모드 호환성
- **Decision**: 기존 `--once` 모드는 유지하고, 기본 실행은 loop 모드로 전환한다.
- **Rationale**: 기존 운영/디버깅 시나리오와 호환성을 유지하면서 신규 요구를 충족한다.
- **Alternatives considered**:
  - once 제거: 수동 점검/테스트 워크플로 저해

## Decision 6: 로그 표준화
- **Decision**: 루프 시작/종료/실패/다음 실행 대기 시간을 구조화된 키 형태로 로그 남긴다.
- **Rationale**: 운영 가시성과 분석 용이성을 확보한다.
- **Alternatives considered**:
  - 단순 프린트 로그: 상태 추적 및 장애 분석 어려움
