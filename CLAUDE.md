# 명언수집기

큐레이션된 명언 라이브러리 + 개인화 추천을 목표로 하는 프로젝트.

## 기술 스택

- **언어**: Python
- **DB**: PostgreSQL (pg_trgm 확장 — 유사도 검색)
- **LLM**: Claude API (anthropic SDK) — 명언 수집용
- **웹**: Flask (대시보드)
- **기타**: pytrends (Google Trends 분석)

## 프로젝트 구조

- `db/schema.sql` — PostgreSQL 테이블 정의 (quotes, authors, author_relations)
- `scripts/collect.py` — Claude API로 명언 수집 + DB 저장 (메인 스크립트)
- `scripts/trends.py` — Google Trends 카테고리 관심도 분석
- `scripts/dashboard.py` — Flask 기반 데이터 현황 대시보드 (localhost:5050)
- `scripts/seed_*.py` — 초기 데이터 시딩 스크립트
- `insert_quotes.py` — 수동 명언 삽입 (고사성어, 과학/철학)
- `data/trends/` — 트렌드 분석 결과 JSON

## 실행 방법

```bash
pip install -r requirements.txt
cp .env.example .env              # API키, DB 접속 정보 설정

# DB 초기화
psql -U youheaukjun -f db/schema.sql

# 명언 수집
python scripts/collect.py                    # 전체 카테고리
python scripts/collect.py --category 인생/삶  # 특정 카테고리
python scripts/collect.py --dry-run           # DB 저장 없이 확인

# 대시보드
python scripts/dashboard.py
```

## 환경변수 (.env)

- `ANTHROPIC_API_KEY` — Claude API 키
- `PG_HOST`, `PG_PORT`, `PG_USER`, `PG_PASSWORD`, `PG_DATABASE` — PostgreSQL 접속 정보

## 주의사항

- 모든 스크립트는 psycopg2 (PostgreSQL) 사용
- keywords, situation 필드는 JSONB 타입
- 중복 검사: 정확 매칭 + trigram 유사도 (threshold 0.4)

## 명언 수집 규칙

### 데이터 검증

1. **실존 명언만 수집** — 절대 지어내지 않는다. 출처가 불확실하면 source를 null로 한다.
2. **저자 정보 검증** — name, profession, field, nationality, birth_year는 사실 기반이어야 한다. 추정값은 사용하지 않는다.
3. **원문 필수** — 번역 명언은 반드시 text_original과 original_language를 함께 제공한다. 한국어 원문이면 original_language를 "ko"로 한다.
4. **중복 방지** — DB 저장 전 반드시 중복 검사를 거친다 (정확 매칭 → trigram 유사도 0.4 이상이면 중복 판정).
5. **태깅 일관성** — keywords, situation은 DB의 마스터 테이블 목록에서 선택한다. 새 항목 추가 시 `_new:이름` 형식을 사용하고 로그에 기록한다.

### 저자 관계 (author_relations)

- 역사적으로 확인된 관계만 기록한다. 추측 금지.
- mentor: 직접적인 스승→제자
- influenced_by: 사상적 영향 (준 사람→받은 사람)
- contemporary: 같은 시대 교류 (양방향 저장)
- 관계가 없으면 빈 배열 []

### 수집 이력 관리

1. **collection_logs 테이블** — 모든 수집은 카테고리별로 요청 수, 저장 수, 중복 수, 오류 수를 기록한다.
2. **dry-run 우선** — 새로운 카테고리나 대량 수집 전에 `--dry-run`으로 먼저 확인한다.
3. **카테고리별 수집** — 한 번에 전체를 수집하기보다 `--category`로 나눠서 진행하고, 각 결과를 확인한 뒤 다음으로 넘어간다.
4. **수동 삽입 시** — `insert_quotes.py`나 seed 스크립트로 수동 데이터를 넣을 때도 중복 검사를 반드시 수행한다.

### 수집 계획 (COLLECTION_PLAN)

| 카테고리 | 목표 | 비고 |
|---|---|---|
| 인생/삶 | 25개 | 가장 범용적 |
| 사랑/관계 | 15개 | 글로벌 1위 관심도 |
| 동기부여/성공 | 15개 | 꾸준한 수요 |
| 유머/위트 | 10개 | 차별화 |
| 공부/학습 | 10개 | 한국 시장 특화 |
| 고사성어 | 15개 | 한국 시장 2위 |
| 과학/철학 | 10개 | 지적 깊이 확보 |

### 데이터 품질 기준

- **다양성**: 시대, 국적, 분야, 성별이 편중되지 않도록 한다.
- **nationality**: 반드시 ISO 3166-1 alpha-2 코드 사용 (KR, US, GB, DE, CN 등). "한국", "미국" 같은 한글 국가명 사용 금지.
- **고사성어**: text에 한자 + 뜻풀이 포함, text_original에 한자만, original_language는 "zh".
