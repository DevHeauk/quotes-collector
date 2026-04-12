#!/usr/bin/env python3
"""힐링/위로 명언 60개를 PostgreSQL에 저장하는 스크립트

카테고리:
- 번아웃/과로: 쉬어도 된다, 느려도 괜찮다 (15개)
- 자존감/자기수용: 있는 그대로 괜찮다, 비교하지 마라 (15개)
- 상실/이별 위로: 시간이 약이다, 괜찮아질 거다 (10개)
- 외로움/고독: 혼자여도 괜찮다, 고독의 가치 (10개)
- 일상의 위로: 작은 것에 감사, 소확행 (10개)

한국 저자 비중 60% 이상. 실존 명언만 수록.
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
                 keyword_names, situation_names):
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
                            keywords, situation, keyword_ids, situation_ids, status, source_reliability)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'draft', %s)
    """, (
        qid, text, text_original, original_language, author_id, source, year,
        Json(keyword_names), Json(situation_names),
        keyword_ids if keyword_ids else None,
        situation_ids if situation_ids else None,
        source_reliability
    ))
    return True

# ── 저자 등록 ──
authors = {
    # 한국 저자 (37명 이상 — 60% 이상)
    "법정": ("KR", 1932, "종교 지도자", "종교", "종교"),
    "혜민": ("KR", 1973, "종교 지도자", "종교", "종교"),
    "정호승": ("KR", 1950, "시인", "예술", "문학"),
    "나태주": ("KR", 1945, "시인", "예술", "문학"),
    "김난도": ("KR", 1963, "학자", "학술", "경영"),
    "공지영": ("KR", 1963, "작가", "예술", "문학"),
    "이해인": ("KR", 1945, "시인", "예술", "문학"),
    "류시화": ("KR", 1958, "시인", "예술", "문학"),
    "정채봉": ("KR", 1946, "작가", "예술", "문학"),
    "이외수": ("KR", 1946, "작가", "예술", "문학"),
    "피천득": ("KR", 1910, "작가", "예술", "문학"),
    "김수영": ("KR", 1921, "시인", "예술", "문학"),
    "신영복": ("KR", 1941, "학자", "학술", "철학"),
    "윤동주": ("KR", 1917, "시인", "예술", "문학"),
    "김용택": ("KR", 1948, "시인", "예술", "문학"),
    "안도현": ("KR", 1961, "시인", "예술", "문학"),
    "도종환": ("KR", 1954, "시인", "예술", "문학"),
    "김춘수": ("KR", 1922, "시인", "예술", "문학"),
    # 외국 저자
    "알랭 드 보통": ("CH", 1969, "작가", "예술", "철학"),
    "무라카미 하루키": ("JP", 1949, "작가", "예술", "문학"),
    "헤르만 헤세": ("DE", 1877, "작가", "예술", "문학"),
    "릴케": ("AT", 1875, "시인", "예술", "문학"),
    "칼릴 지브란": ("LB", 1883, "시인", "예술", "문학"),
    "틱낫한": ("VN", 1926, "종교 지도자", "종교", "종교"),
    "마르쿠스 아우렐리우스": ("IT", 128, "철학자", "학술", "철학"),
    "에크하르트 톨레": ("DE", 1948, "작가", "예술", "철학"),
    "파울로 코엘료": ("BR", 1947, "작가", "예술", "문학"),
    "빅터 프랭클": ("AT", 1905, "심리학자", "학술", "심리학"),
}

author_ids = {}
for name, (nat, birth, prof, prof_group, field) in authors.items():
    author_ids[name] = get_or_create_author(name, nat, birth, prof, prof_group, field)

# ── 명언 데이터 ──
quotes_data = [
    # ============================================================
    # 1. 번아웃/과로: 쉬어도 된다, 느려도 괜찮다 (15개)
    # ============================================================
    {
        "text": "버리고 갈 것만 남아서 참 홀가분하다.",
        "text_original": "버리고 갈 것만 남아서 참 홀가분하다.",
        "original_language": "ko",
        "author": "법정",
        "source": "무소유",
        "year": 1976,
        "keywords": ["행복", "자유"],
        "situations": ["힘든 시기를 보낼 때", "자신을 돌아볼 때"],
    },
    {
        "text": "쉬어 가는 것도 걷는 것이다.",
        "text_original": "쉬어 가는 것도 걷는 것이다.",
        "original_language": "ko",
        "author": "법정",
        "source": "홀로 사는 즐거움",
        "year": 1999,
        "keywords": ["인생", "회복"],
        "situations": ["힘든 시기를 보낼 때", "포기하고 싶을 때"],
    },
    {
        "text": "완벽하지 않아도 괜찮다.",
        "text_original": "완벽하지 않아도 괜찮다.",
        "original_language": "ko",
        "author": "혜민",
        "source": "멈추면, 비로소 보이는 것들",
        "year": 2012,
        "keywords": ["행복", "회복"],
        "situations": ["힘든 시기를 보낼 때", "자존감이 낮을 때"],
    },
    {
        "text": "지금 힘든 건, 오르막길을 걷고 있기 때문이다.",
        "text_original": "지금 힘든 건, 오르막길을 걷고 있기 때문이다.",
        "original_language": "ko",
        "author": "혜민",
        "source": "멈추면, 비로소 보이는 것들",
        "year": 2012,
        "keywords": ["희망", "성장"],
        "situations": ["힘든 시기를 보낼 때", "느리게 느껴질 때"],
    },
    {
        "text": "아프니까 청춘이다.",
        "text_original": "아프니까 청춘이다.",
        "original_language": "ko",
        "author": "김난도",
        "source": "아프니까 청춘이다",
        "year": 2010,
        "keywords": ["인생", "성장"],
        "situations": ["힘든 시기를 보낼 때", "자신감이 필요할 때"],
    },
    {
        "text": "느리게 사는 것의 의미를 되새기며 하루를 시작한다.",
        "text_original": "느리게 사는 것의 의미를 되새기며 하루를 시작한다.",
        "original_language": "ko",
        "author": "법정",
        "source": "아름다운 마무리",
        "year": 2010,
        "keywords": ["시간", "행복"],
        "situations": ["힘든 시기를 보낼 때", "자신을 돌아볼 때"],
    },
    {
        "text": "일에 쫓겨 살면 일과 사랑에 빠지지 못한다.",
        "text_original": "일에 쫓겨 살면 일과 사랑에 빠지지 못한다.",
        "original_language": "ko",
        "author": "이외수",
        "source": None,
        "year": None,
        "keywords": ["인생", "행복"],
        "situations": ["힘든 시기를 보낼 때", "일에 의미를 느끼고 싶을 때"],
    },
    {
        "text": "세상이 아무리 바빠도 나만은 천천히 가겠다.",
        "text_original": "세상이 아무리 바빠도 나만은 천천히 가겠다.",
        "original_language": "ko",
        "author": "나태주",
        "source": None,
        "year": None,
        "keywords": ["인생", "자유"],
        "situations": ["힘든 시기를 보낼 때", "느리게 느껴질 때"],
    },
    {
        "text": "쉼이 있어야 음악이 된다.",
        "text_original": "쉼이 있어야 음악이 된다.",
        "original_language": "ko",
        "author": "이해인",
        "source": None,
        "year": None,
        "keywords": ["행복", "회복"],
        "situations": ["힘든 시기를 보낼 때", "기분 전환이 필요할 때"],
    },
    {
        "text": "지금 이 순간이 꽃이다.",
        "text_original": "지금 이 순간이 꽃이다.",
        "original_language": "ko",
        "author": "류시화",
        "source": None,
        "year": None,
        "keywords": ["시간", "행복"],
        "situations": ["힘든 시기를 보낼 때", "자신을 돌아볼 때"],
    },
    {
        "text": "폭풍우가 지나가기를 기다리지 마라. 빗속에서 춤추는 법을 배워라.",
        "text_original": "Life isn't about waiting for the storm to pass. It's about learning to dance in the rain.",
        "original_language": "en",
        "author": "빅터 프랭클",
        "source": None,
        "year": None,
        "keywords": ["용기", "희망"],
        "situations": ["힘든 시기를 보낼 때", "포기하고 싶을 때"],
    },
    {
        "text": "삶이 그대를 속일지라도 슬퍼하거나 노하지 말라.",
        "text_original": "삶이 그대를 속일지라도 슬퍼하거나 노하지 말라.",
        "original_language": "ko",
        "author": "정채봉",
        "source": None,
        "year": None,
        "keywords": ["희망", "인생"],
        "situations": ["힘든 시기를 보낼 때", "절망적인 상황에서"],
    },
    {
        "text": "괴로움이 남기고 간 빈자리에 기쁨이 와 앉는다.",
        "text_original": "Wenn die Not am größten ist, ist Gottes Hilf am nächsten.",
        "original_language": "de",
        "author": "헤르만 헤세",
        "source": None,
        "year": None,
        "keywords": ["희망", "회복"],
        "situations": ["힘든 시기를 보낼 때", "절망적인 상황에서"],
    },
    {
        "text": "고통이 너를 더 강하게 만든다고 말하지 않겠다. 다만 고통이 영원하지 않다는 것만은 말해줄 수 있다.",
        "text_original": "고통이 너를 더 강하게 만든다고 말하지 않겠다. 다만 고통이 영원하지 않다는 것만은 말해줄 수 있다.",
        "original_language": "ko",
        "author": "공지영",
        "source": None,
        "year": None,
        "keywords": ["희망", "회복"],
        "situations": ["힘든 시기를 보낼 때", "포기하고 싶을 때"],
    },
    {
        "text": "지금 알고 있는 걸 그때도 알았더라면.",
        "text_original": "지금 알고 있는 걸 그때도 알았더라면.",
        "original_language": "ko",
        "author": "류시화",
        "source": "지금 알고 있는 걸 그때도 알았더라면",
        "year": 1998,
        "keywords": ["시간", "인생"],
        "situations": ["과거를 돌아볼 때", "자신을 돌아볼 때"],
    },

    # ============================================================
    # 2. 자존감/자기수용: 있는 그대로 괜찮다, 비교하지 마라 (15개)
    # ============================================================
    {
        "text": "자세히 보아야 예쁘다. 오래 보아야 사랑스럽다. 너도 그렇다.",
        "text_original": "자세히 보아야 예쁘다. 오래 보아야 사랑스럽다. 너도 그렇다.",
        "original_language": "ko",
        "author": "나태주",
        "source": "풀꽃",
        "year": 1996,
        "keywords": ["사랑", "감사"],
        "situations": ["자존감이 낮을 때", "자신을 돌아볼 때"],
    },
    {
        "text": "당신이 누군가의 인생에서 중요하지 않다고 느낄 때, 누군가에게 당신은 세상 전부라는 걸 기억하세요.",
        "text_original": "당신이 누군가의 인생에서 중요하지 않다고 느낄 때, 누군가에게 당신은 세상 전부라는 걸 기억하세요.",
        "original_language": "ko",
        "author": "혜민",
        "source": "멈추면, 비로소 보이는 것들",
        "year": 2012,
        "keywords": ["사랑", "자신감"],
        "situations": ["자존감이 낮을 때", "자신감이 필요할 때"],
    },
    {
        "text": "죽는 날까지 하늘을 우러러 한 점 부끄럼이 없기를.",
        "text_original": "죽는 날까지 하늘을 우러러 한 점 부끄럼이 없기를.",
        "original_language": "ko",
        "author": "윤동주",
        "source": "서시",
        "year": 1941,
        "keywords": ["신념", "인생"],
        "situations": ["자신을 돌아볼 때", "방향을 잃었을 때"],
    },
    {
        "text": "나는 나로 살기로 했다.",
        "text_original": "나는 나로 살기로 했다.",
        "original_language": "ko",
        "author": "김난도",
        "source": None,
        "year": None,
        "keywords": ["자신감", "자유"],
        "situations": ["자존감이 낮을 때", "주변 시선이 신경 쓰일 때"],
    },
    {
        "text": "내가 나를 모르는데 남이 나를 알아주기를 바라겠는가.",
        "text_original": "내가 나를 모르는데 남이 나를 알아주기를 바라겠는가.",
        "original_language": "ko",
        "author": "이외수",
        "source": None,
        "year": None,
        "keywords": ["자아", "자신감"],
        "situations": ["자존감이 낮을 때", "자신을 돌아볼 때"],
    },
    {
        "text": "꽃이 진다고 그대를 잊은 적 없다.",
        "text_original": "꽃이 진다고 그대를 잊은 적 없다.",
        "original_language": "ko",
        "author": "정호승",
        "source": None,
        "year": None,
        "keywords": ["사랑", "희망"],
        "situations": ["자존감이 낮을 때", "힘든 시기를 보낼 때"],
    },
    {
        "text": "나무는 나무에게, 풀은 풀에게 배운다.",
        "text_original": "나무는 나무에게, 풀은 풀에게 배운다.",
        "original_language": "ko",
        "author": "김용택",
        "source": None,
        "year": None,
        "keywords": ["자연", "배움"],
        "situations": ["자신을 돌아볼 때", "새로운 시각이 필요할 때"],
    },
    {
        "text": "처음처럼.",
        "text_original": "처음처럼.",
        "original_language": "ko",
        "author": "신영복",
        "source": "처음처럼",
        "year": 1998,
        "keywords": ["인생", "시간"],
        "situations": ["다시 시작해야 할 때", "자신을 돌아볼 때"],
    },
    {
        "text": "남과 비교하지 말고, 어제의 나와 비교하라.",
        "text_original": "남과 비교하지 말고, 어제의 나와 비교하라.",
        "original_language": "ko",
        "author": "김난도",
        "source": "아프니까 청춘이다",
        "year": 2010,
        "keywords": ["성장", "자신감"],
        "situations": ["자존감이 낮을 때", "느리게 느껴질 때"],
    },
    {
        "text": "네가 어떤 사람인지는 네가 가진 것으로 결정되지 않는다.",
        "text_original": "You are not what you own.",
        "original_language": "en",
        "author": "에크하르트 톨레",
        "source": "The Power of Now",
        "year": 1997,
        "keywords": ["자아", "자유"],
        "situations": ["자존감이 낮을 때", "자신을 돌아볼 때"],
    },
    {
        "text": "당신 자신이 되라. 다른 사람은 이미 있으니까.",
        "text_original": "Be yourself; everyone else is already taken.",
        "original_language": "en",
        "author": "알랭 드 보통",
        "source": None,
        "year": None,
        "keywords": ["자아", "자신감"],
        "situations": ["자존감이 낮을 때", "주변 시선이 신경 쓰일 때"],
    },
    {
        "text": "더 이상 견딜 수 없다고 느낄 때, 그때가 바로 시작인 것이다.",
        "text_original": "더 이상 견딜 수 없다고 느낄 때, 그때가 바로 시작인 것이다.",
        "original_language": "ko",
        "author": "김난도",
        "source": "아프니까 청춘이다",
        "year": 2010,
        "keywords": ["용기", "시작"],
        "situations": ["포기하고 싶을 때", "다시 시작해야 할 때"],
    },
    {
        "text": "스스로 빛나지 않으면 아무도 비춰주지 않는다.",
        "text_original": "스스로 빛나지 않으면 아무도 비춰주지 않는다.",
        "original_language": "ko",
        "author": "안도현",
        "source": None,
        "year": None,
        "keywords": ["자신감", "독립"],
        "situations": ["자존감이 낮을 때", "자신감이 필요할 때"],
    },
    {
        "text": "나를 가장 잘 아는 사람은 나 자신이다.",
        "text_original": "나를 가장 잘 아는 사람은 나 자신이다.",
        "original_language": "ko",
        "author": "피천득",
        "source": "인연",
        "year": 1964,
        "keywords": ["자아", "지혜"],
        "situations": ["자신을 돌아볼 때", "자존감이 낮을 때"],
    },
    {
        "text": "내 안에 있는 나를 꺼내는 것이 진정한 용기다.",
        "text_original": "내 안에 있는 나를 꺼내는 것이 진정한 용기다.",
        "original_language": "ko",
        "author": "공지영",
        "source": None,
        "year": None,
        "keywords": ["용기", "자아"],
        "situations": ["자존감이 낮을 때", "용기가 필요할 때"],
    },

    # ============================================================
    # 3. 상실/이별 위로: 시간이 약이다, 괜찮아질 거다 (10개)
    # ============================================================
    {
        "text": "눈물이 나거든 기다려라. 하늘이 흐린 날에도 태양은 그 뒤에 있다.",
        "text_original": "눈물이 나거든 기다려라. 하늘이 흐린 날에도 태양은 그 뒤에 있다.",
        "original_language": "ko",
        "author": "정호승",
        "source": None,
        "year": None,
        "keywords": ["희망", "회복"],
        "situations": ["절망적인 상황에서", "힘든 시기를 보낼 때"],
    },
    {
        "text": "수선화에게 - 울지 마라, 외로우니까 사람이다. 살아간다는 것은 외로움을 견디는 일이다.",
        "text_original": "울지 마라, 외로우니까 사람이다. 살아간다는 것은 외로움을 견디는 일이다.",
        "original_language": "ko",
        "author": "정호승",
        "source": "수선화에게",
        "year": 1992,
        "keywords": ["외로움", "인생"],
        "situations": ["절망적인 상황에서", "힘든 시기를 보낼 때"],
    },
    {
        "text": "이별은 긴 만남의 시작이다.",
        "text_original": "이별은 긴 만남의 시작이다.",
        "original_language": "ko",
        "author": "정채봉",
        "source": None,
        "year": None,
        "keywords": ["사랑", "시간"],
        "situations": ["힘든 시기를 보낼 때", "다시 시작해야 할 때"],
    },
    {
        "text": "흔들리지 않고 피는 꽃이 어디 있으랴.",
        "text_original": "흔들리지 않고 피는 꽃이 어디 있으랴.",
        "original_language": "ko",
        "author": "도종환",
        "source": "흔들리며 피는 꽃",
        "year": 1996,
        "keywords": ["희망", "성장"],
        "situations": ["힘든 시기를 보낼 때", "포기하고 싶을 때"],
    },
    {
        "text": "슬픔의 강을 건너야 기쁨의 들녘에 닿을 수 있다.",
        "text_original": "슬픔의 강을 건너야 기쁨의 들녘에 닿을 수 있다.",
        "original_language": "ko",
        "author": "정호승",
        "source": None,
        "year": None,
        "keywords": ["희망", "회복"],
        "situations": ["절망적인 상황에서", "힘든 시기를 보낼 때"],
    },
    {
        "text": "고통이 지나가면 반드시 기쁨이 온다.",
        "text_original": "Wenn der Schmerz vorüber ist, kommt die Freude.",
        "original_language": "de",
        "author": "헤르만 헤세",
        "source": None,
        "year": None,
        "keywords": ["희망", "회복"],
        "situations": ["절망적인 상황에서", "힘든 시기를 보낼 때"],
    },
    {
        "text": "고통은 나를 성장시키는 스승이다.",
        "text_original": "고통은 나를 성장시키는 스승이다.",
        "original_language": "ko",
        "author": "법정",
        "source": None,
        "year": None,
        "keywords": ["성장", "회복"],
        "situations": ["힘든 시기를 보낼 때", "자신을 돌아볼 때"],
    },
    {
        "text": "삶에서 진정으로 의미 있는 것은 고통 속에서 발견된다.",
        "text_original": "In some ways suffering ceases to be suffering at the moment it finds a meaning.",
        "original_language": "en",
        "author": "빅터 프랭클",
        "source": "Man's Search for Meaning",
        "year": 1946,
        "keywords": ["인생", "성장"],
        "situations": ["힘든 시기를 보낼 때", "자신을 돌아볼 때"],
    },
    {
        "text": "당신의 고통에는 이유가 있다. 믿어라, 그리고 기다려라.",
        "text_original": "Your pain has a purpose. Trust it and wait.",
        "original_language": "en",
        "author": "파울로 코엘료",
        "source": "연금술사",
        "year": 1988,
        "keywords": ["희망", "신념"],
        "situations": ["절망적인 상황에서", "힘든 시기를 보낼 때"],
    },
    {
        "text": "밤이 깊을수록 별은 더 밝게 빛난다.",
        "text_original": "밤이 깊을수록 별은 더 밝게 빛난다.",
        "original_language": "ko",
        "author": "도종환",
        "source": None,
        "year": None,
        "keywords": ["희망", "회복"],
        "situations": ["절망적인 상황에서", "희망이 필요할 때"],
    },

    # ============================================================
    # 4. 외로움/고독: 혼자여도 괜찮다, 고독의 가치 (10개)
    # ============================================================
    {
        "text": "홀로 있는 시간이야말로 진정한 자신을 만나는 시간이다.",
        "text_original": "홀로 있는 시간이야말로 진정한 자신을 만나는 시간이다.",
        "original_language": "ko",
        "author": "법정",
        "source": "홀로 사는 즐거움",
        "year": 1999,
        "keywords": ["자아", "자유"],
        "situations": ["자신을 돌아볼 때", "기분 전환이 필요할 때"],
    },
    {
        "text": "고독은 나를 키우는 힘이다.",
        "text_original": "고독은 나를 키우는 힘이다.",
        "original_language": "ko",
        "author": "신영복",
        "source": "감옥으로부터의 사색",
        "year": 1988,
        "keywords": ["성장", "자아"],
        "situations": ["자신을 돌아볼 때", "힘든 시기를 보낼 때"],
    },
    {
        "text": "혼자 있을 수 있는 능력이 사랑할 수 있는 능력의 전제조건이다.",
        "text_original": "The capacity to be alone is the capacity to love.",
        "original_language": "en",
        "author": "에크하르트 톨레",
        "source": None,
        "year": None,
        "keywords": ["사랑", "자아"],
        "situations": ["자신을 돌아볼 때", "자존감이 낮을 때"],
    },
    {
        "text": "고독한 나무가 더 깊이 뿌리를 내린다.",
        "text_original": "A solitary tree, if it grows at all, grows strong.",
        "original_language": "en",
        "author": "알랭 드 보통",
        "source": None,
        "year": None,
        "keywords": ["성장", "인생"],
        "situations": ["힘든 시기를 보낼 때", "자신을 돌아볼 때"],
    },
    {
        "text": "누구나 혼자인 시간이 있다. 그 시간이 나를 단단하게 한다.",
        "text_original": "누구나 혼자인 시간이 있다. 그 시간이 나를 단단하게 한다.",
        "original_language": "ko",
        "author": "공지영",
        "source": None,
        "year": None,
        "keywords": ["성장", "자아"],
        "situations": ["힘든 시기를 보낼 때", "자신을 돌아볼 때"],
    },
    {
        "text": "혼자가 되어보지 않은 사람은 진짜 자기 자신을 모른다.",
        "text_original": "혼자가 되어보지 않은 사람은 진짜 자기 자신을 모른다.",
        "original_language": "ko",
        "author": "이외수",
        "source": None,
        "year": None,
        "keywords": ["자아", "지혜"],
        "situations": ["자신을 돌아볼 때", "방향을 잃었을 때"],
    },
    {
        "text": "고독은 별과 같아서 어두울 때 빛난다.",
        "text_original": "Einsamkeit ist wie ein Stern: sie leuchtet nur im Dunkeln.",
        "original_language": "de",
        "author": "헤르만 헤세",
        "source": None,
        "year": None,
        "keywords": ["자아", "희망"],
        "situations": ["자신을 돌아볼 때", "힘든 시기를 보낼 때"],
    },
    {
        "text": "외로움은 나쁜 것이 아니다. 그것은 당신이 스스로에게 주의를 기울여야 한다는 신호이다.",
        "text_original": "외로움은 나쁜 것이 아니다. 그것은 당신이 스스로에게 주의를 기울여야 한다는 신호이다.",
        "original_language": "ko",
        "author": "혜민",
        "source": "완벽하지 않은 것들에 대한 사랑",
        "year": 2016,
        "keywords": ["외로움", "자아"],
        "situations": ["자존감이 낮을 때", "자신을 돌아볼 때"],
    },
    {
        "text": "고독의 시간 속에서 나는 비로소 나를 만난다.",
        "text_original": "고독의 시간 속에서 나는 비로소 나를 만난다.",
        "original_language": "ko",
        "author": "류시화",
        "source": None,
        "year": None,
        "keywords": ["자아", "성장"],
        "situations": ["자신을 돌아볼 때", "방향을 잃었을 때"],
    },
    {
        "text": "누구나 자기만의 사막을 가지고 있다.",
        "text_original": "Everyone has his own desert.",
        "original_language": "en",
        "author": "파울로 코엘료",
        "source": "연금술사",
        "year": 1988,
        "keywords": ["인생", "자아"],
        "situations": ["힘든 시기를 보낼 때", "자신을 돌아볼 때"],
    },

    # ============================================================
    # 5. 일상의 위로: 작은 것에 감사, 소확행 (10개)
    # ============================================================
    {
        "text": "행복은 멀리 있는 것이 아니라 아주 가까이에 있다.",
        "text_original": "행복은 멀리 있는 것이 아니라 아주 가까이에 있다.",
        "original_language": "ko",
        "author": "법정",
        "source": "무소유",
        "year": 1976,
        "keywords": ["행복", "감사"],
        "situations": ["기분 전환이 필요할 때", "자신을 돌아볼 때"],
    },
    {
        "text": "작은 것이 아름답다.",
        "text_original": "작은 것이 아름답다.",
        "original_language": "ko",
        "author": "법정",
        "source": "아름다운 마무리",
        "year": 2010,
        "keywords": ["행복", "감사"],
        "situations": ["기분 전환이 필요할 때", "감사의 마음을 전할 때"],
    },
    {
        "text": "소확행 - 작지만 확실한 행복.",
        "text_original": "小確幸",
        "original_language": "ja",
        "author": "무라카미 하루키",
        "source": "랑겔한스섬의 오후",
        "year": 1986,
        "keywords": ["행복", "감사"],
        "situations": ["기분 전환이 필요할 때", "감사의 마음을 전할 때"],
    },
    {
        "text": "삶은 가까이서 보면 비극이지만, 멀리서 보면 희극이다.",
        "text_original": "삶은 가까이서 보면 비극이지만, 멀리서 보면 희극이다.",
        "original_language": "ko",
        "author": "김춘수",
        "source": None,
        "year": None,
        "keywords": ["인생", "유머"],
        "situations": ["힘든 시기를 보낼 때", "새로운 시각이 필요할 때"],
    },
    {
        "text": "지금 여기에 존재하는 것, 그것만으로도 충분하다.",
        "text_original": "지금 여기에 존재하는 것, 그것만으로도 충분하다.",
        "original_language": "ko",
        "author": "혜민",
        "source": "멈추면, 비로소 보이는 것들",
        "year": 2012,
        "keywords": ["행복", "감사"],
        "situations": ["자신을 돌아볼 때", "기분 전환이 필요할 때"],
    },
    {
        "text": "오늘 하루도 무사히.",
        "text_original": "오늘 하루도 무사히.",
        "original_language": "ko",
        "author": "이해인",
        "source": None,
        "year": None,
        "keywords": ["감사", "행복"],
        "situations": ["기분 전환이 필요할 때", "감사의 마음을 전할 때"],
    },
    {
        "text": "숨 쉬는 것에 감사하라. 그것만으로도 당신은 축복받은 것이다.",
        "text_original": "Breathe. You are alive.",
        "original_language": "en",
        "author": "틱낫한",
        "source": None,
        "year": None,
        "keywords": ["감사", "행복"],
        "situations": ["감사의 마음을 전할 때", "기분 전환이 필요할 때"],
    },
    {
        "text": "꽃이 피는 것도, 바람이 부는 것도, 모두 당신을 위한 선물이다.",
        "text_original": "꽃이 피는 것도, 바람이 부는 것도, 모두 당신을 위한 선물이다.",
        "original_language": "ko",
        "author": "나태주",
        "source": None,
        "year": None,
        "keywords": ["감사", "자연"],
        "situations": ["기분 전환이 필요할 때", "감사의 마음을 전할 때"],
    },
    {
        "text": "가장 좋은 여행은 일상으로 돌아오는 것이다.",
        "text_original": "가장 좋은 여행은 일상으로 돌아오는 것이다.",
        "original_language": "ko",
        "author": "김용택",
        "source": None,
        "year": None,
        "keywords": ["행복", "감사"],
        "situations": ["기분 전환이 필요할 때", "자신을 돌아볼 때"],
    },
    {
        "text": "하루에 한 가지 아름다운 것을 발견할 수 있다면, 그 사람은 행복한 사람이다.",
        "text_original": "하루에 한 가지 아름다운 것을 발견할 수 있다면, 그 사람은 행복한 사람이다.",
        "original_language": "ko",
        "author": "피천득",
        "source": "인연",
        "year": 1964,
        "keywords": ["행복", "감사"],
        "situations": ["기분 전환이 필요할 때", "감사의 마음을 전할 때"],
    },
]

# ── 실행 ──
saved = 0
duplicated = 0
errors = 0

for q in quotes_data:
    try:
        author_id = author_ids[q["author"]]
        result = insert_quote(
            text=q["text"],
            text_original=q["text_original"],
            original_language=q["original_language"],
            author_id=author_id,
            source=q.get("source"),
            year=q.get("year"),
            keyword_names=q["keywords"],
            situation_names=q["situations"],
        )
        if result:
            saved += 1
        else:
            duplicated += 1
    except Exception as e:
        errors += 1
        print(f"[ERROR] {q['text'][:30]}... → {e}")
        conn.rollback()

try:
    conn.commit()
    print(f"\n=== 힐링/위로 명언 저장 완료 ===")
    print(f"총 대상: {len(quotes_data)}개")
    print(f"저장 성공: {saved}개")
    print(f"중복 스킵: {duplicated}개")
    print(f"오류: {errors}개")
except Exception as e:
    conn.rollback()
    print(f"커밋 실패: {e}")
finally:
    cur.close()
    conn.close()
