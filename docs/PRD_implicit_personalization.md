# PRD: 암묵적 피드백 기반 자동 개인화

> 작성: 기획자 김큐레이터 | 2026-04-19
> 상태: Draft

## 1. 문제 정의

**현재 상태**: 온보딩에서 사용자가 직접 선택한 situation_group / keyword_group으로만 추천
- `_build_personalization()`이 group 매칭 시 고정 보너스(+3, +2)를 부여
- 좋아요 데이터는 AsyncStorage에만 저장 (서버 동기화 없음)
- 사용자의 실제 행동이 추천에 전혀 반영되지 않음

**문제**:
1. 사용자가 자기 취향을 정확히 모를 수 있음 (온보딩 선택 ≠ 실제 선호)
2. 시간이 지나면 관심사가 바뀌는데 반영할 방법이 없음
3. 모든 사용자가 같은 보너스 가중치를 받음 (개인화가 아님)

## 2. 목표

> 사용자가 앱을 쓸수록 추천이 자동으로 정확해지는 구조를 만든다.

**핵심 지표**:
- 좋아요 전환율: 노출 대비 좋아요 비율 (현재 측정 불가 → 측정 가능하게)
- 세션당 스와이프 수: 더 많이 보면 관심 있다는 신호
- D7 리텐션: 개인화가 잘 되면 재방문율 상승

## 3. 설계: 행동 시그널 → 선호 프로필 → 추천 반영

### 3.1 수집할 행동 시그널

시그널을 **확신/참고 2등급**으로 분리합니다. 참고 시그널은 단독으로 프로필에 반영하지 않고, 확신 시그널을 강화하는 용도로만 사용합니다.

> **원칙: 앱을 그냥 둘러본 것만으로는 프로필이 오염되지 않아야 한다.**

| 등급 | 시그널 | 기본 점수 | 역할 | 수집 위치 | 저장 |
|---|---|---|---|---|---|
| **확신** | 좋아요 | 3.0 | 프로필 직접 반영 | 하트 버튼 탭 | 로컬 + 서버 |
| **확신** | 공유 | 5.0 | 프로필 직접 반영 | 공유 버튼 탭 | 로컬 + 서버 |
| **확신** | 좋아요 취소 | -3.0 | 프로필 직접 반영 (차감) | 하트 버튼 재탭 | 로컬 + 서버 |
| **참고** | 체류 시간 (3초+) | 0 (단독 무시) | 같은 명언에 확신 시그널 있을 때 ×1.5 증폭 | 카드 뷰포트 진입~이탈 | 로컬 배치 |
| **참고** | 상세 진입 | 0 (단독 무시) | 같은 명언에 확신 시그널 있을 때 ×1.3 증폭 | QuoteDetail 이동 | 로컬 배치 |

**증폭은 곱연산으로 중첩됩니다:**
```
명언A: 좋아요(3.0) + 체류 7초(×1.5) + 상세 진입(×1.3) = 3.0 × 1.5 × 1.3 = 5.85
명언B: 좋아요(3.0)만 = 3.0
명언C: 체류 10초 + 상세 진입 (확신 없음) = 0  ← 프로필 오염 방지
명언D: 공유(5.0) + 체류 5초(×1.5) = 5.0 × 1.5 = 7.5
```

### 3.2 선호 프로필 계산 로직

```
사용자가 좋아요/공유한 명언 3개 (확신 시그널 기준):
  명언A: 좋아요 + 체류 + 상세 → 점수 5.85
         keywords=[용기, 도전], situations=[새로운 시작]
  명언B: 좋아요만 → 점수 3.0
         keywords=[용기, 인내], situations=[시련 극복]
  명언C: 공유 + 체류 → 점수 7.5
         keywords=[지혜, 성찰], situations=[자기 반성]

참고만 있는 행동은 무시:
  명언D: 체류 8초 + 상세 진입 (좋아요/공유 없음) → 점수 0 ← 반영 안 함

→ keyword별 가중 점수:
  용기: 5.85 + 3.0 = 8.85
  도전: 5.85
  인내: 3.0
  지혜: 7.5
  성찰: 7.5

→ 정규화 (최대값 대비):
  용기: 1.0, 지혜: 0.85, 성찰: 0.85, 도전: 0.66, 인내: 0.34

→ group 수준 집계:
  행동/태도: 0.67  (용기, 도전, 인내의 평균)
  지성: 0.85  (지혜, 성찰의 평균)
```

**시간 감쇠(decay)**: 최근 7일 행동은 가중치 100%, 30일 전은 50%, 90일 전은 25%

### 3.3 추천 API 반영 방식

현재 `_build_personalization()`의 고정 보너스를 **동적 가중치**로 교체:

```
현재: 매칭 시 무조건 +3 (situation), +2 (keyword)
변경: 매칭 시 +{해당 group의 선호 점수 × 5}

예시:
  행동/태도 그룹 선호 0.83 → 매칭 시 +4.15
  지성 그룹 선호 0.50 → 매칭 시 +2.50
  (온보딩만 한 사용자는 기존처럼 +3/+2 유지)
```

## 4. 구현 단계

### Phase 1: 행동 로그 수집 (우선순위 1 / 난이도 낮음)

**앱 (React Native)**

1. `storage/interactions.ts` 생성 — 행동 로그 로컬 저장
```typescript
interface Interaction {
  quote_id: string;
  type: 'like' | 'unlike' | 'share' | 'view_detail' | 'dwell';
  timestamp: string;
  metadata?: { dwell_seconds?: number };
}
```

2. `useFavorites` 훅 수정 — toggle 시 interaction 기록 추가
3. `HomeScreen` 수정 — 공유 시 interaction 기록
4. `HomeScreen` 수정 — 카드 체류 시간 측정 (FlatList의 `onViewableItemsChanged` 활용)

**백엔드 (Flask)**

5. DB 테이블 추가:
```sql
CREATE TABLE IF NOT EXISTS user_interactions (
    id VARCHAR(36) PRIMARY KEY,
    device_id VARCHAR(64) NOT NULL,
    quote_id VARCHAR(36) NOT NULL REFERENCES quotes(id),
    interaction_type VARCHAR(20) NOT NULL,  -- like, unlike, share, view_detail, dwell
    dwell_seconds FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interactions_device ON user_interactions(device_id);
CREATE INDEX idx_interactions_created ON user_interactions(created_at);
```

6. `POST /app/api/v1/interactions` 엔드포인트 — 배치 업로드
```
Body: { device_id: string, interactions: Interaction[] }
```

### Phase 2: 선호 프로필 생성 (우선순위 1 / 난이도 중)

**백엔드**

7. `GET /app/api/v1/profile?device_id=xxx` 엔드포인트
   - user_interactions에서 device_id의 확신 시그널(like, unlike, share) 집계
   - 같은 quote_id에 참고 시그널(dwell, view_detail)이 있으면 증폭 계수 적용
   - 각 keyword/situation의 가중 점수 계산
   - group 수준으로 집계 후 정규화
   - 시간 감쇠 적용
   - 응답:
```json
{
  "keyword_weights": {"행동/태도": 0.83, "지성": 0.50, ...},
  "situation_weights": {"위기/고난": 0.70, "성장/도전": 0.65, ...},
  "total_interactions": 15,
  "profile_strength": "moderate"  // weak(<5), moderate(5-20), strong(>20)
}
```

8. `_build_personalization()` 수정
   - `keyword_weights`, `situation_weights` 파라미터 추가
   - 가중치가 있으면 동적 보너스 적용, 없으면 기존 로직 유지

### Phase 3: 앱 연동 (우선순위 1 / 난이도 낮음)

9. 앱 시작 시 로컬 interaction을 서버에 배치 전송 (5분 간격 또는 앱 포그라운드 복귀 시)
10. 프로필 API 호출 → 추천 요청에 가중치 포함
11. 선호 프로필을 HomeScreen에 반영 (fetchRecommend에 weights 파라미터 추가)

### Phase 4: 고도화 (우선순위 2 / 중장기)

12. "오늘 기분이 어때요?" 원탭 감정 입력 (선택사항)
13. 시간대별 추천 (아침/저녁 다른 톤)
14. 프로필 시각화 ("당신의 명언 취향" 화면)

## 5. 데이터 흐름 요약

```
[사용자 행동]
  좋아요 / 공유 / 체류 / 상세 진입
       ↓
[로컬 저장] storage/interactions.ts
       ↓ (배치 전송, 5분 간격)
[서버] POST /interactions → user_interactions 테이블
       ↓
[프로필 계산] GET /profile
  행동 로그 집계 → keyword/situation 가중 빈도 → group 정규화 → 시간 감쇠
       ↓
[추천 반영] GET /daily, GET /recommend
  _build_personalization()에서 동적 가중치 사용
       ↓
[더 나은 추천] → 사용자 만족 → 더 많은 행동 → 더 정확한 프로필
```

## 6. 콜드 스타트 전략

| 상태 | 행동 데이터 | 추천 전략 |
|---|---|---|
| **신규** (0회) | 없음 | 온보딩 선택 기반 (+3/+2 고정 보너스) |
| **초기** (1~4회) | 부족 | 온보딩 70% + 행동 30% 혼합 |
| **안정** (5~20회) | 적당 | 행동 70% + 온보딩 30% |
| **성숙** (20회+) | 충분 | 행동 100% (온보딩 무시) |

`profile_strength`에 따라 자동 전환됩니다.

## 7. 개인정보 고려사항

- **계정 없음**: device_id (UUID)로만 식별 → 개인 식별 불가
- **로컬 우선**: 모든 데이터는 먼저 로컬에 저장, 서버 전송은 선택적
- **삭제 가능**: 설정에서 "내 데이터 초기화" 제공
- **최소 수집**: 명언 ID + 행동 타입 + 타임스탬프만 수집 (위치, 기기정보 등 불필요)

## 8. 성공 기준

| 지표 | 현재 | 목표 (Phase 3 완료 후) |
|---|---|---|
| 좋아요 전환율 | 측정 불가 | 8~12% |
| 세션당 스와이프 수 | 측정 불가 | 7개 이상 |
| D7 리텐션 | 측정 불가 | 30% 이상 |
| 프로필 도달율 (5회+) | 해당 없음 | DAU의 40% |

## 9. 구현 우선순위 요약

| 순서 | 작업 | 예상 규모 | 임팩트 |
|---|---|---|---|
| 1 | interaction 로컬 저장 + 기록 | 앱 2시간 | 기반 |
| 2 | user_interactions 테이블 + POST API | 백엔드 1시간 | 기반 |
| 3 | 프로필 계산 API | 백엔드 2시간 | 핵심 |
| 4 | _build_personalization 동적 가중치 | 백엔드 1시간 | 핵심 |
| 5 | 앱 → 서버 배치 동기화 | 앱 1시간 | 연결 |
| 6 | 추천 요청에 프로필 반영 | 앱 1시간 | 완성 |
| **합계** | | **~8시간** | |
