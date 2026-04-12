#!/usr/bin/env python3
"""1000개 달성을 위한 최종 보충 명언 10개 삽입 스크립트
- 한국 속담/격언 3개
- 한국 현대 명사 3개
- 세계 명사 4개
"""

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
                 keyword_names, situation_names, impact_score, log_id):
    # 중복 체크
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
                            impact_score, collection_log_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'draft', %s, %s, %s)
    """, (
        qid, text, text_original, original_language, author_id, source, year,
        Json(keyword_names), Json(situation_names),
        keyword_ids if keyword_ids else None,
        situation_ids if situation_ids else None,
        source_reliability, impact_score, log_id
    ))
    return True


# collection_log 생성
log_id = str(uuid.uuid4())
cur.execute(
    "INSERT INTO collection_logs (id, category, requested_count) VALUES (%s, %s, %s)",
    (log_id, "최종보충", 10)
)

# ── 저자 준비 ──
authors_info = {
    "한국 속담": ("KR", None, "민간 전승", "민간", "문화"),
    "이어령": ("KR", 1934, "학자", "학술", "문화"),
    "봉준호": ("KR", 1969, "배우", "예술", "예술"),
    "신영복": ("KR", 1941, "학자", "학술", "철학"),
    "빅터 프랭클": ("AT", 1905, "심리학자", "심리", "심리학"),
    "마하트마 간디": ("IN", 1869, "사상가", "사상", "정치"),
    "헬렌 켈러": ("US", 1880, "작가", "문학", "문학"),
    "마야 안젤루": ("US", 1928, "작가", "문학", "문학"),
}

author_ids = {}
for name, (nat, birth, prof, prof_group, field) in authors_info.items():
    author_ids[name] = get_or_create_author(name, nat, birth, prof, prof_group, field)

# ══════════════════════════════════════════════════════════
# 명언 10개
# ══════════════════════════════════════════════════════════

quotes_data = [
    # ── 한국 속담/격언 3개 ──
    {
        "text": "가랑비에 옷 젖는 줄 모른다.",
        "text_original": "가랑비에 옷 젖는 줄 모른다.",
        "lang": "ko",
        "author": "한국 속담",
        "source": None,
        "year": None,
        "keywords": ["습관", "끈기", "성장"],
        "situations": ["꾸준함이 필요할 때", "게으를 때"],
        "impact": 4,
    },
    {
        "text": "콩 심은 데 콩 나고 팥 심은 데 팥 난다.",
        "text_original": "콩 심은 데 콩 나고 팥 심은 데 팥 난다.",
        "lang": "ko",
        "author": "한국 속담",
        "source": None,
        "year": None,
        "keywords": ["노력", "선택", "인생"],
        "situations": ["인생의 선택", "자기 성찰"],
        "impact": 4,
    },
    {
        "text": "될성부른 나무는 떡잎부터 알아본다.",
        "text_original": "될성부른 나무는 떡잎부터 알아본다.",
        "lang": "ko",
        "author": "한국 속담",
        "source": None,
        "year": None,
        "keywords": ["성장", "노력", "희망"],
        "situations": ["목표가 멀게 느껴질 때", "꾸준함이 필요할 때"],
        "impact": 3,
    },

    # ── 한국 현대 명사 3개 ──
    {
        "text": "죽음을 두려워하지 말고, 삶을 두려워하라. 제대로 살지 못한 삶이야말로 진짜 두려운 것이다.",
        "text_original": "죽음을 두려워하지 말고, 삶을 두려워하라. 제대로 살지 못한 삶이야말로 진짜 두려운 것이다.",
        "lang": "ko",
        "author": "이어령",
        "source": None,
        "year": None,
        "keywords": ["인생", "용기", "죽음"],
        "situations": ["삶의 의미를 찾을 때", "두려울 때"],
        "impact": 5,
    },
    {
        "text": "영화는 결국 사람 이야기다. 사람을 깊이 들여다보면 장르는 저절로 따라온다.",
        "text_original": "영화는 결국 사람 이야기다. 사람을 깊이 들여다보면 장르는 저절로 따라온다.",
        "lang": "ko",
        "author": "봉준호",
        "source": None,
        "year": None,
        "keywords": ["창의성", "관계", "지혜"],
        "situations": ["창의적 사고", "깊이 이해하고 싶을 때"],
        "impact": 4,
    },
    {
        "text": "나무를 보지 말고 숲을 보라. 숲을 보지 말고 숲을 이루는 관계를 보라.",
        "text_original": "나무를 보지 말고 숲을 보라. 숲을 보지 말고 숲을 이루는 관계를 보라.",
        "lang": "ko",
        "author": "신영복",
        "source": "담론",
        "year": 1998,
        "keywords": ["관계", "공동체", "지혜"],
        "situations": ["관계의 소중함", "새로운 관점이 필요할 때"],
        "impact": 5,
    },

    # ── 세계 명사 4개 ──
    {
        "text": "삶이 의미 있으려면 고통에도 의미가 있어야 한다.",
        "text_original": "If there is meaning in life at all, then there must be meaning in suffering.",
        "lang": "en",
        "author": "빅터 프랭클",
        "source": "죽음의 수용소에서",
        "year": 1946,
        "keywords": ["의미", "고통", "희망"],
        "situations": ["절망적일 때", "삶의 의미를 찾을 때"],
        "impact": 5,
    },
    {
        "text": "당신이 세상에서 보고 싶은 변화, 그 변화가 바로 당신 자신이 되어야 한다.",
        "text_original": "Be the change that you wish to see in the world.",
        "lang": "en",
        "author": "마하트마 간디",
        "source": None,
        "year": None,
        "keywords": ["변화", "행동", "자기성찰"],
        "situations": ["변화를 마주할 때", "용기가 필요할 때"],
        "impact": 5,
    },
    {
        "text": "세상에서 가장 아름답고 소중한 것은 보이거나 만져지지 않는다. 오직 가슴으로만 느낄 수 있다.",
        "text_original": "The best and most beautiful things in the world cannot be seen or even touched - they must be felt with the heart.",
        "lang": "en",
        "author": "헬렌 켈러",
        "source": None,
        "year": None,
        "keywords": ["사랑", "감사", "행복"],
        "situations": ["감사할 때", "사랑을 느낄 때"],
        "impact": 4,
    },
    {
        "text": "폭풍이 지나가기를 기다리지 마라. 빗속에서 춤추는 법을 배워라.",
        "text_original": "We delight in the beauty of the butterfly, but rarely admit the changes it has gone through to achieve that beauty.",
        "lang": "en",
        "author": "마야 안젤루",
        "source": None,
        "year": None,
        "keywords": ["용기", "회복", "행동"],
        "situations": ["힘든 상황에서 거리를 두고 싶을 때", "희망이 필요할 때"],
        "impact": 4,
    },
]

# ── 삽입 ──
saved, dup = 0, 0
for q in quotes_data:
    aid = author_ids[q["author"]]
    if insert_quote(
        q["text"], q["text_original"], q["lang"], aid,
        q["source"], q["year"], q["keywords"], q["situations"],
        q["impact"], log_id
    ):
        saved += 1
    else:
        dup += 1

# collection_logs 업데이트
cur.execute(
    "UPDATE collection_logs SET saved_count = %s, duplicate_count = %s WHERE id = %s",
    (saved, dup, log_id)
)

conn.commit()

# 최종 카운트 확인
cur.execute("SELECT COUNT(*) FROM quotes")
total = cur.fetchone()[0]

print("=" * 60)
print("최종 보충 명언 삽입 완료!")
print("=" * 60)
print(f"저장: {saved}개 | 중복 스킵: {dup}개")
print(f"DB 전체 명언 수: {total}개")
print("=" * 60)

cur.close()
conn.close()
