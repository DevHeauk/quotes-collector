-- 마스터 테이블 그룹 체계 (현행 DB 기준, 2026-04-19 동기화)
-- 사용: psql -U youheaukjun -d quotes_db -f db/seed_groups.sql
--
-- 기존 데이터의 group_name을 업데이트하고,
-- 아직 없는 항목은 INSERT 한다.

-- ============================================================
-- 키워드 그룹 (56개, 8그룹)
-- ============================================================

-- 관계
INSERT INTO keywords (id, name, group_name) VALUES
    (gen_random_uuid(), '가족', '관계'),
    (gen_random_uuid(), '감사', '관계'),
    (gen_random_uuid(), '공동체', '관계'),
    (gen_random_uuid(), '관계', '관계'),
    (gen_random_uuid(), '사랑', '관계'),
    (gen_random_uuid(), '우정', '관계'),
    (gen_random_uuid(), '헌신', '관계')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 동기부여
INSERT INTO keywords (id, name, group_name) VALUES
    (gen_random_uuid(), '끈기', '동기부여'),
    (gen_random_uuid(), '노력', '동기부여'),
    (gen_random_uuid(), '도전', '동기부여'),
    (gen_random_uuid(), '동기부여', '동기부여'),
    (gen_random_uuid(), '목표', '동기부여'),
    (gen_random_uuid(), '성공', '동기부여'),
    (gen_random_uuid(), '신념', '동기부여'),
    (gen_random_uuid(), '실천', '동기부여'),
    (gen_random_uuid(), '실패', '동기부여'),
    (gen_random_uuid(), '열정', '동기부여'),
    (gen_random_uuid(), '용기', '동기부여'),
    (gen_random_uuid(), '인내', '동기부여'),
    (gen_random_uuid(), '행동', '동기부여'),
    (gen_random_uuid(), '회복', '동기부여'),
    (gen_random_uuid(), '희망', '동기부여')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 성장
INSERT INTO keywords (id, name, group_name) VALUES
    (gen_random_uuid(), '독립', '성장'),
    (gen_random_uuid(), '변화', '성장'),
    (gen_random_uuid(), '성장', '성장'),
    (gen_random_uuid(), '습관', '성장'),
    (gen_random_uuid(), '자기성찰', '성장'),
    (gen_random_uuid(), '자신감', '성장')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 유머
INSERT INTO keywords (id, name, group_name) VALUES
    (gen_random_uuid(), '위트', '유머'),
    (gen_random_uuid(), '유머', '유머')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 과학/철학
INSERT INTO keywords (id, name, group_name) VALUES
    (gen_random_uuid(), '결정론', '과학/철학'),
    (gen_random_uuid(), '과학', '과학/철학'),
    (gen_random_uuid(), '우주', '과학/철학'),
    (gen_random_uuid(), '자연', '과학/철학'),
    (gen_random_uuid(), '창의성', '과학/철학'),
    (gen_random_uuid(), '철학', '과학/철학')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 인생/삶
INSERT INTO keywords (id, name, group_name) VALUES
    (gen_random_uuid(), '고통', '인생/삶'),
    (gen_random_uuid(), '두려움', '인생/삶'),
    (gen_random_uuid(), '선택', '인생/삶'),
    (gen_random_uuid(), '시간', '인생/삶'),
    (gen_random_uuid(), '외로움', '인생/삶'),
    (gen_random_uuid(), '운명', '인생/삶'),
    (gen_random_uuid(), '의미', '인생/삶'),
    (gen_random_uuid(), '인생', '인생/삶'),
    (gen_random_uuid(), '자아', '인생/삶'),
    (gen_random_uuid(), '자유', '인생/삶'),
    (gen_random_uuid(), '존재', '인생/삶'),
    (gen_random_uuid(), '죽음', '인생/삶'),
    (gen_random_uuid(), '초월', '인생/삶'),
    (gen_random_uuid(), '행복', '인생/삶')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 학습/지혜
INSERT INTO keywords (id, name, group_name) VALUES
    (gen_random_uuid(), '겸손', '학습/지혜'),
    (gen_random_uuid(), '교육', '학습/지혜'),
    (gen_random_uuid(), '지식', '학습/지혜'),
    (gen_random_uuid(), '지혜', '학습/지혜'),
    (gen_random_uuid(), '학습', '학습/지혜')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 기타
INSERT INTO keywords (id, name, group_name) VALUES
    (gen_random_uuid(), '전통', '기타')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- ============================================================
-- 상황 그룹 (40개, 8그룹)
-- ============================================================

-- 위기/극복
INSERT INTO situations (id, name, group_name) VALUES
    (gen_random_uuid(), '두려울 때', '위기/극복'),
    (gen_random_uuid(), '불운할 때', '위기/극복'),
    (gen_random_uuid(), '실패했을 때', '위기/극복'),
    (gen_random_uuid(), '외로울 때', '위기/극복'),
    (gen_random_uuid(), '절망적일 때', '위기/극복'),
    (gen_random_uuid(), '좌절했을 때', '위기/극복'),
    (gen_random_uuid(), '자신감이 없을 때', '위기/극복'),
    (gen_random_uuid(), '포기하고 싶을 때', '위기/극복'),
    (gen_random_uuid(), '희망이 필요할 때', '위기/극복'),
    (gen_random_uuid(), '힘든 시기를 보낼 때', '위기/극복'),
    (gen_random_uuid(), '힘든 상황에서 거리를 두고 싶을 때', '위기/극복')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 시작/도전
INSERT INTO situations (id, name, group_name) VALUES
    (gen_random_uuid(), '새로운 시작', '시작/도전'),
    (gen_random_uuid(), '도전을 망설일 때', '시작/도전'),
    (gen_random_uuid(), '용기가 필요할 때', '시작/도전'),
    (gen_random_uuid(), '새로운 관점이 필요할 때', '시작/도전')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 동기부여
INSERT INTO situations (id, name, group_name) VALUES
    (gen_random_uuid(), '게으를 때', '동기부여'),
    (gen_random_uuid(), '꾸준함이 필요할 때', '동기부여'),
    (gen_random_uuid(), '목표가 멀게 느껴질 때', '동기부여')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 사랑/관계
INSERT INTO situations (id, name, group_name) VALUES
    (gen_random_uuid(), '관계의 소중함', '사랑/관계'),
    (gen_random_uuid(), '관계가 어려울 때', '사랑/관계'),
    (gen_random_uuid(), '사랑을 느낄 때', '사랑/관계'),
    (gen_random_uuid(), '사랑의 본질을 고민할 때', '사랑/관계')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 인생/성찰
INSERT INTO situations (id, name, group_name) VALUES
    (gen_random_uuid(), '감사할 때', '인생/성찰'),
    (gen_random_uuid(), '인생의 선택', '인생/성찰'),
    (gen_random_uuid(), '자기 성찰', '인생/성찰'),
    (gen_random_uuid(), '과거를 돌아볼 때', '인생/성찰'),
    (gen_random_uuid(), '미래가 불안할 때', '인생/성찰'),
    (gen_random_uuid(), '변화를 마주할 때', '인생/성찰'),
    (gen_random_uuid(), '죽음을 생각할 때', '인생/성찰'),
    (gen_random_uuid(), '삶의 의미를 찾을 때', '인생/성찰'),
    (gen_random_uuid(), '현재를 살고 싶을 때', '인생/성찰')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 학습
INSERT INTO situations (id, name, group_name) VALUES
    (gen_random_uuid(), '배움의 자세', '학습'),
    (gen_random_uuid(), '지식의 가치', '학습'),
    (gen_random_uuid(), '공부하기 싫을 때', '학습'),
    (gen_random_uuid(), '깊이 이해하고 싶을 때', '학습')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 과학/탐구
INSERT INTO situations (id, name, group_name) VALUES
    (gen_random_uuid(), '과학적 사고', '과학/탐구'),
    (gen_random_uuid(), '창의적 사고', '과학/탐구')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 유머/일상
INSERT INTO situations (id, name, group_name) VALUES
    (gen_random_uuid(), '일상의 소소함', '유머/일상'),
    (gen_random_uuid(), '웃음이 필요할 때', '유머/일상'),
    (gen_random_uuid(), '기분 전환이 필요할 때', '유머/일상')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- ============================================================
-- 직업 그룹 (현행 DB 기준)
-- ============================================================

-- 학술
INSERT INTO professions (id, name, group_name) VALUES
    (gen_random_uuid(), '경영학자', '학술'),
    (gen_random_uuid(), '사상가', '학술'),
    (gen_random_uuid(), '심리학자', '학술'),
    (gen_random_uuid(), '역사가', '학술'),
    (gen_random_uuid(), '철학자', '학술'),
    (gen_random_uuid(), '학자', '학술')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 과학/기술
INSERT INTO professions (id, name, group_name) VALUES
    (gen_random_uuid(), '과학자', '과학/기술'),
    (gen_random_uuid(), '물리학자', '과학/기술'),
    (gen_random_uuid(), '발명가', '과학/기술'),
    (gen_random_uuid(), '수학자', '과학/기술'),
    (gen_random_uuid(), '의사', '과학/기술')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 예술
INSERT INTO professions (id, name, group_name) VALUES
    (gen_random_uuid(), '배우', '예술'),
    (gen_random_uuid(), '시인', '예술'),
    (gen_random_uuid(), '예술가', '예술'),
    (gen_random_uuid(), '음악가', '예술'),
    (gen_random_uuid(), '작가', '예술'),
    (gen_random_uuid(), '코미디언', '예술'),
    (gen_random_uuid(), '패션 디자이너', '예술')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 정치/군사
INSERT INTO professions (id, name, group_name) VALUES
    (gen_random_uuid(), '군인', '정치/군사'),
    (gen_random_uuid(), '정치가', '정치/군사')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 경영
INSERT INTO professions (id, name, group_name) VALUES
    (gen_random_uuid(), '기업가', '경영')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 종교
INSERT INTO professions (id, name, group_name) VALUES
    (gen_random_uuid(), '종교 지도자', '종교')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 미디어
INSERT INTO professions (id, name, group_name) VALUES
    (gen_random_uuid(), '방송인', '미디어'),
    (gen_random_uuid(), '언론인', '미디어')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 스포츠
INSERT INTO professions (id, name, group_name) VALUES
    (gen_random_uuid(), '운동선수', '스포츠')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 기타
INSERT INTO professions (id, name, group_name) VALUES
    (gen_random_uuid(), '민간 전승', '기타')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;
