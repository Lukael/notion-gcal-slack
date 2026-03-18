<!--
Sync Impact Report
- Version change: template -> 1.0.0
- Modified principles:
  - placeholder principle 1 -> I. 코드 품질
  - placeholder principle 2 -> II. 테스트 기준
  - placeholder principle 3 -> III. 보안
  - placeholder principle 4 -> IV. 문서 정비
- Added sections:
  - 품질 게이트
  - 개발 워크플로
- Removed sections:
  - placeholder principle 5 section
- Templates requiring updates:
  - ✅ updated: .specify/templates/plan-template.md
  - ✅ updated: .specify/templates/spec-template.md
  - ✅ updated: .specify/templates/tasks-template.md
  - ⚠ pending: .cursor/commands/speckit.*.md (원칙 반영 문구는 권고되나 동작상 필수 변경 없음)
- Deferred follow-up TODOs:
  - 없음
-->
# notion-gcal-slack Constitution

## Core Principles

### I. 코드 품질
모든 코드는 프로젝트의 스타일 가이드와 린팅 규칙을 MUST 준수한다. 모든 풀 리퀘스트는
병합 전에 최소 1회 이상의 코드 리뷰 승인을 MUST 획득한다. 유지보수성과 확장성을 저해하는
구조가 확인되면 기능 추가보다 리팩토링을 우선 MUST 고려한다. 이는 장기 운영 비용을 줄이고
변경 실패 확률을 낮추기 위한 비가역 품질 기준이다.

### II. 테스트 기준
모든 기능 변경은 edge case를 포함한 단위 테스트를 MUST 제공한다. 사용자 가치 또는 데이터
정합성에 영향을 주는 핵심 처리 플로우는 통합 테스트를 MUST 포함한다. 코어 모듈의 테스트
커버리지는 지속적으로 85% 이상을 MUST 유지한다. 테스트가 누락되거나 커버리지 기준을
하회하는 변경은 배포 가능 상태로 간주하지 않는다.

### III. 보안
의존성은 정기 업데이트와 취약점 스캔을 MUST 수행한다. API 키, 비밀번호, 토큰 등 기밀정보는
코드베이스에 직접 포함해서는 안 되며 비밀 관리 수단을 MUST 사용한다. 보안 점검은 OWASP
Top 10 기준을 MUST 참조하여 위협 식별, 예방, 검증 단계를 포함해야 한다. 보안 결함은 기능
결함과 동등한 우선순위로 처리한다.

### IV. 문서 정비
프로젝트 공식 문서는 한국어를 MUST 기본 언어로 사용한다. 신기능 또는 중요한 변경은 개발자용
문서 업데이트를 MUST 동반한다. `README`, 설정 절차, API 사양은 실제 동작과 항상 일치해야
하며 릴리스 시점에 최신 상태여야 한다. 사용자 가이드와 튜토리얼은 릴리스와 동시에 공개 또는
갱신되어야 한다.

## 품질 게이트

- PR 생성 전: 린트, 단위 테스트, 통합 테스트, 커버리지(코어 85% 이상) 검증을 MUST 완료한다.
- PR 리뷰 중: 리뷰어는 코드 품질, 보안, 문서 변경 반영 여부를 체크리스트로 MUST 확인한다.
- 릴리스 전: OWASP Top 10 기반 점검 결과와 문서 최신화 여부를 릴리스 노트에 MUST 남긴다.

## 개발 워크플로

- 모든 작업은 작은 변경 단위로 진행하고, 각 단위는 테스트와 문서 갱신을 함께 완료한다.
- 리팩토링은 동작 동일성 검증(회귀 테스트) 없이 병합하지 않는다.
- 설정/비밀/보안 정책 변경은 구현 변경과 분리해 검토 가능하도록 기록한다.
- 자동화 도구(린터, 테스트, 취약점 스캐너) 실패 시 병합을 차단한다.

## Governance

이 헌장은 프로젝트의 최상위 운영 규칙이며, 하위 문서/관행과 충돌 시 본 문서를 우선 적용한다.
개정은 PR 기반으로 수행하며, 변경 제안자는 영향 범위, 마이그레이션 또는 운영 조정 계획, 관련
템플릿 동기화 결과를 MUST 명시해야 한다. 준수성 검토는 모든 PR에서 수행하며, 미준수 항목은
해결 또는 공식 예외 승인 전까지 병합할 수 없다.

버전 정책은 semantic versioning을 적용한다. MAJOR는 원칙 제거/재정의와 같은 비호환 개정,
MINOR는 새 원칙/섹션 추가 또는 실질적 확장, PATCH는 의미 변경 없는 문구 명확화에 사용한다.

**Version**: 1.0.0 | **Ratified**: 2026-03-17 | **Last Amended**: 2026-03-17
