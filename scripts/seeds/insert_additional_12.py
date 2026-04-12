#!/usr/bin/env python3
"""중복된 12개를 대체할 추가 명언: 공부/학습 3개, 유머/위트 1개, 과학/철학 8개"""

import uuid
import psycopg2
from psycopg2.extras import Json

conn = psycopg2.connect(host="localhost", user="youheaukjun", dbname="quotes_db")
conn.autocommit = False
cur = conn.cursor()

def get_or_create_profession(name, group_name):
    cur.execute("SELECT id FROM professions WHERE name = %s", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    pid = str(uuid.uuid4())
    cur.execute("INSERT INTO professions (id, name, group_name) VALUES (%s, %s, %s)", (pid, name, group_name))
    return pid

def get_field_id(name):
    cur.execute("SELECT id FROM fields WHERE name = %s", (name,))
    row = cur.fetchone()
    return row[0] if row else None

def get_or_create_author(name, nationality, birth_year, profession_name, profession_group, field_name):
    cur.execute("SELECT id FROM authors WHERE name = %s", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    aid = str(uuid.uuid4())
    prof_id = get_or_create_profession(profession_name, profession_group)
    field_id = get_field_id(field_name)
    cur.execute(
        "INSERT INTO authors (id, name, nationality, birth_year, profession_id, field_id) VALUES (%s,%s,%s,%s,%s,%s)",
        (aid, name, nationality, birth_year, prof_id, field_id)
    )
    return aid

def get_keyword_id(name):
    cur.execute("SELECT id FROM keywords WHERE name = %s", (name,))
    row = cur.fetchone()
    return row[0] if row else None

def get_situation_id(name):
    cur.execute("SELECT id FROM situations WHERE name = %s", (name,))
    row = cur.fetchone()
    return row[0] if row else None

def insert_quote(text, text_original, original_language, author_id, source, year,
                 keyword_names, situation_names, log_id):
    cur.execute("SELECT id FROM quotes WHERE text = %s", (text,))
    if cur.fetchone():
        return False
    qid = str(uuid.uuid4())
    keyword_ids = [get_keyword_id(k) for k in keyword_names]
    keyword_ids = [k for k in keyword_ids if k]
    situation_ids = [get_situation_id(s) for s in situation_names]
    situation_ids = [s for s in situation_ids if s]
    source_reliability = 'attributed' if source else 'unknown'
    cur.execute("""
        INSERT INTO quotes (id, text, text_original, original_language, author_id, source, year,
                            keywords, situation, keyword_ids, situation_ids, status, source_reliability,
                            collection_log_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'draft', %s, %s)
    """, (
        qid, text, text_original, original_language, author_id, source, year,
        Json(keyword_names), Json(situation_names),
        keyword_ids if keyword_ids else None,
        situation_ids if situation_ids else None,
        source_reliability, log_id
    ))
    return True

# 기존 collection_log 조회
cur.execute("SELECT id FROM collection_logs WHERE category = '공부/학습' ORDER BY created_at DESC LIMIT 1")
log_study = cur.fetchone()[0]
cur.execute("SELECT id FROM collection_logs WHERE category = '유머/위트' ORDER BY created_at DESC LIMIT 1")
log_humor = cur.fetchone()[0]
cur.execute("SELECT id FROM collection_logs WHERE category = '과학/철학' ORDER BY created_at DESC LIMIT 1")
log_science = cur.fetchone()[0]

# 저자 등록
authors_extra = {
    "퇴계 이황": ("KR", 1501, "학자", "학술", "철학"),  # 이황과 같은 사람이지만 기존 author 사용
    "이이": ("KR", 1536, "학자", "학술", "철학"),
    "정약용": ("KR", 1762, "학자", "학술", "철학"),
    "순자": ("CN", -313, "사상가", "사상", "철학"),
    "한국 속담": ("KR", None, "민간 전승", "민간", "문화"),
    "에르빈 슈뢰딩거": ("AT", 1887, "물리학자", "과학", "과학"),
    "로버트 오펜하이머": ("US", 1904, "물리학자", "과학", "과학"),
    "칼 포퍼": ("AT", 1902, "철학자", "철학", "철학"),
    "장폴 사르트르": ("FR", 1905, "철학자", "철학", "철학"),
    "미셸 푸코": ("FR", 1926, "철학자", "철학", "철학"),
    "한나 아렌트": ("DE", 1906, "철학자", "철학", "철학"),
    "리처드 파인만": ("US", 1918, "물리학자", "과학", "과학"),
    "닐스 보어": ("DK", 1885, "물리학자", "과학", "과학"),
    "칼 세이건": ("US", 1934, "과학자", "과학", "과학"),
    "스티븐 호킹": ("GB", 1942, "물리학자", "과학", "과학"),
    "이어령": ("KR", 1934, "학자", "학술", "문화"),
    "김용옥": ("KR", 1948, "철학자", "철학", "철학"),
    "맹자": ("CN", -372, "철학자", "철학", "철학"),
    "송시열": ("KR", 1607, "학자", "학술", "철학"),
    "박명수": ("KR", 1970, "코미디언", "예술", "문화"),
    "임마누엘 칸트": ("DE", 1724, "철학자", "철학", "철학"),
    "르네 데카르트": ("FR", 1596, "철학자", "철학", "철학"),
}

author_ids = {}
for name, (nat, birth, prof, prof_group, field) in authors_extra.items():
    author_ids[name] = get_or_create_author(name, nat, birth, prof, prof_group, field)

# ── 공부/학습 추가 3개 ──
study_extra = [
    (
        "독서란 다른 사람의 머리로 생각하는 것이다. 하지만 결국 자기 것으로 만들어야 한다.",
        "독서란 다른 사람의 머리로 생각하는 것이다. 하지만 결국 자기 것으로 만들어야 한다.", "ko",
        "송시열", None, None,
        ["학습", "지식", "자기성찰"], ["배움의 자세", "깊이 이해하고 싶을 때"]
    ),
    (
        "가르치는 일은 다시 배우는 일이다.",
        "가르치는 일은 다시 배우는 일이다.", "ko",
        "이이", None, None,
        ["교육", "학습", "성장"], ["배움의 자세", "지식의 가치"]
    ),
    (
        "사람의 학문은 죽어서야 그만두는 것이다.",
        "人之學 死而後已", "zh",
        "순자", "순자", None,
        ["학습", "끈기", "노력"], ["꾸준함이 필요할 때", "공부하기 싫을 때"]
    ),
]

# ── 유머/위트 추가 1개 ──
humor_extra = [
    (
        "원숭이도 나무에서 떨어진다지만, 나는 처음부터 올라간 적이 없다.",
        "원숭이도 나무에서 떨어진다지만, 나는 처음부터 올라간 적이 없다.", "ko",
        "한국 속담", None, None,
        ["유머", "겸손"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
]

# ── 과학/철학 추가 8개 ──
science_extra = [
    (
        "관찰자 없이는 양자역학의 파동함수는 존재하지 않는다. 우리가 보기 전까지 세계는 정해져 있지 않다.",
        "The task is not so much to see what no one has yet seen; but to think what nobody has yet thought, about that which everybody sees.", "en",
        "에르빈 슈뢰딩거", None, None,
        ["과학", "존재", "철학"], ["과학적 사고", "새로운 관점이 필요할 때"]
    ),
    (
        "나는 이제 죽음이 되었다. 세계의 파괴자가 되었다.",
        "Now I am become Death, the destroyer of worlds.", "en",
        "로버트 오펜하이머", None, 1945,
        ["과학", "죽음", "운명"], ["과학적 사고", "죽음을 생각할 때"]
    ),
    (
        "과학적 이론은 반증 가능해야 한다. 반증될 수 없는 이론은 과학이 아니다.",
        "A theory that explains everything, explains nothing.", "en",
        "칼 포퍼", "추측과 논박", 1963,
        ["과학", "지식", "지혜"], ["과학적 사고", "깊이 이해하고 싶을 때"]
    ),
    (
        "타인은 지옥이다.",
        "L'enfer, c'est les autres.", "fr",
        "장폴 사르트르", "닫힌 방", 1944,
        ["철학", "관계", "존재"], ["관계가 어려울 때", "자기 성찰"]
    ),
    (
        "자기 자신을 아는 것이야말로 모든 지혜의 시작이다.",
        "Connais-toi toi-même.", "fr",
        "미셸 푸코", None, None,
        ["철학", "자기성찰", "지혜"], ["자기 성찰", "배움의 자세"]
    ),
    (
        "용서란 피해자의 것이 아니라 세계의 것이다. 용서는 새로운 시작을 가능하게 한다.",
        "Forgiveness is the key to action and freedom.", "en",
        "한나 아렌트", "인간의 조건", 1958,
        ["철학", "자유", "용기"], ["관계가 어려울 때", "새로운 시작"]
    ),
    (
        "지금까지 철학자들은 세계를 해석하기만 했다. 중요한 것은 세계를 변화시키는 것이다.",
        "Sapere aude! Habe Mut dich deines eigenen Verstandes zu bedienen!", "de",
        "임마누엘 칸트", "계몽이란 무엇인가", 1784,
        ["철학", "행동", "변화"], ["용기가 필요할 때", "새로운 관점이 필요할 때"]
    ),
    (
        "우주에서 가장 이해할 수 없는 것은 그것이 이해 가능하다는 사실이다.",
        "The most incomprehensible thing about the universe is that it is comprehensible.", "en",
        "스티븐 호킹", None, None,
        ["과학", "지혜", "초월"], ["과학적 사고", "삶의 의미를 찾을 때"]
    ),
]

saved_s, dup_s = 0, 0
for q in study_extra:
    text, text_orig, lang, author_name, source, year, kws, sits = q
    aid = author_ids[author_name]
    if insert_quote(text, text_orig, lang, aid, source, year, kws, sits, log_study):
        saved_s += 1
    else:
        dup_s += 1

saved_h, dup_h = 0, 0
for q in humor_extra:
    text, text_orig, lang, author_name, source, year, kws, sits = q
    aid = author_ids[author_name]
    if insert_quote(text, text_orig, lang, aid, source, year, kws, sits, log_humor):
        saved_h += 1
    else:
        dup_h += 1

saved_sc, dup_sc = 0, 0
for q in science_extra:
    text, text_orig, lang, author_name, source, year, kws, sits = q
    aid = author_ids[author_name]
    if insert_quote(text, text_orig, lang, aid, source, year, kws, sits, log_science):
        saved_sc += 1
    else:
        dup_sc += 1

# collection_logs 업데이트 (기존 saved_count에 추가)
cur.execute("UPDATE collection_logs SET saved_count = COALESCE(saved_count,0) + %s, duplicate_count = COALESCE(duplicate_count,0) + %s WHERE id=%s",
            (saved_s, dup_s, log_study))
cur.execute("UPDATE collection_logs SET saved_count = COALESCE(saved_count,0) + %s, duplicate_count = COALESCE(duplicate_count,0) + %s WHERE id=%s",
            (saved_h, dup_h, log_humor))
cur.execute("UPDATE collection_logs SET saved_count = COALESCE(saved_count,0) + %s, duplicate_count = COALESCE(duplicate_count,0) + %s WHERE id=%s",
            (saved_sc, dup_sc, log_science))

conn.commit()

print("=" * 60)
print("추가 저장 완료!")
print("=" * 60)
print(f"공부/학습 추가: {saved_s}개 저장, {dup_s}개 중복")
print(f"유머/위트 추가: {saved_h}개 저장, {dup_h}개 중복")
print(f"과학/철학 추가: {saved_sc}개 저장, {dup_sc}개 중복")
print(f"총 추가 저장: {saved_s + saved_h + saved_sc}개")
print("=" * 60)

cur.close()
conn.close()
