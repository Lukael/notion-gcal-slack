# Quickstart: Docker Persistent 10-Minute Scheduler

## 1. 사전 준비

1. 루트에 `.env` 파일을 준비한다 (`env.example` 기반).
2. `token.json`, `contact.json` 파일을 준비한다.
3. 이미지 빌드:

```bash
docker build -t notion-gcal-sync -f ops/Dockerfile .
```

## 2. 기본 loop 모드 실행 (권장)

```bash
docker run --rm --env-file .env \
  -v "$PWD/token.json:/app/token.json" \
  -v "$PWD/contact.json:/app/contact.json" \
  notion-gcal-sync
```

기대 동작:
- 컨테이너가 종료되지 않고 유지됨
- 10분마다 동기화 실행
- 각 cycle 결과와 다음 실행 예정 로그 출력

## 3. 단일 실행 모드

```bash
docker run --rm --env-file .env \
  -v "$PWD/token.json:/app/token.json" \
  -v "$PWD/contact.json:/app/contact.json" \
  notion-gcal-sync python -m src.main --once
```

## 4. 간격 커스터마이징

`.env`에 아래 값 설정:

```bash
SYNC_INTERVAL_SECONDS=600
SHUTDOWN_TIMEOUT_SECONDS=30
DRIFT_WARNING_SECONDS=30
```

## 5. 검증 시나리오

1. 컨테이너를 25분 이상 실행한다.
2. 최소 3회 cycle 로그가 출력되는지 확인한다.
3. cycle 간격이 약 10분인지 확인하고 지연 시 drift warning 로그를 확인한다.
4. 의도적 오류를 1회 유도해도 다음 cycle이 계속 실행되는지 확인한다.
5. 종료 전 `loop_stopped` 로그의 `recovery_rate` 값을 확인한다.
6. 컨테이너 종료 시 종료 로그와 정상 종료를 확인한다.
