#!/usr/bin/env python3
"""한국 교과서/수능에 자주 인용되는 세계 명언 100개를 PostgreSQL에 저장하는 스크립트"""

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
authors_data = {
    # 철학
    "플라톤": ("GR", -428, "철학자", "학술", "철학"),
    "임마누엘 칸트": ("DE", 1724, "철학자", "학술", "철학"),
    "프리드리히 니체": ("DE", 1844, "철학자", "학술", "철학"),
    "블레즈 파스칼": ("FR", 1623, "철학자", "학술", "철학"),
    "세네카": ("IT", -4, "철학자", "학술", "철학"),
    "에피쿠로스": ("GR", -341, "철학자", "학술", "철학"),
    "에피크테토스": ("GR", 50, "철학자", "학술", "철학"),
    "마르쿠스 아우렐리우스": ("IT", 121, "철학자", "학술", "철학"),
    "존 스튜어트 밀": ("GB", 1806, "철학자", "학술", "철학"),
    "쇠렌 키르케고르": ("DK", 1813, "철학자", "학술", "철학"),
    "루트비히 비트겐슈타인": ("AT", 1889, "철학자", "학술", "철학"),
    "순자": ("CN", -313, "철학자", "학술", "철학"),
    # 문학
    "윌리엄 셰익스피어": ("GB", 1564, "작가", "예술", "문학"),
    "레프 톨스토이": ("RU", 1828, "작가", "예술", "문학"),
    "어니스트 헤밍웨이": ("US", 1899, "작가", "예술", "문학"),
    "알베르 카뮈": ("FR", 1913, "작가", "예술", "문학"),
    "헤르만 헤세": ("DE", 1877, "작가", "예술", "문학"),
    "빅토르 위고": ("FR", 1802, "작가", "예술", "문학"),
    "마크 트웨인": ("US", 1835, "작가", "예술", "문학"),
    "조지 버나드 쇼": ("IE", 1856, "작가", "예술", "문학"),
    "라이너 마리아 릴케": ("AT", 1875, "작가", "예술", "문학"),
    "밀란 쿤데라": ("CZ", 1929, "작가", "예술", "문학"),
    "헬렌 켈러": ("US", 1880, "작가", "예술", "문학"),
    "랄프 왈도 에머슨": ("US", 1803, "작가", "예술", "문학"),
    "오프라 윈프리": ("US", 1954, "방송인", "미디어", "문화"),
    # 과학
    "찰스 다윈": ("GB", 1809, "과학자", "과학/기술", "과학"),
    "마리 퀴리": ("PL", 1867, "물리학자", "과학/기술", "과학"),
    "스티븐 호킹": ("GB", 1942, "물리학자", "과학/기술", "과학"),
    "닐스 보어": ("DK", 1885, "물리학자", "과학/기술", "과학"),
    "루이 파스퇴르": ("FR", 1822, "과학자", "과학/기술", "과학"),
    "레오나르도 다빈치": ("IT", 1452, "예술가", "예술", "예술"),
    "칼 세이건": ("US", 1934, "과학자", "과학/기술", "과학"),
    "리처드 파인만": ("US", 1918, "물리학자", "과학/기술", "과학"),
    "니콜라 테슬라": ("RS", 1856, "발명가", "과학/기술", "기술"),
    # 정치/사회
    "에이브러햄 링컨": ("US", 1809, "정치가", "정치/군사", "정치"),
    "마틴 루터 킹 주니어": ("US", 1929, "사상가", "학술", "정치"),
    "존 F. 케네디": ("US", 1917, "정치가", "정치/군사", "정치"),
    "토머스 제퍼슨": ("US", 1743, "정치가", "정치/군사", "정치"),
    "마더 테레사": ("IN", 1910, "종교 지도자", "종교", "종교"),
    "달라이 라마": ("CN", 1935, "종교 지도자", "종교", "종교"),
    "아웅산 수지": ("MM", 1945, "정치가", "정치/군사", "정치"),
    "데즈먼드 투투": ("ZA", 1931, "종교 지도자", "종교", "종교"),
    "시몬 드 보부아르": ("FR", 1908, "철학자", "학술", "철학"),
    # 예술/기타
    "파블로 피카소": ("ES", 1881, "예술가", "예술", "예술"),
    "빌 게이츠": ("US", 1955, "기업가", "경영", "기술"),
    "월트 디즈니": ("US", 1901, "기업가", "경영", "예술"),
    "무하마드 알리": ("US", 1942, "운동선수", "스포츠", "문화"),
    "브루스 리": ("US", 1940, "배우", "예술", "문화"),
    "마야 안젤루": ("US", 1928, "작가", "예술", "문학"),
    "앨버트 슈바이처": ("DE", 1875, "의사", "과학/기술", "종교"),
    "워런 버핏": ("US", 1930, "기업가", "경영", "경영"),
    "일론 머스크": ("ZA", 1971, "기업가", "경영", "기술"),
}

author_ids = {}
for name, (nat, birth, prof, prof_group, field) in authors_data.items():
    author_ids[name] = get_or_create_author(name, nat, birth, prof, prof_group, field)

# 기존 저자도 가져오기
for existing_name in ["소크라테스", "아리스토텔레스", "르네 데카르트", "공자", "맹자", "노자",
                       "장자", "알베르트 아인슈타인", "아이작 뉴턴", "넬슨 만델라",
                       "마하트마 간디", "앙투안 드 생텍쥐페리", "요한 볼프강 폰 괴테",
                       "스티브 잡스", "갈릴레오 갈릴레이", "토머스 에디슨",
                       "빅토르 프랭클", "장폴 사르트르", "에리히 프롬",
                       "윈스턴 처칠", "벤저민 프랭클린", "헨리 포드",
                       "랄프 왈도 에머슨", "프랜시스 베이컨", "표도르 도스토옙스키",
                       "찰리 채플린", "오스카 와일드", "코코 샤넬",
                       "장자크 루소", "프랭클린 D. 루스벨트"]:
    cur.execute("SELECT id FROM authors WHERE name = %s", (existing_name,))
    row = cur.fetchone()
    if row:
        author_ids[existing_name] = row[0]

# ── 명언 100개 ──
quotes_data = [
    # ===== 철학 (25개) =====
    # 소크라테스 - 기존에 7개 있으므로 추가 없음
    # 플라톤
    (
        "좋은 사람은 법이 없어도 착하게 행동하고, 나쁜 사람은 법을 피할 방법을 찾는다.",
        "Good people do not need laws to tell them to act responsibly, while bad people will find a way around the laws.",
        "el", "플라톤", None, None,
        ["철학", "도전"], ["자기 성찰"]
    ),
    (
        "용기란 두려움이 없는 것이 아니라, 두려움보다 더 중요한 것이 있다는 판단이다.",
        "Courage is knowing what not to fear.",
        "el", "플라톤", "국가", -375,
        ["용기", "철학"], ["용기가 필요할 때", "두려울 때"]
    ),
    # 칸트
    (
        "두 가지가 나를 끊임없이 경이로움으로 채운다. 내 위에 있는 별이 빛나는 하늘과 내 안에 있는 도덕 법칙이.",
        "Two things fill the mind with ever new and increasing admiration and awe: the starry heavens above me and the moral law within me.",
        "de", "임마누엘 칸트", "실천이성비판", 1788,
        ["철학", "자기성찰"], ["자기 성찰", "삶의 의미를 찾을 때"]
    ),
    (
        "네 의지의 준칙이 항상 동시에 보편적 입법의 원리가 될 수 있도록 행위하라.",
        "Act only according to that maxim whereby you can at the same time will that it should become a universal law.",
        "de", "임마누엘 칸트", "도덕형이상학 정초", 1785,
        ["철학", "행동"], ["자기 성찰"]
    ),
    (
        "감히 알려고 하라.",
        "Sapere aude! (Dare to know!)",
        "de", "임마누엘 칸트", "계몽이란 무엇인가에 대한 답변", 1784,
        ["지식", "용기", "교육"], ["배움의 자세", "용기가 필요할 때"]
    ),
    # 니체
    (
        "괴물과 싸우는 자는 자신도 괴물이 되지 않도록 조심해야 한다. 심연을 오래 들여다보면, 심연도 너를 들여다본다.",
        "He who fights with monsters should be careful lest he thereby become a monster. And if thou gaze long into an abyss, the abyss will also gaze into thee.",
        "de", "프리드리히 니체", "선악의 저편", 1886,
        ["철학", "자기성찰", "고통"], ["자기 성찰", "힘든 상황에서 거리를 두고 싶을 때"]
    ),
    (
        "나를 죽이지 못하는 것은 나를 더 강하게 만든다.",
        "What does not kill me makes me stronger.",
        "de", "프리드리히 니체", "우상의 황혼", 1888,
        ["용기", "회복", "고통"], ["좌절했을 때", "힘든 상황에서 거리를 두고 싶을 때"]
    ),
    (
        "신은 죽었다.",
        "God is dead.",
        "de", "프리드리히 니체", "즐거운 학문", 1882,
        ["철학", "존재"], ["삶의 의미를 찾을 때"]
    ),
    # 데카르트 - 기존 1개, 추가
    (
        "좋은 정신을 갖는 것만으로는 충분하지 않다. 중요한 것은 그것을 잘 사용하는 것이다.",
        "It is not enough to have a good mind; the main thing is to use it well.",
        "fr", "르네 데카르트", "방법서설", 1637,
        ["지혜", "행동"], ["배움의 자세"]
    ),
    # 파스칼
    (
        "인간은 생각하는 갈대이다.",
        "L'homme n'est qu'un roseau, le plus faible de la nature; mais c'est un roseau pensant.",
        "fr", "블레즈 파스칼", "팡세", 1670,
        ["철학", "존재", "지혜"], ["삶의 의미를 찾을 때", "자기 성찰"]
    ),
    (
        "마음에는 이성이 알지 못하는 이성이 있다.",
        "Le cœur a ses raisons que la raison ne connaît point.",
        "fr", "블레즈 파스칼", "팡세", 1670,
        ["사랑", "철학"], ["사랑의 본질을 고민할 때"]
    ),
    # 세네카
    (
        "삶이 짧은 것이 아니라, 우리가 삶을 낭비하는 것이다.",
        "It is not that we have a short time to live, but that we waste a great deal of it.",
        "la", "세네카", "인생의 짧음에 대하여", 49,
        ["시간", "인생"], ["현재를 살고 싶을 때", "게으를 때"]
    ),
    (
        "운명은 기꺼이 따르는 자를 이끌고, 거부하는 자를 끌고 간다.",
        "Fata volentem ducunt, nolentem trahunt.",
        "la", "세네카", "도덕 서간집", 65,
        ["운명", "용기"], ["변화를 마주할 때"]
    ),
    # 에피쿠로스
    (
        "죽음은 우리에게 아무것도 아니다. 우리가 존재할 때 죽음은 오지 않고, 죽음이 오면 우리는 존재하지 않는다.",
        "Death is nothing to us, since when we are, death has not come, and when death has come, we are not.",
        "el", "에피쿠로스", "메노이케우스에게 보내는 편지", -270,
        ["죽음", "철학"], ["죽음을 생각할 때"]
    ),
    # 에피크테토스
    (
        "우리를 괴롭히는 것은 사건 자체가 아니라 사건에 대한 우리의 판단이다.",
        "It's not what happens to you, but how you react to it that matters.",
        "el", "에피크테토스", "담화록", 108,
        ["자기성찰", "선택"], ["좌절했을 때", "힘든 상황에서 거리를 두고 싶을 때"]
    ),
    # 마르쿠스 아우렐리우스
    (
        "네가 바꿀 수 없는 것에 의해 고통받지 마라.",
        "You have power over your mind — not outside events. Realize this, and you will find strength.",
        "el", "마르쿠스 아우렐리우스", "명상록", 180,
        ["자기성찰", "용기", "초월"], ["힘든 상황에서 거리를 두고 싶을 때"]
    ),
    # 공자 - 기존 4개, 추가
    (
        "아는 것을 안다 하고, 모르는 것을 모른다 하는 것, 이것이 참된 앎이다.",
        "知之為知之，不知為不知，是知也。",
        "zh", "공자", "논어", -500,
        ["지혜", "겸손", "학습"], ["배움의 자세", "깊이 이해하고 싶을 때"]
    ),
    (
        "군자는 의에 밝고, 소인은 이에 밝다.",
        "君子喻於義，小人喻於利。",
        "zh", "공자", "논어", -500,
        ["철학", "자기성찰"], ["자기 성찰"]
    ),
    # 맹자 - 기존 1개, 추가
    (
        "하늘이 장차 큰 임무를 맡기려 할 때에는 반드시 먼저 그 마음과 뜻을 괴롭히고, 그 근골을 지치게 한다.",
        "天將降大任於是人也，必先苦其心志，勞其筋骨。",
        "zh", "맹자", "맹자", -300,
        ["고통", "끈기", "성장"], ["좌절했을 때", "포기하고 싶을 때"]
    ),
    # 노자 - 기존 1개, 추가
    (
        "자신을 아는 자는 현명하고, 자신을 이기는 자는 강하다.",
        "知人者智，自知者明。勝人者有力，自勝者強。",
        "zh", "노자", "도덕경", -500,
        ["지혜", "자기성찰"], ["자기 성찰", "자신감이 없을 때"]
    ),
    (
        "상선약수. 물은 만물을 이롭게 하면서도 다투지 않는다.",
        "上善若水。水善利萬物而不爭。",
        "zh", "노자", "도덕경", -500,
        ["겸손", "지혜", "철학"], ["관계가 어려울 때"]
    ),
    # 장자 - 기존 1개, 추가
    (
        "쓸모없는 나무가 천 년을 산다.",
        "無用之用，方為大用。",
        "zh", "장자", "장자", -300,
        ["지혜", "철학"], ["새로운 관점이 필요할 때"]
    ),
    # 순자
    (
        "푸른색은 쪽에서 나왔지만 쪽보다 더 푸르다.",
        "青，取之於藍，而青於藍。",
        "zh", "순자", "순자", -300,
        ["성장", "학습", "교육"], ["배움의 자세"]
    ),
    # 존 스튜어트 밀
    (
        "만족한 돼지보다 불만족한 인간이 되는 것이 낫고, 만족한 바보보다 불만족한 소크라테스가 되는 것이 낫다.",
        "It is better to be a human being dissatisfied than a pig satisfied; better to be Socrates dissatisfied than a fool satisfied.",
        "en", "존 스튜어트 밀", "공리주의", 1863,
        ["철학", "행복", "지혜"], ["삶의 의미를 찾을 때"]
    ),
    # 키르케고르
    (
        "인생은 뒤돌아보면 이해되지만, 앞을 보며 살아야 한다.",
        "Life can only be understood backwards; but it must be lived forwards.",
        "da", "쇠렌 키르케고르", None, None,
        ["인생", "시간"], ["과거를 돌아볼 때", "미래가 불안할 때"]
    ),

    # ===== 문학 (25개) =====
    # 셰익스피어
    (
        "사느냐 죽느냐, 그것이 문제로다.",
        "To be, or not to be, that is the question.",
        "en", "윌리엄 셰익스피어", "햄릿", 1600,
        ["존재", "선택", "인생"], ["인생의 선택", "삶의 의미를 찾을 때"]
    ),
    (
        "비록 내가 작을지라도, 나는 나를 소중히 여긴다.",
        "Though she be but little, she is fierce.",
        "en", "윌리엄 셰익스피어", "한여름 밤의 꿈", 1596,
        ["자신감", "용기"], ["자신감이 없을 때"]
    ),
    (
        "세상은 하나의 무대이고, 모든 남녀는 배우에 불과하다.",
        "All the world's a stage, and all the men and women merely players.",
        "en", "윌리엄 셰익스피어", "뜻대로 하세요", 1599,
        ["인생", "존재"], ["삶의 의미를 찾을 때"]
    ),
    # 톨스토이
    (
        "행복한 가정은 모두 비슷하지만, 불행한 가정은 저마다의 이유로 불행하다.",
        "All happy families are alike; each unhappy family is unhappy in its own way.",
        "ru", "레프 톨스토이", "안나 카레니나", 1877,
        ["가족", "행복", "인생"], ["관계의 소중함"]
    ),
    (
        "참된 삶은 타인을 위해 사는 것이다.",
        "The sole meaning of life is to serve humanity.",
        "ru", "레프 톨스토이", None, None,
        ["사랑", "의미"], ["삶의 의미를 찾을 때"]
    ),
    # 헤밍웨이
    (
        "인간은 패배할 수 있을지 모르지만, 파괴될 수는 없다.",
        "A man can be destroyed but not defeated.",
        "en", "어니스트 헤밍웨이", "노인과 바다", 1952,
        ["용기", "끈기", "고통"], ["포기하고 싶을 때", "좌절했을 때"]
    ),
    (
        "세상은 아름답고, 싸울 가치가 있다.",
        "The world is a fine place and worth fighting for.",
        "en", "어니스트 헤밍웨이", "누구를 위하여 종은 울리나", 1940,
        ["희망", "용기"], ["절망적일 때", "희망이 필요할 때"]
    ),
    # 카뮈
    (
        "시시포스는 행복했으리라고 상상해야 한다.",
        "Il faut imaginer Sisyphe heureux.",
        "fr", "알베르 카뮈", "시시포스의 신화", 1942,
        ["행복", "존재", "초월"], ["좌절했을 때", "삶의 의미를 찾을 때"]
    ),
    (
        "한겨울에 나는 마침내 내 안에 꺾이지 않는 여름이 있음을 알았다.",
        "In the midst of winter, I found there was, within me, an invincible summer.",
        "fr", "알베르 카뮈", "반항인", 1954,
        ["희망", "회복", "용기"], ["절망적일 때", "희망이 필요할 때"]
    ),
    # 헤르만 헤세
    (
        "새는 알에서 나오려고 투쟁한다. 알은 세계이다. 태어나려는 자는 하나의 세계를 파괴해야 한다.",
        "Der Vogel kämpft sich aus dem Ei. Das Ei ist die Welt. Wer geboren werden will, muß eine Welt zerstören.",
        "de", "헤르만 헤세", "데미안", 1919,
        ["성장", "변화", "도전"], ["새로운 시작", "변화를 마주할 때"]
    ),
    (
        "진정한 직업은 오직 하나, 자기 자신에게로 이르는 것이다.",
        "Eines jeden wahrer Beruf ist, zu sich selbst zu kommen.",
        "de", "헤르만 헤세", "데미안", 1919,
        ["자기성찰", "존재"], ["자기 성찰", "삶의 의미를 찾을 때"]
    ),
    # 생텍쥐페리 - 기존 1개, 추가
    (
        "중요한 것은 눈에 보이지 않아. 마음으로만 볼 수 있어.",
        "On ne voit bien qu'avec le cœur. L'essentiel est invisible pour les yeux.",
        "fr", "앙투안 드 생텍쥐페리", "어린 왕자", 1943,
        ["사랑", "지혜"], ["사랑의 본질을 고민할 때", "깊이 이해하고 싶을 때"]
    ),
    # 빅토르 위고
    (
        "미래에는 여러 이름이 있다. 약한 자에게는 불가능, 두려운 자에게는 미지, 용감한 자에게는 기회.",
        "The future has several names. For the weak, it is impossible; for the fainthearted, it is unknown; but for the valiant, it is ideal.",
        "fr", "빅토르 위고", None, None,
        ["용기", "희망", "도전"], ["도전을 망설일 때", "미래가 불안할 때"]
    ),
    # 마크 트웨인
    (
        "지금부터 20년 후, 당신은 했던 일보다 하지 않았던 일로 인해 더 실망할 것이다.",
        "Twenty years from now you will be more disappointed by the things that you didn't do than by the ones you did do.",
        "en", "마크 트웨인", None, None,
        ["도전", "행동", "용기"], ["도전을 망설일 때", "용기가 필요할 때"]
    ),
    (
        "용기란 두려움에 대한 저항이며 두려움의 극복이지, 두려움이 없는 것이 아니다.",
        "Courage is resistance to fear, mastery of fear — not absence of fear.",
        "en", "마크 트웨인", "얼간이 윌슨", 1894,
        ["용기"], ["두려울 때", "용기가 필요할 때"]
    ),
    # 조지 버나드 쇼
    (
        "인생에는 두 가지 비극이 있다. 하나는 소원을 이루지 못하는 것이고, 다른 하나는 그것을 이루는 것이다.",
        "There are two tragedies in life. One is to lose your heart's desire. The other is to gain it.",
        "en", "조지 버나드 쇼", "인간과 초인", 1903,
        ["인생", "행복", "철학"], ["삶의 의미를 찾을 때"]
    ),
    # 릴케
    (
        "지금 당장 해답을 줄 수 없는 질문들을 사랑하라.",
        "Have patience with everything unresolved in your heart and try to love the questions themselves.",
        "de", "라이너 마리아 릴케", "젊은 시인에게 보내는 편지", 1903,
        ["인생", "자기성찰"], ["삶의 의미를 찾을 때", "미래가 불안할 때"]
    ),
    # 밀란 쿤데라
    (
        "인간의 시간은 원을 그리며 돌지 않는다. 일직선으로 흘러간다. 그래서 인간은 행복할 수 없다.",
        "The light that radiates from the great novels time can never dim, for human existence is perpetually being forgotten by man.",
        "cs", "밀란 쿤데라", "참을 수 없는 존재의 가벼움", 1984,
        ["존재", "시간", "인생"], ["삶의 의미를 찾을 때"]
    ),
    # 괴테 - 기존 1개, 추가
    (
        "모든 이론은 회색이고, 오직 영원한 것은 생명의 푸른 나무이다.",
        "Grau, teurer Freund, ist alle Theorie, und grün des Lebens goldner Baum.",
        "de", "요한 볼프강 폰 괴테", "파우스트", 1808,
        ["인생", "지혜", "철학"], ["새로운 관점이 필요할 때"]
    ),
    # 도스토옙스키 - 기존 1개, 추가
    (
        "아름다움이 세상을 구할 것이다.",
        "Красота спасёт мир.",
        "ru", "표도르 도스토옙스키", "백치", 1869,
        ["희망", "철학"], ["희망이 필요할 때"]
    ),
    # 헬렌 켈러
    (
        "세상에서 가장 아름다운 것들은 보이거나 만질 수 없다. 오직 마음으로 느낄 수 있다.",
        "The best and most beautiful things in the world cannot be seen or even touched — they must be felt with the heart.",
        "en", "헬렌 켈러", None, None,
        ["사랑", "행복"], ["사랑의 본질을 고민할 때"]
    ),
    (
        "혼자서는 할 수 있는 일이 적지만, 함께하면 많은 것을 할 수 있다.",
        "Alone we can do so little; together we can do so much.",
        "en", "헬렌 켈러", None, None,
        ["공동체", "관계"], ["관계의 소중함"]
    ),
    # 오프라 윈프리
    (
        "당신이 되고자 하는 사람이 될 수 있는 가장 큰 모험은 당신 자신의 삶을 사는 것이다.",
        "The biggest adventure you can ever take is to live the life of your dreams.",
        "en", "오프라 윈프리", None, None,
        ["도전", "자신감", "인생"], ["새로운 시작", "자신감이 없을 때"]
    ),
    # 에머슨 - 기존 1개, 추가
    (
        "자기 자신을 신뢰하는 자만이 타인의 신뢰를 얻을 수 있다.",
        "Self-trust is the first secret of success.",
        "en", "랄프 왈도 에머슨", "자기 신뢰", 1841,
        ["자신감", "성공"], ["자신감이 없을 때"]
    ),

    # ===== 과학 (15개) =====
    # 아인슈타인 - 기존 5개, 추가
    (
        "같은 일을 반복하면서 다른 결과를 기대하는 것은 미친 짓이다.",
        "Insanity is doing the same thing over and over again and expecting different results.",
        "en", "알베르트 아인슈타인", None, None,
        ["변화", "창의성"], ["새로운 관점이 필요할 때"]
    ),
    # 뉴턴 - 기존 1개, 추가
    (
        "나는 해변에서 노는 소년에 불과하다. 때때로 더 매끄러운 조약돌이나 더 예쁜 조개를 발견하는 것에 즐거워하면서, 진리의 대양은 여전히 미지의 채로 내 앞에 놓여 있다.",
        "I do not know what I may appear to the world, but to myself I seem to have been only like a boy playing on the sea-shore.",
        "en", "아이작 뉴턴", None, None,
        ["겸손", "지식", "과학"], ["배움의 자세"]
    ),
    # 다윈
    (
        "살아남는 종은 가장 강한 종도, 가장 똑똑한 종도 아니다. 변화에 가장 잘 적응하는 종이다.",
        "It is not the strongest of the species that survives, nor the most intelligent, but the one most responsive to change.",
        "en", "찰스 다윈", None, None,
        ["변화", "성장"], ["변화를 마주할 때"]
    ),
    (
        "무지는 지식보다 더 자주 자신감을 낳는다.",
        "Ignorance more frequently begets confidence than does knowledge.",
        "en", "찰스 다윈", "인간의 유래", 1871,
        ["겸손", "지식"], ["배움의 자세"]
    ),
    # 퀴리
    (
        "인생에서 두려워할 것은 아무것도 없다. 다만 이해해야 할 것만 있을 뿐이다.",
        "Nothing in life is to be feared, it is only to be understood.",
        "fr", "마리 퀴리", None, None,
        ["용기", "과학", "지식"], ["두려울 때", "과학적 사고"]
    ),
    (
        "나는 그저 꿈이 이루어지는 것을 막는 모든 것에 맞서 싸울 뿐이다.",
        "I was taught that the way of progress is neither swift nor easy.",
        "fr", "마리 퀴리", None, None,
        ["끈기", "노력"], ["꾸준함이 필요할 때"]
    ),
    # 호킹
    (
        "아무리 인생이 어렵게 보여도, 당신이 할 수 있고 성공할 수 있는 일은 반드시 있다.",
        "However difficult life may seem, there is always something you can do and succeed at.",
        "en", "스티븐 호킹", None, None,
        ["희망", "용기"], ["절망적일 때", "희망이 필요할 때"]
    ),
    (
        "우리는 매우 평범한 별의 작은 행성 위에 사는 진화한 원숭이에 불과하다. 그러나 우리는 우주를 이해할 수 있다.",
        "We are just an advanced breed of monkeys on a minor planet of a very average star. But we can understand the Universe.",
        "en", "스티븐 호킹", None, None,
        ["과학", "겸손", "지식"], ["과학적 사고"]
    ),
    # 갈릴레오 - 기존 1개, 추가
    (
        "그래도 지구는 돈다.",
        "Eppur si muove.",
        "it", "갈릴레오 갈릴레이", None, 1633,
        ["용기", "과학"], ["용기가 필요할 때"]
    ),
    # 닐스 보어
    (
        "전문가란 아주 좁은 분야에서 가능한 모든 실수를 다 저질러 본 사람이다.",
        "An expert is a person who has made all the mistakes that can be made in a very narrow field.",
        "da", "닐스 보어", None, None,
        ["실패", "학습"], ["실패했을 때"]
    ),
    # 파스퇴르
    (
        "행운은 준비된 마음에 찾아온다.",
        "In the fields of observation, chance favors only the prepared mind.",
        "fr", "루이 파스퇴르", None, 1854,
        ["노력", "성공"], ["꾸준함이 필요할 때"]
    ),
    # 레오나르도 다빈치
    (
        "단순함은 궁극의 정교함이다.",
        "Simplicity is the ultimate sophistication.",
        "it", "레오나르도 다빈치", None, None,
        ["창의성", "지혜"], ["창의적 사고"]
    ),
    # 칼 세이건
    (
        "어딘가에 믿을 수 없는 무언가가 알려지기를 기다리고 있다.",
        "Somewhere, something incredible is waiting to be known.",
        "en", "칼 세이건", None, None,
        ["과학", "희망"], ["과학적 사고"]
    ),
    # 리처드 파인만
    (
        "과학의 첫 번째 원칙은 자기 자신을 속이지 않는 것이다. 그리고 당신은 가장 속이기 쉬운 사람이다.",
        "The first principle is that you must not fool yourself — and you are the easiest person to fool.",
        "en", "리처드 파인만", None, 1974,
        ["과학", "자기성찰"], ["과학적 사고", "자기 성찰"]
    ),
    # 테슬라
    (
        "현재는 그들의 것이지만, 내가 노력한 미래는 나의 것이다.",
        "The present is theirs; the future, for which I really worked, is mine.",
        "en", "니콜라 테슬라", None, None,
        ["노력", "목표"], ["꾸준함이 필요할 때", "목표가 멀게 느껴질 때"]
    ),

    # ===== 정치/사회 (20개) =====
    # 링컨
    (
        "미래의 가장 좋은 점은 한 번에 하루씩만 온다는 것이다.",
        "The best thing about the future is that it comes one day at a time.",
        "en", "에이브러햄 링컨", None, None,
        ["희망", "시간"], ["미래가 불안할 때", "현재를 살고 싶을 때"]
    ),
    (
        "40세가 넘으면 자기 얼굴에 책임을 져야 한다.",
        "Every man over forty is responsible for his face.",
        "en", "에이브러햄 링컨", None, None,
        ["자기성찰", "인생"], ["자기 성찰"]
    ),
    # 간디 - 기존 1개, 추가
    (
        "당신이 세상에서 보고 싶은 변화가 되어라.",
        "Be the change that you wish to see in the world.",
        "en", "마하트마 간디", None, None,
        ["변화", "행동"], ["변화를 마주할 때"]
    ),
    (
        "약한 자는 용서할 수 없다. 용서는 강한 자의 속성이다.",
        "The weak can never forgive. Forgiveness is the attribute of the strong.",
        "en", "마하트마 간디", None, None,
        ["용기", "관계"], ["관계가 어려울 때"]
    ),
    # 만델라 - 기존 2개, 추가
    (
        "교육은 세상을 바꿀 수 있는 가장 강력한 무기이다.",
        "Education is the most powerful weapon which you can use to change the world.",
        "en", "넬슨 만델라", None, None,
        ["교육", "변화"], ["배움의 자세", "지식의 가치"]
    ),
    # 마틴 루터 킹
    (
        "나에게는 꿈이 있습니다.",
        "I have a dream.",
        "en", "마틴 루터 킹 주니어", "워싱턴 행진 연설", 1963,
        ["희망", "자유", "도전"], ["희망이 필요할 때"]
    ),
    (
        "어둠은 어둠을 몰아낼 수 없다. 오직 빛만이 그렇게 할 수 있다. 미움은 미움을 몰아낼 수 없다. 오직 사랑만이 그렇게 할 수 있다.",
        "Darkness cannot drive out darkness; only light can do that. Hate cannot drive out hate; only love can do that.",
        "en", "마틴 루터 킹 주니어", "사랑의 힘", 1963,
        ["사랑", "희망"], ["절망적일 때", "관계가 어려울 때"]
    ),
    # 케네디
    (
        "국가가 당신을 위해 무엇을 해줄 수 있는지 묻지 말고, 당신이 국가를 위해 무엇을 할 수 있는지 물어보라.",
        "Ask not what your country can do for you — ask what you can do for your country.",
        "en", "존 F. 케네디", "대통령 취임 연설", 1961,
        ["행동", "공동체"], ["새로운 시작"]
    ),
    # 처칠 - 기존 1개, 추가
    (
        "나는 피, 수고, 눈물, 그리고 땀 외에는 드릴 것이 없습니다.",
        "I have nothing to offer but blood, toil, tears, and sweat.",
        "en", "윈스턴 처칠", "하원 연설", 1940,
        ["용기", "끈기", "노력"], ["포기하고 싶을 때"]
    ),
    (
        "낙관주의자는 모든 위기에서 기회를 보고, 비관주의자는 모든 기회에서 위기를 본다.",
        "A pessimist sees the difficulty in every opportunity; an optimist sees the opportunity in every difficulty.",
        "en", "윈스턴 처칠", None, None,
        ["희망", "도전"], ["절망적일 때", "새로운 관점이 필요할 때"]
    ),
    # 토머스 제퍼슨
    (
        "나는 행운을 크게 믿는다. 그리고 더 열심히 일할수록 행운이 더 많아진다는 것을 알게 되었다.",
        "I'm a great believer in luck, and I find the harder I work, the more I have of it.",
        "en", "토머스 제퍼슨", None, None,
        ["노력", "성공"], ["게으를 때", "꾸준함이 필요할 때"]
    ),
    # 마더 테레사
    (
        "어제는 갔고, 내일은 아직 오지 않았다. 우리에게는 오직 오늘만 있다. 시작하자.",
        "Yesterday is gone. Tomorrow has not yet come. We have only today. Let us begin.",
        "en", "마더 테레사", None, None,
        ["행동", "시간"], ["현재를 살고 싶을 때", "게으를 때"]
    ),
    (
        "세상에는 사랑에 굶주려 있고, 인정에 목말라 있는 사람이 너무 많다.",
        "The greatest disease in the West today is not TB or leprosy; it is being unwanted, unloved, and uncared for.",
        "en", "마더 테레사", None, None,
        ["사랑", "공동체"], ["관계의 소중함", "외로울 때"]
    ),
    # 달라이 라마
    (
        "행복은 기성품이 아니다. 그것은 당신 자신의 행동에서 나온다.",
        "Happiness is not something ready made. It comes from your own actions.",
        "en", "달라이 라마", None, None,
        ["행복", "행동"], ["현재를 살고 싶을 때"]
    ),
    # 루스벨트 - 기존 1개, 추가
    (
        "할 수 있는 것을, 가진 것으로, 있는 곳에서 하라.",
        "Do what you can, with what you have, where you are.",
        "en", "프랭클린 D. 루스벨트", None, None,
        ["행동", "용기"], ["도전을 망설일 때"]
    ),
    # 사르트르 - 기존 1개, 추가
    (
        "존재는 본질에 앞선다.",
        "L'existence précède l'essence.",
        "fr", "장폴 사르트르", "존재와 무", 1943,
        ["존재", "자유", "철학"], ["삶의 의미를 찾을 때"]
    ),
    # 아웅산 수지
    (
        "두려움으로부터의 자유가 진정한 자유이다.",
        "The only real prison is fear, and the only real freedom is freedom from fear.",
        "en", "아웅산 수지", None, None,
        ["자유", "용기"], ["두려울 때"]
    ),
    # 데즈먼드 투투
    (
        "희망은 어둠 속에서 빛을 보는 것이 아니라, 빛이 있다고 믿는 것이다.",
        "Hope is being able to see that there is light despite all of the darkness.",
        "en", "데즈먼드 투투", None, None,
        ["희망"], ["희망이 필요할 때", "절망적일 때"]
    ),
    # 시몬 드 보부아르
    (
        "여자는 태어나는 것이 아니라 만들어지는 것이다.",
        "On ne naît pas femme, on le devient.",
        "fr", "시몬 드 보부아르", "제2의 성", 1949,
        ["자유", "변화"], ["새로운 관점이 필요할 때"]
    ),

    # ===== 예술/기타 (15개) =====
    # 피카소
    (
        "모든 아이는 예술가이다. 문제는 어른이 되어서도 예술가로 남을 수 있느냐이다.",
        "Every child is an artist. The problem is how to remain an artist once he grows up.",
        "es", "파블로 피카소", None, None,
        ["창의성", "성장"], ["창의적 사고"]
    ),
    (
        "좋은 예술가는 모방하고, 위대한 예술가는 훔친다.",
        "Good artists copy, great artists steal.",
        "es", "파블로 피카소", None, None,
        ["창의성", "학습"], ["창의적 사고", "배움의 자세"]
    ),
    # 잡스 - 기존 2개, 추가
    (
        "배고파라. 미련해져라.",
        "Stay Hungry. Stay Foolish.",
        "en", "스티브 잡스", "스탠퍼드 졸업식 연설", 2005,
        ["도전", "성장", "겸손"], ["새로운 시작", "배움의 자세"]
    ),
    # 빌 게이츠
    (
        "성공을 축하하는 것은 좋지만, 실패의 교훈에 더 주목하는 것이 중요하다.",
        "It's fine to celebrate success but it is more important to heed the lessons of failure.",
        "en", "빌 게이츠", None, None,
        ["실패", "학습", "성공"], ["실패했을 때"]
    ),
    (
        "대부분의 사람들은 1년 안에 할 수 있는 것을 과대평가하고, 10년 안에 할 수 있는 것을 과소평가한다.",
        "Most people overestimate what they can do in one year and underestimate what they can do in ten years.",
        "en", "빌 게이츠", None, None,
        ["끈기", "목표"], ["목표가 멀게 느껴질 때", "꾸준함이 필요할 때"]
    ),
    # 월트 디즈니
    (
        "꿈꿀 수 있다면, 이룰 수 있다.",
        "All our dreams can come true, if we have the courage to pursue them.",
        "en", "월트 디즈니", None, None,
        ["도전", "희망"], ["도전을 망설일 때"]
    ),
    # 에디슨 - 기존 2개, 추가
    (
        "천재란 1퍼센트의 영감과 99퍼센트의 노력으로 이루어진다.",
        "Genius is one percent inspiration and ninety-nine percent perspiration.",
        "en", "토머스 에디슨", None, None,
        ["노력", "끈기"], ["게으를 때", "꾸준함이 필요할 때"]
    ),
    # 무하마드 알리
    (
        "불가능은 사실이 아니다. 불가능은 의견일 뿐이다.",
        "Impossible is not a fact. It's an opinion.",
        "en", "무하마드 알리", None, None,
        ["도전", "자신감"], ["포기하고 싶을 때", "자신감이 없을 때"]
    ),
    # 브루스 리
    (
        "물처럼 되어라, 친구여.",
        "Be water, my friend.",
        "en", "브루스 리", None, 1971,
        ["변화", "지혜"], ["변화를 마주할 때"]
    ),
    # 마야 안젤루
    (
        "사람들은 당신이 한 말을 잊고, 당신이 한 행동을 잊지만, 당신이 느끼게 해 준 감정은 절대 잊지 않는다.",
        "People will forget what you said, people will forget what you did, but people will never forget how you made them feel.",
        "en", "마야 안젤루", None, None,
        ["관계", "감사"], ["관계의 소중함"]
    ),
    # 슈바이처
    (
        "행복의 비결은 자유이고, 자유의 비결은 용기이다.",
        "Happiness is nothing more than good health and a bad memory.",
        "de", "앨버트 슈바이처", None, None,
        ["행복", "자유", "용기"], ["현재를 살고 싶을 때"]
    ),
    # 찰리 채플린 - 기존 1개, 추가
    (
        "비 오는 날을 즐길 줄 모르는 사람은 맑은 날도 즐기지 못한다.",
        "A day without laughter is a day wasted.",
        "en", "찰리 채플린", None, None,
        ["유머", "행복"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
    # 워런 버핏
    (
        "명성을 쌓는 데는 20년이 걸리지만, 무너뜨리는 데는 5분이면 충분하다.",
        "It takes 20 years to build a reputation and five minutes to ruin it.",
        "en", "워런 버핏", None, None,
        ["겸손", "자기성찰"], ["자기 성찰"]
    ),
    # 헨리 포드 - 기존 1개, 추가
    (
        "실패는 더 현명하게 다시 시작할 수 있는 기회일 뿐이다.",
        "Failure is simply the opportunity to begin again, this time more intelligently.",
        "en", "헨리 포드", None, None,
        ["실패", "성장", "희망"], ["실패했을 때", "새로운 시작"]
    ),
    # 빅토르 프랭클 - 기존 1개, 추가
    (
        "인간에게서 모든 것을 빼앗을 수 있지만, 단 한 가지, 주어진 환경에서 자신의 태도를 선택하는 자유만은 빼앗을 수 없다.",
        "Everything can be taken from a man but one thing: the last of the human freedoms — to choose one's attitude in any given set of circumstances.",
        "de", "빅토르 프랭클", "죽음의 수용소에서", 1946,
        ["자유", "선택", "용기"], ["절망적일 때", "인생의 선택"]
    ),
]

# ── 실행 ──
inserted = 0
skipped = 0

for q in quotes_data:
    text, text_original, original_language, author_name, source, year, kw, sit = q
    author_id = author_ids.get(author_name)
    if not author_id:
        print(f"  [SKIP] 저자를 찾을 수 없음: {author_name}")
        skipped += 1
        continue
    result = insert_quote(text, text_original, original_language, author_id, source, year, kw, sit)
    if result:
        inserted += 1
    else:
        print(f"  [중복] {text[:30]}...")
        skipped += 1

conn.commit()
cur.close()
conn.close()

print(f"\n=== 완료 ===")
print(f"저장된 명언: {inserted}개")
print(f"건너뛴 명언 (중복 등): {skipped}개")
print(f"총 시도: {len(quotes_data)}개")
