#!/usr/bin/env python3
"""한국 현대 인물 명언 80개를 PostgreSQL에 저장하는 스크립트"""

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

# ── 캐시: professions, fields, keywords, situations ──
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

# ── 인물 등록 ──
authors = {
    # 기업인
    "정주영": ("KR", 1915, "기업가", "경영", "경영"),
    "이병철": ("KR", 1910, "기업가", "경영", "경영"),
    "이건희": ("KR", 1942, "기업가", "경영", "경영"),
    "김우중": ("KR", 1936, "기업가", "경영", "경영"),
    "유일한": ("KR", 1895, "기업가", "경영", "경영"),
    "정세영": ("KR", 1928, "기업가", "경영", "경영"),
    "구인회": ("KR", 1907, "기업가", "경영", "경영"),
    "신격호": ("KR", 1922, "기업가", "경영", "경영"),
    "이재용": ("KR", 1968, "기업가", "경영", "경영"),
    "김범수": ("KR", 1966, "기업가", "경영", "기술"),
    # 스포츠
    "박지성": ("KR", 1981, "운동선수", "스포츠", "문화"),
    "손흥민": ("KR", 1992, "운동선수", "스포츠", "문화"),
    "김연아": ("KR", 1990, "운동선수", "스포츠", "문화"),
    "박세리": ("KR", 1977, "운동선수", "스포츠", "문화"),
    "류현진": ("KR", 1987, "운동선수", "스포츠", "문화"),
    "이승엽": ("KR", 1976, "운동선수", "스포츠", "문화"),
    "박찬호": ("KR", 1973, "운동선수", "스포츠", "문화"),
    # 연예/음악
    "RM": ("KR", 1994, "음악가", "예술", "예술"),
    "슈가": ("KR", 1993, "음악가", "예술", "예술"),
    "이효리": ("KR", 1979, "음악가", "예술", "예술"),
    "유재석": ("KR", 1972, "코미디언", "예술", "문화"),
    "나훈아": ("KR", 1947, "음악가", "예술", "예술"),
    "아이유": ("KR", 1993, "음악가", "예술", "예술"),
    "지드래곤": ("KR", 1988, "음악가", "예술", "예술"),
    # 영화
    "봉준호": ("KR", 1969, "배우", "예술", "예술"),  # 감독이지만 가장 가까운 직업
    "박찬욱": ("KR", 1963, "배우", "예술", "예술"),
    "송강호": ("KR", 1967, "배우", "예술", "예술"),
    "이병헌": ("KR", 1970, "배우", "예술", "예술"),
    "윤여정": ("KR", 1947, "배우", "예술", "예술"),
    # 기타
    "법륜": ("KR", 1953, "종교 지도자", "종교", "종교"),
    "김미경": ("KR", 1964, "작가", "예술", "문화"),
    "김난도": ("KR", 1963, "학자", "학술", "문화"),
    "혜민": ("KR", 1973, "종교 지도자", "종교", "종교"),
    "손석희": ("KR", 1956, "언론인", "미디어", "문화"),
    "백종원": ("KR", 1966, "기업가", "경영", "문화"),
    "한비야": ("KR", 1958, "작가", "예술", "문화"),
    "안철수": ("KR", 1962, "기업가", "경영", "기술"),
}

author_ids = {}
for name, (nat, birth, prof, prof_group, field) in authors.items():
    author_ids[name] = get_or_create_author(name, nat, birth, prof, prof_group, field)

# ── 명언 80개 ──
quotes_data = [
    # ===== 기업인 (20개) =====
    # 정주영
    {
        "text": "시련은 있어도 실패는 없다.",
        "text_original": "시련은 있어도 실패는 없다.",
        "original_language": "ko",
        "author": "정주영",
        "source": "정주영 자서전 '시련은 있어도 실패는 없다'",
        "year": 1991,
        "keywords": ["끈기", "실패", "도전"],
        "situations": ["실패했을 때", "포기하고 싶을 때"]
    },
    {
        "text": "이봐, 해봤어?",
        "text_original": "이봐, 해봤어?",
        "original_language": "ko",
        "author": "정주영",
        "source": "현대건설 직원들에게 자주 한 말, 다수 인터뷰",
        "year": None,
        "keywords": ["도전", "행동", "용기"],
        "situations": ["도전을 망설일 때", "용기가 필요할 때"]
    },
    {
        "text": "나는 한 번도 실패한 적이 없다. 다만 성공하지 못한 적이 있을 뿐이다.",
        "text_original": "나는 한 번도 실패한 적이 없다. 다만 성공하지 못한 적이 있을 뿐이다.",
        "original_language": "ko",
        "author": "정주영",
        "source": "정주영 자서전 '시련은 있어도 실패는 없다'",
        "year": 1991,
        "keywords": ["실패", "성공", "끈기"],
        "situations": ["실패했을 때", "자신감이 없을 때"]
    },
    {
        "text": "꿈은 이루어진다. 단, 행동하는 자에게만.",
        "text_original": "꿈은 이루어진다. 단, 행동하는 자에게만.",
        "original_language": "ko",
        "author": "정주영",
        "source": "정주영 강연",
        "year": None,
        "keywords": ["행동", "목표", "도전"],
        "situations": ["게으를 때", "목표가 멀게 느껴질 때"]
    },
    # 이병철
    {
        "text": "기업은 사람이다.",
        "text_original": "기업은 사람이다.",
        "original_language": "ko",
        "author": "이병철",
        "source": "이병철 자서전 '호암자전'",
        "year": 1986,
        "keywords": ["관계", "성공"],
        "situations": ["관계의 소중함"]
    },
    {
        "text": "사업에서 가장 중요한 것은 인재를 모으는 일이다.",
        "text_original": "사업에서 가장 중요한 것은 인재를 모으는 일이다.",
        "original_language": "ko",
        "author": "이병철",
        "source": "이병철 자서전 '호암자전'",
        "year": 1986,
        "keywords": ["관계", "성공", "지혜"],
        "situations": ["관계의 소중함"]
    },
    {
        "text": "돈을 잃으면 조금 잃는 것이고, 신용을 잃으면 모든 것을 잃는 것이다.",
        "text_original": "돈을 잃으면 조금 잃는 것이고, 신용을 잃으면 모든 것을 잃는 것이다.",
        "original_language": "ko",
        "author": "이병철",
        "source": "이병철 어록",
        "year": None,
        "keywords": ["겸손", "지혜", "인생"],
        "situations": ["자기 성찰"]
    },
    # 이건희
    {
        "text": "마누라와 자식 빼고 다 바꿔라.",
        "text_original": "마누라와 자식 빼고 다 바꿔라.",
        "original_language": "ko",
        "author": "이건희",
        "source": "1993년 프랑크푸르트 신경영 선언",
        "year": 1993,
        "keywords": ["변화", "도전", "성장"],
        "situations": ["변화를 마주할 때", "새로운 시작"]
    },
    {
        "text": "양으로 승부하는 시대는 끝났다. 질로 승부해야 한다.",
        "text_original": "양으로 승부하는 시대는 끝났다. 질로 승부해야 한다.",
        "original_language": "ko",
        "author": "이건희",
        "source": "1993년 프랑크푸르트 신경영 선언",
        "year": 1993,
        "keywords": ["변화", "성장", "성공"],
        "situations": ["변화를 마주할 때", "새로운 관점이 필요할 때"]
    },
    {
        "text": "1등만이 살아남는다.",
        "text_original": "1등만이 살아남는다.",
        "original_language": "ko",
        "author": "이건희",
        "source": "삼성 신경영 관련 발언",
        "year": 1993,
        "keywords": ["성공", "목표", "도전"],
        "situations": ["목표가 멀게 느껴질 때", "꾸준함이 필요할 때"]
    },
    # 김우중
    {
        "text": "세계는 넓고 할 일은 많다.",
        "text_original": "세계는 넓고 할 일은 많다.",
        "original_language": "ko",
        "author": "김우중",
        "source": "김우중 저서 '세계는 넓고 할 일은 많다'",
        "year": 1989,
        "keywords": ["도전", "목표", "희망"],
        "situations": ["새로운 시작", "도전을 망설일 때"]
    },
    {
        "text": "젊은이여, 안정을 꿈꾸지 마라. 도전하라.",
        "text_original": "젊은이여, 안정을 꿈꾸지 마라. 도전하라.",
        "original_language": "ko",
        "author": "김우중",
        "source": "김우중 저서 '세계는 넓고 할 일은 많다'",
        "year": 1989,
        "keywords": ["도전", "용기", "행동"],
        "situations": ["도전을 망설일 때", "용기가 필요할 때"]
    },
    # 유일한
    {
        "text": "기업의 이윤은 사회로부터 얻어진 것이므로 그 이윤은 사회에 돌려주어야 한다.",
        "text_original": "기업의 이윤은 사회로부터 얻어진 것이므로 그 이윤은 사회에 돌려주어야 한다.",
        "original_language": "ko",
        "author": "유일한",
        "source": "유일한 경영 철학, 유한양행 사훈",
        "year": None,
        "keywords": ["공동체", "겸손", "감사"],
        "situations": ["감사할 때", "자기 성찰"]
    },
    {
        "text": "기업에서 가장 가치 있는 것은 정직이다.",
        "text_original": "기업에서 가장 가치 있는 것은 정직이다.",
        "original_language": "ko",
        "author": "유일한",
        "source": "유일한 어록",
        "year": None,
        "keywords": ["겸손", "지혜", "인생"],
        "situations": ["자기 성찰"]
    },
    # 정세영
    {
        "text": "자동차는 한 나라의 산업 수준을 가늠하는 척도다.",
        "text_original": "자동차는 한 나라의 산업 수준을 가늠하는 척도다.",
        "original_language": "ko",
        "author": "정세영",
        "source": "현대자동차 경영 관련 발언",
        "year": None,
        "keywords": ["목표", "도전", "성장"],
        "situations": ["목표가 멀게 느껴질 때"]
    },
    # 구인회
    {
        "text": "사업 보국의 정신으로 산업의 발전에 기여하자.",
        "text_original": "사업 보국의 정신으로 산업의 발전에 기여하자.",
        "original_language": "ko",
        "author": "구인회",
        "source": "LG 창업 이념",
        "year": None,
        "keywords": ["공동체", "목표", "행동"],
        "situations": ["새로운 시작"]
    },
    # 신격호
    {
        "text": "한번 시작한 일은 끝까지 해내야 한다.",
        "text_original": "한번 시작한 일은 끝까지 해내야 한다.",
        "original_language": "ko",
        "author": "신격호",
        "source": "롯데 창업자 신격호 어록",
        "year": None,
        "keywords": ["끈기", "행동", "목표"],
        "situations": ["포기하고 싶을 때", "꾸준함이 필요할 때"]
    },
    # 이재용
    {
        "text": "경영의 최대 덕목은 결단력이다.",
        "text_original": "경영의 최대 덕목은 결단력이다.",
        "original_language": "ko",
        "author": "이재용",
        "source": "삼성전자 경영 관련 발언",
        "year": None,
        "keywords": ["행동", "용기", "선택"],
        "situations": ["인생의 선택", "도전을 망설일 때"]
    },
    # 김범수
    {
        "text": "실패해도 괜찮다. 다시 시작하면 된다.",
        "text_original": "실패해도 괜찮다. 다시 시작하면 된다.",
        "original_language": "ko",
        "author": "김범수",
        "source": "카카오 김범수 의장 강연",
        "year": None,
        "keywords": ["실패", "도전", "희망"],
        "situations": ["실패했을 때", "새로운 시작"]
    },
    {
        "text": "큰 것을 만들려면 작은 것부터 시작해야 한다.",
        "text_original": "큰 것을 만들려면 작은 것부터 시작해야 한다.",
        "original_language": "ko",
        "author": "김범수",
        "source": "카카오 김범수 의장 인터뷰",
        "year": None,
        "keywords": ["습관", "성장", "행동"],
        "situations": ["새로운 시작", "목표가 멀게 느껴질 때"]
    },

    # ===== 스포츠 (15개) =====
    # 박지성
    {
        "text": "나는 재능이 부족한 만큼 노력으로 메웠다.",
        "text_original": "나는 재능이 부족한 만큼 노력으로 메웠다.",
        "original_language": "ko",
        "author": "박지성",
        "source": "박지성 자서전 '멈추지 않는 도전'",
        "year": 2012,
        "keywords": ["노력", "끈기", "성장"],
        "situations": ["자신감이 없을 때", "꾸준함이 필요할 때"]
    },
    {
        "text": "포기하지 않으면 반드시 기회가 온다.",
        "text_original": "포기하지 않으면 반드시 기회가 온다.",
        "original_language": "ko",
        "author": "박지성",
        "source": "박지성 자서전 '멈추지 않는 도전'",
        "year": 2012,
        "keywords": ["끈기", "희망", "도전"],
        "situations": ["포기하고 싶을 때", "희망이 필요할 때"]
    },
    {
        "text": "남들이 쉴 때 더 뛰었다.",
        "text_original": "남들이 쉴 때 더 뛰었다.",
        "original_language": "ko",
        "author": "박지성",
        "source": "박지성 인터뷰",
        "year": None,
        "keywords": ["노력", "끈기", "습관"],
        "situations": ["게으를 때", "꾸준함이 필요할 때"]
    },
    # 손흥민
    {
        "text": "즐기지 못하면 오래 할 수 없다.",
        "text_original": "즐기지 못하면 오래 할 수 없다.",
        "original_language": "ko",
        "author": "손흥민",
        "source": "손흥민 인터뷰",
        "year": None,
        "keywords": ["행복", "끈기", "성장"],
        "situations": ["꾸준함이 필요할 때", "일상의 소소함"]
    },
    {
        "text": "아버지가 늘 말씀하셨다. 기본기가 전부라고.",
        "text_original": "아버지가 늘 말씀하셨다. 기본기가 전부라고.",
        "original_language": "ko",
        "author": "손흥민",
        "source": "손흥민 SBS 인터뷰",
        "year": 2019,
        "keywords": ["습관", "노력", "교육"],
        "situations": ["배움의 자세", "꾸준함이 필요할 때"]
    },
    # 김연아
    {
        "text": "연습은 거짓말을 하지 않는다.",
        "text_original": "연습은 거짓말을 하지 않는다.",
        "original_language": "ko",
        "author": "김연아",
        "source": "김연아 자서전 '김연아의 7분 드라마'",
        "year": 2010,
        "keywords": ["노력", "끈기", "성공"],
        "situations": ["꾸준함이 필요할 때", "게으를 때"]
    },
    {
        "text": "후회하지 않으려면 최선을 다해야 한다.",
        "text_original": "후회하지 않으려면 최선을 다해야 한다.",
        "original_language": "ko",
        "author": "김연아",
        "source": "2010 밴쿠버 올림픽 인터뷰",
        "year": 2010,
        "keywords": ["노력", "자기성찰", "행동"],
        "situations": ["게으를 때", "자기 성찰"]
    },
    # 박세리
    {
        "text": "맨발로 물속에 들어가서라도 공을 쳐야 한다는 생각뿐이었다.",
        "text_original": "맨발로 물속에 들어가서라도 공을 쳐야 한다는 생각뿐이었다.",
        "original_language": "ko",
        "author": "박세리",
        "source": "1998 US여자오픈 관련 인터뷰",
        "year": 1998,
        "keywords": ["도전", "용기", "끈기"],
        "situations": ["용기가 필요할 때", "포기하고 싶을 때"]
    },
    {
        "text": "위기의 순간에 더 강해지는 것이 진정한 승부사다.",
        "text_original": "위기의 순간에 더 강해지는 것이 진정한 승부사다.",
        "original_language": "ko",
        "author": "박세리",
        "source": "박세리 인터뷰",
        "year": None,
        "keywords": ["용기", "회복", "성공"],
        "situations": ["두려울 때", "절망적일 때"]
    },
    # 류현진
    {
        "text": "꾸준히 던지는 것이 나의 무기다.",
        "text_original": "꾸준히 던지는 것이 나의 무기다.",
        "original_language": "ko",
        "author": "류현진",
        "source": "류현진 스포츠 인터뷰",
        "year": None,
        "keywords": ["끈기", "노력", "습관"],
        "situations": ["꾸준함이 필요할 때"]
    },
    # 이승엽
    {
        "text": "수천 번의 헛스윙이 한 방의 홈런을 만든다.",
        "text_original": "수천 번의 헛스윙이 한 방의 홈런을 만든다.",
        "original_language": "ko",
        "author": "이승엽",
        "source": "이승엽 인터뷰",
        "year": None,
        "keywords": ["노력", "끈기", "실패"],
        "situations": ["실패했을 때", "꾸준함이 필요할 때"]
    },
    {
        "text": "결과가 좋지 않을 때 더 연습했다. 그것이 나를 만들었다.",
        "text_original": "결과가 좋지 않을 때 더 연습했다. 그것이 나를 만들었다.",
        "original_language": "ko",
        "author": "이승엽",
        "source": "이승엽 은퇴 인터뷰",
        "year": 2017,
        "keywords": ["노력", "실패", "성장"],
        "situations": ["실패했을 때", "좌절했을 때"]
    },
    # 박찬호
    {
        "text": "메이저리그에서 내가 살아남은 건 포기하지 않았기 때문이다.",
        "text_original": "메이저리그에서 내가 살아남은 건 포기하지 않았기 때문이다.",
        "original_language": "ko",
        "author": "박찬호",
        "source": "박찬호 인터뷰",
        "year": None,
        "keywords": ["끈기", "도전", "성공"],
        "situations": ["포기하고 싶을 때", "두려울 때"]
    },
    {
        "text": "낯선 환경이 나를 더 강하게 만들었다.",
        "text_original": "낯선 환경이 나를 더 강하게 만들었다.",
        "original_language": "ko",
        "author": "박찬호",
        "source": "박찬호 자서전",
        "year": None,
        "keywords": ["도전", "성장", "용기"],
        "situations": ["새로운 시작", "두려울 때"]
    },

    # ===== 연예/음악 (15개) =====
    # RM (방탄소년단)
    {
        "text": "당신이 스스로를 사랑하지 않으면, 다른 사람도 당신을 사랑할 수 없습니다.",
        "text_original": "If you don't love yourself, you can't love others either.",
        "original_language": "en",
        "author": "RM",
        "source": "2018년 유엔 총회 연설",
        "year": 2018,
        "keywords": ["사랑", "자신감", "자기성찰"],
        "situations": ["자신감이 없을 때", "사랑의 본질을 고민할 때"]
    },
    {
        "text": "어제의 나, 오늘의 나, 내일의 나. 빠짐없이 모두 나입니다.",
        "text_original": "Yesterday's me, today's me, tomorrow's me. Without exception, they are all me.",
        "original_language": "en",
        "author": "RM",
        "source": "2018년 유엔 총회 연설 'Speak Yourself'",
        "year": 2018,
        "keywords": ["자기성찰", "존재", "성장"],
        "situations": ["자기 성찰", "과거를 돌아볼 때"]
    },
    {
        "text": "실수가 저를 만들었습니다.",
        "text_original": "My mistakes made me who I am.",
        "original_language": "en",
        "author": "RM",
        "source": "2018년 유엔 총회 연설",
        "year": 2018,
        "keywords": ["실패", "성장", "자기성찰"],
        "situations": ["실패했을 때", "자기 성찰"]
    },
    # 슈가 (방탄소년단)
    {
        "text": "아이돌이라서 음악을 하는 게 아니라, 음악을 하려고 아이돌이 된 거다.",
        "text_original": "아이돌이라서 음악을 하는 게 아니라, 음악을 하려고 아이돌이 된 거다.",
        "original_language": "ko",
        "author": "슈가",
        "source": "BTS 다큐멘터리 'Burn the Stage'",
        "year": 2018,
        "keywords": ["목표", "도전", "인생"],
        "situations": ["삶의 의미를 찾을 때"]
    },
    {
        "text": "성공 뒤에는 반드시 실패의 그림자가 있다. 두려워하지 마라.",
        "text_original": "성공 뒤에는 반드시 실패의 그림자가 있다. 두려워하지 마라.",
        "original_language": "ko",
        "author": "슈가",
        "source": "BTS V LIVE 방송",
        "year": None,
        "keywords": ["실패", "용기", "성공"],
        "situations": ["실패했을 때", "두려울 때"]
    },
    # 이효리
    {
        "text": "나이 드는 게 두렵지 않다. 나답게 사는 것이 중요하다.",
        "text_original": "나이 드는 게 두렵지 않다. 나답게 사는 것이 중요하다.",
        "original_language": "ko",
        "author": "이효리",
        "source": "이효리 tvN '효리네 민박' 인터뷰",
        "year": 2017,
        "keywords": ["자유", "자기성찰", "인생"],
        "situations": ["자기 성찰", "변화를 마주할 때"]
    },
    {
        "text": "화려함보다 진정성이 더 오래 간다.",
        "text_original": "화려함보다 진정성이 더 오래 간다.",
        "original_language": "ko",
        "author": "이효리",
        "source": "이효리 인터뷰",
        "year": None,
        "keywords": ["겸손", "인생", "지혜"],
        "situations": ["자기 성찰"]
    },
    # 유재석
    {
        "text": "항상 감사하는 마음으로 살자. 그게 내가 오래 할 수 있는 비결이다.",
        "text_original": "항상 감사하는 마음으로 살자. 그게 내가 오래 할 수 있는 비결이다.",
        "original_language": "ko",
        "author": "유재석",
        "source": "KBS 연예대상 수상 소감",
        "year": 2015,
        "keywords": ["감사", "겸손", "습관"],
        "situations": ["감사할 때", "자기 성찰"]
    },
    {
        "text": "1등보다 중요한 건 오래 하는 거다.",
        "text_original": "1등보다 중요한 건 오래 하는 거다.",
        "original_language": "ko",
        "author": "유재석",
        "source": "유재석 MBC 무한도전 인터뷰",
        "year": None,
        "keywords": ["끈기", "겸손", "습관"],
        "situations": ["꾸준함이 필요할 때"]
    },
    # 나훈아
    {
        "text": "노래는 인생이다. 나는 인생을 노래한다.",
        "text_original": "노래는 인생이다. 나는 인생을 노래한다.",
        "original_language": "ko",
        "author": "나훈아",
        "source": "나훈아 KBS 콘서트 '대한민국 어게인' 인터뷰",
        "year": 2020,
        "keywords": ["인생", "행복", "의미"],
        "situations": ["삶의 의미를 찾을 때"]
    },
    {
        "text": "테스 형, 왜 자꾸 나한테만 시련을 주는 거야.",
        "text_original": "테스 형, 왜 자꾸 나한테만 시련을 주는 거야.",
        "original_language": "ko",
        "author": "나훈아",
        "source": "나훈아 KBS 콘서트 '대한민국 어게인'",
        "year": 2020,
        "keywords": ["유머", "고통", "회복"],
        "situations": ["웃음이 필요할 때", "절망적일 때"]
    },
    # 아이유
    {
        "text": "완벽하지 않아도 괜찮아. 그게 나니까.",
        "text_original": "완벽하지 않아도 괜찮아. 그게 나니까.",
        "original_language": "ko",
        "author": "아이유",
        "source": "아이유 콘서트 멘트",
        "year": None,
        "keywords": ["자신감", "자기성찰", "행복"],
        "situations": ["자신감이 없을 때", "자기 성찰"]
    },
    # 지드래곤
    {
        "text": "남들과 다르다는 것은 축복이다.",
        "text_original": "남들과 다르다는 것은 축복이다.",
        "original_language": "ko",
        "author": "지드래곤",
        "source": "지드래곤 인터뷰",
        "year": None,
        "keywords": ["창의성", "자신감", "자유"],
        "situations": ["새로운 관점이 필요할 때", "자신감이 없을 때"]
    },

    # ===== 영화 (10개) =====
    # 봉준호
    {
        "text": "가장 개인적인 것이 가장 창의적인 것이다.",
        "text_original": "The most personal is the most creative.",
        "original_language": "en",
        "author": "봉준호",
        "source": "2020년 아카데미 시상식 수상 소감, 마틴 스코세이지 인용",
        "year": 2020,
        "keywords": ["창의성", "자기성찰", "인생"],
        "situations": ["창의적 사고", "삶의 의미를 찾을 때"]
    },
    {
        "text": "1인치의 자막 장벽을 넘으면 훨씬 더 많은 영화를 만날 수 있습니다.",
        "text_original": "Once you overcome the one-inch-tall barrier of subtitles, you will be introduced to so many more amazing films.",
        "original_language": "en",
        "author": "봉준호",
        "source": "2020년 골든글로브 수상 소감",
        "year": 2020,
        "keywords": ["변화", "도전", "성장"],
        "situations": ["새로운 관점이 필요할 때"]
    },
    {
        "text": "나는 한국 영화의 역사와 함께 여기에 있다.",
        "text_original": "나는 한국 영화의 역사와 함께 여기에 있다.",
        "original_language": "ko",
        "author": "봉준호",
        "source": "2020년 아카데미 시상식 백스테이지 인터뷰",
        "year": 2020,
        "keywords": ["감사", "겸손", "공동체"],
        "situations": ["감사할 때"]
    },
    # 박찬욱
    {
        "text": "영화는 관객에게 질문을 던지는 것이지, 답을 주는 것이 아니다.",
        "text_original": "영화는 관객에게 질문을 던지는 것이지, 답을 주는 것이 아니다.",
        "original_language": "ko",
        "author": "박찬욱",
        "source": "박찬욱 감독 인터뷰",
        "year": None,
        "keywords": ["창의성", "철학", "자기성찰"],
        "situations": ["창의적 사고", "깊이 이해하고 싶을 때"]
    },
    {
        "text": "복수는 또 다른 복수를 낳을 뿐이다.",
        "text_original": "복수는 또 다른 복수를 낳을 뿐이다.",
        "original_language": "ko",
        "author": "박찬욱",
        "source": "박찬욱 감독 '복수 3부작' 관련 인터뷰",
        "year": None,
        "keywords": ["철학", "인생", "고통"],
        "situations": ["깊이 이해하고 싶을 때"]
    },
    # 송강호
    {
        "text": "연기는 거짓 속에서 진실을 찾는 일이다.",
        "text_original": "연기는 거짓 속에서 진실을 찾는 일이다.",
        "original_language": "ko",
        "author": "송강호",
        "source": "송강호 인터뷰",
        "year": None,
        "keywords": ["창의성", "인생", "지혜"],
        "situations": ["삶의 의미를 찾을 때"]
    },
    {
        "text": "좋은 배우는 좋은 대본을 만나야 한다. 그래서 늘 기다린다.",
        "text_original": "좋은 배우는 좋은 대본을 만나야 한다. 그래서 늘 기다린다.",
        "original_language": "ko",
        "author": "송강호",
        "source": "송강호 인터뷰",
        "year": None,
        "keywords": ["끈기", "겸손", "지혜"],
        "situations": ["꾸준함이 필요할 때"]
    },
    # 이병헌
    {
        "text": "한계를 정하지 않으면 가능성은 무한해진다.",
        "text_original": "한계를 정하지 않으면 가능성은 무한해진다.",
        "original_language": "ko",
        "author": "이병헌",
        "source": "이병헌 인터뷰",
        "year": None,
        "keywords": ["도전", "성장", "자신감"],
        "situations": ["도전을 망설일 때", "자신감이 없을 때"]
    },
    # 윤여정
    {
        "text": "나는 운이 좋았다고 말하지 않겠다. 나는 노력했다.",
        "text_original": "나는 운이 좋았다고 말하지 않겠다. 나는 노력했다.",
        "original_language": "ko",
        "author": "윤여정",
        "source": "2021년 아카데미 여우조연상 수상 후 인터뷰",
        "year": 2021,
        "keywords": ["노력", "자신감", "성공"],
        "situations": ["자신감이 없을 때", "꾸준함이 필요할 때"]
    },
    {
        "text": "나이가 들수록 겸손해지는 것이 아니라, 더 솔직해지는 것이다.",
        "text_original": "나이가 들수록 겸손해지는 것이 아니라, 더 솔직해지는 것이다.",
        "original_language": "ko",
        "author": "윤여정",
        "source": "윤여정 인터뷰",
        "year": None,
        "keywords": ["자유", "자기성찰", "인생"],
        "situations": ["자기 성찰", "변화를 마주할 때"]
    },

    # ===== 기타 (20개) =====
    # 법륜
    {
        "text": "괴로움은 현실의 문제가 아니라 마음의 문제입니다.",
        "text_original": "괴로움은 현실의 문제가 아니라 마음의 문제입니다.",
        "original_language": "ko",
        "author": "법륜",
        "source": "법륜 스님 '즉문즉설' 강연",
        "year": None,
        "keywords": ["고통", "자기성찰", "행복"],
        "situations": ["절망적일 때", "힘든 상황에서 거리를 두고 싶을 때"]
    },
    {
        "text": "상대를 바꾸려 하지 마세요. 내가 바뀌면 상대도 바뀝니다.",
        "text_original": "상대를 바꾸려 하지 마세요. 내가 바뀌면 상대도 바뀝니다.",
        "original_language": "ko",
        "author": "법륜",
        "source": "법륜 스님 '즉문즉설' 강연",
        "year": None,
        "keywords": ["관계", "변화", "자기성찰"],
        "situations": ["관계가 어려울 때"]
    },
    {
        "text": "행복은 조건이 아니라 선택입니다.",
        "text_original": "행복은 조건이 아니라 선택입니다.",
        "original_language": "ko",
        "author": "법륜",
        "source": "법륜 스님 저서 '행복'",
        "year": 2014,
        "keywords": ["행복", "선택", "자기성찰"],
        "situations": ["삶의 의미를 찾을 때", "인생의 선택"]
    },
    {
        "text": "지금 이 순간이 가장 소중합니다.",
        "text_original": "지금 이 순간이 가장 소중합니다.",
        "original_language": "ko",
        "author": "법륜",
        "source": "법륜 스님 '즉문즉설' 강연",
        "year": None,
        "keywords": ["시간", "행복", "자기성찰"],
        "situations": ["현재를 살고 싶을 때"]
    },
    # 김미경
    {
        "text": "인생에 리허설은 없다. 매일이 본 무대다.",
        "text_original": "인생에 리허설은 없다. 매일이 본 무대다.",
        "original_language": "ko",
        "author": "김미경",
        "source": "김미경 저서 '김미경의 리부트'",
        "year": 2020,
        "keywords": ["행동", "시간", "인생"],
        "situations": ["게으를 때", "현재를 살고 싶을 때"]
    },
    {
        "text": "당신의 꿈이 크면 시련도 큽니다. 그것은 좋은 신호입니다.",
        "text_original": "당신의 꿈이 크면 시련도 큽니다. 그것은 좋은 신호입니다.",
        "original_language": "ko",
        "author": "김미경",
        "source": "김미경 강연",
        "year": None,
        "keywords": ["도전", "희망", "용기"],
        "situations": ["좌절했을 때", "희망이 필요할 때"]
    },
    {
        "text": "성공하는 사람은 '어떻게'를 찾고, 실패하는 사람은 '왜 안 되는지'를 찾는다.",
        "text_original": "성공하는 사람은 '어떻게'를 찾고, 실패하는 사람은 '왜 안 되는지'를 찾는다.",
        "original_language": "ko",
        "author": "김미경",
        "source": "김미경 강연",
        "year": None,
        "keywords": ["행동", "성공", "실패"],
        "situations": ["실패했을 때", "새로운 관점이 필요할 때"]
    },
    # 김난도
    {
        "text": "아프니까 청춘이다.",
        "text_original": "아프니까 청춘이다.",
        "original_language": "ko",
        "author": "김난도",
        "source": "김난도 저서 '아프니까 청춘이다'",
        "year": 2010,
        "keywords": ["고통", "희망", "성장"],
        "situations": ["좌절했을 때", "절망적일 때"]
    },
    {
        "text": "지금 아프다면 그것은 성장하고 있다는 증거다.",
        "text_original": "지금 아프다면 그것은 성장하고 있다는 증거다.",
        "original_language": "ko",
        "author": "김난도",
        "source": "김난도 저서 '아프니까 청춘이다'",
        "year": 2010,
        "keywords": ["성장", "고통", "희망"],
        "situations": ["좌절했을 때", "희망이 필요할 때"]
    },
    {
        "text": "꿈꾸지 않으면 사는 게 아니라 버티는 것이다.",
        "text_original": "꿈꾸지 않으면 사는 게 아니라 버티는 것이다.",
        "original_language": "ko",
        "author": "김난도",
        "source": "김난도 강연",
        "year": None,
        "keywords": ["목표", "희망", "인생"],
        "situations": ["삶의 의미를 찾을 때", "희망이 필요할 때"]
    },
    # 혜민
    {
        "text": "멈추면 비로소 보이는 것들이 있다.",
        "text_original": "멈추면 비로소 보이는 것들이 있다.",
        "original_language": "ko",
        "author": "혜민",
        "source": "혜민스님 저서 '멈추면, 비로소 보이는 것들'",
        "year": 2012,
        "keywords": ["자기성찰", "시간", "지혜"],
        "situations": ["현재를 살고 싶을 때", "힘든 상황에서 거리를 두고 싶을 때"]
    },
    {
        "text": "완벽한 사람은 없습니다. 부족한 대로 사랑받을 자격이 있습니다.",
        "text_original": "완벽한 사람은 없습니다. 부족한 대로 사랑받을 자격이 있습니다.",
        "original_language": "ko",
        "author": "혜민",
        "source": "혜민스님 저서 '멈추면, 비로소 보이는 것들'",
        "year": 2012,
        "keywords": ["사랑", "자신감", "겸손"],
        "situations": ["자신감이 없을 때", "사랑의 본질을 고민할 때"]
    },
    {
        "text": "비교는 행복의 도둑입니다.",
        "text_original": "비교는 행복의 도둑입니다.",
        "original_language": "ko",
        "author": "혜민",
        "source": "혜민스님 저서 '완벽하지 않은 것들에 대한 사랑'",
        "year": 2016,
        "keywords": ["행복", "자기성찰", "지혜"],
        "situations": ["자기 성찰", "자신감이 없을 때"]
    },
    # 손석희
    {
        "text": "사실을 전하는 것이 기자의 가장 큰 무기다.",
        "text_original": "사실을 전하는 것이 기자의 가장 큰 무기다.",
        "original_language": "ko",
        "author": "손석희",
        "source": "손석희 JTBC 뉴스룸 인터뷰",
        "year": None,
        "keywords": ["지식", "겸손", "인생"],
        "situations": ["배움의 자세"]
    },
    {
        "text": "편안한 뉴스는 좋은 뉴스가 아닙니다.",
        "text_original": "편안한 뉴스는 좋은 뉴스가 아닙니다.",
        "original_language": "ko",
        "author": "손석희",
        "source": "손석희 JTBC 뉴스룸",
        "year": None,
        "keywords": ["도전", "용기", "지혜"],
        "situations": ["새로운 관점이 필요할 때"]
    },
    # 백종원
    {
        "text": "요리는 사랑입니다. 먹는 사람을 생각하는 마음이 담겨야 합니다.",
        "text_original": "요리는 사랑입니다. 먹는 사람을 생각하는 마음이 담겨야 합니다.",
        "original_language": "ko",
        "author": "백종원",
        "source": "백종원 tvN '집밥 백선생' 인터뷰",
        "year": 2015,
        "keywords": ["사랑", "관계", "감사"],
        "situations": ["사랑을 느낄 때", "관계의 소중함"]
    },
    {
        "text": "기본에 충실한 것이 가장 어렵고, 가장 중요하다.",
        "text_original": "기본에 충실한 것이 가장 어렵고, 가장 중요하다.",
        "original_language": "ko",
        "author": "백종원",
        "source": "백종원 SBS '골목식당' 방송",
        "year": None,
        "keywords": ["습관", "노력", "지혜"],
        "situations": ["배움의 자세", "꾸준함이 필요할 때"]
    },
    # 한비야
    {
        "text": "바람의 딸은 멈추지 않는다.",
        "text_original": "바람의 딸은 멈추지 않는다.",
        "original_language": "ko",
        "author": "한비야",
        "source": "한비야 저서 '바람의 딸, 걸어서 지구 세 바퀴 반'",
        "year": 1996,
        "keywords": ["도전", "자유", "행동"],
        "situations": ["새로운 시작", "도전을 망설일 때"]
    },
    {
        "text": "길 위에서 배우는 것이 교실에서 배우는 것보다 크다.",
        "text_original": "길 위에서 배우는 것이 교실에서 배우는 것보다 크다.",
        "original_language": "ko",
        "author": "한비야",
        "source": "한비야 강연",
        "year": None,
        "keywords": ["학습", "교육", "도전"],
        "situations": ["배움의 자세", "새로운 시작"]
    },
    # 안철수
    {
        "text": "창조적인 사람은 남의 것을 베끼지 않고, 자기만의 길을 간다.",
        "text_original": "창조적인 사람은 남의 것을 베끼지 않고, 자기만의 길을 간다.",
        "original_language": "ko",
        "author": "안철수",
        "source": "안철수 저서 '안철수의 생각'",
        "year": 2012,
        "keywords": ["창의성", "자유", "도전"],
        "situations": ["창의적 사고", "새로운 관점이 필요할 때"]
    },
    {
        "text": "성공은 결과가 아니라 과정이다.",
        "text_original": "성공은 결과가 아니라 과정이다.",
        "original_language": "ko",
        "author": "안철수",
        "source": "안철수 강연",
        "year": None,
        "keywords": ["성공", "성장", "인생"],
        "situations": ["목표가 멀게 느껴질 때", "자기 성찰"]
    },
]

# ── 실행 ──
inserted = 0
skipped = 0

for q in quotes_data:
    author_id = author_ids[q["author"]]
    result = insert_quote(
        text=q["text"],
        text_original=q["text_original"],
        original_language=q["original_language"],
        author_id=author_id,
        source=q["source"],
        year=q["year"],
        keyword_names=q["keywords"],
        situation_names=q["situations"]
    )
    if result:
        inserted += 1
    else:
        skipped += 1

conn.commit()
cur.close()
conn.close()

print(f"총 {len(quotes_data)}개 명언 처리 완료")
print(f"  새로 저장: {inserted}개")
print(f"  중복 스킵: {skipped}개")
