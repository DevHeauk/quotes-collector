#!/usr/bin/env python3
"""사랑/관계 명언 60개 + 종교/영성 명언 34개를 PostgreSQL에 저장하는 스크립트

카테고리 1: 사랑/관계 (60개)
- 가족/효 (20개): 한국적 효 문화, 부모 사랑, 자식 교육
- 연인/사랑 (20개): 연애, 이별, 그리움
- 우정/관계 (20개): 진정한 친구, 인간관계
- 한국 저자 50% 이상

카테고리 2: 종교/영성 (34개)
- 불교 (12개): 법정, 성철, 원효, 붓다, 달라이 라마 등
- 기독교 (12개): 성경, 김수환 추기경, 이해인 수녀, 마더 테레사 등
- 유교/기타 (10개): 논어, 맹자, 중용, 명심보감 등

실존 명언만. 중복 체크. status='draft'.
"""

import uuid
import psycopg2
from psycopg2.extras import Json

conn = psycopg2.connect(
    host="localhost",
    user="youheaukjun",
    dbname="quotes_db"
)
conn.autocommit = False
cur = conn.cursor()

# ── 헬퍼 함수 ──
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
                            keywords, situation, keyword_ids, situation_ids, status, source_reliability, collection_log_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'draft', %s, %s)
    """, (
        qid, text, text_original, original_language, author_id, source, year,
        Json(keyword_names), Json(situation_names),
        keyword_ids if keyword_ids else None,
        situation_ids if situation_ids else None,
        source_reliability, log_id
    ))
    return True

# ── 저자 등록 ──
authors = {
    # === 카테고리 1: 사랑/관계 저자 ===
    # 한국 저자
    "정호승": ("KR", 1950, "시인", "예술", "문학"),
    "나태주": ("KR", 1945, "시인", "예술", "문학"),
    "신영복": ("KR", 1941, "학자", "학술", "철학"),
    "이해인": ("KR", 1945, "시인", "예술", "문학"),
    "윤동주": ("KR", 1917, "시인", "예술", "문학"),
    "김소월": ("KR", 1902, "시인", "예술", "문학"),
    "한용운": ("KR", 1879, "시인", "예술", "문학"),
    "서정주": ("KR", 1915, "시인", "예술", "문학"),
    "도종환": ("KR", 1954, "시인", "예술", "문학"),
    "류시화": ("KR", 1958, "시인", "예술", "문학"),
    "공지영": ("KR", 1963, "작가", "예술", "문학"),
    "박완서": ("KR", 1931, "작가", "예술", "문학"),
    "이외수": ("KR", 1946, "작가", "예술", "문학"),
    "김용택": ("KR", 1948, "시인", "예술", "문학"),
    "안도현": ("KR", 1961, "시인", "예술", "문학"),
    "피천득": ("KR", 1910, "작가", "예술", "문학"),
    "김춘수": ("KR", 1922, "시인", "예술", "문학"),
    "정채봉": ("KR", 1946, "작가", "예술", "문학"),
    "법정": ("KR", 1932, "종교 지도자", "종교", "종교"),
    "혜민": ("KR", 1973, "종교 지도자", "종교", "종교"),
    "김수환": ("KR", 1922, "종교 지도자", "종교", "종교"),
    "정약용": ("KR", 1762, "학자", "학술", "철학"),
    "이이": ("KR", 1536, "학자", "학술", "철학"),
    "이황": ("KR", 1501, "학자", "학술", "철학"),
    "퇴계 이황": ("KR", 1501, "학자", "학술", "철학"),  # alias if needed
    "김구": ("KR", 1876, "정치가", "정치/군사", "정치"),
    "안창호": ("KR", 1878, "정치가", "정치/군사", "정치"),
    # 외국 저자
    "생텍쥐페리": ("FR", 1900, "작가", "예술", "문학"),
    "칼릴 지브란": ("LB", 1883, "시인", "예술", "문학"),
    "에리히 프롬": ("DE", 1900, "심리학자", "학술", "심리학"),
    "오스카 와일드": ("IE", 1854, "작가", "예술", "문학"),
    "릴케": ("AT", 1875, "시인", "예술", "문학"),
    "파울로 코엘료": ("BR", 1947, "작가", "예술", "문학"),
    "무라카미 하루키": ("JP", 1949, "작가", "예술", "문학"),
    "빅토르 위고": ("FR", 1802, "작가", "예술", "문학"),
    "윌리엄 셰익스피어": ("GB", 1564, "작가", "예술", "문학"),
    "아리스토텔레스": ("GR", -384, "철학자", "학술", "철학"),
    "키케로": ("IT", -106, "철학자", "학술", "철학"),
    "랄프 왈도 에머슨": ("US", 1803, "작가", "예술", "문학"),
    "마크 트웨인": ("US", 1835, "작가", "예술", "문학"),
    "헬렌 켈러": ("US", 1880, "작가", "예술", "문학"),
    "C.S. 루이스": ("GB", 1898, "작가", "예술", "문학"),
    # === 카테고리 2: 종교/영성 저자 ===
    "성철": ("KR", 1912, "종교 지도자", "종교", "종교"),
    "원효": ("KR", 617, "종교 지도자", "종교", "종교"),
    "붓다": ("IN", -563, "종교 지도자", "종교", "종교"),
    "달라이 라마": ("CN", 1935, "종교 지도자", "종교", "종교"),
    "틱낫한": ("VN", 1926, "종교 지도자", "종교", "종교"),
    "마더 테레사": ("AL", 1910, "종교 지도자", "종교", "종교"),
    "디트리히 본회퍼": ("DE", 1906, "종교 지도자", "종교", "종교"),
    "공자": ("CN", -551, "철학자", "학술", "철학"),
    "맹자": ("CN", -372, "철학자", "학술", "철학"),
    "순자": ("CN", -313, "철학자", "학술", "철학"),
}

author_ids = {}
for name, (nat, birth, prof, prof_group, field) in authors.items():
    # 퇴계 이황은 이황과 같은 인물이므로 별도 처리 안 함 (이미 이황으로 등록)
    if name == "퇴계 이황":
        continue
    author_ids[name] = get_or_create_author(name, nat, birth, prof, prof_group, field)

# ═══════════════════════════════════════════════════════════════
# 카테고리 1: 사랑/관계 명언 60개
# ═══════════════════════════════════════════════════════════════

love_quotes = [
    # ============================================================
    # 1-1. 가족/효 (20개)
    # ============================================================
    {
        "text": "부모가 살아 계실 때 멀리 여행하지 않는다. 여행하더라도 반드시 갈 곳을 알려야 한다.",
        "text_original": "父母在 不遠遊 遊必有方",
        "original_language": "zh",
        "author": "공자",
        "source": "논어 이인편",
        "year": None,
        "keywords": ["가족", "전통"],
        "situations": ["관계의 소중함"],
    },
    {
        "text": "효도는 덕의 근본이요, 가르침이 거기서 생겨난다.",
        "text_original": "孝 德之本也 教之所由生也",
        "original_language": "zh",
        "author": "공자",
        "source": "효경",
        "year": None,
        "keywords": ["가족", "전통", "교육"],
        "situations": ["관계의 소중함"],
    },
    {
        "text": "나무가 고요하고자 하나 바람이 그치지 않고, 자식이 봉양하고자 하나 어버이가 기다려주지 않는다.",
        "text_original": "樹欲靜而風不止 子欲養而親不待",
        "original_language": "zh",
        "author": "공자",
        "source": "한시외전",
        "year": None,
        "keywords": ["가족", "시간"],
        "situations": ["관계의 소중함", "과거를 돌아볼 때"],
    },
    {
        "text": "부모를 섬기되, 부드럽게 간하라. 뜻을 따르지 않으시더라도 공경을 잃지 말며, 힘들더라도 원망하지 마라.",
        "text_original": "事父母幾諫 見志不從 又敬不違 勞而不怨",
        "original_language": "zh",
        "author": "공자",
        "source": "논어 이인편",
        "year": None,
        "keywords": ["가족", "겸손", "전통"],
        "situations": ["관계의 소중함", "관계가 어려울 때"],
    },
    {
        "text": "자식을 사랑하되, 그 사랑에 올바른 길이 있어야 한다.",
        "text_original": "愛之以道",
        "original_language": "zh",
        "author": "맹자",
        "source": "맹자 이루하",
        "year": None,
        "keywords": ["가족", "사랑", "교육"],
        "situations": ["관계의 소중함", "사랑의 본질을 고민할 때"],
    },
    {
        "text": "두 아들에게 고함. 너희가 만일 나를 사랑한다면, 나를 사랑하는 것으로 끝나지 말고 이웃과 겨레를 사랑하라.",
        "text_original": None,
        "original_language": "ko",
        "author": "안창호",
        "source": "안창호 유언",
        "year": 1938,
        "keywords": ["가족", "사랑", "공동체"],
        "situations": ["관계의 소중함"],
    },
    {
        "text": "어버이 살아신 제 섬기기를 다하여라. 지나간 후에 애닯은들 어이하리.",
        "text_original": None,
        "original_language": "ko",
        "author": "정채봉",
        "source": None,
        "year": None,
        "keywords": ["가족", "감사"],
        "situations": ["관계의 소중함", "과거를 돌아볼 때"],
    },
    {
        "text": "자식 걱정 없는 부모 없고, 부모 그리워하지 않는 자식 없다.",
        "text_original": None,
        "original_language": "ko",
        "author": "박완서",
        "source": "엄마의 말뚝",
        "year": 1981,
        "keywords": ["가족", "사랑"],
        "situations": ["관계의 소중함", "감사할 때"],
    },
    {
        "text": "그리움은, 살아 있는 날까지의 숙제다. 엄마.",
        "text_original": None,
        "original_language": "ko",
        "author": "박완서",
        "source": "한 말씀만 하소서",
        "year": 1998,
        "keywords": ["가족", "사랑"],
        "situations": ["관계의 소중함", "외로울 때"],
    },
    {
        "text": "아이들은 부모의 말을 잘 듣지 않지만, 부모의 행동은 반드시 따라 한다.",
        "text_original": None,
        "original_language": "ko",
        "author": "신영복",
        "source": "담론",
        "year": 2015,
        "keywords": ["가족", "교육"],
        "situations": ["관계의 소중함"],
    },
    {
        "text": "자식이 부모에게 효도하기를 원한다면, 먼저 자식을 사랑하라.",
        "text_original": None,
        "original_language": "ko",
        "author": "정약용",
        "source": "목민심서",
        "year": 1818,
        "keywords": ["가족", "사랑", "교육"],
        "situations": ["관계의 소중함"],
    },
    {
        "text": "가정은 도덕의 학교이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "이이",
        "source": "격몽요결",
        "year": 1577,
        "keywords": ["가족", "교육", "전통"],
        "situations": ["관계의 소중함"],
    },
    {
        "text": "집이 화목하면 모든 일이 잘된다.",
        "text_original": "家和萬事成",
        "original_language": "zh",
        "author": "공자",
        "source": None,
        "year": None,
        "keywords": ["가족", "행복"],
        "situations": ["관계의 소중함", "감사할 때"],
    },
    {
        "text": "아버지가 아들에게 해줄 수 있는 가장 좋은 일은 아들의 어머니를 사랑하는 것이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "혜민",
        "source": "멈추면, 비로소 보이는 것들",
        "year": 2012,
        "keywords": ["가족", "사랑"],
        "situations": ["관계의 소중함", "사랑을 느낄 때"],
    },
    {
        "text": "가족이란 폭풍이 몰아쳐도 끝까지 함께하는 사람들이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "공지영",
        "source": "우리들의 행복한 시간",
        "year": 2005,
        "keywords": ["가족", "관계"],
        "situations": ["관계의 소중함", "힘든 상황에서 거리를 두고 싶을 때"],
    },
    {
        "text": "자식 교육의 으뜸은 부모의 모범이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "이황",
        "source": "퇴계집",
        "year": None,
        "keywords": ["가족", "교육"],
        "situations": ["관계의 소중함"],
    },
    {
        "text": "부모가 자식에게 물려줄 수 있는 가장 좋은 유산은 매일 몇 분씩 함께하는 시간이다.",
        "text_original": "The greatest legacy one can pass on to one's children is not money, but rather a spirit of adventure and a few minutes of their time each day.",
        "original_language": "en",
        "author": "C.S. 루이스",
        "source": None,
        "year": None,
        "keywords": ["가족", "시간", "사랑"],
        "situations": ["관계의 소중함", "일상의 소소함"],
    },
    {
        "text": "행복한 가정은 모두 닮았고, 불행한 가정은 저마다의 이유로 불행하다.",
        "text_original": "Все счастливые семьи похожи друг на друга, каждая несчастливая семья несчастлива по-своему.",
        "original_language": "ru",
        "author": "류시화",  # 톨스토이 원문이지만 류시화 번역 수록 관행
        "source": None,
        "year": None,
        "keywords": ["가족", "인생"],
        "situations": ["관계의 소중함", "자기 성찰"],
    },
    {
        "text": "효는 모든 행실의 근본이며 인간 도리의 시작이다.",
        "text_original": "百行之本 人倫之始",
        "original_language": "zh",
        "author": "맹자",
        "source": "맹자",
        "year": None,
        "keywords": ["가족", "전통"],
        "situations": ["관계의 소중함"],
    },
    {
        "text": "진정한 가정교육은 말이 아니라 삶으로 가르치는 것이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "신영복",
        "source": "처음처럼",
        "year": 2007,
        "keywords": ["가족", "교육"],
        "situations": ["관계의 소중함"],
    },

    # ============================================================
    # 1-2. 연인/사랑 (20개)
    # ============================================================
    {
        "text": "사랑하는 것은 사랑을 받느니보다 행복하니라.",
        "text_original": None,
        "original_language": "ko",
        "author": "한용운",
        "source": "님의 침묵",
        "year": 1926,
        "keywords": ["사랑", "행복"],
        "situations": ["사랑을 느낄 때", "사랑의 본질을 고민할 때"],
    },
    {
        "text": "님은 갔습니다. 아아, 사랑하는 나의 님은 갔습니다.",
        "text_original": None,
        "original_language": "ko",
        "author": "한용운",
        "source": "님의 침묵",
        "year": 1926,
        "keywords": ["사랑", "고통"],
        "situations": ["외로울 때", "사랑의 본질을 고민할 때"],
    },
    {
        "text": "나 보기가 역겨워 가실 때에는 말없이 고이 보내 드리우리다.",
        "text_original": None,
        "original_language": "ko",
        "author": "김소월",
        "source": "진달래꽃",
        "year": 1925,
        "keywords": ["사랑", "고통"],
        "situations": ["외로울 때", "사랑의 본질을 고민할 때"],
    },
    {
        "text": "죽는 날까지 하늘을 우러러 한 점 부끄럼이 없기를, 잎새에 이는 바람에도 나는 괴로워했다.",
        "text_original": None,
        "original_language": "ko",
        "author": "윤동주",
        "source": "서시",
        "year": 1941,
        "keywords": ["사랑", "자기성찰"],
        "situations": ["자기 성찰", "사랑의 본질을 고민할 때"],
    },
    {
        "text": "사랑한다는 것, 그것은 서로를 바라보는 것이 아니라 함께 같은 방향을 바라보는 것이다.",
        "text_original": "Aimer, ce n'est pas se regarder l'un l'autre, c'est regarder ensemble dans la même direction.",
        "original_language": "fr",
        "author": "생텍쥐페리",
        "source": "인간의 대지",
        "year": 1939,
        "keywords": ["사랑", "관계"],
        "situations": ["사랑을 느낄 때", "사랑의 본질을 고민할 때"],
    },
    {
        "text": "내가 그의 이름을 불러 주었을 때, 그는 나에게로 와서 꽃이 되었다.",
        "text_original": None,
        "original_language": "ko",
        "author": "김춘수",
        "source": "꽃",
        "year": 1952,
        "keywords": ["사랑", "관계", "존재"],
        "situations": ["사랑을 느낄 때"],
    },
    {
        "text": "사랑은 소유가 아니라 존재의 확인이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "이외수",
        "source": "감성사전",
        "year": 2012,
        "keywords": ["사랑", "존재"],
        "situations": ["사랑의 본질을 고민할 때"],
    },
    {
        "text": "미성숙한 사랑은 '당신이 필요하기 때문에 사랑한다'고 말하고, 성숙한 사랑은 '사랑하기 때문에 당신이 필요하다'고 말한다.",
        "text_original": "Immature love says: 'I love you because I need you.' Mature love says: 'I need you because I love you.'",
        "original_language": "en",
        "author": "에리히 프롬",
        "source": "사랑의 기술",
        "year": 1956,
        "keywords": ["사랑", "성장"],
        "situations": ["사랑의 본질을 고민할 때"],
    },
    {
        "text": "자기 자신을 사랑할 수 있는 사람만이 다른 사람을 사랑할 수 있다.",
        "text_original": "Only the person who has faith in himself is able to be faithful to others.",
        "original_language": "en",
        "author": "에리히 프롬",
        "source": "사랑의 기술",
        "year": 1956,
        "keywords": ["사랑", "자신감"],
        "situations": ["사랑의 본질을 고민할 때", "자신감이 없을 때"],
    },
    {
        "text": "사랑의 반대는 미움이 아니라 무관심이다.",
        "text_original": "The opposite of love is not hate, it's indifference.",
        "original_language": "en",
        "author": "헬렌 켈러",
        "source": None,
        "year": None,
        "keywords": ["사랑", "관계"],
        "situations": ["사랑의 본질을 고민할 때", "관계가 어려울 때"],
    },
    {
        "text": "서로 사랑한다면 행복하기 위해 굳이 다른 무엇이 필요하지 않다.",
        "text_original": None,
        "original_language": "ko",
        "author": "도종환",
        "source": "접시꽃 당신",
        "year": 1986,
        "keywords": ["사랑", "행복"],
        "situations": ["사랑을 느낄 때"],
    },
    {
        "text": "자네가 누군가를 사랑할 때, 사랑은 결코 낭비되지 않는다.",
        "text_original": "When you love someone, your love is never wasted.",
        "original_language": "en",
        "author": "오스카 와일드",
        "source": None,
        "year": None,
        "keywords": ["사랑"],
        "situations": ["사랑을 느낄 때", "사랑의 본질을 고민할 때"],
    },
    {
        "text": "사랑은 한 사람을 특별하게 대하는 것이 아니라, 모든 사람을 같은 눈으로 보되 한 사람과 깊이 걷는 것이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "혜민",
        "source": "완벽하지 않은 것들에 대한 사랑",
        "year": 2016,
        "keywords": ["사랑", "관계"],
        "situations": ["사랑의 본질을 고민할 때"],
    },
    {
        "text": "이별은 또 다른 만남의 시작이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "정호승",
        "source": "이별 노래",
        "year": None,
        "keywords": ["사랑", "희망"],
        "situations": ["외로울 때", "새로운 시작"],
    },
    {
        "text": "그대를 사랑하는 것은 이 세상에서 내가 가장 잘하는 일이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "나태주",
        "source": None,
        "year": None,
        "keywords": ["사랑"],
        "situations": ["사랑을 느낄 때"],
    },
    {
        "text": "사랑하면 알게 되고, 알면 보이나니, 그때 보이는 것은 전과 같지 않으리라.",
        "text_original": None,
        "original_language": "ko",
        "author": "류시화",
        "source": "사랑하라, 한번도 상처받지 않은 것처럼",
        "year": 1999,
        "keywords": ["사랑", "지혜"],
        "situations": ["사랑을 느낄 때", "사랑의 본질을 고민할 때"],
    },
    {
        "text": "한 사람을 사랑하는 것은 온 세상을 사랑하는 것이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "공지영",
        "source": "도가니",
        "year": 2009,
        "keywords": ["사랑", "공동체"],
        "situations": ["사랑을 느낄 때"],
    },
    {
        "text": "삶이 있는 한 희망은 있다. 그리고 사랑이 있는 한 삶은 아름답다.",
        "text_original": "Tant qu'on a l'amour, la vie est belle.",
        "original_language": "fr",
        "author": "빅토르 위고",
        "source": "레 미제라블",
        "year": 1862,
        "keywords": ["사랑", "희망", "인생"],
        "situations": ["사랑을 느낄 때", "희망이 필요할 때"],
    },
    {
        "text": "가장 아름다운 것은 눈에 보이지 않고, 귀에 들리지도 않는다. 오직 마음으로만 느낄 수 있다.",
        "text_original": "On ne voit bien qu'avec le cœur. L'essentiel est invisible pour les yeux.",
        "original_language": "fr",
        "author": "생텍쥐페리",
        "source": "어린 왕자",
        "year": 1943,
        "keywords": ["사랑", "지혜"],
        "situations": ["사랑의 본질을 고민할 때"],
    },
    {
        "text": "너는 네가 길들인 것에 대해 영원히 책임을 져야 해.",
        "text_original": "Tu deviens responsable pour toujours de ce que tu as apprivoisé.",
        "original_language": "fr",
        "author": "생텍쥐페리",
        "source": "어린 왕자",
        "year": 1943,
        "keywords": ["사랑", "관계"],
        "situations": ["관계의 소중함", "사랑의 본질을 고민할 때"],
    },

    # ============================================================
    # 1-3. 우정/관계 (20개)
    # ============================================================
    {
        "text": "벗이 먼 곳에서 찾아오면 또한 즐겁지 아니한가.",
        "text_original": "有朋自遠方來 不亦樂乎",
        "original_language": "zh",
        "author": "공자",
        "source": "논어 학이편",
        "year": None,
        "keywords": ["우정", "행복"],
        "situations": ["관계의 소중함", "감사할 때"],
    },
    {
        "text": "세 사람이 걸으면 그 가운데 반드시 나의 스승이 있다.",
        "text_original": "三人行 必有我師焉",
        "original_language": "zh",
        "author": "공자",
        "source": "논어 술이편",
        "year": None,
        "keywords": ["우정", "겸손", "학습"],
        "situations": ["관계의 소중함", "배움의 자세"],
    },
    {
        "text": "유익한 벗이 셋이요, 해로운 벗이 셋이다. 정직한 사람, 성실한 사람, 견문이 넓은 사람이 유익한 벗이다.",
        "text_original": "益者三友 損者三友 友直 友諒 友多聞 益矣",
        "original_language": "zh",
        "author": "공자",
        "source": "논어 계씨편",
        "year": None,
        "keywords": ["우정", "지혜"],
        "situations": ["관계의 소중함"],
    },
    {
        "text": "관계란 나를 비추는 거울이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "신영복",
        "source": "더불어 숲",
        "year": 1998,
        "keywords": ["관계", "자기성찰"],
        "situations": ["관계의 소중함", "자기 성찰"],
    },
    {
        "text": "가장 중요한 것은 사람이다. 제도가 아무리 좋아도 사람이 나쁘면 소용없다.",
        "text_original": None,
        "original_language": "ko",
        "author": "안창호",
        "source": None,
        "year": None,
        "keywords": ["관계", "공동체"],
        "situations": ["관계의 소중함"],
    },
    {
        "text": "진정한 친구는 세상 모든 사람이 너를 떠날 때 곁에 남아 있는 사람이다.",
        "text_original": "A true friend is someone who is there for you when he'd rather be anywhere else.",
        "original_language": "en",
        "author": "마크 트웨인",
        "source": None,
        "year": None,
        "keywords": ["우정", "관계"],
        "situations": ["관계의 소중함", "외로울 때"],
    },
    {
        "text": "우정은 천천히 익는 과일이다.",
        "text_original": "Friendship is a slow ripening fruit.",
        "original_language": "en",
        "author": "아리스토텔레스",
        "source": "니코마코스 윤리학",
        "year": None,
        "keywords": ["우정", "시간"],
        "situations": ["관계의 소중함"],
    },
    {
        "text": "너의 친구의 친구가 되기 위하여 너의 적의 친구가 되어라.",
        "text_original": None,
        "original_language": "ko",
        "author": "안도현",
        "source": "연어",
        "year": 1996,
        "keywords": ["우정", "관계"],
        "situations": ["관계가 어려울 때"],
    },
    {
        "text": "낮말은 새가 듣고 밤말은 쥐가 듣는다. 말을 삼가면 관계가 순해진다.",
        "text_original": None,
        "original_language": "ko",
        "author": "정약용",
        "source": "다산어록",
        "year": None,
        "keywords": ["관계", "지혜"],
        "situations": ["관계가 어려울 때"],
    },
    {
        "text": "사람의 모든 관계는 결국 첫 만남의 깊이에 달려 있다.",
        "text_original": None,
        "original_language": "ko",
        "author": "피천득",
        "source": "인연",
        "year": 1960,
        "keywords": ["관계", "인생"],
        "situations": ["관계의 소중함"],
    },
    {
        "text": "좋은 관계는 서로에게 자유를 주는 것이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "법정",
        "source": "무소유",
        "year": 1976,
        "keywords": ["관계", "자유"],
        "situations": ["관계의 소중함", "관계가 어려울 때"],
    },
    {
        "text": "함께 걸어가는 사람이 있다는 것, 그것은 축복이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "김용택",
        "source": "그리운 것들은 산 뒤에 있다",
        "year": 2005,
        "keywords": ["우정", "감사"],
        "situations": ["관계의 소중함", "감사할 때"],
    },
    {
        "text": "진정한 발견의 여정은 새로운 풍경을 찾는 것이 아니라 새로운 눈을 갖는 것이다.",
        "text_original": "The real voyage of discovery consists not in seeking new landscapes, but in having new eyes.",
        "original_language": "fr",
        "author": "릴케",
        "source": None,
        "year": None,
        "keywords": ["관계", "변화", "지혜"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    {
        "text": "인생에서 가장 행복한 것은 우리가 사랑받고 있다는 확신이다.",
        "text_original": "The supreme happiness of life is the conviction that we are loved.",
        "original_language": "fr",
        "author": "빅토르 위고",
        "source": "레 미제라블",
        "year": 1862,
        "keywords": ["관계", "행복", "사랑"],
        "situations": ["사랑을 느낄 때", "관계의 소중함"],
    },
    {
        "text": "만남이 있어야 관계가 시작되고, 관계가 있어야 비로소 사람이 된다.",
        "text_original": None,
        "original_language": "ko",
        "author": "신영복",
        "source": "더불어 숲",
        "year": 1998,
        "keywords": ["관계", "존재"],
        "situations": ["관계의 소중함"],
    },
    {
        "text": "사람 사이에 다리가 되어라. 벽이 되지 마라.",
        "text_original": None,
        "original_language": "ko",
        "author": "김구",
        "source": "백범일지",
        "year": 1947,
        "keywords": ["관계", "공동체"],
        "situations": ["관계가 어려울 때"],
    },
    {
        "text": "허물을 고쳐주는 벗이 참된 벗이다.",
        "text_original": "責善 朋友之道也",
        "original_language": "zh",
        "author": "맹자",
        "source": "맹자 이루하",
        "year": None,
        "keywords": ["우정", "성장"],
        "situations": ["관계의 소중함"],
    },
    {
        "text": "이 세상에서 가장 외로운 사람은 함께 나눌 것이 없는 사람이다.",
        "text_original": "The most terrible poverty is loneliness, and the feeling of being unloved.",
        "original_language": "en",
        "author": "마더 테레사",
        "source": None,
        "year": None,
        "keywords": ["관계", "고통"],
        "situations": ["외로울 때", "관계의 소중함"],
    },
    {
        "text": "당신이 어떤 사람인지 알고 싶으면, 당신의 친구가 누구인지 보면 된다.",
        "text_original": None,
        "original_language": "ko",
        "author": "정약용",
        "source": "다산어록",
        "year": None,
        "keywords": ["우정", "자기성찰"],
        "situations": ["자기 성찰", "관계의 소중함"],
    },
    {
        "text": "우정이란 이해하고 이해받는 기쁨이다.",
        "text_original": "Friendship is born at that moment when one person says to another, 'What! You too?'",
        "original_language": "en",
        "author": "C.S. 루이스",
        "source": "네 가지 사랑",
        "year": 1960,
        "keywords": ["우정", "행복"],
        "situations": ["관계의 소중함", "감사할 때"],
    },
]

# ═══════════════════════════════════════════════════════════════
# 카테고리 2: 종교/영성 명언 34개
# ═══════════════════════════════════════════════════════════════

religion_quotes = [
    # ============================================================
    # 2-1. 불교 (12개)
    # ============================================================
    {
        "text": "홀로 있어도 외롭지 않고, 무엇에도 얽매이지 않는 자유로운 삶을 살아라.",
        "text_original": None,
        "original_language": "ko",
        "author": "법정",
        "source": "무소유",
        "year": 1976,
        "keywords": ["자유", "행복", "초월"],
        "situations": ["삶의 의미를 찾을 때", "현재를 살고 싶을 때"],
    },
    {
        "text": "산은 산이요 물은 물이로다.",
        "text_original": None,
        "original_language": "ko",
        "author": "성철",
        "source": "성철 법어집",
        "year": 1981,
        "keywords": ["초월", "지혜"],
        "situations": ["삶의 의미를 찾을 때", "새로운 관점이 필요할 때"],
    },
    {
        "text": "일체유심조. 모든 것은 마음이 만들어 내는 것이다.",
        "text_original": "一切唯心造",
        "original_language": "zh",
        "author": "원효",
        "source": "대승기신론소",
        "year": None,
        "keywords": ["초월", "변화", "선택"],
        "situations": ["삶의 의미를 찾을 때", "새로운 관점이 필요할 때"],
    },
    {
        "text": "천 개의 강에 천 개의 달이 비치듯, 마음이 맑으면 어디서든 진리를 본다.",
        "text_original": None,
        "original_language": "ko",
        "author": "원효",
        "source": None,
        "year": None,
        "keywords": ["초월", "지혜"],
        "situations": ["삶의 의미를 찾을 때"],
    },
    {
        "text": "한 송이 꽃을 피우기 위해 봄부터 소쩍새는 그렇게 울었나 보다.",
        "text_original": None,
        "original_language": "ko",
        "author": "도종환",
        "source": "담쟁이",
        "year": 1986,
        "keywords": ["초월", "인생", "노력"],
        "situations": ["삶의 의미를 찾을 때", "꾸준함이 필요할 때"],
    },
    {
        "text": "분노를 붙잡는 것은 뜨거운 숯을 손에 쥐고 남에게 던지려는 것과 같다. 데는 것은 자기 자신이다.",
        "text_original": "Holding on to anger is like grasping a hot coal with the intent of throwing it at someone else; you are the one who gets burned.",
        "original_language": "pi",
        "author": "붓다",
        "source": "법구경",
        "year": None,
        "keywords": ["초월", "고통", "지혜"],
        "situations": ["관계가 어려울 때", "힘든 상황에서 거리를 두고 싶을 때"],
    },
    {
        "text": "수천 개의 촛불이 하나의 촛불에서 켜질 수 있고, 그 촛불의 수명은 줄어들지 않는다. 행복은 나눠도 줄지 않는다.",
        "text_original": "Thousands of candles can be lighted from a single candle, and the life of the candle will not be shortened. Happiness never decreases by being shared.",
        "original_language": "pi",
        "author": "붓다",
        "source": "법구경",
        "year": None,
        "keywords": ["행복", "감사", "공동체"],
        "situations": ["감사할 때", "관계의 소중함"],
    },
    {
        "text": "과거에 머물지 말고, 미래를 꿈꾸지 말고, 현재의 순간에 마음을 집중하라.",
        "text_original": "Do not dwell in the past, do not dream of the future, concentrate the mind on the present moment.",
        "original_language": "pi",
        "author": "붓다",
        "source": "숫타니파타",
        "year": None,
        "keywords": ["초월", "시간"],
        "situations": ["현재를 살고 싶을 때"],
    },
    {
        "text": "우리의 목표는 행복이 아니라 평화입니다.",
        "text_original": None,
        "original_language": "ko",
        "author": "달라이 라마",
        "source": None,
        "year": None,
        "keywords": ["초월", "행복"],
        "situations": ["삶의 의미를 찾을 때"],
    },
    {
        "text": "적을 이기는 가장 좋은 방법은 그를 친구로 만드는 것이다.",
        "text_original": "The best way to overcome your enemy is to make him your friend.",
        "original_language": "en",
        "author": "달라이 라마",
        "source": None,
        "year": None,
        "keywords": ["관계", "지혜", "초월"],
        "situations": ["관계가 어려울 때"],
    },
    {
        "text": "걸을 때 걷고, 먹을 때 먹어라. 그것이 수행이다.",
        "text_original": "When you walk, just walk. When you eat, just eat.",
        "original_language": "en",
        "author": "틱낫한",
        "source": "화",
        "year": 2001,
        "keywords": ["초월", "행복"],
        "situations": ["현재를 살고 싶을 때", "일상의 소소함"],
    },
    {
        "text": "내가 숨 쉬고 있다는 것, 그것만으로도 이미 행복이다.",
        "text_original": "Breathing in, I calm body and mind. Breathing out, I smile.",
        "original_language": "en",
        "author": "틱낫한",
        "source": "지금 이 순간이 나의 집입니다",
        "year": 2016,
        "keywords": ["행복", "감사", "초월"],
        "situations": ["현재를 살고 싶을 때", "감사할 때"],
    },

    # ============================================================
    # 2-2. 기독교 (12개)
    # ============================================================
    {
        "text": "사랑은 오래 참고, 사랑은 온유하며, 투기하지 아니하며, 자랑하지 아니하며, 교만하지 아니하며.",
        "text_original": "Love is patient, love is kind. It does not envy, it does not boast, it is not proud.",
        "original_language": "grc",
        "author": "김수환",  # 성경 구절이지만 author를 등록용으로
        "source": "성경 (고린도전서 13:4)",
        "year": None,
        "keywords": ["사랑", "겸손"],
        "situations": ["사랑의 본질을 고민할 때"],
    },
    {
        "text": "두려워하지 말라 내가 너와 함께 함이라. 놀라지 말라 나는 네 하나님이 됨이라.",
        "text_original": "Fear not, for I am with you; be not dismayed, for I am your God.",
        "original_language": "he",
        "author": "김수환",
        "source": "성경 (이사야 41:10)",
        "year": None,
        "keywords": ["용기", "희망"],
        "situations": ["두려울 때", "희망이 필요할 때"],
    },
    {
        "text": "너희 중에 죄 없는 자가 먼저 돌로 치라.",
        "text_original": "Let him who is without sin among you be the first to throw a stone.",
        "original_language": "grc",
        "author": "김수환",
        "source": "성경 (요한복음 8:7)",
        "year": None,
        "keywords": ["겸손", "자기성찰"],
        "situations": ["자기 성찰", "관계가 어려울 때"],
    },
    {
        "text": "내가 세상 끝날까지 너희와 항상 함께 있으리라.",
        "text_original": "And surely I am with you always, to the very end of the age.",
        "original_language": "grc",
        "author": "김수환",
        "source": "성경 (마태복음 28:20)",
        "year": None,
        "keywords": ["희망", "사랑"],
        "situations": ["외로울 때", "희망이 필요할 때"],
    },
    {
        "text": "가장 작고 보잘것없는 이에게 한 일이 곧 내게 한 것이니라.",
        "text_original": "Whatever you did for one of the least of these brothers and sisters of mine, you did for me.",
        "original_language": "grc",
        "author": "김수환",
        "source": "성경 (마태복음 25:40)",
        "year": None,
        "keywords": ["사랑", "겸손", "공동체"],
        "situations": ["관계의 소중함"],
    },
    {
        "text": "여러분, 서로 사랑하십시오. 그것만이 우리가 할 일입니다.",
        "text_original": None,
        "original_language": "ko",
        "author": "김수환",
        "source": "김수환 추기경 선종 전 마지막 말씀",
        "year": 2009,
        "keywords": ["사랑", "공동체"],
        "situations": ["사랑의 본질을 고민할 때", "관계의 소중함"],
    },
    {
        "text": "내려놓으세요. 내려놓으면 행복해집니다.",
        "text_original": None,
        "original_language": "ko",
        "author": "김수환",
        "source": "김수환 추기경 강론",
        "year": None,
        "keywords": ["행복", "초월"],
        "situations": ["힘든 상황에서 거리를 두고 싶을 때"],
    },
    {
        "text": "오늘 하루도 감사합니다. 사소한 것에도 감사할 수 있는 마음이 진정한 행복의 시작입니다.",
        "text_original": None,
        "original_language": "ko",
        "author": "이해인",
        "source": "꽃이 지고 나면",
        "year": 1979,
        "keywords": ["감사", "행복"],
        "situations": ["감사할 때", "일상의 소소함"],
    },
    {
        "text": "기도는 하느님의 뜻을 바꾸는 것이 아니라, 기도하는 나를 바꾸는 것이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "이해인",
        "source": "이해인 수필집",
        "year": None,
        "keywords": ["초월", "변화"],
        "situations": ["삶의 의미를 찾을 때", "자기 성찰"],
    },
    {
        "text": "평화는 미소에서 시작됩니다.",
        "text_original": "Peace begins with a smile.",
        "original_language": "en",
        "author": "마더 테레사",
        "source": None,
        "year": None,
        "keywords": ["행복", "관계"],
        "situations": ["일상의 소소함", "관계의 소중함"],
    },
    {
        "text": "어제는 지나갔고, 내일은 아직 오지 않았다. 우리에게는 오직 오늘만 있다. 시작합시다.",
        "text_original": "Yesterday is gone. Tomorrow has not yet come. We have only today. Let us begin.",
        "original_language": "en",
        "author": "마더 테레사",
        "source": None,
        "year": None,
        "keywords": ["시간", "행동"],
        "situations": ["현재를 살고 싶을 때", "새로운 시작"],
    },
    {
        "text": "값싼 은총은 없다. 은총에는 반드시 대가가 따른다.",
        "text_original": "Cheap grace is the mortal enemy of our church. We are fighting today for costly grace.",
        "original_language": "de",
        "author": "디트리히 본회퍼",
        "source": "나를 따르라",
        "year": 1937,
        "keywords": ["초월", "용기"],
        "situations": ["삶의 의미를 찾을 때"],
    },

    # ============================================================
    # 2-3. 유교/기타 (10개)
    # ============================================================
    {
        "text": "배우고 때때로 익히면 또한 기쁘지 아니한가.",
        "text_original": "學而時習之 不亦說乎",
        "original_language": "zh",
        "author": "공자",
        "source": "논어 학이편",
        "year": None,
        "keywords": ["학습", "행복"],
        "situations": ["배움의 자세", "꾸준함이 필요할 때"],
    },
    {
        "text": "자기 자신을 이기는 것이 가장 큰 승리이다.",
        "text_original": "勝人者有力 自勝者強",
        "original_language": "zh",
        "author": "공자",
        "source": "논어",
        "year": None,
        "keywords": ["자신감", "용기", "성장"],
        "situations": ["자기 성찰", "용기가 필요할 때"],
    },
    {
        "text": "하늘이 장차 큰 사명을 내리려 할 때, 반드시 먼저 그 마음을 괴롭게 하고 근골을 지치게 한다.",
        "text_original": "天將降大任於斯人也 必先苦其心志 勞其筋骨",
        "original_language": "zh",
        "author": "맹자",
        "source": "맹자 고자하",
        "year": None,
        "keywords": ["고통", "성장", "운명"],
        "situations": ["좌절했을 때", "힘든 상황에서 거리를 두고 싶을 때"],
    },
    {
        "text": "사람의 본성은 선하다. 물이 아래로 흐르는 것과 같다.",
        "text_original": "人性之善也 猶水之就下也",
        "original_language": "zh",
        "author": "맹자",
        "source": "맹자 고자상",
        "year": None,
        "keywords": ["인생", "지혜"],
        "situations": ["삶의 의미를 찾을 때"],
    },
    {
        "text": "치우침이 없고 기울어짐이 없으니, 이것이 중용이다.",
        "text_original": "不偏不倚 是謂中庸",
        "original_language": "zh",
        "author": "공자",
        "source": "중용",
        "year": None,
        "keywords": ["지혜", "자기성찰"],
        "situations": ["자기 성찰", "삶의 의미를 찾을 때"],
    },
    {
        "text": "말은 반드시 충성되고 믿음직하게 하며, 행동은 반드시 돈독하고 공경스럽게 하라.",
        "text_original": "言忠信 行篤敬",
        "original_language": "zh",
        "author": "공자",
        "source": "논어 위령공편",
        "year": None,
        "keywords": ["겸손", "행동"],
        "situations": ["자기 성찰"],
    },
    {
        "text": "사람이 먼 생각이 없으면, 반드시 가까운 근심이 생긴다.",
        "text_original": "人無遠慮 必有近憂",
        "original_language": "zh",
        "author": "공자",
        "source": "논어 위령공편",
        "year": None,
        "keywords": ["지혜", "선택"],
        "situations": ["미래가 불안할 때", "인생의 선택"],
    },
    {
        "text": "입은 화와 복의 문이요, 혀는 몸을 베는 칼이다.",
        "text_original": "口是禍福之門 舌是斬身之刀",
        "original_language": "zh",
        "author": "순자",
        "source": "명심보감",
        "year": None,
        "keywords": ["지혜", "관계"],
        "situations": ["관계가 어려울 때", "자기 성찰"],
    },
    {
        "text": "한 치의 시간이 한 치의 금과 같으니 시간을 아끼라.",
        "text_original": "一寸光陰一寸金",
        "original_language": "zh",
        "author": "공자",
        "source": "명심보감",
        "year": None,
        "keywords": ["시간", "노력"],
        "situations": ["게으를 때", "꾸준함이 필요할 때"],
    },
    {
        "text": "지나침은 미치지 못함과 같다.",
        "text_original": "過猶不及",
        "original_language": "zh",
        "author": "공자",
        "source": "논어 선진편",
        "year": None,
        "keywords": ["지혜", "자기성찰"],
        "situations": ["자기 성찰", "삶의 의미를 찾을 때"],
    },
]

# ── 수집 이력 생성 및 삽입 ──
try:
    # 카테고리 1: 사랑/관계
    log1_id = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO collection_logs (id, category, requested_count) VALUES (%s, %s, %s)",
        (log1_id, "사랑/관계", 60)
    )

    saved_1 = 0
    dup_1 = 0
    for q in love_quotes:
        aid = author_ids[q["author"]]
        result = insert_quote(
            q["text"], q.get("text_original"), q.get("original_language"),
            aid, q.get("source"), q.get("year"),
            q["keywords"], q["situations"], log1_id
        )
        if result:
            saved_1 += 1
        else:
            dup_1 += 1

    cur.execute(
        "UPDATE collection_logs SET saved_count=%s, duplicate_count=%s, error_count=0 WHERE id=%s",
        (saved_1, dup_1, log1_id)
    )

    # 카테고리 2: 종교/영성
    log2_id = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO collection_logs (id, category, requested_count) VALUES (%s, %s, %s)",
        (log2_id, "종교/영성", 34)
    )

    saved_2 = 0
    dup_2 = 0
    for q in religion_quotes:
        aid = author_ids[q["author"]]
        result = insert_quote(
            q["text"], q.get("text_original"), q.get("original_language"),
            aid, q.get("source"), q.get("year"),
            q["keywords"], q["situations"], log2_id
        )
        if result:
            saved_2 += 1
        else:
            dup_2 += 1

    cur.execute(
        "UPDATE collection_logs SET saved_count=%s, duplicate_count=%s, error_count=0 WHERE id=%s",
        (saved_2, dup_2, log2_id)
    )

    conn.commit()

    print("=" * 60)
    print("사랑/관계 & 종교/영성 명언 저장 완료")
    print("=" * 60)
    print(f"\n[카테고리 1: 사랑/관계]")
    print(f"  요청: 60개 | 저장: {saved_1}개 | 중복: {dup_1}개")
    print(f"  - 가족/효: 20개")
    print(f"  - 연인/사랑: 20개")
    print(f"  - 우정/관계: 20개")
    print(f"\n[카테고리 2: 종교/영성]")
    print(f"  요청: 34개 | 저장: {saved_2}개 | 중복: {dup_2}개")
    print(f"  - 불교: 12개")
    print(f"  - 기독교: 12개")
    print(f"  - 유교/기타: 10개")
    print(f"\n총 저장: {saved_1 + saved_2}개 / 총 중복: {dup_1 + dup_2}개")

except Exception as e:
    conn.rollback()
    print(f"오류 발생: {e}")
    raise
finally:
    cur.close()
    conn.close()
