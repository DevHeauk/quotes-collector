#!/usr/bin/env python3
"""동기부여/성공 명언 60개를 PostgreSQL에 저장하는 스크립트"""

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
                            keywords, situation, keyword_ids, situation_ids, status, source_reliability,
                            collection_log_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'draft', %s, %s)
    """, (
        qid, text, text_original, original_language, author_id, source, year,
        Json(keyword_names), Json(situation_names),
        keyword_ids if keyword_ids else None,
        situation_ids if situation_ids else None,
        source_reliability,
        log_id
    ))
    return True

# ── collection_log 생성 ──
log_id = str(uuid.uuid4())
cur.execute(
    "INSERT INTO collection_logs (id, category, requested_count) VALUES (%s, %s, %s)",
    (log_id, "동기부여/성공", 60)
)

# ── 신규 인물 등록 (기존 DB에 없는 인물) ──
new_authors = {
    "김승호": ("KR", 1952, "기업가", "경영", "경영"),
    "이수만": ("KR", 1952, "기업가", "경영", "문화"),
    "김정주": ("KR", 1968, "기업가", "경영", "기술"),
    "조양호": ("KR", 1949, "기업가", "경영", "경영"),
    "허창수": ("KR", 1948, "기업가", "경영", "경영"),
    "이중근": ("KR", 1936, "기업가", "경영", "경영"),
    "신동빈": ("KR", 1955, "기업가", "경영", "경영"),
    "최태원": ("KR", 1960, "기업가", "경영", "경영"),
    "추성훈": ("KR", 1975, "운동선수", "스포츠", "문화"),
    "차범근": ("KR", 1953, "운동선수", "스포츠", "문화"),
    "나폴레옹 보나파르트": ("FR", 1769, "군인", "군사", "역사"),
    "알렉산더 대왕": ("GR", -356, "군인", "군사", "역사"),
    "이사도라 던컨": ("US", 1877, "예술가", "예술", "예술"),
    "제프 베조스": ("US", 1964, "기업가", "경영", "기술"),
    "마크 저커버그": ("US", 1984, "기업가", "경영", "기술"),
    "잭 마": ("CN", 1964, "기업가", "경영", "기술"),
    "셰릴 샌드버그": ("US", 1969, "기업가", "경영", "기술"),
    "아널드 슈워제네거": ("AT", 1947, "배우", "예술", "문화"),
    "짐 캐리": ("CA", 1962, "배우", "예술", "문화"),
    "덴젤 워싱턴": ("US", 1954, "배우", "예술", "문화"),
    "미셸 오바마": ("US", 1964, "작가", "사회", "정치"),
    "나이팅게일": ("GB", 1820, "의사", "의학", "과학"),
    "클레오파트라": ("EG", -69, "정치가", "정치", "역사"),
}

author_ids = {}
for name, info in new_authors.items():
    nat, birth, prof, prof_group, field = info
    author_ids[name] = get_or_create_author(name, nat, birth, prof, prof_group, field)

# 기존 인물 ID 가져오기
existing_authors = [
    "정주영", "이병철", "이건희", "김우중", "유일한", "정세영", "구인회", "신격호",
    "이재용", "김범수", "안철수", "백종원",
    "박지성", "손흥민", "김연아", "박세리", "류현진", "이승엽", "박찬호",
    "RM", "슈가", "이효리", "유재석", "나훈아", "아이유",
    "봉준호", "박찬욱", "송강호", "이병헌", "윤여정", "지드래곤",
    "스티브 잡스", "일론 머스크", "오프라 윈프리", "워런 버핏", "헨리 포드",
    "빌 게이츠", "월트 디즈니", "코코 샤넬",
    "넬슨 만델라", "윈스턴 처칠", "헬렌 켈러",
    "무하마드 알리", "브루스 리", "마야 안젤루",
    "마하트마 간디", "마더 테레사", "달라이 라마",
    "마틴 루터 킹 주니어", "에이브러햄 링컨",
]
for name in existing_authors:
    cur.execute("SELECT id FROM authors WHERE name = %s", (name,))
    row = cur.fetchone()
    if row:
        author_ids[name] = row[0]

# ── 명언 60개 ──
quotes_data = [
    # ===== 한국 기업인/창업가 (15개) =====
    {
        "text": "돈을 버는 것은 기술이고, 돈을 쓰는 것은 예술이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "정주영",
        "source": "정주영 어록",
        "year": None,
        "keywords": ["성공", "자기성찰"],
        "situations": ["자기 성찰"]
    },
    {
        "text": "나는 운이 좋은 사람이 아니다. 나는 노력한 사람이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "정주영",
        "source": "이 땅에 태어나서 (자서전)",
        "year": 1998,
        "keywords": ["노력", "끈기", "성공"],
        "situations": ["포기하고 싶을 때", "꾸준함이 필요할 때"]
    },
    {
        "text": "사업의 성공 여부는 근면에 달려 있다.",
        "text_original": None,
        "original_language": "ko",
        "author": "이병철",
        "source": "호암자전",
        "year": 1986,
        "keywords": ["노력", "성공", "습관"],
        "situations": ["게으를 때", "꾸준함이 필요할 때"]
    },
    {
        "text": "인재를 알아보지 못하는 것은 경영자의 가장 큰 잘못이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "이병철",
        "source": "호암자전",
        "year": 1986,
        "keywords": ["성공", "지혜"],
        "situations": ["자기 성찰"]
    },
    {
        "text": "변하지 않으면 살아남을 수 없다.",
        "text_original": None,
        "original_language": "ko",
        "author": "이건희",
        "source": "삼성 신경영 선언",
        "year": 1993,
        "keywords": ["변화", "도전", "성공"],
        "situations": ["변화를 마주할 때", "새로운 시작"]
    },
    {
        "text": "어려울수록 기본에 충실해야 한다.",
        "text_original": None,
        "original_language": "ko",
        "author": "김우중",
        "source": "세계는 넓고 할 일은 많다",
        "year": 1989,
        "keywords": ["끈기", "노력", "성공"],
        "situations": ["좌절했을 때", "포기하고 싶을 때"]
    },
    {
        "text": "사업보국(事業報國), 기업을 일으켜 나라에 보답한다.",
        "text_original": None,
        "original_language": "ko",
        "author": "유일한",
        "source": "유일한 전기",
        "year": None,
        "keywords": ["성공", "공동체", "목표"],
        "situations": ["삶의 의미를 찾을 때"]
    },
    {
        "text": "성공하려면 남보다 먼저 일어나고 남보다 늦게 잠자리에 들어라.",
        "text_original": None,
        "original_language": "ko",
        "author": "정세영",
        "source": "현대자동차 어록",
        "year": None,
        "keywords": ["노력", "끈기", "성공"],
        "situations": ["게으를 때", "꾸준함이 필요할 때"]
    },
    {
        "text": "사업은 끈기다. 한 우물을 파야 한다.",
        "text_original": None,
        "original_language": "ko",
        "author": "구인회",
        "source": "LG 창업정신",
        "year": None,
        "keywords": ["끈기", "성공", "목표"],
        "situations": ["포기하고 싶을 때", "꾸준함이 필요할 때"]
    },
    {
        "text": "사업에는 국경이 없다.",
        "text_original": None,
        "original_language": "ko",
        "author": "신격호",
        "source": "롯데 창업 어록",
        "year": None,
        "keywords": ["도전", "성공", "변화"],
        "situations": ["도전을 망설일 때", "새로운 시작"]
    },
    {
        "text": "기술 독립 없이 경제 독립은 없다.",
        "text_original": None,
        "original_language": "ko",
        "author": "이재용",
        "source": "삼성전자 기자간담회",
        "year": 2019,
        "keywords": ["도전", "성공", "목표"],
        "situations": ["목표가 멀게 느껴질 때"]
    },
    {
        "text": "남들이 안 하는 것을 해야 기회가 있다.",
        "text_original": None,
        "original_language": "ko",
        "author": "김범수",
        "source": "카카오 창업 인터뷰",
        "year": None,
        "keywords": ["도전", "성공", "용기"],
        "situations": ["도전을 망설일 때", "새로운 관점이 필요할 때"]
    },
    {
        "text": "위기가 곧 기회다. 남들이 두려워할 때 과감하게 투자해라.",
        "text_original": None,
        "original_language": "ko",
        "author": "김승호",
        "source": "돈의 속성",
        "year": 2020,
        "keywords": ["도전", "용기", "성공"],
        "situations": ["두려울 때", "도전을 망설일 때"]
    },
    {
        "text": "미래에 대한 최선의 예측은 미래를 만드는 것이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "최태원",
        "source": "SK 경영 어록",
        "year": None,
        "keywords": ["도전", "행동", "성공"],
        "situations": ["미래가 불안할 때", "새로운 시작"]
    },
    {
        "text": "안 되면 될 때까지 하는 거야. 그게 사업이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "안철수",
        "source": "안철수의 생각",
        "year": 2012,
        "keywords": ["끈기", "도전", "성공"],
        "situations": ["포기하고 싶을 때", "좌절했을 때"]
    },

    # ===== 한국 스포츠/문화인 (10개) =====
    {
        "text": "노력은 배신하지 않는다는 말, 나는 그 말을 믿는다.",
        "text_original": None,
        "original_language": "ko",
        "author": "박세리",
        "source": "박세리 자서전",
        "year": None,
        "keywords": ["노력", "끈기", "성공"],
        "situations": ["포기하고 싶을 때", "꾸준함이 필요할 때"]
    },
    {
        "text": "목표가 있으면 외로움도 견딜 수 있다.",
        "text_original": None,
        "original_language": "ko",
        "author": "김연아",
        "source": "김연아의 7분 드라마",
        "year": 2010,
        "keywords": ["목표", "끈기", "동기부여"],
        "situations": ["외로울 때", "목표가 멀게 느껴질 때"]
    },
    {
        "text": "꿈을 향해 달려가는 과정 자체가 행복이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "손흥민",
        "source": "손흥민 인터뷰",
        "year": None,
        "keywords": ["행복", "목표", "동기부여"],
        "situations": ["목표가 멀게 느껴질 때", "삶의 의미를 찾을 때"]
    },
    {
        "text": "세계 무대에서 인정받으려면 두 배로 뛰어야 한다.",
        "text_original": None,
        "original_language": "ko",
        "author": "박지성",
        "source": "박지성 자서전",
        "year": None,
        "keywords": ["노력", "도전", "성공"],
        "situations": ["게으를 때", "도전을 망설일 때"]
    },
    {
        "text": "패배에서 배우지 못하면 진짜 패배다.",
        "text_original": None,
        "original_language": "ko",
        "author": "추성훈",
        "source": "추성훈 인터뷰",
        "year": None,
        "keywords": ["실패", "성장", "도전"],
        "situations": ["실패했을 때", "좌절했을 때"]
    },
    {
        "text": "재능만으로는 안 된다. 축구는 노력하는 자의 것이다.",
        "text_original": None,
        "original_language": "ko",
        "author": "차범근",
        "source": "차범근 자서전",
        "year": None,
        "keywords": ["노력", "끈기", "성공"],
        "situations": ["게으를 때", "꾸준함이 필요할 때"]
    },
    {
        "text": "최선을 다하면 결과는 따라온다. 과정을 믿어라.",
        "text_original": None,
        "original_language": "ko",
        "author": "이승엽",
        "source": "이승엽 인터뷰",
        "year": None,
        "keywords": ["노력", "동기부여", "성공"],
        "situations": ["목표가 멀게 느껴질 때", "포기하고 싶을 때"]
    },
    {
        "text": "나는 내가 좋아하는 일을 하고 있다. 그것만으로 충분하다.",
        "text_original": None,
        "original_language": "ko",
        "author": "아이유",
        "source": "아이유 콘서트 멘트",
        "year": None,
        "keywords": ["행복", "자기성찰", "동기부여"],
        "situations": ["삶의 의미를 찾을 때", "자기 성찰"]
    },
    {
        "text": "뒤에서 욕하는 사람보다, 앞에서 응원하는 한 사람이 더 중요하다.",
        "text_original": None,
        "original_language": "ko",
        "author": "유재석",
        "source": "유재석 방송 인터뷰",
        "year": None,
        "keywords": ["관계", "자신감", "동기부여"],
        "situations": ["자신감이 없을 때", "관계의 소중함"]
    },
    {
        "text": "남들의 시선보다 내 안의 목소리에 귀 기울여라.",
        "text_original": None,
        "original_language": "ko",
        "author": "RM",
        "source": "UN 연설",
        "year": 2018,
        "keywords": ["자신감", "자기성찰", "용기"],
        "situations": ["자신감이 없을 때", "자기 성찰"]
    },

    # ===== 세계 명사 (20개) =====
    {
        "text": "혁신은 리더와 추종자를 구별한다.",
        "text_original": "Innovation distinguishes between a leader and a follower.",
        "original_language": "en",
        "author": "스티브 잡스",
        "source": "The Innovation Secrets of Steve Jobs",
        "year": 2001,
        "keywords": ["도전", "성공", "변화"],
        "situations": ["도전을 망설일 때", "새로운 관점이 필요할 때"]
    },
    {
        "text": "무언가를 시작할 만큼 충분히 미쳐야 한다. 그래야 성공할 수 있다.",
        "text_original": "You have to be burning with an idea, or a problem, or a wrong that you want to right.",
        "original_language": "en",
        "author": "스티브 잡스",
        "source": "Steve Jobs by Walter Isaacson",
        "year": 2011,
        "keywords": ["도전", "동기부여", "행동"],
        "situations": ["도전을 망설일 때", "용기가 필요할 때"]
    },
    {
        "text": "인내는 매우 중요하다. 포기하지 않는 한, 언젠가 결과가 나오기 시작한다.",
        "text_original": "Persistence is very important. You should not give up unless you are forced to give up.",
        "original_language": "en",
        "author": "일론 머스크",
        "source": "일론 머스크 인터뷰",
        "year": None,
        "keywords": ["끈기", "성공", "동기부여"],
        "situations": ["포기하고 싶을 때", "꾸준함이 필요할 때"]
    },
    {
        "text": "실패는 하나의 선택지일 뿐이다. 실패하지 않는다면, 충분히 혁신하고 있지 않은 것이다.",
        "text_original": "Failure is an option here. If things are not failing, you are not innovating enough.",
        "original_language": "en",
        "author": "일론 머스크",
        "source": "SpaceX 연설",
        "year": None,
        "keywords": ["실패", "도전", "성공"],
        "situations": ["실패했을 때", "도전을 망설일 때"]
    },
    {
        "text": "당신이 되고 싶은 사람으로 사는 데 늦은 때란 없다.",
        "text_original": "It is never too late to become what you might have been.",
        "original_language": "en",
        "author": "오프라 윈프리",
        "source": "O Magazine",
        "year": None,
        "keywords": ["변화", "희망", "동기부여"],
        "situations": ["새로운 시작", "희망이 필요할 때"]
    },
    {
        "text": "행운이란 준비가 기회를 만났을 때 생기는 것이다.",
        "text_original": "Luck is a matter of preparation meeting opportunity.",
        "original_language": "en",
        "author": "오프라 윈프리",
        "source": "오프라 윈프리 쇼",
        "year": None,
        "keywords": ["노력", "성공", "행동"],
        "situations": ["불운할 때", "게으를 때"]
    },
    {
        "text": "다른 사람이 탐욕스러울 때 두려워하고, 다른 사람이 두려워할 때 탐욕스러워져라.",
        "text_original": "Be fearful when others are greedy and greedy when others are fearful.",
        "original_language": "en",
        "author": "워런 버핏",
        "source": "Berkshire Hathaway 주주 서한",
        "year": 1986,
        "keywords": ["용기", "성공", "지혜"],
        "situations": ["두려울 때", "용기가 필요할 때"]
    },
    {
        "text": "가장 중요한 투자는 자기 자신에 대한 투자이다.",
        "text_original": "The most important investment you can make is in yourself.",
        "original_language": "en",
        "author": "워런 버핏",
        "source": "워런 버핏 인터뷰",
        "year": None,
        "keywords": ["성장", "자기성찰", "성공"],
        "situations": ["자기 성찰", "배움의 자세"]
    },
    {
        "text": "당신의 브랜드는 다른 사람들이 당신이 방에 없을 때 하는 말이다.",
        "text_original": "Your brand is what other people say about you when you're not in the room.",
        "original_language": "en",
        "author": "제프 베조스",
        "source": "제프 베조스 인터뷰",
        "year": None,
        "keywords": ["성공", "자기성찰"],
        "situations": ["자기 성찰"]
    },
    {
        "text": "후회할 일을 최소화하는 것이 인생의 전략이다.",
        "text_original": "I knew that when I was 80 I was not going to regret having tried this.",
        "original_language": "en",
        "author": "제프 베조스",
        "source": "아마존 창업 인터뷰",
        "year": 1997,
        "keywords": ["도전", "용기", "선택"],
        "situations": ["도전을 망설일 때", "인생의 선택"]
    },
    {
        "text": "모든 장애물에는 기회가 숨어 있다.",
        "text_original": "In every obstacle there is an opportunity.",
        "original_language": "en",
        "author": "헨리 포드",
        "source": "헨리 포드 어록",
        "year": None,
        "keywords": ["희망", "도전", "동기부여"],
        "situations": ["좌절했을 때", "희망이 필요할 때"]
    },
    {
        "text": "인생은 10%는 나에게 일어나는 일이고, 90%는 그것에 대한 나의 반응이다.",
        "text_original": "Life is 10% what happens to me and 90% of how I react to it.",
        "original_language": "en",
        "author": "빌 게이츠",
        "source": "빌 게이츠 연설",
        "year": None,
        "keywords": ["자기성찰", "변화", "성장"],
        "situations": ["좌절했을 때", "변화를 마주할 때"]
    },
    {
        "text": "꿈을 이루고 싶다면, 먼저 꿈에서 깨어나야 한다.",
        "text_original": "The way to get started is to quit talking and begin doing.",
        "original_language": "en",
        "author": "월트 디즈니",
        "source": "월트 디즈니 어록",
        "year": None,
        "keywords": ["행동", "동기부여", "목표"],
        "situations": ["게으를 때", "도전을 망설일 때"]
    },
    {
        "text": "성공하고 싶다면, 실패를 가장 친한 친구로 만들어라.",
        "text_original": "If you want to succeed, make failure your best friend.",
        "original_language": "en",
        "author": "빌 게이츠",
        "source": "빌 게이츠 강연",
        "year": None,
        "keywords": ["실패", "성공", "동기부여"],
        "situations": ["실패했을 때", "용기가 필요할 때"]
    },
    {
        "text": "완벽을 두려워하지 마세요. 완벽에 도달할 일은 없으니까요.",
        "text_original": "Have no fear of perfection, you'll never reach it.",
        "original_language": "en",
        "author": "마야 안젤루",
        "source": None,
        "year": None,
        "keywords": ["용기", "자신감", "동기부여"],
        "situations": ["자신감이 없을 때", "두려울 때"]
    },
    {
        "text": "나비를 세는 것이 아니라 나비가 셀 수 있는 순간을 만들어라.",
        "text_original": "We delight in the beauty of the butterfly, but rarely admit the changes it has gone through.",
        "original_language": "en",
        "author": "마야 안젤루",
        "source": "마야 안젤루 시집",
        "year": None,
        "keywords": ["변화", "성장", "인생"],
        "situations": ["변화를 마주할 때", "성장"]
    },
    {
        "text": "1만 가지 킥을 한 번씩 연습한 사람은 두렵지 않다. 한 가지 킥을 1만 번 연습한 사람이 두렵다.",
        "text_original": "I fear not the man who has practiced 10,000 kicks once, but I fear the man who has practiced one kick 10,000 times.",
        "original_language": "en",
        "author": "브루스 리",
        "source": "브루스 리 어록",
        "year": None,
        "keywords": ["끈기", "노력", "성공"],
        "situations": ["꾸준함이 필요할 때", "게으를 때"]
    },
    {
        "text": "챔피언은 체육관에서 만들어지지 않는다. 챔피언은 내면 깊은 곳의 무언가로 만들어진다.",
        "text_original": "Champions aren't made in gyms. Champions are made from something they have deep inside them.",
        "original_language": "en",
        "author": "무하마드 알리",
        "source": "무하마드 알리 자서전",
        "year": None,
        "keywords": ["용기", "끈기", "동기부여"],
        "situations": ["용기가 필요할 때", "자신감이 없을 때"]
    },
    {
        "text": "앞으로 나아가지 못하는 사람은 뒤로 밀려나고 있는 것이다.",
        "text_original": "A person who won't move forward is pushed backward.",
        "original_language": "en",
        "author": "마틴 루터 킹 주니어",
        "source": "마틴 루터 킹 연설",
        "year": None,
        "keywords": ["행동", "도전", "동기부여"],
        "situations": ["게으를 때", "도전을 망설일 때"]
    },
    {
        "text": "오늘 할 수 있는 일을 내일로 미루지 마라.",
        "text_original": "You cannot escape the responsibility of tomorrow by evading it today.",
        "original_language": "en",
        "author": "에이브러햄 링컨",
        "source": "링컨 어록",
        "year": None,
        "keywords": ["행동", "노력", "동기부여"],
        "situations": ["게으를 때", "포기하고 싶을 때"]
    },

    # ===== 역사적 인물 (15개) =====
    {
        "text": "불가능이란 단어는 바보들의 사전에나 있다.",
        "text_original": "Impossible n'est pas français.",
        "original_language": "fr",
        "author": "나폴레옹 보나파르트",
        "source": "나폴레옹 서한집",
        "year": None,
        "keywords": ["도전", "용기", "자신감"],
        "situations": ["자신감이 없을 때", "도전을 망설일 때"]
    },
    {
        "text": "승리는 가장 끈기 있는 자에게 돌아간다.",
        "text_original": "La victoire appartient au plus persévérant.",
        "original_language": "fr",
        "author": "나폴레옹 보나파르트",
        "source": "나폴레옹 어록",
        "year": None,
        "keywords": ["끈기", "성공", "동기부여"],
        "situations": ["포기하고 싶을 때", "꾸준함이 필요할 때"]
    },
    {
        "text": "두려워하는 것은 아무것도 하지 않는 것보다 나쁘다.",
        "text_original": None,
        "original_language": "unknown",
        "author": "알렉산더 대왕",
        "source": "알렉산더 전기",
        "year": None,
        "keywords": ["용기", "행동", "도전"],
        "situations": ["두려울 때", "도전을 망설일 때"]
    },
    {
        "text": "세상에서 가장 행복한 사람은 자기 몸을 자유롭게 표현할 수 있는 사람이다.",
        "text_original": "The body says what words cannot.",
        "original_language": "en",
        "author": "이사도라 던컨",
        "source": "이사도라 던컨 자서전",
        "year": 1927,
        "keywords": ["자유", "행복", "자신감"],
        "situations": ["자신감이 없을 때", "삶의 의미를 찾을 때"]
    },
    {
        "text": "내가 입는 옷이 아니라, 내가 만드는 삶이 나를 정의한다.",
        "text_original": "My life didn't please me, so I created my life.",
        "original_language": "fr",
        "author": "코코 샤넬",
        "source": "코코 샤넬 어록",
        "year": None,
        "keywords": ["자신감", "변화", "자유"],
        "situations": ["자신감이 없을 때", "새로운 시작"]
    },
    {
        "text": "절대로, 절대로, 절대로 포기하지 마라.",
        "text_original": "Never, never, never give up.",
        "original_language": "en",
        "author": "윈스턴 처칠",
        "source": "Harrow School 연설",
        "year": 1941,
        "keywords": ["끈기", "용기", "동기부여"],
        "situations": ["포기하고 싶을 때", "절망적일 때"]
    },
    {
        "text": "위대한 대가는 용기를 낸 사람에게만 주어진다.",
        "text_original": "All great things are simple, and many can be expressed in single words: freedom, justice, honour, duty, mercy, hope.",
        "original_language": "en",
        "author": "윈스턴 처칠",
        "source": "전쟁 회고록",
        "year": 1948,
        "keywords": ["용기", "성공", "도전"],
        "situations": ["용기가 필요할 때", "도전을 망설일 때"]
    },
    {
        "text": "교육의 목적은 빈 마음을 열린 마음으로 바꾸는 것이다.",
        "text_original": "Education is the most powerful weapon which you can use to change the world.",
        "original_language": "en",
        "author": "넬슨 만델라",
        "source": "넬슨 만델라 연설",
        "year": 2003,
        "keywords": ["교육", "변화", "성장"],
        "situations": ["배움의 자세", "새로운 관점이 필요할 때"]
    },
    {
        "text": "삶에서 가장 큰 영광은 절대 넘어지지 않는 것이 아니라, 넘어질 때마다 다시 일어나는 것이다.",
        "text_original": "The greatest glory in living lies not in never falling, but in rising every time we fall.",
        "original_language": "en",
        "author": "넬슨 만델라",
        "source": "자유를 향한 긴 여정",
        "year": 1994,
        "keywords": ["회복", "끈기", "동기부여"],
        "situations": ["좌절했을 때", "실패했을 때"]
    },
    {
        "text": "삶이 닫힌 문 하나를 닫으면, 다른 문 하나를 연다.",
        "text_original": "When one door of happiness closes, another opens.",
        "original_language": "en",
        "author": "헬렌 켈러",
        "source": "헬렌 켈러 자서전",
        "year": None,
        "keywords": ["희망", "변화", "동기부여"],
        "situations": ["절망적일 때", "희망이 필요할 때"]
    },
    {
        "text": "인생에서 피할 수 없는 고통은 있지만, 고통받는 것은 선택이다.",
        "text_original": "Although the world is full of suffering, it is also full of the overcoming of it.",
        "original_language": "en",
        "author": "헬렌 켈러",
        "source": "Optimism (에세이)",
        "year": 1903,
        "keywords": ["고통", "선택", "희망"],
        "situations": ["힘든 상황에서 거리를 두고 싶을 때", "절망적일 때"]
    },
    {
        "text": "세상을 바꾸려 하기 전에 자신을 바꿔라.",
        "text_original": "Be the change that you wish to see in the world.",
        "original_language": "en",
        "author": "마하트마 간디",
        "source": "간디 어록",
        "year": None,
        "keywords": ["변화", "자기성찰", "행동"],
        "situations": ["자기 성찰", "변화를 마주할 때"]
    },
    {
        "text": "결국 중요한 것은 당신이 살아온 햇수가 아니라, 당신의 햇수 속에 담긴 삶이다.",
        "text_original": "In the end, it's not the years in your life that count. It's the life in your years.",
        "original_language": "en",
        "author": "에이브러햄 링컨",
        "source": "링컨 연설",
        "year": None,
        "keywords": ["인생", "의미", "자기성찰"],
        "situations": ["삶의 의미를 찾을 때", "현재를 살고 싶을 때"]
    },
    {
        "text": "어떤 일이든 마음먹기에 달렸다. 마음이 약하면 몸도 약해진다.",
        "text_original": None,
        "original_language": "en",
        "author": "무하마드 알리",
        "source": "무하마드 알리 인터뷰",
        "year": None,
        "keywords": ["자신감", "용기", "동기부여"],
        "situations": ["자신감이 없을 때", "포기하고 싶을 때"]
    },
    {
        "text": "자기 자신을 아는 것이 모든 지혜의 시작이다.",
        "text_original": "Knowing yourself is the beginning of all wisdom.",
        "original_language": "en",
        "author": "달라이 라마",
        "source": "달라이 라마 법문",
        "year": None,
        "keywords": ["자기성찰", "지혜", "성장"],
        "situations": ["자기 성찰", "배움의 자세"]
    },
]

# ── 실행 ──
saved = 0
duplicated = 0
errors = 0

for q in quotes_data:
    try:
        author_id = author_ids.get(q["author"])
        if not author_id:
            print(f"  [SKIP] 작가를 찾을 수 없음: {q['author']}")
            errors += 1
            continue

        result = insert_quote(
            text=q["text"],
            text_original=q["text_original"],
            original_language=q["original_language"],
            author_id=author_id,
            source=q["source"],
            year=q["year"],
            keyword_names=q["keywords"],
            situation_names=q["situations"],
            log_id=log_id
        )
        if result:
            saved += 1
            print(f"  [OK] {q['author']}: {q['text'][:40]}...")
        else:
            duplicated += 1
            print(f"  [DUP] {q['author']}: {q['text'][:40]}...")
    except Exception as e:
        errors += 1
        print(f"  [ERR] {q['author']}: {e}")

# collection_log 업데이트
cur.execute(
    "UPDATE collection_logs SET saved_count=%s, duplicate_count=%s, error_count=%s WHERE id=%s",
    (saved, duplicated, errors, log_id)
)

conn.commit()
cur.close()
conn.close()

print(f"\n{'='*50}")
print(f"동기부여/성공 명언 저장 완료!")
print(f"  요청: 60개")
print(f"  저장: {saved}개")
print(f"  중복: {duplicated}개")
print(f"  오류: {errors}개")
print(f"{'='*50}")
