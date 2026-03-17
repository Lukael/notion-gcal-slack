# Quickstart: Notion-GCal Todo Sync

## 1. 사전 준비

1. Notion Integration을 생성하고 대상 데이터베이스를 공유한다.
2. Google Calendar OAuth 클라이언트를 준비한다.
3. 루트에 비밀 파일을 준비한다(버전 관리 제외):
   - `.env` (권장: `env.example` 복사 후 값 주입)
   - `token.json` (최초 인증 이후 생성)
   - `contact.json`

## 2. 환경 변수 설정

`.env` 예시:

```bash
NOTION_TOKEN=secret_xxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxx
GCAL_CALENDAR_ID=primary
TZ=Asia/Seoul
```

## 3. 개발 실행

```bash
poetry install
poetry run python -m src.main --once
```

기대 결과:
- Due Date가 있는 Notion 항목만 처리
- `Google ID`가 없는 항목은 이벤트 생성 후 Notion에 ID 저장
- `Google ID`가 있는 항목은 이벤트 갱신

## 4. 테스트 실행

```bash
poetry run pytest -q
poetry run pytest --cov=src --cov-report=term-missing
poetry run pytest tests/integration/test_sync_latency.py -q
poetry run pytest tests/integration/test_sync_performance.py -q
```

합격 기준:
- 단위/통합 테스트 통과
- 코어 모듈 커버리지 85% 이상

## 5. 코드 품질 검사

```bash
poetry run black --check src tests
poetry run pylint src
```

## 6. Docker 실행(단일 실행)

```bash
docker build -t notion-gcal-sync -f ops/Dockerfile .
docker run --rm --env-file .env -v "$PWD/token.json:/app/token.json" -v "$PWD/contact.json:/app/contact.json" notion-gcal-sync
```

## 7. 주기 실행 예시 (cron)

```cron
*/5 * * * * /usr/bin/docker run --rm --env-file /path/.env \
  -v /path/token.json:/app/token.json \
  -v /path/contact.json:/app/contact.json \
  notion-gcal-sync
```

## 8. 장애 복구 검증 시나리오

1. 일부 항목에서 의도적으로 잘못된 참여자 매핑을 넣는다.
2. 동기화를 실행해 항목 단위 실패가 기록되는지 확인한다.
3. 매핑을 수정한 뒤 다음 실행에서 자동 복구되는지 확인한다.
