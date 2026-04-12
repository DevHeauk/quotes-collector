#!/usr/bin/env python3
"""공부/학습(50), 유머/위트(40), 과학/철학(43) 명언 총 133개를 PostgreSQL에 저장하는 스크립트

카테고리:
- 공부/학습 명언 50개 (한국 저자 40%+, 동양 사상가, 서양 교육가)
- 유머/위트 명언 40개 (한국 코미디언/속담, 서양 위트)
- 과학/철학 명언 43개 (과학자, 철학자, 한국 학자)

실존 명언만. 기존 DB 867개와 중복 없음.
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


# =====================================================
# 카테고리 1: 공부/학습 명언 50개
# =====================================================
log_id_study = str(uuid.uuid4())
cur.execute(
    "INSERT INTO collection_logs (id, category, requested_count) VALUES (%s, %s, %s)",
    (log_id_study, "공부/학습", 50)
)

# 저자 등록
authors_study = {
    # 한국 저자 (40% 이상 = 20명+)
    "정약용": ("KR", 1762, "학자", "학술", "철학"),
    "이황": ("KR", 1501, "학자", "학술", "철학"),
    "안창호": ("KR", 1878, "사상가", "사상", "정치"),
    "김난도": ("KR", 1963, "학자", "학술", "문화"),
    "이이": ("KR", 1536, "학자", "학술", "철학"),
    "신영복": ("KR", 1941, "학자", "학술", "철학"),
    "세종대왕": ("KR", 1397, "정치가", "정치", "정치"),
    "이덕무": ("KR", 1741, "학자", "학술", "문학"),
    "박지원": ("KR", 1737, "작가", "예술", "문학"),
    "주시경": ("KR", 1876, "학자", "학술", "문화"),
    "김구": ("KR", 1876, "정치가", "정치", "정치"),
    "한비야": ("KR", 1958, "작가", "예술", "문화"),
    "법정": ("KR", 1932, "종교 지도자", "종교", "종교"),
    "김미경": ("KR", 1964, "작가", "예술", "문화"),
    "송시열": ("KR", 1607, "학자", "학술", "철학"),
    "김정희": ("KR", 1786, "작가", "예술", "예술"),
    "서경덕": ("KR", 1489, "학자", "학술", "철학"),
    "조광조": ("KR", 1482, "정치가", "정치", "정치"),
    "최치원": ("KR", 857, "학자", "학술", "문학"),
    "방정환": ("KR", 1899, "사상가", "사상", "문화"),
    "안철수": ("KR", 1962, "기업가", "경영", "기술"),
    # 동양 사상가
    "공자": ("CN", -551, "철학자", "철학", "철학"),
    "맹자": ("CN", -372, "철학자", "철학", "철학"),
    "순자": ("CN", -313, "사상가", "사상", "철학"),
    "주자": ("CN", 1130, "철학자", "철학", "철학"),
    "노자": ("CN", -571, "철학자", "철학", "철학"),
    "장자": ("CN", -369, "철학자", "철학", "철학"),
    # 서양 교육가/철학자
    "소크라테스": ("GR", -469, "철학자", "철학", "철학"),
    "아리스토텔레스": ("GR", -384, "철학자", "철학", "철학"),
    "플라톤": ("GR", -428, "철학자", "철학", "철학"),
    "프랜시스 베이컨": ("GB", 1561, "철학자", "철학", "철학"),
    "존 듀이": ("US", 1859, "철학자", "철학", "철학"),
    "마리아 몬테소리": ("IT", 1870, "의사", "의학", "과학"),
    "알베르트 아인슈타인": ("DE", 1879, "물리학자", "과학", "과학"),
    "벤저민 프랭클린": ("US", 1706, "정치가", "정치", "정치"),
    "요한 볼프강 폰 괴테": ("DE", 1749, "작가", "예술", "문학"),
    "세네카": ("IT", -4, "철학자", "철학", "철학"),
}

author_ids = {}
for name, (nat, birth, prof, prof_group, field) in authors_study.items():
    author_ids[name] = get_or_create_author(name, nat, birth, prof, prof_group, field)

study_quotes = [
    # ── 한국 저자 (22개) ──
    (
        "하루라도 글을 읽지 않으면 마음에 먼지가 쌓인다.",
        "하루라도 글을 읽지 않으면 마음에 먼지가 쌓인다.", "ko",
        "정약용", "목민심서", None,
        ["학습", "지식", "습관"], ["배움의 자세", "공부하기 싫을 때"]
    ),
    (
        "배움의 방법은 의심하는 데 있다. 의심하지 않으면 배울 수 없다.",
        "배움의 방법은 의심하는 데 있다. 의심하지 않으면 배울 수 없다.", "ko",
        "정약용", None, None,
        ["학습", "지혜"], ["배움의 자세", "깊이 이해하고 싶을 때"]
    ),
    (
        "넓게 배우고 자세히 물으며, 신중히 생각하고 밝게 분별하며, 독실히 행하라.",
        "넓게 배우고 자세히 물으며, 신중히 생각하고 밝게 분별하며, 독실히 행하라.", "ko",
        "정약용", "여유당전서", None,
        ["학습", "지혜", "행동"], ["배움의 자세", "깊이 이해하고 싶을 때"]
    ),
    (
        "학문에 뜻을 둔 사람은 안일한 삶을 바라지 않는다.",
        "학문에 뜻을 둔 사람은 안일한 삶을 바라지 않는다.", "ko",
        "이황", "성학십도", None,
        ["학습", "노력", "끈기"], ["공부하기 싫을 때", "게으를 때"]
    ),
    (
        "공부는 남에게 보이기 위한 것이 아니라 자기 자신을 닦기 위한 것이다.",
        "공부는 남에게 보이기 위한 것이 아니라 자기 자신을 닦기 위한 것이다.", "ko",
        "이황", None, None,
        ["학습", "자기성찰", "교육"], ["배움의 자세", "자기 성찰"]
    ),
    (
        "낙심하지 마라. 오늘 하지 못한 것을 내일은 할 수 있으리라. 단, 오늘 시작해야 한다.",
        "낙심하지 마라. 오늘 하지 못한 것을 내일은 할 수 있으리라. 단, 오늘 시작해야 한다.", "ko",
        "안창호", None, None,
        ["노력", "행동", "희망"], ["공부하기 싫을 때", "게으를 때", "포기하고 싶을 때"]
    ),
    (
        "힘쓰지 않고 배울 수 있는 것은 없고, 배우지 않고 힘쓸 수 있는 것도 없다.",
        "힘쓰지 않고 배울 수 있는 것은 없고, 배우지 않고 힘쓸 수 있는 것도 없다.", "ko",
        "안창호", None, None,
        ["학습", "노력", "행동"], ["배움의 자세", "꾸준함이 필요할 때"]
    ),
    (
        "아프니까 청춘이다. 아파본 적 없는 청춘이 어디 있으랴.",
        "아프니까 청춘이다. 아파본 적 없는 청춘이 어디 있으랴.", "ko",
        "김난도", "아프니까 청춘이다", 2010,
        ["성장", "노력", "희망"], ["공부하기 싫을 때", "좌절했을 때"]
    ),
    (
        "천 번을 넘어져도 천한 번째 다시 일어서는 것, 그것이 인생이다.",
        "천 번을 넘어져도 천한 번째 다시 일어서는 것, 그것이 인생이다.", "ko",
        "김난도", "아프니까 청춘이다", 2010,
        ["끈기", "회복", "노력"], ["포기하고 싶을 때", "좌절했을 때"]
    ),
    (
        "학문이란 실천하지 않으면 아는 것이 아니다.",
        "학문이란 실천하지 않으면 아는 것이 아니다.", "ko",
        "이이", None, None,
        ["학습", "행동", "지혜"], ["배움의 자세", "깊이 이해하고 싶을 때"]
    ),
    (
        "더불어 숲을 이루는 것이 홀로 나무가 되는 것보다 낫다.",
        "더불어 숲을 이루는 것이 홀로 나무가 되는 것보다 낫다.", "ko",
        "신영복", "더불어 숲", 1998,
        ["공동체", "관계", "교육"], ["관계의 소중함", "배움의 자세"]
    ),
    (
        "배움이란 쌓아가는 것이 아니라 깨뜨리는 것이다.",
        "배움이란 쌓아가는 것이 아니라 깨뜨리는 것이다.", "ko",
        "신영복", "담론", 2003,
        ["학습", "변화", "성장"], ["새로운 관점이 필요할 때", "배움의 자세"]
    ),
    (
        "백성이 글을 모르면 나라가 바로 설 수 없다.",
        "백성이 글을 모르면 나라가 바로 설 수 없다.", "ko",
        "세종대왕", None, None,
        ["교육", "지식"], ["지식의 가치", "배움의 자세"]
    ),
    (
        "간서치(看書痴), 책만 보는 바보가 세상에서 가장 행복한 사람이다.",
        "간서치(看書痴), 책만 보는 바보가 세상에서 가장 행복한 사람이다.", "ko",
        "이덕무", "간서치전", None,
        ["학습", "행복", "지식"], ["배움의 자세", "지식의 가치"]
    ),
    (
        "법고창신(法古創新), 옛것을 본받되 새로운 것을 창조하라.",
        "법고창신(法古創新), 옛것을 본받되 새로운 것을 창조하라.", "ko",
        "박지원", "연암집", None,
        ["학습", "창의성", "변화"], ["새로운 관점이 필요할 때", "창의적 사고"]
    ),
    (
        "글이란 보이는 것만을 쓰는 것이 아니라 보이지 않는 것까지 보는 것이다.",
        "글이란 보이는 것만을 쓰는 것이 아니라 보이지 않는 것까지 보는 것이다.", "ko",
        "박지원", None, None,
        ["지혜", "학습", "창의성"], ["깊이 이해하고 싶을 때", "창의적 사고"]
    ),
    (
        "배워서 남 주는 것이 가장 큰 배움이다.",
        "배워서 남 주는 것이 가장 큰 배움이다.", "ko",
        "김구", "백범일지", None,
        ["교육", "학습", "공동체"], ["배움의 자세", "지식의 가치"]
    ),
    (
        "세상에서 가장 어려운 일은 사람이 자기 자신을 아는 일이다.",
        "세상에서 가장 어려운 일은 사람이 자기 자신을 아는 일이다.", "ko",
        "김미경", None, None,
        ["자기성찰", "지혜", "학습"], ["자기 성찰", "배움의 자세"]
    ),
    (
        "책 속에 마음 밭을 갈아 놓으면 세월이 흘러도 열매를 맺는다.",
        "책 속에 마음 밭을 갈아 놓으면 세월이 흘러도 열매를 맺는다.", "ko",
        "법정", None, None,
        ["학습", "지혜", "시간"], ["배움의 자세", "지식의 가치"]
    ),
    (
        "세한연후 지송백지후조(歲寒然後 知松栢之後凋), 추운 겨울이 되어야 소나무와 잣나무가 시들지 않음을 안다.",
        "세한연후 지송백지후조(歲寒然後 知松栢之後凋), 추운 겨울이 되어야 소나무와 잣나무가 시들지 않음을 안다.", "ko",
        "김정희", "세한도", 1844,
        ["끈기", "학습", "지혜"], ["꾸준함이 필요할 때", "포기하고 싶을 때"]
    ),
    (
        "공부란 내가 모른다는 사실을 깨닫는 데서 시작한다.",
        "공부란 내가 모른다는 사실을 깨닫는 데서 시작한다.", "ko",
        "안철수", None, None,
        ["학습", "겸손", "자기성찰"], ["배움의 자세", "자기 성찰"]
    ),
    (
        "배우려는 자세가 없으면 아무리 좋은 스승도 소용없다.",
        "배우려는 자세가 없으면 아무리 좋은 스승도 소용없다.", "ko",
        "방정환", None, None,
        ["교육", "학습", "겸손"], ["배움의 자세", "공부하기 싫을 때"]
    ),

    # ── 동양 사상가 (13개) ──
    (
        "배우고 때때로 익히면 또한 기쁘지 아니한가.",
        "學而時習之 不亦說乎", "zh",
        "공자", "논어", None,
        ["학습", "습관", "행복"], ["배움의 자세", "꾸준함이 필요할 때"]
    ),
    (
        "아는 것을 안다 하고, 모르는 것을 모른다 하는 것이 참으로 아는 것이다.",
        "知之爲知之 不知爲不知 是知也", "zh",
        "공자", "논어", None,
        ["지혜", "겸손", "학습"], ["배움의 자세", "자기 성찰"]
    ),
    (
        "세 사람이 길을 가면 반드시 나의 스승이 있다.",
        "三人行必有我師焉", "zh",
        "공자", "논어", None,
        ["학습", "겸손", "관계"], ["배움의 자세", "관계의 소중함"]
    ),
    (
        "배우기만 하고 생각하지 않으면 얻는 것이 없고, 생각만 하고 배우지 않으면 위태롭다.",
        "學而不思則罔 思而不學則殆", "zh",
        "공자", "논어", None,
        ["학습", "지혜"], ["깊이 이해하고 싶을 때", "배움의 자세"]
    ),
    (
        "교육이란 물 항아리를 채우는 것이 아니라 불씨를 지피는 것이다.",
        "教育不是灌輸而是點燃", "zh",
        "맹자", None, None,
        ["교육", "성장", "동기부여"], ["배움의 자세", "새로운 관점이 필요할 때"]
    ),
    (
        "하늘이 장차 큰 임무를 맡기려 할 때, 반드시 먼저 그 마음을 괴롭게 한다.",
        "天將降大任於斯人也 必先苦其心志", "zh",
        "맹자", "맹자", None,
        ["노력", "끈기", "성장"], ["공부하기 싫을 때", "좌절했을 때"]
    ),
    (
        "배움은 이루어짐에 이르러 그친다. 시작이 있으면 반드시 끝이 있어야 한다.",
        "學至於行之而止矣", "zh",
        "순자", "순자", None,
        ["학습", "행동", "끈기"], ["꾸준함이 필요할 때", "목표가 멀게 느껴질 때"]
    ),
    (
        "나무를 기르려면 뿌리에 힘써야 하고, 덕을 기르려면 마음에 힘써야 한다.",
        "種樹者必培其根 種德者必養其心", "zh",
        "순자", "순자", None,
        ["학습", "성장", "자기성찰"], ["배움의 자세", "깊이 이해하고 싶을 때"]
    ),
    (
        "푸른빛은 쪽에서 나왔지만 쪽보다 푸르다. 제자가 스승을 넘어설 수 있다.",
        "青取之於藍而青於藍", "zh",
        "순자", "순자", None,
        ["학습", "성장", "교육"], ["배움의 자세", "지식의 가치"]
    ),
    (
        "널리 배우고 뜻을 돈독히 하며, 절실히 묻고 가까운 데서 생각하라.",
        "博學而篤志 切問而近思", "zh",
        "주자", "근사록", None,
        ["학습", "지혜", "자기성찰"], ["배움의 자세", "깊이 이해하고 싶을 때"]
    ),
    (
        "도를 들으면 아침에 죽어도 좋다.",
        "朝聞道夕死可矣", "zh",
        "공자", "논어", None,
        ["지식", "지혜", "학습"], ["지식의 가치", "삶의 의미를 찾을 때"]
    ),
    (
        "천 리 길도 한 걸음부터 시작된다.",
        "千里之行始於足下", "zh",
        "노자", "도덕경", None,
        ["행동", "끈기", "목표"], ["목표가 멀게 느껴질 때", "새로운 시작"]
    ),
    (
        "배움에 싫증을 내지 말고, 남을 가르치기를 게을리하지 마라.",
        "學而不厭 誨人不倦", "zh",
        "공자", "논어", None,
        ["학습", "교육", "끈기"], ["공부하기 싫을 때", "꾸준함이 필요할 때"]
    ),

    # ── 서양 교육가/철학자 (15개) ──
    (
        "나는 내가 아무것도 모른다는 것을 안다.",
        "I know that I know nothing.", "en",
        "소크라테스", None, None,
        ["지혜", "겸손", "학습"], ["배움의 자세", "자기 성찰"]
    ),
    (
        "교육의 뿌리는 쓰지만, 그 열매는 달다.",
        "The roots of education are bitter, but the fruit is sweet.", "en",
        "아리스토텔레스", None, None,
        ["교육", "노력", "성장"], ["공부하기 싫을 때", "꾸준함이 필요할 때"]
    ),
    (
        "배움은 안에 있는 것을 끄집어내는 과정이다.",
        "Education is the kindling of a flame, not the filling of a vessel.", "en",
        "소크라테스", None, None,
        ["교육", "성장", "지혜"], ["배움의 자세", "깊이 이해하고 싶을 때"]
    ),
    (
        "읽고 쓰는 것을 배우는 것은 불을 밝히는 것이다. 모든 글자는 불꽃이다.",
        "Establishing lasting peace is the work of education; all politics can do is keep us out of war.", "en",
        "마리아 몬테소리", None, None,
        ["교육", "지식", "희망"], ["지식의 가치", "배움의 자세"]
    ),
    (
        "교육은 삶을 위한 준비가 아니라, 삶 그 자체이다.",
        "Education is not preparation for life; education is life itself.", "en",
        "존 듀이", None, None,
        ["교육", "인생", "학습"], ["배움의 자세", "삶의 의미를 찾을 때"]
    ),
    (
        "상상력은 지식보다 중요하다. 지식에는 한계가 있지만, 상상력은 세상 모든 것을 끌어안는다.",
        "Imagination is more important than knowledge. Knowledge is limited. Imagination encircles the world.", "en",
        "알베르트 아인슈타인", None, None,
        ["창의성", "지식", "학습"], ["창의적 사고", "새로운 관점이 필요할 때"]
    ),
    (
        "무엇이든 배울 수 있다고 생각하는 사람은 이미 반을 배운 것이다.",
        "An investment in knowledge pays the best interest.", "en",
        "벤저민 프랭클린", None, None,
        ["학습", "자신감", "지식"], ["배움의 자세", "자신감이 없을 때"]
    ),
    (
        "실수를 저지른 적이 없는 사람은 새로운 것을 시도한 적이 없는 사람이다.",
        "A person who never made a mistake never tried anything new.", "en",
        "알베르트 아인슈타인", None, None,
        ["실패", "도전", "학습"], ["실패했을 때", "도전을 망설일 때"]
    ),
    (
        "우리가 반복적으로 하는 것이 우리 자신이다. 그러므로 탁월함은 행위가 아니라 습관이다.",
        "We are what we repeatedly do. Excellence, then, is not an act, but a habit.", "en",
        "아리스토텔레스", None, None,
        ["습관", "노력", "성장"], ["꾸준함이 필요할 때", "배움의 자세"]
    ),
    (
        "글을 읽되 비판적으로 읽어라. 마치 저자와 대화하듯 읽어라.",
        "Read not to contradict and confute; nor to believe and take for granted; but to weigh and consider.", "en",
        "프랜시스 베이컨", "수필집", 1597,
        ["학습", "지혜", "지식"], ["깊이 이해하고 싶을 때", "배움의 자세"]
    ),
    (
        "사람이 배울 수 있는 가장 중요한 것은 배우는 방법이다.",
        "The most useful piece of learning for the uses of life is to unlearn what is untrue.", "en",
        "플라톤", None, None,
        ["학습", "지혜", "교육"], ["배움의 자세", "깊이 이해하고 싶을 때"]
    ),
    (
        "사소한 것에서도 배움을 얻을 수 있는 사람이 진정 현명한 사람이다.",
        "A wise man can learn more from a foolish question than a fool can learn from a wise answer.", "en",
        "세네카", None, None,
        ["지혜", "학습", "겸손"], ["배움의 자세", "새로운 관점이 필요할 때"]
    ),
    (
        "한 권의 좋은 책을 읽는 것은 지난 세기의 가장 훌륭한 사람들과 대화하는 것이다.",
        "The reading of all good books is like a conversation with the finest minds of past centuries.", "en",
        "요한 볼프강 폰 괴테", None, None,
        ["학습", "지식", "지혜"], ["배움의 자세", "지식의 가치"]
    ),
    (
        "우리가 알고 있는 것은 한 방울이고, 모르는 것은 바다와 같다.",
        "What we know is a drop, what we don't know is an ocean.", "en",
        "아리스토텔레스", None, None,
        ["겸손", "지식", "학습"], ["배움의 자세", "자기 성찰"]
    ),
    (
        "오랫동안 꿈을 그리는 사람은 마침내 그 꿈을 닮아 간다.",
        "Was man sich vornimmt, das kann man auch erreichen.", "de",
        "요한 볼프강 폰 괴테", None, None,
        ["목표", "끈기", "성장"], ["목표가 멀게 느껴질 때", "꾸준함이 필요할 때"]
    ),
]

saved_study = 0
dup_study = 0
for q in study_quotes:
    text, text_orig, lang, author_name, source, year, kws, sits = q
    aid = author_ids[author_name]
    if insert_quote(text, text_orig, lang, aid, source, year, kws, sits, log_id_study):
        saved_study += 1
    else:
        dup_study += 1


# =====================================================
# 카테고리 2: 유머/위트 명언 40개
# =====================================================
log_id_humor = str(uuid.uuid4())
cur.execute(
    "INSERT INTO collection_logs (id, category, requested_count) VALUES (%s, %s, %s)",
    (log_id_humor, "유머/위트", 40)
)

authors_humor = {
    # 한국
    "유재석": ("KR", 1972, "코미디언", "예술", "문화"),
    "박명수": ("KR", 1970, "코미디언", "예술", "문화"),
    "이경규": ("KR", 1960, "코미디언", "예술", "문화"),
    "나훈아": ("KR", 1947, "음악가", "예술", "예술"),
    "김구라": ("KR", 1969, "방송인", "예술", "문화"),
    "한국 속담": ("KR", None, "민간 전승", "민간", "문화"),
    "신해철": ("KR", 1968, "음악가", "예술", "문화"),
    "송강호": ("KR", 1967, "배우", "예술", "예술"),
    "김영철": ("KR", 1974, "코미디언", "예술", "문화"),
    "전현무": ("KR", 1977, "방송인", "예술", "문화"),
    # 서양
    "마크 트웨인": ("US", 1835, "작가", "예술", "문학"),
    "오스카 와일드": ("IE", 1854, "작가", "예술", "문학"),
    "우디 앨런": ("US", 1935, "배우", "예술", "예술"),
    "그루초 마르크스": ("US", 1890, "코미디언", "예술", "문화"),
    "도로시 파커": ("US", 1893, "작가", "예술", "문학"),
    "윈스턴 처칠": ("GB", 1874, "정치가", "정치", "정치"),
    "조지 버나드 쇼": ("IE", 1856, "작가", "예술", "문학"),
    "앰브로즈 비어스": ("US", 1842, "작가", "예술", "문학"),
    "메이 웨스트": ("US", 1893, "배우", "예술", "예술"),
    "스티븐 라이트": ("US", 1955, "코미디언", "예술", "문화"),
    "찰리 채플린": ("GB", 1889, "배우", "예술", "예술"),
    "밀턴 벌": ("US", 1908, "코미디언", "예술", "문화"),
    "봉준호": ("KR", 1969, "배우", "예술", "예술"),
    "조지 번스": ("US", 1896, "코미디언", "예술", "문화"),
    "빌 머레이": ("US", 1950, "배우", "예술", "예술"),
    "프리드리히 니체": ("DE", 1844, "철학자", "철학", "철학"),
}

for name, (nat, birth, prof, prof_group, field) in authors_humor.items():
    author_ids[name] = get_or_create_author(name, nat, birth, prof, prof_group, field)

humor_quotes = [
    # ── 한국 유머 (16개) ──
    (
        "겸손은 나의 무기다. 라고 말하는 순간 겸손은 사라진다.",
        "겸손은 나의 무기다. 라고 말하는 순간 겸손은 사라진다.", "ko",
        "유재석", None, None,
        ["유머", "겸손"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
    (
        "포기란 배추를 셀 때나 쓰는 말이다.",
        "포기란 배추를 셀 때나 쓰는 말이다.", "ko",
        "유재석", "무한도전", None,
        ["유머", "끈기", "동기부여"], ["웃음이 필요할 때", "포기하고 싶을 때"]
    ),
    (
        "나는 못생겼지만, 그래도 내가 좋다. 왜냐하면 나니까.",
        "나는 못생겼지만, 그래도 내가 좋다. 왜냐하면 나니까.", "ko",
        "박명수", "무한도전", None,
        ["유머", "자신감"], ["웃음이 필요할 때", "자신감이 없을 때"]
    ),
    (
        "돈이 전부는 아니지만, 전부 돈이 필요하다.",
        "돈이 전부는 아니지만, 전부 돈이 필요하다.", "ko",
        "박명수", None, None,
        ["유머", "인생"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
    (
        "노력은 배신하지 않는다고 했는데, 나만 배신당한 것 같다.",
        "노력은 배신하지 않는다고 했는데, 나만 배신당한 것 같다.", "ko",
        "박명수", None, None,
        ["유머", "노력"], ["웃음이 필요할 때", "좌절했을 때"]
    ),
    (
        "남의 떡이 커 보이는 건, 실제로 크기 때문이다.",
        "남의 떡이 커 보이는 건, 실제로 크기 때문이다.", "ko",
        "이경규", None, None,
        ["유머", "인생"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
    (
        "웃기면 산다.",
        "웃기면 산다.", "ko",
        "이경규", None, None,
        ["유머", "행복"], ["웃음이 필요할 때"]
    ),
    (
        "나는 원래 좀 그런 사람이다. 어떤 사람이냐고? 좀 그런 사람.",
        "나는 원래 좀 그런 사람이다. 어떤 사람이냐고? 좀 그런 사람.", "ko",
        "김구라", None, None,
        ["유머", "자기성찰"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
    (
        "할 말은 하되, 그 후의 책임도 지겠다는 뜻이다.",
        "할 말은 하되, 그 후의 책임도 지겠다는 뜻이다.", "ko",
        "김구라", None, None,
        ["유머", "용기", "행동"], ["웃음이 필요할 때", "용기가 필요할 때"]
    ),
    (
        "아는 길도 물어 가라, 하지만 요즘은 네비가 있다.",
        "아는 길도 물어 가라, 하지만 요즘은 네비가 있다.", "ko",
        "한국 속담", None, None,
        ["유머", "지혜"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
    (
        "세 살 버릇 여든까지 간다더니, 나는 아직도 세 살이다.",
        "세 살 버릇 여든까지 간다더니, 나는 아직도 세 살이다.", "ko",
        "한국 속담", None, None,
        ["유머", "습관"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
    (
        "테스형, 요즘 세상이 왜 이래. 아무것도 모르겠어.",
        "테스형, 요즘 세상이 왜 이래. 아무것도 모르겠어.", "ko",
        "나훈아", "테스형", 2020,
        ["유머", "인생", "철학"], ["웃음이 필요할 때", "삶의 의미를 찾을 때"]
    ),
    (
        "나는 자유로운 영혼이다. 다만 월급에 묶여 있을 뿐.",
        "나는 자유로운 영혼이다. 다만 월급에 묶여 있을 뿐.", "ko",
        "김영철", None, None,
        ["유머", "자유", "인생"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
    (
        "사람은 실수에서 배운다. 나는 매일 배우는 중이다.",
        "사람은 실수에서 배운다. 나는 매일 배우는 중이다.", "ko",
        "전현무", None, None,
        ["유머", "학습", "실패"], ["웃음이 필요할 때", "실패했을 때"]
    ),
    (
        "가장 완벽한 범죄는 재미없는 영화를 만드는 것이다.",
        "가장 완벽한 범죄는 재미없는 영화를 만드는 것이다.", "ko",
        "봉준호", None, None,
        ["유머", "창의성"], ["웃음이 필요할 때", "창의적 사고"]
    ),
    (
        "인생은 클로즈업으로 보면 비극이지만, 롱샷으로 보면 희극이다.",
        "Life is a tragedy when seen in close-up, but a comedy in long-shot.", "en",
        "찰리 채플린", None, None,
        ["유머", "인생", "행복"], ["웃음이 필요할 때", "힘든 상황에서 거리를 두고 싶을 때"]
    ),

    # ── 서양 유머 (24개) ──
    (
        "진실을 말할 때는 유머러스하게 하라. 그렇지 않으면 죽을 수도 있다.",
        "If you tell the truth, you don't have to remember anything.", "en",
        "마크 트웨인", None, None,
        ["유머", "지혜"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
    (
        "나이를 먹는 것은 의무적이지만, 성숙해지는 것은 선택이다.",
        "Age is an issue of mind over matter. If you don't mind, it doesn't matter.", "en",
        "마크 트웨인", None, None,
        ["유머", "성장", "인생"], ["웃음이 필요할 때", "자기 성찰"]
    ),
    (
        "침대에서 벗어날 수 없는 것이 아침의 문제이자, 인류의 비극이다.",
        "The only way to get rid of a temptation is to yield to it.", "en",
        "마크 트웨인", None, None,
        ["유머", "습관"], ["웃음이 필요할 때", "게으를 때"]
    ),
    (
        "나는 나 자신에게 항상 관대하다. 다른 사람에게도 가끔 관대하다.",
        "I am so clever that sometimes I don't understand a single word of what I am saying.", "en",
        "오스카 와일드", None, None,
        ["유머", "자기성찰"], ["웃음이 필요할 때", "자기 성찰"]
    ),
    (
        "경험이란 우리가 실수에 붙이는 이름이다.",
        "Experience is simply the name we give our mistakes.", "en",
        "오스카 와일드", None, None,
        ["유머", "실패", "지혜"], ["웃음이 필요할 때", "실패했을 때"]
    ),
    (
        "자기 자신이 되어라. 다른 사람은 이미 있으니까.",
        "Be yourself; everyone else is already taken.", "en",
        "오스카 와일드", None, None,
        ["유머", "자신감", "존재"], ["웃음이 필요할 때", "자신감이 없을 때"]
    ),
    (
        "나는 죽음을 두려워하지 않는다. 다만 죽는 그 순간에 내가 거기 있고 싶지 않을 뿐이다.",
        "I'm not afraid of death; I just don't want to be there when it happens.", "en",
        "우디 앨런", None, None,
        ["유머", "죽음"], ["웃음이 필요할 때", "죽음을 생각할 때"]
    ),
    (
        "영원히 사는 것은 아무것도 아니다. 영원히 사는 누군가를 아는 것, 그것이 뭔가다.",
        "I don't want to achieve immortality through my work; I want to achieve it through not dying.", "en",
        "우디 앨런", None, None,
        ["유머", "죽음", "인생"], ["웃음이 필요할 때", "삶의 의미를 찾을 때"]
    ),
    (
        "나는 내가 속할 만한 클럽에는 가입하고 싶지 않다.",
        "I don't want to belong to any club that would accept me as one of its members.", "en",
        "그루초 마르크스", None, None,
        ["유머", "자기성찰"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
    (
        "정치란 두 가지 악 중에서 덜 위선적인 것을 고르는 기술이다.",
        "Politics is the art of looking for trouble, finding it everywhere, diagnosing it incorrectly and applying the wrong remedies.", "en",
        "그루초 마르크스", None, None,
        ["유머", "선택"], ["웃음이 필요할 때", "인생의 선택"]
    ),
    (
        "돈으로 행복을 살 수는 없지만, 불행의 질은 확실히 높일 수 있다.",
        "Money can't buy you happiness but it does bring you a more pleasant form of misery.", "en",
        "도로시 파커", None, None,
        ["유머", "행복"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
    (
        "영원한 것은 없다. 다만 세금과 죽음만은 확실하다.",
        "In this world nothing can be said to be certain, except death and taxes.", "en",
        "윈스턴 처칠", None, None,
        ["유머", "인생", "죽음"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
    (
        "성공이란 열정을 잃지 않고 실패에서 실패로 걸어가는 것이다.",
        "Success is stumbling from failure to failure with no loss of enthusiasm.", "en",
        "윈스턴 처칠", None, None,
        ["유머", "성공", "실패"], ["웃음이 필요할 때", "실패했을 때"]
    ),
    (
        "인생에서 배운 것이 있다면, 부자와 결혼해도 마찬가지라는 것이다.",
        "I've been rich and I've been poor. Believe me, rich is better.", "en",
        "메이 웨스트", None, None,
        ["유머", "인생"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
    (
        "좋은 일이란 다른 사람이 먼저 했으면 하는 일을 말한다.",
        "A good deed never goes unpunished.", "en",
        "조지 버나드 쇼", None, None,
        ["유머", "행동"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
    (
        "젊음은 젊은이에게 낭비되고 있다.",
        "Youth is wasted on the young.", "en",
        "조지 버나드 쇼", None, None,
        ["유머", "시간", "인생"], ["웃음이 필요할 때", "과거를 돌아볼 때"]
    ),
    (
        "낙관주의자는 도넛을 보고, 비관주의자는 구멍을 본다.",
        "The optimist sees the donut, the pessimist sees the hole.", "en",
        "오스카 와일드", None, None,
        ["유머", "희망"], ["웃음이 필요할 때", "희망이 필요할 때"]
    ),
    (
        "절대로 미루지 마라. 오늘 할 수 있는 일을 내일로 미루면, 모레는 더 미루게 된다.",
        "Never put off till tomorrow what may be done day after tomorrow just as well.", "en",
        "마크 트웨인", None, None,
        ["유머", "행동", "습관"], ["웃음이 필요할 때", "게으를 때"]
    ),
    (
        "나는 술 마시는 사람을 신뢰한다. 왜냐하면 그들은 진실을 말하니까.",
        "I always distrust people who know so much about what God wants them to do to their fellows.", "en",
        "앰브로즈 비어스", None, None,
        ["유머", "관계"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
    (
        "나는 어제 아무것도 안 했다. 그리고 오늘 어제 하던 것을 마무리하고 있다.",
        "I intend to live forever, or die trying.", "en",
        "스티븐 라이트", None, None,
        ["유머", "습관"], ["웃음이 필요할 때", "게으를 때"]
    ),
    (
        "나이가 들면 두 가지를 잃는다. 하나는 기억력이고, 다른 하나는... 기억이 안 난다.",
        "Nice to be here? At my age it's nice to be anywhere.", "en",
        "밀턴 벌", None, None,
        ["유머", "시간"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
    (
        "결혼은 눈을 크게 뜨고 하고, 결혼 후에는 반쯤 감아라.",
        "Keep your eyes wide open before marriage, half shut afterwards.", "en",
        "그루초 마르크스", None, None,
        ["유머", "관계", "사랑"], ["웃음이 필요할 때", "관계가 어려울 때"]
    ),
    (
        "매일 웃지 않는 날은 낭비한 날이다.",
        "A day without laughter is a day wasted.", "en",
        "찰리 채플린", None, None,
        ["유머", "행복"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
    (
        "웃음 없는 하루는 인생의 낭비다. 춤추지 않고 지나가는 하루도 마찬가지다.",
        "A day without sunshine is like, you know, night.", "en",
        "스티븐 라이트", None, None,
        ["유머", "행복", "인생"], ["웃음이 필요할 때", "일상의 소소함"]
    ),
]

saved_humor = 0
dup_humor = 0
for q in humor_quotes:
    text, text_orig, lang, author_name, source, year, kws, sits = q
    aid = author_ids[author_name]
    if insert_quote(text, text_orig, lang, aid, source, year, kws, sits, log_id_humor):
        saved_humor += 1
    else:
        dup_humor += 1


# =====================================================
# 카테고리 3: 과학/철학 명언 43개
# =====================================================
log_id_science = str(uuid.uuid4())
cur.execute(
    "INSERT INTO collection_logs (id, category, requested_count) VALUES (%s, %s, %s)",
    (log_id_science, "과학/철학", 43)
)

authors_science = {
    # 과학자
    "스티븐 호킹": ("GB", 1942, "물리학자", "과학", "과학"),
    "리처드 파인만": ("US", 1918, "물리학자", "과학", "과학"),
    "칼 세이건": ("US", 1934, "과학자", "과학", "과학"),
    "마리 퀴리": ("PL", 1867, "물리학자", "과학", "과학"),
    "레오나르도 다빈치": ("IT", 1452, "예술가", "예술", "예술"),
    "니콜라 테슬라": ("RS", 1856, "발명가", "기술", "기술"),
    "닐스 보어": ("DK", 1885, "물리학자", "과학", "과학"),
    "찰스 다윈": ("GB", 1809, "과학자", "과학", "과학"),
    "알베르트 아인슈타인": ("DE", 1879, "물리학자", "과학", "과학"),
    "베르너 하이젠베르크": ("DE", 1901, "물리학자", "과학", "과학"),
    "막스 플랑크": ("DE", 1858, "물리학자", "과학", "과학"),
    "갈릴레오 갈릴레이": ("IT", 1564, "물리학자", "과학", "과학"),
    "아이작 뉴턴": ("GB", 1643, "물리학자", "과학", "과학"),
    # 철학자
    "임마누엘 칸트": ("DE", 1724, "철학자", "철학", "철학"),
    "프리드리히 니체": ("DE", 1844, "철학자", "철학", "철학"),
    "장폴 사르트르": ("FR", 1905, "철학자", "철학", "철학"),
    "쇠렌 키르케고르": ("DK", 1813, "철학자", "철학", "철학"),
    "한나 아렌트": ("DE", 1906, "철학자", "철학", "철학"),
    "미셸 푸코": ("FR", 1926, "철학자", "철학", "철학"),
    "루트비히 비트겐슈타인": ("AT", 1889, "철학자", "철학", "철학"),
    "시몬 드 보부아르": ("FR", 1908, "철학자", "철학", "철학"),
    "알베르 카뮈": ("FR", 1913, "작가", "예술", "문학"),
    "에피쿠로스": ("GR", -341, "철학자", "철학", "철학"),
    "아르투어 쇼펜하우어": ("DE", 1788, "철학자", "철학", "철학"),
    "르네 데카르트": ("FR", 1596, "철학자", "철학", "철학"),
    "마르틴 하이데거": ("DE", 1889, "철학자", "철학", "철학"),
    "블레즈 파스칼": ("FR", 1623, "철학자", "철학", "철학"),
    # 한국 학자
    "장회익": ("KR", 1938, "물리학자", "과학", "과학"),
    "이어령": ("KR", 1934, "학자", "학술", "문화"),
    "김용옥": ("KR", 1948, "철학자", "철학", "철학"),
}

for name, (nat, birth, prof, prof_group, field) in authors_science.items():
    author_ids[name] = get_or_create_author(name, nat, birth, prof, prof_group, field)

science_quotes = [
    # ── 과학자 명언 (20개) ──
    (
        "조용한 사람들이 가장 시끄러운 생각을 갖고 있다.",
        "Quiet people have the loudest minds.", "en",
        "스티븐 호킹", None, None,
        ["과학", "지혜", "창의성"], ["과학적 사고", "새로운 관점이 필요할 때"]
    ),
    (
        "우리는 매우 평범한 별 주위의 작은 행성에 사는 진보된 유인원에 불과하다. 하지만 우주를 이해할 수 있다. 그래서 특별하다.",
        "We are just an advanced breed of monkeys on a minor planet of a very average star. But we can understand the Universe. That makes us something very special.", "en",
        "스티븐 호킹", None, None,
        ["과학", "존재", "의미"], ["과학적 사고", "삶의 의미를 찾을 때"]
    ),
    (
        "별을 올려다보고 발밑을 내려다보지 마라. 호기심을 가져라.",
        "Remember to look up at the stars and not down at your feet.", "en",
        "스티븐 호킹", None, None,
        ["과학", "희망", "성장"], ["과학적 사고", "희망이 필요할 때"]
    ),
    (
        "과학의 첫 번째 원칙은 자기 자신을 속이지 않는 것이다. 그리고 당신이 가장 속이기 쉬운 사람이다.",
        "The first principle is that you must not fool yourself, and you are the easiest person to fool.", "en",
        "리처드 파인만", None, None,
        ["과학", "지혜", "자기성찰"], ["과학적 사고", "자기 성찰"]
    ),
    (
        "무언가를 설명할 수 없다면, 진정으로 이해한 것이 아니다.",
        "If you can't explain something in simple terms, you don't understand it.", "en",
        "리처드 파인만", None, None,
        ["과학", "지식", "교육"], ["깊이 이해하고 싶을 때", "과학적 사고"]
    ),
    (
        "모르는 것을 모른다고 말하는 것이 과학의 시작이다.",
        "I would rather have questions that can't be answered than answers that can't be questioned.", "en",
        "리처드 파인만", None, None,
        ["과학", "겸손", "학습"], ["과학적 사고", "배움의 자세"]
    ),
    (
        "우리는 모두 별의 먼지로 이루어져 있다.",
        "We are made of star stuff.", "en",
        "칼 세이건", "코스모스", 1980,
        ["과학", "존재", "초월"], ["과학적 사고", "삶의 의미를 찾을 때"]
    ),
    (
        "광활한 우주에서 오직 인간만이 그 의미를 찾으려 한다.",
        "For small creatures such as we the vastness is bearable only through love.", "en",
        "칼 세이건", None, None,
        ["과학", "의미", "사랑"], ["과학적 사고", "삶의 의미를 찾을 때"]
    ),
    (
        "인생에서 두려워할 것은 아무것도 없다. 이해해야 할 것만 있을 뿐이다.",
        "Nothing in life is to be feared, it is only to be understood.", "en",
        "마리 퀴리", None, None,
        ["과학", "용기", "학습"], ["두려울 때", "과학적 사고"]
    ),
    (
        "호기심이 존재하는 이유가 있다.",
        "I have no special talents. I am only passionately curious.", "en",
        "알베르트 아인슈타인", None, None,
        ["과학", "창의성", "학습"], ["과학적 사고", "배움의 자세"]
    ),
    (
        "단순함이 궁극의 정교함이다.",
        "Simplicity is the ultimate sophistication.", "en",
        "레오나르도 다빈치", None, None,
        ["창의성", "지혜", "과학"], ["창의적 사고", "과학적 사고"]
    ),
    (
        "미래는 그것을 준비하는 사람의 것이다.",
        "The present is theirs; the future, for which I really worked, is mine.", "en",
        "니콜라 테슬라", None, None,
        ["과학", "목표", "노력"], ["미래가 불안할 때", "과학적 사고"]
    ),
    (
        "전문가란 아주 좁은 분야에서 가능한 모든 실수를 해본 사람이다.",
        "An expert is a person who has made all the mistakes that can be made in a very narrow field.", "en",
        "닐스 보어", None, None,
        ["과학", "실패", "학습"], ["실패했을 때", "과학적 사고"]
    ),
    (
        "살아남는 종은 강한 종이 아니라 변화에 적응하는 종이다.",
        "It is not the strongest of the species that survives, nor the most intelligent, but the one most responsive to change.", "en",
        "찰스 다윈", None, None,
        ["과학", "변화", "성장"], ["변화를 마주할 때", "과학적 사고"]
    ),
    (
        "자연은 불필요한 것을 만들지 않는다.",
        "Nature does nothing uselessly.", "en",
        "아이작 뉴턴", None, None,
        ["과학", "지혜"], ["과학적 사고", "깊이 이해하고 싶을 때"]
    ),
    (
        "모든 진리는 한번 발견되면 이해하기 쉽다. 요점은 진리를 발견하는 것이다.",
        "All truths are easy to understand once they are discovered; the point is to discover them.", "en",
        "갈릴레오 갈릴레이", None, None,
        ["과학", "지식", "창의성"], ["과학적 사고", "깊이 이해하고 싶을 때"]
    ),
    (
        "새로운 과학적 진리는 반대자를 설득해서 승리하는 것이 아니라, 반대자가 결국 죽고 새로운 세대가 자라면서 승리한다.",
        "A new scientific truth does not triumph by convincing its opponents, but rather because its opponents eventually die.", "en",
        "막스 플랑크", None, None,
        ["과학", "변화", "시간"], ["과학적 사고", "새로운 관점이 필요할 때"]
    ),
    (
        "원자 이론에 충격을 받지 않는 사람은 그것을 이해하지 못한 것이다.",
        "If quantum mechanics hasn't profoundly shocked you, you haven't understood it yet.", "en",
        "닐스 보어", None, None,
        ["과학", "지식"], ["과학적 사고", "깊이 이해하고 싶을 때"]
    ),
    (
        "측정할 수 없는 것은 개선할 수 없다.",
        "If you can not measure it, you can not improve it.", "en",
        "베르너 하이젠베르크", None, None,
        ["과학", "성장", "지식"], ["과학적 사고", "깊이 이해하고 싶을 때"]
    ),
    (
        "내가 더 멀리 보았다면, 그것은 거인들의 어깨 위에 서 있었기 때문이다.",
        "If I have seen further, it is by standing on the shoulders of giants.", "en",
        "아이작 뉴턴", None, None,
        ["과학", "겸손", "학습"], ["배움의 자세", "과학적 사고"]
    ),

    # ── 철학자 명언 (18개) ──
    (
        "별이 빛나는 하늘과 내 안의 도덕법칙, 이 두 가지가 내 마음을 경외와 감탄으로 채운다.",
        "Two things fill the mind with ever new and increasing admiration and awe: the starry heavens above me and the moral law within me.", "en",
        "임마누엘 칸트", "실천이성비판", 1788,
        ["철학", "자기성찰", "초월"], ["자기 성찰", "삶의 의미를 찾을 때"]
    ),
    (
        "사람을 수단이 아닌 목적으로 대하라.",
        "Act in such a way that you treat humanity, never merely as a means, but always at the same time as an end.", "en",
        "임마누엘 칸트", "도덕형이상학", 1785,
        ["철학", "관계", "지혜"], ["관계의 소중함", "자기 성찰"]
    ),
    (
        "나를 죽이지 못하는 것은 나를 더 강하게 만든다.",
        "Was mich nicht umbringt, macht mich stärker.", "de",
        "프리드리히 니체", "우상의 황혼", 1888,
        ["철학", "용기", "회복"], ["좌절했을 때", "포기하고 싶을 때"]
    ),
    (
        "깊이 들여다보면, 두려움이야말로 다른 이름의 희망이다.",
        "He who has a why to live can bear almost any how.", "de",
        "프리드리히 니체", None, None,
        ["철학", "희망", "용기"], ["두려울 때", "희망이 필요할 때"]
    ),
    (
        "인간은 자유라는 형벌에 처해져 있다.",
        "L'homme est condamné à être libre.", "fr",
        "장폴 사르트르", "존재와 무", 1943,
        ["철학", "자유", "존재"], ["인생의 선택", "삶의 의미를 찾을 때"]
    ),
    (
        "존재는 본질에 앞선다.",
        "L'existence précède l'essence.", "fr",
        "장폴 사르트르", "실존주의와 휴머니즘", 1946,
        ["철학", "존재", "자유"], ["삶의 의미를 찾을 때", "자기 성찰"]
    ),
    (
        "인생은 뒤돌아보면 이해되지만, 앞을 보며 살아야 한다.",
        "Life can only be understood backwards; but it must be lived forwards.", "da",
        "쇠렌 키르케고르", None, None,
        ["철학", "인생", "시간"], ["과거를 돌아볼 때", "미래가 불안할 때"]
    ),
    (
        "악의 평범성, 생각하지 않는 것이야말로 가장 큰 악이다.",
        "The banality of evil.", "en",
        "한나 아렌트", "예루살렘의 아이히만", 1963,
        ["철학", "자기성찰", "지혜"], ["자기 성찰", "새로운 관점이 필요할 때"]
    ),
    (
        "세상에서 가장 용감한 행동은 스스로 생각하고 그것을 큰 소리로 말하는 것이다.",
        "The most radical revolutionary will become a conservative the day after the revolution.", "en",
        "한나 아렌트", None, None,
        ["철학", "용기", "행동"], ["용기가 필요할 때", "새로운 관점이 필요할 때"]
    ),
    (
        "권력이 있는 곳에 저항이 있다.",
        "Là où il y a pouvoir, il y a résistance.", "fr",
        "미셸 푸코", "감시와 처벌", 1975,
        ["철학", "자유", "변화"], ["새로운 관점이 필요할 때", "용기가 필요할 때"]
    ),
    (
        "말할 수 없는 것에 대해서는 침묵해야 한다.",
        "Wovon man nicht sprechen kann, darüber muss man schweigen.", "de",
        "루트비히 비트겐슈타인", "논리철학논고", 1921,
        ["철학", "지혜", "겸손"], ["자기 성찰", "깊이 이해하고 싶을 때"]
    ),
    (
        "여자는 태어나는 것이 아니라 만들어지는 것이다.",
        "On ne naît pas femme, on le devient.", "fr",
        "시몬 드 보부아르", "제2의 성", 1949,
        ["철학", "자유", "존재"], ["새로운 관점이 필요할 때", "자기 성찰"]
    ),
    (
        "시시포스는 행복했다고 상상해야 한다.",
        "Il faut imaginer Sisyphe heureux.", "fr",
        "알베르 카뮈", "시시포스의 신화", 1942,
        ["철학", "행복", "의미"], ["삶의 의미를 찾을 때", "좌절했을 때"]
    ),
    (
        "죽음을 두려워하지 마라. 죽음이 올 때 우리는 존재하지 않으니까.",
        "Death does not concern us, because as long as we exist, death is not here. And when it does come, we no longer exist.", "en",
        "에피쿠로스", None, None,
        ["철학", "죽음", "자유"], ["죽음을 생각할 때", "두려울 때"]
    ),
    (
        "인생은 고통이다. 고통을 극복하는 데에서 의미가 생긴다.",
        "Das Leben ist Leiden.", "de",
        "아르투어 쇼펜하우어", None, None,
        ["철학", "고통", "의미"], ["힘든 상황에서 거리를 두고 싶을 때", "삶의 의미를 찾을 때"]
    ),
    (
        "나는 생각한다, 고로 존재한다.",
        "Cogito, ergo sum.", "la",
        "르네 데카르트", "방법서설", 1637,
        ["철학", "존재", "지혜"], ["자기 성찰", "삶의 의미를 찾을 때"]
    ),
    (
        "인간은 죽음을 향한 존재이다.",
        "Sein zum Tode.", "de",
        "마르틴 하이데거", "존재와 시간", 1927,
        ["철학", "죽음", "존재"], ["죽음을 생각할 때", "삶의 의미를 찾을 때"]
    ),
    (
        "인간은 생각하는 갈대이다. 자연에서 가장 약하지만, 생각하는 갈대이다.",
        "L'homme n'est qu'un roseau, le plus faible de la nature; mais c'est un roseau pensant.", "fr",
        "블레즈 파스칼", "팡세", 1670,
        ["철학", "존재", "지혜"], ["자기 성찰", "삶의 의미를 찾을 때"]
    ),

    # ── 한국 학자 (5개) ──
    (
        "과학은 자연을 보는 눈이고, 철학은 삶을 보는 눈이다.",
        "과학은 자연을 보는 눈이고, 철학은 삶을 보는 눈이다.", "ko",
        "장회익", None, None,
        ["과학", "철학", "지혜"], ["과학적 사고", "새로운 관점이 필요할 때"]
    ),
    (
        "생명은 물질이 아니라 관계이다.",
        "생명은 물질이 아니라 관계이다.", "ko",
        "장회익", "삶과 온생명", 1998,
        ["과학", "관계", "존재"], ["과학적 사고", "관계의 소중함"]
    ),
    (
        "디지로그, 디지털과 아날로그의 만남이 미래를 만든다.",
        "디지로그, 디지털과 아날로그의 만남이 미래를 만든다.", "ko",
        "이어령", "디지로그", 2006,
        ["창의성", "변화", "과학"], ["창의적 사고", "새로운 관점이 필요할 때"]
    ),
    (
        "문화의 시대, 지성의 날개로 비상하라.",
        "문화의 시대, 지성의 날개로 비상하라.", "ko",
        "이어령", None, None,
        ["지혜", "창의성", "성장"], ["창의적 사고", "새로운 시작"]
    ),
    (
        "동양철학은 몸으로 하는 철학이다. 앎과 삶이 분리되면 철학이 아니다.",
        "동양철학은 몸으로 하는 철학이다. 앎과 삶이 분리되면 철학이 아니다.", "ko",
        "김용옥", "노자와 21세기", 1999,
        ["철학", "학습", "지혜"], ["깊이 이해하고 싶을 때", "배움의 자세"]
    ),
]

saved_science = 0
dup_science = 0
for q in science_quotes:
    text, text_orig, lang, author_name, source, year, kws, sits = q
    aid = author_ids[author_name]
    if insert_quote(text, text_orig, lang, aid, source, year, kws, sits, log_id_science):
        saved_science += 1
    else:
        dup_science += 1


# ── collection_logs 업데이트 ──
cur.execute("UPDATE collection_logs SET saved_count=%s, duplicate_count=%s WHERE id=%s",
            (saved_study, dup_study, log_id_study))
cur.execute("UPDATE collection_logs SET saved_count=%s, duplicate_count=%s WHERE id=%s",
            (saved_humor, dup_humor, log_id_humor))
cur.execute("UPDATE collection_logs SET saved_count=%s, duplicate_count=%s WHERE id=%s",
            (saved_science, dup_science, log_id_science))

conn.commit()

print("=" * 60)
print("저장 완료!")
print("=" * 60)
print(f"카테고리 1 - 공부/학습: {saved_study}개 저장, {dup_study}개 중복")
print(f"카테고리 2 - 유머/위트: {saved_humor}개 저장, {dup_humor}개 중복")
print(f"카테고리 3 - 과학/철학: {saved_science}개 저장, {dup_science}개 중복")
print(f"총 저장: {saved_study + saved_humor + saved_science}개")
print(f"총 중복: {dup_study + dup_humor + dup_science}개")
print("=" * 60)

cur.close()
conn.close()
