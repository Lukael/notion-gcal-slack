# Research: Notion-GCal Todo Sync

## Decision 1: 동기화 실행 모델은 외부 스케줄러 기반 주기 실행
- **Decision**: 애플리케이션은 1회 동기화 실행 단위로 구현하고, 주기성은 cron/systemd가 담당한다.
- **Rationale**: 장애 복구, 배포 롤백, 로그 추적이 단순하며 컨테이너 환경에서 운영 표준에 부합한다.
- **Alternatives considered**:
  - 내부 daemon loop: 코드 단순성은 있으나 프로세스 상태/헬스체크/재시작 관리 복잡도 증가

## Decision 2: 멱등성 기준은 Notion의 `Google ID` 속성
- **Decision**: `Google ID` 비어있음 -> 생성, 값 존재 -> 업데이트 로직을 고정한다.
- **Rationale**: 중복 생성 방지와 상태 추적 기준이 명확하며, 스키마 변경 비용이 낮다.
- **Alternatives considered**:
  - 제목/날짜 기반 매칭: 충돌 가능성 높고 수정 시 오탐 위험 존재

## Decision 3: 시간 정책은 all-day + Asia/Seoul fallback
- **Decision**: 모든 이벤트는 all-day로 처리하고 timezone 누락 시 Asia/Seoul을 기본값으로 적용한다.
- **Rationale**: 요구사항과 일치하며 날짜 해석 오차를 줄인다.
- **Alternatives considered**:
  - 시간 포함 이벤트 혼합 처리: 복잡도 증가, 현재 요구 범위 밖

## Decision 4: 참여자 매핑은 `contact.json` 단방향 사전 조회
- **Decision**: Notion `Assignees` 값(이름)을 `contact.json` key로 조회해 이메일을 이벤트 참석자에 추가한다.
- **Rationale**: 운영자가 명시적으로 매핑을 통제 가능하고 잘못된 이메일 주입을 방지한다.
- **Alternatives considered**:
  - Notion 내 이메일 직접 저장: 데이터 정합성 관리 비용 증가
  - 외부 디렉토리 연동: 초기 범위 대비 구현/운영 부담 과다

## Decision 5: 오류 처리 전략은 항목 단위 격리 + 다음 주기 재시도
- **Decision**: 항목 처리 단위로 예외를 기록하고 실행 전체는 계속 진행한다.
- **Rationale**: 부분 실패에도 서비스 가용성을 유지하고 성공률을 최적화할 수 있다.
- **Alternatives considered**:
  - 첫 오류 즉시 중단: 대량 동기화에서 처리량 저하 및 운영 부담 증가

## Decision 6: 품질/보안 게이트
- **Decision**: `black`, `pylint`, `pytest`, `pytest-cov(>=85%)`를 기본 게이트로 사용한다.
- **Rationale**: 헌장(코드 품질/테스트 기준/보안) 준수와 회귀 방지에 필요한 최소 기준이다.
- **Alternatives considered**:
  - 린트/커버리지 게이트 생략: 변경 누적 시 품질 저하 위험이 높음
