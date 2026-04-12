-- 마스터 테이블 그룹 체계화
-- 사용: psql -U youheaukjun -d quotes_db -f db/seed_groups.sql
--
-- 기존 데이터의 group_name을 업데이트하고,
-- 아직 없는 항목은 INSERT 한다.

-- ============================================================
-- 키워드 그룹
-- ============================================================

-- 감정
INSERT INTO keywords (id, name, group_name) VALUES
    (gen_random_uuid(), '희망', '감정'),
    (gen_random_uuid(), '사랑', '감정'),
    (gen_random_uuid(), '슬픔', '감정'),
    (gen_random_uuid(), '분노', '감정'),
    (gen_random_uuid(), '기쁨', '감정'),
    (gen_random_uuid(), '외로움', '감정'),
    (gen_random_uuid(), '불안', '감정'),
    (gen_random_uuid(), '감사', '감정'),
    (gen_random_uuid(), '행복', '감정'),
    (gen_random_uuid(), '절망', '감정')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 가치관
INSERT INTO keywords (id, name, group_name) VALUES
    (gen_random_uuid(), '정의', '가치관'),
    (gen_random_uuid(), '자유', '가치관'),
    (gen_random_uuid(), '진실', '가치관'),
    (gen_random_uuid(), '용기', '가치관'),
    (gen_random_uuid(), '겸손', '가치관'),
    (gen_random_uuid(), '의리', '가치관'),
    (gen_random_uuid(), '신념', '가치관'),
    (gen_random_uuid(), '충의', '가치관'),
    (gen_random_uuid(), '평등', '가치관'),
    (gen_random_uuid(), '존재', '가치관')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 행동/태도
INSERT INTO keywords (id, name, group_name) VALUES
    (gen_random_uuid(), '노력', '행동/태도'),
    (gen_random_uuid(), '끈기', '행동/태도'),
    (gen_random_uuid(), '인내', '행동/태도'),
    (gen_random_uuid(), '실천', '행동/태도'),
    (gen_random_uuid(), '도전', '행동/태도'),
    (gen_random_uuid(), '시작', '행동/태도'),
    (gen_random_uuid(), '행동', '행동/태도'),
    (gen_random_uuid(), '근면', '행동/태도'),
    (gen_random_uuid(), '대담함', '행동/태도'),
    (gen_random_uuid(), '열정', '행동/태도'),
    (gen_random_uuid(), '긍정', '행동/태도'),
    (gen_random_uuid(), '낙관', '행동/태도'),
    (gen_random_uuid(), '자신감', '행동/태도'),
    (gen_random_uuid(), '독립', '행동/태도'),
    (gen_random_uuid(), '미루기', '행동/태도')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 관계
INSERT INTO keywords (id, name, group_name) VALUES
    (gen_random_uuid(), '우정', '관계'),
    (gen_random_uuid(), '가족', '관계'),
    (gen_random_uuid(), '소통', '관계'),
    (gen_random_uuid(), '배려', '관계'),
    (gen_random_uuid(), '공감', '관계'),
    (gen_random_uuid(), '결혼', '관계'),
    (gen_random_uuid(), '헌신', '관계'),
    (gen_random_uuid(), '보답', '관계')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 지성
INSERT INTO keywords (id, name, group_name) VALUES
    (gen_random_uuid(), '지식', '지성'),
    (gen_random_uuid(), '지혜', '지성'),
    (gen_random_uuid(), '학문', '지성'),
    (gen_random_uuid(), '사고', '지성'),
    (gen_random_uuid(), '창의성', '지성'),
    (gen_random_uuid(), '상상력', '지성'),
    (gen_random_uuid(), '배움', '지성'),
    (gen_random_uuid(), '교육', '지성'),
    (gen_random_uuid(), '무지', '지성'),
    (gen_random_uuid(), '자각', '지성'),
    (gen_random_uuid(), '판단력', '지성'),
    (gen_random_uuid(), '독서', '지성'),
    (gen_random_uuid(), '복습', '지성'),
    (gen_random_uuid(), '가르침', '지성'),
    (gen_random_uuid(), '탐구', '지성')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 인생
INSERT INTO keywords (id, name, group_name) VALUES
    (gen_random_uuid(), '시간', '인생'),
    (gen_random_uuid(), '죽음', '인생'),
    (gen_random_uuid(), '운명', '인생'),
    (gen_random_uuid(), '성공', '인생'),
    (gen_random_uuid(), '실패', '인생'),
    (gen_random_uuid(), '변화', '인생'),
    (gen_random_uuid(), '인생', '인생'),
    (gen_random_uuid(), '경험', '인생'),
    (gen_random_uuid(), '성장', '인생'),
    (gen_random_uuid(), '자아', '인생'),
    (gen_random_uuid(), '향수', '인생'),
    (gen_random_uuid(), '고립', '인생'),
    (gen_random_uuid(), '위기', '인생'),
    (gen_random_uuid(), '전화위복', '인생'),
    (gen_random_uuid(), '회복', '인생')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 사회
INSERT INTO keywords (id, name, group_name) VALUES
    (gen_random_uuid(), '리더십', '사회'),
    (gen_random_uuid(), '정치', '사회'),
    (gen_random_uuid(), '권력', '사회'),
    (gen_random_uuid(), '여론', '사회'),
    (gen_random_uuid(), '승리', '사회')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 자연/과학
INSERT INTO keywords (id, name, group_name) VALUES
    (gen_random_uuid(), '자연', '자연/과학'),
    (gen_random_uuid(), '과학', '자연/과학'),
    (gen_random_uuid(), '수학', '자연/과학'),
    (gen_random_uuid(), '우주', '자연/과학'),
    (gen_random_uuid(), '측정', '자연/과학')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 유머/표현
INSERT INTO keywords (id, name, group_name) VALUES
    (gen_random_uuid(), '유머', '유머/표현'),
    (gen_random_uuid(), '위트', '유머/표현'),
    (gen_random_uuid(), '재치', '유머/표현'),
    (gen_random_uuid(), '모순', '유머/표현'),
    (gen_random_uuid(), '자조', '유머/표현'),
    (gen_random_uuid(), '웃음', '유머/표현'),
    (gen_random_uuid(), '표현', '유머/표현')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- ============================================================
-- 상황 그룹
-- ============================================================

-- 위기/고난
INSERT INTO situations (id, name, group_name) VALUES
    (gen_random_uuid(), '실패를 겪었을 때', '위기/고난'),
    (gen_random_uuid(), '절망적인 상황에서', '위기/고난'),
    (gen_random_uuid(), '포기하고 싶을 때', '위기/고난'),
    (gen_random_uuid(), '완전히 고립된 상황', '위기/고난'),
    (gen_random_uuid(), '절체절명의 위기에서', '위기/고난'),
    (gen_random_uuid(), '힘든 시기를 보낼 때', '위기/고난'),
    (gen_random_uuid(), '다시 시작해야 할 때', '위기/고난'),
    (gen_random_uuid(), '결과가 안 보일 때', '위기/고난'),
    (gen_random_uuid(), '사방이 적으로 둘러싸였을 때', '위기/고난')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 성장/도전
INSERT INTO situations (id, name, group_name) VALUES
    (gen_random_uuid(), '새로운 일을 시작할 때', '성장/도전'),
    (gen_random_uuid(), '자신감이 필요할 때', '성장/도전'),
    (gen_random_uuid(), '목표를 향해 고난을 견딜 때', '성장/도전'),
    (gen_random_uuid(), '큰 뜻을 품고 참을 때', '성장/도전'),
    (gen_random_uuid(), '용기가 필요할 때', '성장/도전'),
    (gen_random_uuid(), '도전을 망설일 때', '성장/도전'),
    (gen_random_uuid(), '큰 목표 앞에 막막할 때', '성장/도전'),
    (gen_random_uuid(), '계획을 세울 때', '성장/도전'),
    (gen_random_uuid(), '느리게 느껴질 때', '성장/도전')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 관계
INSERT INTO situations (id, name, group_name) VALUES
    (gen_random_uuid(), '갈등을 해결하려 할 때', '관계'),
    (gen_random_uuid(), '상대방을 이해하려 할 때', '관계'),
    (gen_random_uuid(), '은혜를 갚고자 할 때', '관계'),
    (gen_random_uuid(), '감사의 마음을 전할 때', '관계'),
    (gen_random_uuid(), '뜻을 같이하는 동지를 만났을 때', '관계'),
    (gen_random_uuid(), '의리를 강조할 때', '관계'),
    (gen_random_uuid(), '주변 시선이 신경 쓰일 때', '관계')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 자기성찰
INSERT INTO situations (id, name, group_name) VALUES
    (gen_random_uuid(), '자신을 돌아볼 때', '자기성찰'),
    (gen_random_uuid(), '방향을 잃었을 때', '자기성찰'),
    (gen_random_uuid(), '자만에 빠지지 않으려 할 때', '자기성찰'),
    (gen_random_uuid(), '자존감이 낮을 때', '자기성찰'),
    (gen_random_uuid(), '겸손해야 할 때', '자기성찰'),
    (gen_random_uuid(), '고정관념에 빠졌을 때', '자기성찰'),
    (gen_random_uuid(), '새로운 시각이 필요할 때', '자기성찰'),
    (gen_random_uuid(), '자신의 한계를 인정할 때', '자기성찰'),
    (gen_random_uuid(), '과거를 돌아볼 때', '자기성찰')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 일/학업
INSERT INTO situations (id, name, group_name) VALUES
    (gen_random_uuid(), '공부가 힘들 때', '일/학업'),
    (gen_random_uuid(), '직업을 고민할 때', '일/학업'),
    (gen_random_uuid(), '일에 의미를 느끼고 싶을 때', '일/학업'),
    (gen_random_uuid(), '공부 동기가 필요할 때', '일/학업'),
    (gen_random_uuid(), '어려운 환경에서 공부할 때', '일/학업'),
    (gen_random_uuid(), '미루는 습관을 고치고 싶을 때', '일/학업'),
    (gen_random_uuid(), '새로운 분야를 배울 때', '일/학업'),
    (gen_random_uuid(), '다른 사람을 가르칠 때', '일/학업'),
    (gen_random_uuid(), '실험이 안 될 때', '일/학업')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 일상
INSERT INTO situations (id, name, group_name) VALUES
    (gen_random_uuid(), '기분 전환이 필요할 때', '일상'),
    (gen_random_uuid(), '웃음이 필요할 때', '일상'),
    (gen_random_uuid(), '가볍게 웃고 싶을 때', '일상'),
    (gen_random_uuid(), '커피를 마시며', '일상'),
    (gen_random_uuid(), '재치 있는 말이 필요할 때', '일상'),
    (gen_random_uuid(), '희망이 필요할 때', '일상')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- ============================================================
-- 직업 그룹
-- ============================================================

-- 사상/학문
INSERT INTO professions (id, name, group_name) VALUES
    (gen_random_uuid(), '철학자', '사상/학문'),
    (gen_random_uuid(), '사상가', '사상/학문'),
    (gen_random_uuid(), '수학자', '사상/학문'),
    (gen_random_uuid(), '학자', '사상/학문'),
    (gen_random_uuid(), '경영학자', '사상/학문'),
    (gen_random_uuid(), '경제학자', '사상/학문'),
    (gen_random_uuid(), '역사가', '사상/학문'),
    (gen_random_uuid(), '학자·문인', '사상/학문')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 과학/기술
INSERT INTO professions (id, name, group_name) VALUES
    (gen_random_uuid(), '물리학자', '과학/기술'),
    (gen_random_uuid(), '천문학자·물리학자', '과학/기술'),
    (gen_random_uuid(), '발명가', '과학/기술'),
    (gen_random_uuid(), '공학자', '과학/기술'),
    (gen_random_uuid(), '철학자·수학자', '과학/기술'),
    (gen_random_uuid(), '물리학자·수학자', '과학/기술'),
    (gen_random_uuid(), '물리학자·공학자', '과학/기술'),
    (gen_random_uuid(), '철학자·자연학자', '과학/기술')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 문학/예술
INSERT INTO professions (id, name, group_name) VALUES
    (gen_random_uuid(), '작가', '문학/예술'),
    (gen_random_uuid(), '시인', '문학/예술'),
    (gen_random_uuid(), '소설가', '문학/예술'),
    (gen_random_uuid(), '화가', '문학/예술'),
    (gen_random_uuid(), '음악가', '문학/예술'),
    (gen_random_uuid(), '패션 디자이너', '문학/예술')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 정치/군사
INSERT INTO professions (id, name, group_name) VALUES
    (gen_random_uuid(), '정치가', '정치/군사'),
    (gen_random_uuid(), '군인', '정치/군사'),
    (gen_random_uuid(), '외교관', '정치/군사'),
    (gen_random_uuid(), '혁명가', '정치/군사'),
    (gen_random_uuid(), '정치가·상인', '정치/군사'),
    (gen_random_uuid(), '왕족·학자', '정치/군사')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 경제/산업
INSERT INTO professions (id, name, group_name) VALUES
    (gen_random_uuid(), '기업가', '경제/산업'),
    (gen_random_uuid(), '상인', '경제/산업')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 종교/정신
INSERT INTO professions (id, name, group_name) VALUES
    (gen_random_uuid(), '종교인', '종교/정신'),
    (gen_random_uuid(), '성직자', '종교/정신'),
    (gen_random_uuid(), '수도자', '종교/정신')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;

-- 대중문화
INSERT INTO professions (id, name, group_name) VALUES
    (gen_random_uuid(), '코미디언', '대중문화'),
    (gen_random_uuid(), '배우', '대중문화'),
    (gen_random_uuid(), '민간 전승', '대중문화')
ON CONFLICT (name) DO UPDATE SET group_name = EXCLUDED.group_name;
