# PRD: 관리자 콘솔

> 작성: 기획자 김큐레이터 | 2026-04-19
> 상태: Draft

## 1. 문제 정의

**현재 상태**: 관리자가 데이터를 관리할 수 있는 웹 UI가 없음
- 명언 상태 변경: `/admin/publish-all` (일괄만 가능) 또는 직접 SQL
- 명언 수정/삭제/추가: psql 접속 필요
- 저자 관리: SQL만 가능
- 팩트체크 결과 확인: CLI 출력 확인 후 수동 SQL 업데이트
- reviewed, rejected 상태가 스키마에만 존재하고 실제로 사용 불가

**문제**: 1,245개 명언의 품질 관리가 사실상 불가능. 가짜 명언이 사용자에게 노출될 위험.

## 2. 목표

> 관리자가 웹 브라우저에서 명언/저자 데이터의 조회·추가·수정·삭제·상태관리를 할 수 있게 한다.

## 3. 설계

### 3.1 화면 구성

```
/admin                → 관리자 메인 (명언 관리)
/admin/authors        → 저자 관리
/admin/factcheck      → 팩트체크 대기열
```

기존 대시보드(`/`)는 그대로 유지. 관리자 콘솔은 별도 경로.

### 3.2 인증

환경변수 `ADMIN_TOKEN`으로 간단한 토큰 인증:
- `/admin` 최초 접근 시 토큰 입력 폼 표시
- 입력한 토큰을 localStorage에 저장
- 이후 모든 `/admin/api/*` 요청에 `Authorization: Bearer <token>` 헤더 포함
- 서버에서 `ADMIN_TOKEN` 환경변수와 대조, 불일치 시 401

### 3.3 화면 1: 명언 관리 (`/admin`)

#### 상단 액션 바
- `[+ 명언 추가]` 버튼
- `[선택한 N개: 상태 변경 ▼]` `[선택한 N개: 삭제]` (체크박스 선택 시 활성화)

#### 필터 바
- 상태: 전체 / draft / reviewed / published / rejected
- 키워드 그룹: 전체 / 감정 / 가치관 / 행동·태도 / ...
- 신뢰도: 전체 / verified / attributed / disputed / unknown
- 텍스트 검색: 명언 본문 + 저자명 검색

#### 명언 리스트 (20개/페이지)
```
□ "삶이 있는 한 희망은 있다"
  — 키케로 | 철학 | draft | attributed | 2026-04-12
  키워드: #희망 #인생    상황: 시련 극복
  [reviewed] [published] [rejected]  [편집] [삭제]
```

- 상태 버튼: 클릭 시 즉시 변경 (현재 상태 버튼은 비활성)
- 편집: 편집 모달 오픈
- 삭제: 확인 모달 → 삭제 (user_interactions cascade)

#### 명언 추가/편집 모달
```
┌──────────────────────────────────────────┐
│  명언 추가 (또는 편집)              [✕]  │
├──────────────────────────────────────────┤
│  텍스트 *:                               │
│  ┌────────────────────────────────────┐  │
│  │                                    │  │
│  └────────────────────────────────────┘  │
│  원문:                                   │
│  ┌────────────────────────────────────┐  │
│  │                                    │  │
│  └────────────────────────────────────┘  │
│  원문 언어: [ko ▼]                       │
│                                          │
│  저자: [검색/선택 ▼]  [+ 신규 저자]      │
│  출처:  [                           ]    │
│  연도:  [    ]                           │
│                                          │
│  상태: [draft ▼]   신뢰도: [unknown ▼]   │
│                                          │
│  키워드: [선택 ▼ (다중)]                 │
│  상황:   [선택 ▼ (다중)]                 │
│                                          │
│           [취소]  [저장]                  │
└──────────────────────────────────────────┘
```

- 저자: 기존 저자 검색 선택 또는 "신규 저자" 클릭 시 인라인 입력 폼
- 키워드/상황: 마스터 테이블에서 다중 선택 (체크박스 드롭다운)
- 추가 시 기본값: status=draft, source_reliability=unknown

### 3.4 화면 2: 저자 관리 (`/admin/authors`)

#### 상단 액션 바
- `[+ 저자 추가]` 버튼

#### 검색
- 저자 이름 검색

#### 저자 리스트 (20개/페이지)
```
키케로 | 정치인 | 철학 | IT | BC 106 | 명언 3개
  [편집] [삭제 — 명언 3개·관계 2건 포함]

토마스 에디슨 | 발명가 | 과학 | US | 1847 | 명언 5개
  [편집] [삭제 — 명언 5개·관계 1건 포함]
```

#### 저자 추가/편집 모달
```
┌──────────────────────────────────────────┐
│  저자 추가 (또는 편집)              [✕]  │
├──────────────────────────────────────────┤
│  이름 *:     [                      ]    │
│  국적 * (ISO): [KR ▼]                   │
│  출생연도 *: [     ]  (BC는 음수 입력)   │
│  직업:       [선택 ▼]                    │
│  분야:       [선택 ▼]                    │
│                                          │
│           [취소]  [저장]                  │
└──────────────────────────────────────────┘
```

#### 저자 삭제 확인 모달
```
┌──────────────────────────────────────────┐
│  ⚠ 저자 삭제 확인                       │
├──────────────────────────────────────────┤
│  "키케로"를 삭제하시겠습니까?            │
│                                          │
│  다음 데이터가 함께 삭제됩니다:          │
│  · 명언 3개                              │
│  · 저자 관계 2건                         │
│  · 사용자 행동 로그 12건                 │
│                                          │
│  이 작업은 되돌릴 수 없습니다.           │
│                                          │
│           [취소]  [삭제]                  │
└──────────────────────────────────────────┘
```

### 3.5 화면 3: 팩트체크 대기열 (`/admin/factcheck`)

#### 상단 정보
- 미검증 명언 수 표시
- `[10개 일괄 검증]` 버튼 (Claude API 호출)

#### 리스트
```
"천 리 길도 한 걸음부터"
  — 노자 | 미검증
  [팩트체크 실행]

"실패는 성공의 어머니다"
  — 토마스 에디슨 | 검증 완료: disputed
  결과: "이 명언의 정확한 출처는 불명확. 에디슨에게 귀속되나 원전 미확인."
  신뢰도: medium
  [published 유지] [rejected로 변경] [재검증]
```

## 4. API 설계

### 인증 미들웨어
모든 `/admin/api/*` 요청에 적용:
```python
Authorization: Bearer <ADMIN_TOKEN>
# 불일치 시 401 {"error": "unauthorized"}
```

### 명언 API

| 엔드포인트 | 메서드 | 기능 | 요청 | 응답 |
|---|---|---|---|---|
| `/admin/api/quotes` | GET | 목록 조회 | `?status=&keyword_group=&reliability=&search=&page=&limit=` | `{quotes: [...], total: N, page: N}` |
| `/admin/api/quotes` | POST | 명언 추가 | `{text, text_original, original_language, author_id, source, year, status, source_reliability, keyword_ids, situation_ids}` | `{id, ...}` |
| `/admin/api/quotes/<id>` | PATCH | 명언 수정 | 변경할 필드만 | `{id, ...}` |
| `/admin/api/quotes/<id>` | DELETE | 명언 삭제 | — | `{deleted: true}` |
| `/admin/api/quotes/batch-status` | POST | 일괄 상태 변경 | `{ids: [...], status: "published"}` | `{updated: N}` |
| `/admin/api/quotes/batch-delete` | POST | 일괄 삭제 | `{ids: [...]}` | `{deleted: N}` |

### 저자 API

| 엔드포인트 | 메서드 | 기능 | 요청 | 응답 |
|---|---|---|---|---|
| `/admin/api/authors` | GET | 목록 조회 | `?search=&page=&limit=` | `{authors: [...], total: N}` |
| `/admin/api/authors` | POST | 저자 추가 | `{name, nationality, birth_year, profession_id, field_id}` | `{id, ...}` |
| `/admin/api/authors/<id>` | PATCH | 저자 수정 | 변경할 필드만 | `{id, ...}` |
| `/admin/api/authors/<id>` | DELETE | 저자 삭제 | — | `{deleted_quotes: N, deleted_relations: N, deleted_interactions: N}` |
| `/admin/api/authors/<id>/preview-delete` | GET | 삭제 영향 미리보기 | — | `{quote_count: N, relation_count: N, interaction_count: N}` |

### 팩트체크 API

| 엔드포인트 | 메서드 | 기능 |
|---|---|---|
| `/admin/api/factcheck/pending` | GET | 미검증 목록 |
| `/admin/api/factcheck/<quote_id>` | POST | 개별 팩트체크 실행 |
| `/admin/api/factcheck/batch` | POST | N개 일괄 팩트체크 |

### 마스터 데이터 API (드롭다운용)

| 엔드포인트 | 메서드 | 기능 |
|---|---|---|
| `/admin/api/masters/keywords` | GET | 키워드 목록 (group_name 포함) |
| `/admin/api/masters/situations` | GET | 상황 목록 (group_name 포함) |
| `/admin/api/masters/professions` | GET | 직업 목록 |
| `/admin/api/masters/fields` | GET | 분야 목록 |

## 5. 삭제 시 연쇄 처리

### 명언 삭제
```sql
DELETE FROM user_interactions WHERE quote_id = %s;
DELETE FROM quotes WHERE id = %s;
```

### 저자 삭제
```sql
-- 1. 해당 저자 명언의 interaction 삭제
DELETE FROM user_interactions WHERE quote_id IN (SELECT id FROM quotes WHERE author_id = %s);
-- 2. 해당 저자 명언 삭제
DELETE FROM quotes WHERE author_id = %s;
-- 3. 저자 관계 삭제
DELETE FROM author_relations WHERE from_author_id = %s OR to_author_id = %s;
-- 4. 저자 삭제
DELETE FROM authors WHERE id = %s;
```

순서가 중요합니다 (FK 제약 때문에 하위 테이블부터).

## 6. 구현 방식

기존 대시보드와 동일하게 **Flask 라우트에서 HTML 문자열 반환 + vanilla JS**:
- `/admin` → 관리자 HTML 반환 (SPA 스타일, 탭으로 화면 전환)
- `/admin/api/*` → JSON API
- 스타일: 기존 대시보드 CSS 확장 (다크 테마 유지)

별도 프론트엔드 빌드 불필요. `dashboard.py` 파일 하나에 추가.

## 7. 환경변수 추가

```
ADMIN_TOKEN=<랜덤 토큰>  # Railway 환경변수에 설정
```

## 8. 구현 우선순위

| 순서 | 작업 | 예상 규모 |
|---|---|---|
| 1 | 인증 미들웨어 + ADMIN_TOKEN | 30분 |
| 2 | 명언 CRUD API (GET/POST/PATCH/DELETE/batch) | 2시간 |
| 3 | 저자 CRUD API (GET/POST/PATCH/DELETE + preview) | 1.5시간 |
| 4 | 마스터 데이터 API | 30분 |
| 5 | 관리자 HTML + JS (명언 관리 화면) | 3시간 |
| 6 | 관리자 HTML + JS (저자 관리 화면) | 2시간 |
| 7 | 팩트체크 API + 화면 | 2시간 |
| **합계** | | **~11.5시간** |
