#!/usr/bin/env python3
"""한국 드라마/영화 명대사 60개 + 고사성어 60개를 PostgreSQL에 저장하는 스크립트"""

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

# ========================================================================
# 카테고리 1: 한국 드라마/영화 명대사 60개
# ========================================================================

drama_movie_quotes = [
    # 대장금
    {
        "text": "제가 만든 음식이 전하의 수라상에 오를 수 있다면, 그것이 제 꿈입니다.",
        "author": "서장금 (대장금)", "source": "대장금", "year": 2003,
        "keywords": ["목표", "도전"], "situations": ["목표가 멀게 느껴질 때", "새로운 시작"]
    },
    {
        "text": "사람의 혀는 만 가지 맛을 알 수 있사옵니다.",
        "author": "서장금 (대장금)", "source": "대장금", "year": 2003,
        "keywords": ["지식", "학습"], "situations": ["깊이 이해하고 싶을 때"]
    },
    # 미생
    {
        "text": "아직 살아있지 못한 자, 미생.",
        "author": "장그래 (미생)", "source": "미생", "year": 2014,
        "keywords": ["인생", "성장"], "situations": ["새로운 시작"]
    },
    {
        "text": "안 된다고? 아직 해보지도 않았잖아.",
        "author": "오상식 (미생)", "source": "미생", "year": 2014,
        "keywords": ["도전", "용기"], "situations": ["도전을 망설일 때", "포기하고 싶을 때"]
    },
    {
        "text": "바둑에서는 한 수를 둘 때 전체를 본다. 한 수가 아무리 좋아도 전체를 망치면 악수다.",
        "author": "장그래 (미생)", "source": "미생", "year": 2014,
        "keywords": ["지혜", "선택"], "situations": ["인생의 선택", "새로운 관점이 필요할 때"]
    },
    # 이태원클라쓰
    {
        "text": "밤이 길수록 새벽은 가까이 오는 법이다.",
        "author": "박세로이 (이태원클라쓰)", "source": "이태원클라쓰", "year": 2020,
        "keywords": ["희망", "끈기"], "situations": ["절망적일 때", "희망이 필요할 때"]
    },
    {
        "text": "나는 내가 하고 싶은 대로 살았고, 후회 없다.",
        "author": "박세로이 (이태원클라쓰)", "source": "이태원클라쓰", "year": 2020,
        "keywords": ["자유", "선택"], "situations": ["인생의 선택", "자기 성찰"]
    },
    {
        "text": "가치관이 다른 거지, 틀린 게 아니잖아.",
        "author": "박세로이 (이태원클라쓰)", "source": "이태원클라쓰", "year": 2020,
        "keywords": ["자유", "관계"], "situations": ["관계가 어려울 때", "새로운 관점이 필요할 때"]
    },
    # 도깨비
    {
        "text": "첫눈이 오면... 좋겠다.",
        "author": "지은탁 (도깨비)", "source": "도깨비", "year": 2016,
        "keywords": ["사랑", "희망"], "situations": ["사랑을 느낄 때", "희망이 필요할 때"]
    },
    {
        "text": "누군가의 첫사랑이 되는 것보다 마지막 사랑이 되는 것이 더 좋다.",
        "author": "김신 (도깨비)", "source": "도깨비", "year": 2016,
        "keywords": ["사랑", "관계"], "situations": ["사랑을 느낄 때", "사랑의 본질을 고민할 때"]
    },
    {
        "text": "신이 인간에게 줄 수 있는 가장 큰 벌은 기억이야.",
        "author": "김신 (도깨비)", "source": "도깨비", "year": 2016,
        "keywords": ["고통", "시간"], "situations": ["과거를 돌아볼 때", "힘든 상황에서 거리를 두고 싶을 때"]
    },
    # 응답하라 1988
    {
        "text": "사람이 변하는 건 아니야, 변한 것처럼 보일 뿐이야. 원래 그 사람 안에 있던 거야.",
        "author": "성동일 (응답하라 1988)", "source": "응답하라 1988", "year": 2015,
        "keywords": ["인생", "자기성찰"], "situations": ["자기 성찰", "관계의 소중함"]
    },
    {
        "text": "어른이 되면 괜찮을 줄 알았는데, 어른이라서 괜찮은 건 아무것도 없더라.",
        "author": "성동일 (응답하라 1988)", "source": "응답하라 1988", "year": 2015,
        "keywords": ["인생", "성장"], "situations": ["자기 성찰", "외로울 때"]
    },
    {
        "text": "미안하다, 아빠도 아빠가 처음이라.",
        "author": "성동일 (응답하라 1988)", "source": "응답하라 1988", "year": 2015,
        "keywords": ["가족", "사랑"], "situations": ["관계의 소중함", "감사할 때"]
    },
    # 응답하라 1994
    {
        "text": "혼자 잘 살아보겠다는 것은 정말 불가능한 일이다.",
        "author": "쓰레기 (응답하라 1994)", "source": "응답하라 1994", "year": 2013,
        "keywords": ["관계", "공동체"], "situations": ["관계의 소중함", "외로울 때"]
    },
    # 별에서 온 그대
    {
        "text": "보고 싶다는 말 대신 사랑한다는 말 대신, 이 말밖에 떠오르지 않았다. 거기 가지 마.",
        "author": "도민준 (별에서 온 그대)", "source": "별에서 온 그대", "year": 2013,
        "keywords": ["사랑", "고통"], "situations": ["사랑을 느낄 때", "사랑의 본질을 고민할 때"]
    },
    {
        "text": "인간의 삶은 영원하지 않기에 아름다운 거야.",
        "author": "도민준 (별에서 온 그대)", "source": "별에서 온 그대", "year": 2013,
        "keywords": ["인생", "시간"], "situations": ["삶의 의미를 찾을 때", "현재를 살고 싶을 때"]
    },
    # 시그널
    {
        "text": "과거를 바꾸면 현재도 바뀐다.",
        "author": "이재한 (시그널)", "source": "시그널", "year": 2016,
        "keywords": ["변화", "시간"], "situations": ["과거를 돌아볼 때", "변화를 마주할 때"]
    },
    {
        "text": "포기하지 마, 아직 끝나지 않았어.",
        "author": "이재한 (시그널)", "source": "시그널", "year": 2016,
        "keywords": ["끈기", "희망"], "situations": ["포기하고 싶을 때", "희망이 필요할 때"]
    },
    # 나의 아저씨
    {
        "text": "힘내라는 말, 하지 마세요. 힘내고 있으니까.",
        "author": "이지안 (나의 아저씨)", "source": "나의 아저씨", "year": 2018,
        "keywords": ["고통", "끈기"], "situations": ["힘든 상황에서 거리를 두고 싶을 때", "좌절했을 때"]
    },
    {
        "text": "세상에 나쁜 사람은 없다. 불행한 사람이 있을 뿐이다.",
        "author": "박동훈 (나의 아저씨)", "source": "나의 아저씨", "year": 2018,
        "keywords": ["인생", "겸손"], "situations": ["관계가 어려울 때", "새로운 관점이 필요할 때"]
    },
    # SKY캐슬
    {
        "text": "아이의 인생은 아이의 것이에요.",
        "author": "김주영 (SKY캐슬)", "source": "SKY캐슬", "year": 2018,
        "keywords": ["교육", "자유"], "situations": ["관계가 어려울 때", "자기 성찰"]
    },
    {
        "text": "성적이 인생의 전부가 아닙니다.",
        "author": "차민혁 (SKY캐슬)", "source": "SKY캐슬", "year": 2018,
        "keywords": ["교육", "인생"], "situations": ["자기 성찰", "새로운 관점이 필요할 때"]
    },
    # 슬기로운 의사생활
    {
        "text": "세상에 쉬운 수술은 없어. 그러니까 최선을 다하는 거야.",
        "author": "이익준 (슬기로운 의사생활)", "source": "슬기로운 의사생활", "year": 2020,
        "keywords": ["노력", "겸손"], "situations": ["배움의 자세", "용기가 필요할 때"]
    },
    {
        "text": "우리 같이 늙자, 오래오래.",
        "author": "김준완 (슬기로운 의사생활)", "source": "슬기로운 의사생활", "year": 2020,
        "keywords": ["사랑", "우정"], "situations": ["관계의 소중함", "사랑을 느낄 때"]
    },
    # 비밀의 숲
    {
        "text": "진실은 불편하지만, 거짓보다 낫다.",
        "author": "황시목 (비밀의 숲)", "source": "비밀의 숲", "year": 2017,
        "keywords": ["선택", "용기"], "situations": ["용기가 필요할 때", "인생의 선택"]
    },
    # 기생충
    {
        "text": "아들아, 너는 계획이 다 있구나.",
        "author": "기택 (기생충)", "source": "기생충", "year": 2019,
        "keywords": ["인생", "유머"], "situations": ["웃음이 필요할 때", "일상의 소소함"]
    },
    {
        "text": "제일 좋은 계획은 무계획이야. 계획이 없으면 실패할 일도 없어.",
        "author": "기택 (기생충)", "source": "기생충", "year": 2019,
        "keywords": ["인생", "실패"], "situations": ["실패했을 때", "새로운 관점이 필요할 때"]
    },
    {
        "text": "그 선을 넘지 마라.",
        "author": "동익 (기생충)", "source": "기생충", "year": 2019,
        "keywords": ["관계", "선택"], "situations": ["관계가 어려울 때", "인생의 선택"]
    },
    # 올드보이
    {
        "text": "웃어라, 온 세상이 너와 함께 웃을 것이다. 울어라, 너 혼자만 울 것이다.",
        "author": "오대수 (올드보이)", "source": "올드보이", "year": 2003,
        "keywords": ["고통", "인생"], "situations": ["외로울 때", "힘든 상황에서 거리를 두고 싶을 때"]
    },
    # 건축학개론
    {
        "text": "그때 그렇게 하지 않았으면 어떻게 됐을까.",
        "author": "승민 (건축학개론)", "source": "건축학개론", "year": 2012,
        "keywords": ["시간", "선택"], "situations": ["과거를 돌아볼 때", "자기 성찰"]
    },
    {
        "text": "기억은 미화되기 마련이야.",
        "author": "승민 (건축학개론)", "source": "건축학개론", "year": 2012,
        "keywords": ["시간", "자기성찰"], "situations": ["과거를 돌아볼 때"]
    },
    # 써니
    {
        "text": "우리가 만약 다시 만난다면, 그때도 친구할 수 있을까?",
        "author": "나미 (써니)", "source": "써니", "year": 2011,
        "keywords": ["우정", "시간"], "situations": ["관계의 소중함", "과거를 돌아볼 때"]
    },
    {
        "text": "지금 이 순간이 청춘이라는 거, 그때는 몰랐어.",
        "author": "나미 (써니)", "source": "써니", "year": 2011,
        "keywords": ["시간", "인생"], "situations": ["현재를 살고 싶을 때", "과거를 돌아볼 때"]
    },
    # 변호인
    {
        "text": "국가가 국민을 지켜주지 않으면, 국민이 국가를 지킬 이유가 없습니다.",
        "author": "송우석 (변호인)", "source": "변호인", "year": 2013,
        "keywords": ["자유", "용기"], "situations": ["용기가 필요할 때"]
    },
    {
        "text": "대한민국 국민 누구도 법 앞에 차별받아서는 안 됩니다.",
        "author": "송우석 (변호인)", "source": "변호인", "year": 2013,
        "keywords": ["자유", "용기"], "situations": ["용기가 필요할 때", "인생의 선택"]
    },
    # 택시운전사
    {
        "text": "사람이 사람을 도와야지, 그게 사람이지.",
        "author": "김만섭 (택시운전사)", "source": "택시운전사", "year": 2017,
        "keywords": ["공동체", "관계"], "situations": ["관계의 소중함", "용기가 필요할 때"]
    },
    {
        "text": "잘 모르겄는데, 내가 봤으니까 그냥 못 지나치겠어.",
        "author": "김만섭 (택시운전사)", "source": "택시운전사", "year": 2017,
        "keywords": ["용기", "행동"], "situations": ["용기가 필요할 때", "도전을 망설일 때"]
    },
    # 1987
    {
        "text": "역사는 바뀌지 않는다. 다만 역사를 만드는 건 사람이다.",
        "author": "한병용 (1987)", "source": "1987", "year": 2017,
        "keywords": ["변화", "행동"], "situations": ["용기가 필요할 때", "변화를 마주할 때"]
    },
    # 국제시장
    {
        "text": "이만하면 내 잘 살았지예?",
        "author": "덕수 (국제시장)", "source": "국제시장", "year": 2014,
        "keywords": ["인생", "가족"], "situations": ["자기 성찰", "감사할 때"]
    },
    {
        "text": "한 번도 내 하고 싶은 대로 산 적 없다. 근데 후회는 없다.",
        "author": "덕수 (국제시장)", "source": "국제시장", "year": 2014,
        "keywords": ["인생", "가족"], "situations": ["자기 성찰", "삶의 의미를 찾을 때"]
    },
    # 극한직업
    {
        "text": "형사가 치킨을 튀긴다고 이상한 건 아니잖아.",
        "author": "고반장 (극한직업)", "source": "극한직업", "year": 2019,
        "keywords": ["유머", "도전"], "situations": ["웃음이 필요할 때", "새로운 시작"]
    },
    # 범죄와의 전쟁
    {
        "text": "느 내 마 내 가?",
        "author": "최익현 (범죄와의 전쟁)", "source": "범죄와의 전쟁", "year": 2012,
        "keywords": ["용기", "자신감"], "situations": ["용기가 필요할 때"]
    },
    # 광해
    {
        "text": "진정한 왕이란 백성을 위해 존재하는 것이다.",
        "author": "하선 (광해)", "source": "광해, 왕이 된 남자", "year": 2012,
        "keywords": ["겸손", "공동체"], "situations": ["배움의 자세", "삶의 의미를 찾을 때"]
    },
    # 괴물
    {
        "text": "가족을 위해서라면 무엇이든 할 수 있어.",
        "author": "강두 (괴물)", "source": "괴물", "year": 2006,
        "keywords": ["가족", "용기"], "situations": ["용기가 필요할 때", "관계의 소중함"]
    },
    # 해운대
    {
        "text": "살아있다는 것, 그것만으로도 감사한 거야.",
        "author": "만식 (해운대)", "source": "해운대", "year": 2009,
        "keywords": ["감사", "인생"], "situations": ["감사할 때", "현재를 살고 싶을 때"]
    },
    # 태극기 휘날리며
    {
        "text": "동생아, 살아야 한다. 살아남아야 해.",
        "author": "이진태 (태극기 휘날리며)", "source": "태극기 휘날리며", "year": 2004,
        "keywords": ["가족", "사랑"], "situations": ["두려울 때", "관계의 소중함"]
    },
    # 살인의 추억
    {
        "text": "지금 이 순간에도, 그 사람은 어딘가에서 우리를 보고 있을지도 몰라.",
        "author": "박두만 (살인의 추억)", "source": "살인의 추억", "year": 2003,
        "keywords": ["인생", "존재"], "situations": ["자기 성찰"]
    },
    # 아가씨
    {
        "text": "내 인생은 내가 정한다.",
        "author": "숙희 (아가씨)", "source": "아가씨", "year": 2016,
        "keywords": ["자유", "선택"], "situations": ["인생의 선택", "용기가 필요할 때"]
    },
    # 밀양
    {
        "text": "하나님이 그 사람을 용서했다는데, 나는 어떡하라고요.",
        "author": "신애 (밀양)", "source": "밀양", "year": 2007,
        "keywords": ["고통", "자기성찰"], "situations": ["절망적일 때", "힘든 상황에서 거리를 두고 싶을 때"]
    },
    # 오징어 게임
    {
        "text": "사람을 믿는 건 게임에서 지는 거야.",
        "author": "조상우 (오징어 게임)", "source": "오징어 게임", "year": 2021,
        "keywords": ["관계", "선택"], "situations": ["관계가 어려울 때"]
    },
    {
        "text": "사람들한테는 말이야, 도울 가치가 있어.",
        "author": "성기훈 (오징어 게임)", "source": "오징어 게임", "year": 2021,
        "keywords": ["공동체", "희망"], "situations": ["관계의 소중함", "희망이 필요할 때"]
    },
    # 마더
    {
        "text": "엄마가 되면 다 아는 거야, 이건.",
        "author": "혜자 (마더)", "source": "마더", "year": 2009,
        "keywords": ["가족", "사랑"], "situations": ["관계의 소중함"]
    },
    # 스물
    {
        "text": "스물이면 뭐든 할 수 있을 줄 알았어.",
        "author": "치호 (스물)", "source": "스물", "year": 2015,
        "keywords": ["인생", "성장"], "situations": ["자기 성찰", "새로운 시작"]
    },
    # 7번방의 선물
    {
        "text": "아빠, 사랑해요.",
        "author": "예승 (7번방의 선물)", "source": "7번방의 선물", "year": 2013,
        "keywords": ["가족", "사랑"], "situations": ["관계의 소중함", "감사할 때"]
    },
    # 부산행
    {
        "text": "이기적인 놈이 살아남는 세상이다. 착하면 당해.",
        "author": "용석 (부산행)", "source": "부산행", "year": 2016,
        "keywords": ["인생", "선택"], "situations": ["인생의 선택", "새로운 관점이 필요할 때"]
    },
    {
        "text": "딸에게 부끄러운 아빠가 되고 싶지 않았을 뿐이야.",
        "author": "석우 (부산행)", "source": "부산행", "year": 2016,
        "keywords": ["가족", "용기"], "situations": ["용기가 필요할 때", "자기 성찰"]
    },
    # 완벽한 타인
    {
        "text": "비밀이 없는 사람은 없어. 문제는 그걸 어떻게 받아들이느냐야.",
        "author": "석호 (완벽한 타인)", "source": "완벽한 타인", "year": 2018,
        "keywords": ["관계", "자기성찰"], "situations": ["관계가 어려울 때", "자기 성찰"]
    },
    # 공작
    {
        "text": "내가 선택한 길이니까, 끝까지 간다.",
        "author": "박석영 (공작)", "source": "공작", "year": 2018,
        "keywords": ["선택", "끈기"], "situations": ["인생의 선택", "포기하고 싶을 때"]
    },
    # 남산의 부장들
    {
        "text": "충성은 사람에게 하는 것이 아니라 나라에 하는 것이다.",
        "author": "김규평 (남산의 부장들)", "source": "남산의 부장들", "year": 2020,
        "keywords": ["선택", "용기"], "situations": ["인생의 선택", "용기가 필요할 때"]
    },
]

# 드라마/영화 캐릭터 저자 등록 및 명언 삽입
cat1_count = 0
for q in drama_movie_quotes:
    author_name = q["author"]
    author_id = get_or_create_author(
        name=author_name,
        nationality="KR",
        birth_year=None,
        profession_name="배우",
        profession_group="예술",
        field_name="예술"
    )
    ok = insert_quote(
        text=q["text"],
        text_original=None,
        original_language="ko",
        author_id=author_id,
        source=q["source"],
        year=q["year"],
        keyword_names=q["keywords"],
        situation_names=q["situations"]
    )
    if ok:
        cat1_count += 1

# ========================================================================
# 카테고리 2: 고사성어 60개 (기존 15개와 중복 피함)
# ========================================================================

# 기존 DB에 있는 15개:
# 조삼모사, 삼인성호, 도원결의, 와신상담, 맹모삼천, 사면초가,
# 각주구검, 결초보은, 형설지공, 백문불여일견, 역지사지,
# 학여불급, 새옹지마, 온고지신, 우공이산

gosaseongeo_quotes = [
    # 논어
    {
        "text": "삼인행(三人行): 세 사람이 길을 가면 반드시 나의 스승이 있다는 뜻으로, 누구에게나 배울 점이 있음을 이르는 말",
        "text_original": "三人行", "source": "논어", "author_name": "공자", "author_birth": -551,
        "keywords": ["겸손", "학습"], "situations": ["배움의 자세", "관계의 소중함"]
    },
    {
        "text": "과유불급(過猶不及): 지나침은 미치지 못함과 같다는 뜻으로, 모든 일에 중용이 중요함을 이르는 말",
        "text_original": "過猶不及", "source": "논어", "author_name": "공자", "author_birth": -551,
        "keywords": ["지혜", "자기성찰"], "situations": ["자기 성찰", "새로운 관점이 필요할 때"]
    },
    {
        "text": "불치하문(不恥下問): 아랫사람에게 묻는 것을 부끄러워하지 않는다는 뜻으로, 배움에 겸손해야 함을 이르는 말",
        "text_original": "不恥下問", "source": "논어", "author_name": "공자", "author_birth": -551,
        "keywords": ["겸손", "학습"], "situations": ["배움의 자세", "깊이 이해하고 싶을 때"]
    },
    {
        "text": "임중도원(任重道遠): 짐은 무겁고 갈 길은 멀다는 뜻으로, 책임이 크고 해야 할 일이 많음을 이르는 말",
        "text_original": "任重道遠", "source": "논어", "author_name": "공자", "author_birth": -551,
        "keywords": ["끈기", "목표"], "situations": ["목표가 멀게 느껴질 때", "꾸준함이 필요할 때"]
    },
    {
        "text": "절차탁마(切磋琢磨): 자르고 쪼고 쪼고 간다는 뜻으로, 학문이나 인격을 끊임없이 갈고닦음을 이르는 말",
        "text_original": "切磋琢磨", "source": "논어", "author_name": "공자", "author_birth": -551,
        "keywords": ["노력", "성장"], "situations": ["꾸준함이 필요할 때", "배움의 자세"]
    },
    {
        "text": "견리사의(見利思義): 이익을 보면 의로움을 생각한다는 뜻으로, 이익 앞에서 도리를 먼저 생각해야 함을 이르는 말",
        "text_original": "見利思義", "source": "논어", "author_name": "공자", "author_birth": -551,
        "keywords": ["선택", "지혜"], "situations": ["인생의 선택", "자기 성찰"]
    },
    # 맹자
    {
        "text": "호연지기(浩然之氣): 하늘과 땅 사이에 가득 찬 넓고 큰 기운이라는 뜻으로, 도의에 근거하여 조금도 부끄러움이 없는 당당한 마음을 이르는 말",
        "text_original": "浩然之氣", "source": "맹자", "author_name": "맹자", "author_birth": -372,
        "keywords": ["용기", "자신감"], "situations": ["용기가 필요할 때", "자신감이 없을 때"]
    },
    {
        "text": "사필귀정(事必歸正): 모든 일은 반드시 바른 길로 돌아간다는 뜻으로, 진리와 정의는 결국 승리함을 이르는 말",
        "text_original": "事必歸正", "source": "맹자", "author_name": "맹자", "author_birth": -372,
        "keywords": ["희망", "인생"], "situations": ["희망이 필요할 때", "절망적일 때"]
    },
    {
        "text": "자포자기(自暴自棄): 스스로 자신을 해치고 버린다는 뜻으로, 절망하여 자신을 돌보지 않음을 이르는 말",
        "text_original": "自暴自棄", "source": "맹자", "author_name": "맹자", "author_birth": -372,
        "keywords": ["회복", "자기성찰"], "situations": ["좌절했을 때", "자기 성찰"]
    },
    {
        "text": "오십보백보(五十步百步): 오십 보 도망간 사람이 백 보 도망간 사람을 비웃는다는 뜻으로, 본질적으로는 같은 것을 이르는 말",
        "text_original": "五十步百步", "source": "맹자", "author_name": "맹자", "author_birth": -372,
        "keywords": ["자기성찰", "겸손"], "situations": ["자기 성찰", "새로운 관점이 필요할 때"]
    },
    {
        "text": "연목구어(緣木求魚): 나무에 올라가서 물고기를 구한다는 뜻으로, 도저히 불가능한 일을 하려 함을 이르는 말",
        "text_original": "緣木求魚", "source": "맹자", "author_name": "맹자", "author_birth": -372,
        "keywords": ["지혜", "선택"], "situations": ["새로운 관점이 필요할 때", "자기 성찰"]
    },
    # 사기
    {
        "text": "권토중래(捲土重來): 흙먼지를 일으키며 다시 온다는 뜻으로, 한 번 실패한 뒤 힘을 되찾아 다시 일어남을 이르는 말",
        "text_original": "捲土重來", "source": "사기", "author_name": "사마천", "author_birth": -145,
        "keywords": ["회복", "도전"], "situations": ["실패했을 때", "포기하고 싶을 때"]
    },
    {
        "text": "토사구팽(兔死狗烹): 토끼가 죽으면 사냥개를 삶는다는 뜻으로, 필요할 때는 쓰고 필요 없으면 버림을 이르는 말",
        "text_original": "兔死狗烹", "source": "사기", "author_name": "사마천", "author_birth": -145,
        "keywords": ["관계", "지혜"], "situations": ["관계가 어려울 때", "새로운 관점이 필요할 때"]
    },
    {
        "text": "배수지진(背水之陣): 물을 등지고 진을 친다는 뜻으로, 어떤 일에 목숨을 걸고 전력을 다함을 이르는 말",
        "text_original": "背水之陣", "source": "사기", "author_name": "사마천", "author_birth": -145,
        "keywords": ["용기", "도전"], "situations": ["용기가 필요할 때", "포기하고 싶을 때"]
    },
    {
        "text": "일거양득(一擧兩得): 한 가지 일을 하여 두 가지 이익을 얻는다는 뜻으로, 한 번의 행동으로 두 가지 성과를 거둠을 이르는 말",
        "text_original": "一擧兩得", "source": "사기", "author_name": "사마천", "author_birth": -145,
        "keywords": ["지혜", "성공"], "situations": ["새로운 관점이 필요할 때"]
    },
    {
        "text": "사면초가(四面楚歌): 사방에서 초나라 노래가 들린다는 뜻으로, 적에게 둘러싸여 고립된 상태를 이르는 말",
        "text_original": "四面楚歌", "source": "사기", "author_name": "사마천", "author_birth": -145,
        "keywords": ["고통", "인생"], "situations": ["절망적일 때", "외로울 때"]
    },
    # 삼국지
    {
        "text": "삼고초려(三顧草廬): 초가집을 세 번 찾아간다는 뜻으로, 인재를 맞이하기 위해 참을성 있게 노력함을 이르는 말",
        "text_original": "三顧草廬", "source": "삼국지", "author_name": "진수", "author_birth": 233,
        "keywords": ["끈기", "겸손"], "situations": ["꾸준함이 필요할 때", "관계의 소중함"]
    },
    {
        "text": "와룡봉추(臥龍鳳雛): 엎드린 용과 봉황의 새끼라는 뜻으로, 아직 세상에 알려지지 않은 뛰어난 인재를 이르는 말",
        "text_original": "臥龍鳳雛", "source": "삼국지", "author_name": "진수", "author_birth": 233,
        "keywords": ["성장", "자신감"], "situations": ["자신감이 없을 때", "새로운 시작"]
    },
    {
        "text": "괄목상대(刮目相對): 눈을 비비고 다시 본다는 뜻으로, 남의 학식이나 재주가 놀랄 만큼 나아졌음을 이르는 말",
        "text_original": "刮目相對", "source": "삼국지", "author_name": "진수", "author_birth": 233,
        "keywords": ["성장", "변화"], "situations": ["배움의 자세", "변화를 마주할 때"]
    },
    # 장자
    {
        "text": "조삼모사(朝三暮四): 아침에 세 개 저녁에 네 개라는 뜻으로, 눈앞의 차이만 알고 결과가 같음을 모르는 어리석음을 이르는 말",
        "text_original": "朝三暮四", "source": "장자", "author_name": "장자", "author_birth": -369,
        "keywords": ["지혜", "자기성찰"], "situations": ["자기 성찰", "새로운 관점이 필요할 때"]
    },
    {
        "text": "대기만성(大器晩成): 큰 그릇은 늦게 이루어진다는 뜻으로, 크게 될 사람은 오랜 노력 끝에 성공함을 이르는 말",
        "text_original": "大器晩成", "source": "노자", "author_name": "노자", "author_birth": -571,
        "keywords": ["끈기", "성공"], "situations": ["목표가 멀게 느껴질 때", "꾸준함이 필요할 때"]
    },
    {
        "text": "상선약수(上善若水): 최고의 선은 물과 같다는 뜻으로, 물처럼 낮은 곳으로 흘러 만물을 이롭게 함을 이르는 말",
        "text_original": "上善若水", "source": "노자", "author_name": "노자", "author_birth": -571,
        "keywords": ["겸손", "지혜"], "situations": ["배움의 자세", "자기 성찰"]
    },
    {
        "text": "무위자연(無爲自然): 인위적으로 하지 않고 자연에 따른다는 뜻으로, 억지로 하지 않고 자연의 흐름에 맡김을 이르는 말",
        "text_original": "無爲自然", "source": "노자", "author_name": "노자", "author_birth": -571,
        "keywords": ["자유", "철학"], "situations": ["힘든 상황에서 거리를 두고 싶을 때", "현재를 살고 싶을 때"]
    },
    # 한비자
    {
        "text": "모순(矛盾): 창과 방패라는 뜻으로, 앞뒤가 맞지 않는 말이나 행동을 이르는 말",
        "text_original": "矛盾", "source": "한비자", "author_name": "한비자", "author_birth": -280,
        "keywords": ["지혜", "자기성찰"], "situations": ["자기 성찰"]
    },
    {
        "text": "수주대토(守株待兎): 그루터기를 지키며 토끼를 기다린다는 뜻으로, 한 번의 요행을 믿고 노력하지 않음을 이르는 말",
        "text_original": "守株待兎", "source": "한비자", "author_name": "한비자", "author_birth": -280,
        "keywords": ["노력", "행동"], "situations": ["게으를 때", "꾸준함이 필요할 때"]
    },
    # 전국책
    {
        "text": "방약무인(傍若無人): 곁에 사람이 없는 것처럼 행동한다는 뜻으로, 남을 의식하지 않고 제멋대로 행동함을 이르는 말",
        "text_original": "傍若無人", "source": "전국책", "author_name": "유향", "author_birth": -77,
        "keywords": ["자기성찰", "관계"], "situations": ["자기 성찰", "관계가 어려울 때"]
    },
    {
        "text": "일모도원(日暮途遠): 날은 저물고 갈 길은 멀다는 뜻으로, 할 일은 많으나 시간이 부족함을 이르는 말",
        "text_original": "日暮途遠", "source": "전국책", "author_name": "유향", "author_birth": -77,
        "keywords": ["시간", "끈기"], "situations": ["목표가 멀게 느껴질 때", "포기하고 싶을 때"]
    },
    # 예기
    {
        "text": "교학상장(教學相長): 가르치고 배우면서 함께 성장한다는 뜻으로, 가르침과 배움이 서로를 발전시킴을 이르는 말",
        "text_original": "教學相長", "source": "예기", "author_name": "공자", "author_birth": -551,
        "keywords": ["교육", "성장"], "situations": ["배움의 자세", "관계의 소중함"]
    },
    # 시경
    {
        "text": "타산지석(他山之石): 다른 산의 돌이라는 뜻으로, 다른 사람의 잘못이나 하찮은 것도 자신을 갈고닦는 데 도움이 됨을 이르는 말",
        "text_original": "他山之石", "source": "시경", "author_name": "공자", "author_birth": -551,
        "keywords": ["겸손", "학습"], "situations": ["배움의 자세", "자기 성찰"]
    },
    # 순자
    {
        "text": "청출어람(靑出於藍): 푸른색이 쪽에서 나왔으나 쪽보다 더 푸르다는 뜻으로, 제자가 스승보다 나음을 이르는 말",
        "text_original": "靑出於藍", "source": "순자", "author_name": "순자", "author_birth": -313,
        "keywords": ["성장", "교육"], "situations": ["배움의 자세", "자신감이 없을 때"]
    },
    # 좌전
    {
        "text": "퇴고(推敲): 밀 것인가 두드릴 것인가라는 뜻으로, 글을 지을 때 여러 번 생각하여 고침을 이르는 말",
        "text_original": "推敲", "source": "좌전", "author_name": "좌구명", "author_birth": -556,
        "keywords": ["노력", "습관"], "situations": ["깊이 이해하고 싶을 때", "꾸준함이 필요할 때"]
    },
    {
        "text": "다다익선(多多益善): 많으면 많을수록 더 좋다는 뜻으로, 양이 많을수록 유리함을 이르는 말",
        "text_original": "多多益善", "source": "사기", "author_name": "사마천", "author_birth": -145,
        "keywords": ["성공", "지혜"], "situations": ["새로운 관점이 필요할 때"]
    },
    # 중용
    {
        "text": "지성감천(至誠感天): 지극한 정성은 하늘도 감동시킨다는 뜻으로, 정성을 다하면 무엇이든 이룰 수 있음을 이르는 말",
        "text_original": "至誠感天", "source": "중용", "author_name": "자사", "author_birth": -483,
        "keywords": ["끈기", "노력"], "situations": ["꾸준함이 필요할 때", "포기하고 싶을 때"]
    },
    # 후한서
    {
        "text": "유지경성(有志竟成): 뜻이 있으면 마침내 이룬다는 뜻으로, 강한 의지로 노력하면 반드시 성공함을 이르는 말",
        "text_original": "有志竟成", "source": "후한서", "author_name": "범엽", "author_birth": 398,
        "keywords": ["끈기", "성공"], "situations": ["포기하고 싶을 때", "목표가 멀게 느껴질 때"]
    },
    # 전한서
    {
        "text": "일석이조(一石二鳥): 돌 하나로 새 두 마리를 잡는다는 뜻으로, 한 가지 일로 두 가지 이익을 봄을 이르는 말",
        "text_original": "一石二鳥", "source": "전한서", "author_name": "반고", "author_birth": 32,
        "keywords": ["지혜", "성공"], "situations": ["새로운 관점이 필요할 때"]
    },
    {
        "text": "전화위복(轉禍爲福): 화를 바꾸어 복으로 만든다는 뜻으로, 나쁜 일이 계기가 되어 오히려 좋은 일이 됨을 이르는 말",
        "text_original": "轉禍爲福", "source": "전국책", "author_name": "유향", "author_birth": -77,
        "keywords": ["희망", "회복"], "situations": ["실패했을 때", "불운할 때"]
    },
    # 십팔사략
    {
        "text": "고진감래(苦盡甘來): 쓴 것이 다하면 단 것이 온다는 뜻으로, 고생 끝에 즐거움이 옴을 이르는 말",
        "text_original": "苦盡甘來", "source": "십팔사략", "author_name": "증선지", "author_birth": 1300,
        "keywords": ["희망", "끈기"], "situations": ["희망이 필요할 때", "절망적일 때"]
    },
    # 세설신어
    {
        "text": "천리안(千里眼): 천 리 밖을 볼 수 있는 눈이라는 뜻으로, 멀리까지 내다볼 수 있는 뛰어난 안목을 이르는 말",
        "text_original": "千里眼", "source": "세설신어", "author_name": "유의경", "author_birth": 403,
        "keywords": ["지혜", "목표"], "situations": ["새로운 관점이 필요할 때", "미래가 불안할 때"]
    },
    # 후한서
    {
        "text": "초지일관(初志一貫): 처음 세운 뜻을 끝까지 관철한다는 뜻으로, 한 번 정한 목표를 변함없이 밀고 나감을 이르는 말",
        "text_original": "初志一貫", "source": "후한서", "author_name": "범엽", "author_birth": 398,
        "keywords": ["끈기", "목표"], "situations": ["포기하고 싶을 때", "꾸준함이 필요할 때"]
    },
    # 진서
    {
        "text": "배중사영(杯中蛇影): 잔 속의 뱀 그림자라는 뜻으로, 쓸데없는 의심이나 걱정으로 스스로 고통받음을 이르는 말",
        "text_original": "杯中蛇影", "source": "진서", "author_name": "방현령", "author_birth": 578,
        "keywords": ["자기성찰", "고통"], "situations": ["미래가 불안할 때", "자기 성찰"]
    },
    {
        "text": "파죽지세(破竹之勢): 대나무를 쪼개는 기세라는 뜻으로, 거침없이 적을 무찌르는 맹렬한 기세를 이르는 말",
        "text_original": "破竹之勢", "source": "진서", "author_name": "방현령", "author_birth": 578,
        "keywords": ["용기", "행동"], "situations": ["용기가 필요할 때", "도전을 망설일 때"]
    },
    # 대학
    {
        "text": "수신제가(修身齊家): 몸을 닦고 집안을 가지런히 한다는 뜻으로, 자기 수양이 모든 일의 근본임을 이르는 말",
        "text_original": "修身齊家", "source": "대학", "author_name": "공자", "author_birth": -551,
        "keywords": ["자기성찰", "가족"], "situations": ["자기 성찰", "배움의 자세"]
    },
    # 서경
    {
        "text": "작심삼일(作心三日): 결심한 것이 삼 일을 가지 못한다는 뜻으로, 결심이 오래가지 못함을 경계하는 말",
        "text_original": "作心三日", "source": "서경", "author_name": "공자", "author_birth": -551,
        "keywords": ["습관", "끈기"], "situations": ["게으를 때", "꾸준함이 필요할 때"]
    },
    # 중국 속담/고전
    {
        "text": "동병상련(同病相憐): 같은 병을 앓는 사람끼리 서로 가엾게 여긴다는 뜻으로, 같은 처지에 있는 사람끼리 동정함을 이르는 말",
        "text_original": "同病相憐", "source": "오월춘추", "author_name": "조엽", "author_birth": 40,
        "keywords": ["공동체", "관계"], "situations": ["관계의 소중함", "외로울 때"]
    },
    {
        "text": "일취월장(日就月將): 날로 나아가고 달로 나아간다는 뜻으로, 나날이 발전함을 이르는 말",
        "text_original": "日就月將", "source": "시경", "author_name": "공자", "author_birth": -551,
        "keywords": ["성장", "노력"], "situations": ["꾸준함이 필요할 때", "배움의 자세"]
    },
    {
        "text": "유비무환(有備無患): 준비가 되어 있으면 걱정할 것이 없다는 뜻으로, 미리 대비하면 근심이 없음을 이르는 말",
        "text_original": "有備無患", "source": "서경", "author_name": "공자", "author_birth": -551,
        "keywords": ["습관", "지혜"], "situations": ["미래가 불안할 때", "배움의 자세"]
    },
    {
        "text": "사즉생(死則生): 죽고자 하면 살고 살고자 하면 죽는다는 뜻으로, 필사적인 각오로 임해야 살 길이 열림을 이르는 말",
        "text_original": "死則生", "source": "오자병법", "author_name": "오기", "author_birth": -440,
        "keywords": ["용기", "도전"], "situations": ["두려울 때", "용기가 필요할 때"]
    },
    {
        "text": "자승자박(自繩自縛): 스스로 자기 몸을 묶는다는 뜻으로, 자기가 한 말이나 행동에 스스로 얽매임을 이르는 말",
        "text_original": "自繩自縛", "source": "북사", "author_name": "이연수", "author_birth": 599,
        "keywords": ["자기성찰", "자유"], "situations": ["자기 성찰", "힘든 상황에서 거리를 두고 싶을 때"]
    },
    {
        "text": "금상첨화(錦上添花): 비단 위에 꽃을 더한다는 뜻으로, 좋은 일에 좋은 일이 더해짐을 이르는 말",
        "text_original": "錦上添花", "source": "왕안석 시문집", "author_name": "왕안석", "author_birth": 1021,
        "keywords": ["행복", "감사"], "situations": ["감사할 때", "일상의 소소함"]
    },
    {
        "text": "설상가상(雪上加霜): 눈 위에 서리가 덮인다는 뜻으로, 안 좋은 일이 겹침을 이르는 말",
        "text_original": "雪上加霜", "source": "경덕전등록", "author_name": "도원", "author_birth": 1004,
        "keywords": ["고통", "인생"], "situations": ["불운할 때", "절망적일 때"]
    },
    {
        "text": "아전인수(我田引水): 자기 논에 물을 끌어들인다는 뜻으로, 자기에게 유리하도록 생각하거나 행동함을 이르는 말",
        "text_original": "我田引水", "source": "민간 속담", "author_name": "민간 전승", "author_birth": None,
        "keywords": ["자기성찰", "관계"], "situations": ["자기 성찰", "관계가 어려울 때"]
    },
    {
        "text": "동상이몽(同床異夢): 같은 자리에 누워 다른 꿈을 꾼다는 뜻으로, 겉으로는 같이 행동하면서 속으로는 각각 다른 생각을 가지고 있음을 이르는 말",
        "text_original": "同床異夢", "source": "진서", "author_name": "방현령", "author_birth": 578,
        "keywords": ["관계", "자기성찰"], "situations": ["관계가 어려울 때"]
    },
    {
        "text": "사생결단(死生決斷): 죽고 사는 것을 가리지 않고 결단한다는 뜻으로, 목숨을 걸고 결판을 냄을 이르는 말",
        "text_original": "死生決斷", "source": "삼국지", "author_name": "진수", "author_birth": 233,
        "keywords": ["용기", "행동"], "situations": ["용기가 필요할 때", "도전을 망설일 때"]
    },
    {
        "text": "읍참마속(泣斬馬謖): 울면서 마속의 목을 베다는 뜻으로, 사사로운 정에 이끌리지 않고 공정하게 처벌함을 이르는 말",
        "text_original": "泣斬馬謖", "source": "삼국지", "author_name": "진수", "author_birth": 233,
        "keywords": ["선택", "용기"], "situations": ["인생의 선택", "용기가 필요할 때"]
    },
    {
        "text": "일편단심(一片丹心): 한 조각의 붉은 마음이라는 뜻으로, 진심에서 우러나오는 변하지 않는 마음을 이르는 말",
        "text_original": "一片丹心", "source": "과영정양유", "author_name": "문천상", "author_birth": 1236,
        "keywords": ["사랑", "끈기"], "situations": ["사랑을 느낄 때", "꾸준함이 필요할 때"]
    },
    {
        "text": "막역지우(莫逆之友): 거스를 것이 없는 벗이라는 뜻으로, 마음이 서로 잘 맞아 거리낌이 없는 매우 친한 벗을 이르는 말",
        "text_original": "莫逆之友", "source": "장자", "author_name": "장자", "author_birth": -369,
        "keywords": ["우정", "관계"], "situations": ["관계의 소중함"]
    },
    {
        "text": "자강불식(自强不息): 스스로 힘쓰고 쉬지 않는다는 뜻으로, 끊임없이 스스로를 강하게 함을 이르는 말",
        "text_original": "自强不息", "source": "주역", "author_name": "공자", "author_birth": -551,
        "keywords": ["노력", "끈기"], "situations": ["게으를 때", "꾸준함이 필요할 때"]
    },
    {
        "text": "풍전등화(風前燈火): 바람 앞의 등불이라는 뜻으로, 매우 위태로운 처지에 놓여 있음을 이르는 말",
        "text_original": "風前燈火", "source": "여씨춘추", "author_name": "여불위", "author_birth": -292,
        "keywords": ["인생", "고통"], "situations": ["절망적일 때", "두려울 때"]
    },
    {
        "text": "구사일생(九死一生): 아홉 번 죽을 뻔하고 한 번 살아난다는 뜻으로, 죽을 고비를 여러 번 넘기고 겨우 살아남을 이르는 말",
        "text_original": "九死一生", "source": "초사", "author_name": "굴원", "author_birth": -340,
        "keywords": ["회복", "인생"], "situations": ["실패했을 때", "희망이 필요할 때"]
    },
    {
        "text": "촌철살인(寸鐵殺人): 한 치의 쇠로 사람을 죽인다는 뜻으로, 짧은 말로 급소를 찌르듯 핵심을 찌름을 이르는 말",
        "text_original": "寸鐵殺人", "source": "경덕전등록", "author_name": "도원", "author_birth": 1004,
        "keywords": ["지혜", "지식"], "situations": ["깊이 이해하고 싶을 때"]
    },
    {
        "text": "좌우명(座右銘): 자리 오른쪽에 새겨 놓은 글이라는 뜻으로, 늘 가까이 두고 자신을 경계하는 글귀를 이르는 말",
        "text_original": "座右銘", "source": "후한서", "author_name": "범엽", "author_birth": 398,
        "keywords": ["습관", "자기성찰"], "situations": ["자기 성찰", "배움의 자세"]
    },
]

# 고사성어 저자 등록 및 명언 삽입
cat2_count = 0
for q in gosaseongeo_quotes:
    author_name = q["author_name"]
    # 민간 전승의 경우 특별 처리
    if author_name == "민간 전승":
        prof_name = "민간 전승"
        prof_group = "문화"
        field_name = "문화"
    else:
        prof_name = "사상가"
        prof_group = "철학"
        field_name = "철학"

    author_id = get_or_create_author(
        name=author_name,
        nationality="CN",
        birth_year=q["author_birth"],
        profession_name=prof_name,
        profession_group=prof_group,
        field_name=field_name
    )
    ok = insert_quote(
        text=q["text"],
        text_original=q["text_original"],
        original_language="zh",
        author_id=author_id,
        source=q["source"],
        year=None,
        keyword_names=q["keywords"],
        situation_names=q["situations"]
    )
    if ok:
        cat2_count += 1

try:
    conn.commit()
    print(f"=== 저장 완료 ===")
    print(f"카테고리 1 (한국 드라마/영화 명대사): {cat1_count}개 저장")
    print(f"카테고리 2 (고사성어): {cat2_count}개 저장")
    print(f"총 저장: {cat1_count + cat2_count}개")
except Exception as e:
    conn.rollback()
    print(f"오류 발생: {e}")
finally:
    cur.close()
    conn.close()
