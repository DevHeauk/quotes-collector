#!/usr/bin/env python3
"""
Reddit 인기 명언 중 quotes 테이블에 없는 것을 추가하는 스크립트.
"""
import uuid
import psycopg2

conn = psycopg2.connect(host="localhost", user="youheaukjun", dbname="quotes_db")
conn.autocommit = False
cur = conn.cursor()

# ── 마스터 ID 매핑 ──
KEYWORD_IDS = {
    "끈기": "7c7c8294-d1b3-46aa-ad51-f783a87aae65",
    "노력": "6c754215-05ee-41a5-941f-34e06ccd98fb",
    "도전": "4831bf97-6f72-4249-8ad0-e9c49bd1b0e4",
    "동기부여": "539a5767-21df-4581-87ac-99c609fc2a1c",
    "목표": "61df2a6f-596f-4cb2-84ae-c52c36a9507c",
    "성공": "78401342-7f90-43a7-a0e1-aec70a381d2e",
    "실패": "be02c4f0-ffb7-48a8-a3b1-7dc6c419eeba",
    "용기": "1f50f41f-14f2-42d1-a752-5aa8def3ac7c",
    "행동": "c3ebf710-efbe-4adf-ab41-43f7e4655596",
    "회복": "9063fe68-11bc-4e87-8bc6-f2053a23ffd6",
    "희망": "cdc39269-2be1-4820-b1b9-ad2aa176ad03",
    "변화": "52bae2df-0be5-4742-a92b-85e5bbc346e4",
    "성장": "85fb472e-c4ef-4650-80f1-a5e066f981d4",
    "습관": "9bc3e538-6b0c-40bb-8419-b8b9b4c03341",
    "자기성찰": "c19a948c-1d40-49f7-91f6-a571e5e2e8bb",
    "자신감": "89600526-460d-4b5a-804e-3d0ed1c28f7a",
    "유머": "acd1b482-14dd-4f9c-be12-267706456030",
    "결정론": "8955aef1-1bc5-4d7f-9236-e8d824107cf7",
    "과학": "51677d53-ec92-488a-a8ae-00acb42b2fa7",
    "창의성": "69a25d2c-9e7e-4a56-b3e3-6a9aaac16b2c",
    "철학": "cf3c8dc0-a47a-4287-9065-77dab3f37b19",
    "고통": "bb1939c5-0139-484d-99d1-1c1c8d46b905",
    "선택": "f3a39a34-f806-41f4-a257-d6dce331fdf5",
    "시간": "b07231eb-7943-4ce8-9b49-32923f428871",
    "운명": "3b5e0353-25b4-45f7-b188-c430bd1cddf4",
    "의미": "f4555a03-2f44-4b0e-89a1-7b97ce763955",
    "인생": "f02c4b39-ea6a-45b2-a1ab-f04cc48d31cb",
    "자유": "badc8ad6-b881-4836-b236-11e4f894ad51",
    "존재": "53695c66-0b1e-4588-a038-b7b2a17dc35c",
    "죽음": "a599cd7c-74d5-4976-9446-3e02cbe38865",
    "초월": "9ea447f8-cebb-4c2a-ac3c-dada7a136655",
    "행복": "41428e53-1573-4ddb-ab3c-b38180b6c5c2",
    "겸손": "77bd21f0-e20b-4102-ac5e-bca935c930e7",
    "교육": "6f4973b3-c084-491e-904d-2437fc15435b",
    "지식": "b7a9a3cb-d9b7-4fe2-b784-cfd2c002bd72",
    "지혜": "78fb6664-c4bf-4cb6-b4f2-3b5ed7027cce",
    "학습": "24be98e2-7a35-4d77-be08-a6b43bcabb30",
    "가족": "eeb0fe0a-e97b-443c-9f2e-96c9ed93230c",
    "감사": "0e8762ee-ee31-4258-a6d8-f619bf6eb216",
    "공동체": "4639b285-2464-46e9-86ee-157a09e3a809",
    "관계": "fcaaae22-aba2-4fdc-ad9f-8c47d7f430f0",
    "사랑": "9b94f86f-4c0b-4a61-bd7e-640fac6f5145",
    "우정": "c95985f0-68b8-4fb2-a5f6-dbdff8cb5f2e",
    "전통": "39563bcd-0a0c-46b0-aeef-4d3a7d6af74c",
}

SITUATION_IDS = {
    "게으를 때": "4f602cab-27b2-4e7c-ab94-88a70237dbc4",
    "꾸준함이 필요할 때": "c0fc2f5b-d857-42c9-9ae9-94d521cb60c4",
    "목표가 멀게 느껴질 때": "a7bb5873-4246-4156-954b-7b1e158fbe04",
    "배움의 자세": "10804407-c9b8-4174-84d3-93bdeebfb8f1",
    "지식의 가치": "cb746fd8-65b6-4bbb-9da7-d647f3466674",
    "공부하기 싫을 때": "f779acb1-b2a9-489d-917b-49099ca896f3",
    "깊이 이해하고 싶을 때": "8b5545c7-e1cf-4f39-b986-dd649878c54b",
    "과학적 사고": "e33d1f71-f0df-4d99-92df-f39a04481dab",
    "창의적 사고": "f7f618d3-f236-4ed7-8e1e-9bd8ca06540d",
    "관계의 소중함": "3c4e84bc-f016-41ae-b39a-7c5b0c052565",
    "관계가 어려울 때": "5b2e1a95-8492-48dd-9fcb-8001207b9057",
    "사랑을 느낄 때": "cb5df990-7312-419e-9301-dd36f55e4850",
    "사랑의 본질을 고민할 때": "4fb71e2e-ab2e-461d-b2a4-78da3f80c7ec",
    "새로운 시작": "c600bdc0-b160-4dd4-afbd-278a05c84aee",
    "도전을 망설일 때": "473865e3-5d79-4ff6-88b9-47367004f516",
    "용기가 필요할 때": "9df23e09-3d6c-46dc-a9a0-d794734f226e",
    "새로운 관점이 필요할 때": "1612db8a-d71e-4b4c-ac6b-93a2ce98c20b",
    "두려울 때": "171fc634-972b-4321-ae65-81111848b51d",
    "불운할 때": "49f0fe8b-a048-4044-ad46-6cedd255d2f1",
    "실패했을 때": "36f98730-1712-4b07-85f8-df5ff7545d06",
    "외로울 때": "e0565ebd-cab2-40fe-a51e-c752a737ddf3",
    "절망적일 때": "6847c928-72a9-474b-a012-d3d41f78fa34",
    "좌절했을 때": "7c3efbc1-2094-4467-b3e2-b28f0468831a",
    "자신감이 없을 때": "2107ba90-baf3-4224-8845-cffb3f9c1312",
    "포기하고 싶을 때": "843fe6cb-ad4d-4ff5-95b1-1b2b9435b4bf",
    "희망이 필요할 때": "4515042a-b295-4bff-bc71-8577ce58e9f4",
    "힘든 상황에서 거리를 두고 싶을 때": "c7d70096-f0e7-44e1-b1c0-fe4f3e0c77b5",
    "일상의 소소함": "b0223dc0-0b55-4578-bb26-e846273b7f57",
    "웃음이 필요할 때": "6cf98ace-8166-42be-9cae-4c5751c790a1",
    "감사할 때": "cd9571fe-e8f6-479d-88d8-3fd9ff4f45f4",
    "인생의 선택": "f926c0e2-f9d1-49fc-a4f7-2112358b3180",
    "자기 성찰": "96e87775-a1db-4805-bf04-1bf0325a7cb9",
    "과거를 돌아볼 때": "591d5b43-b91b-4588-99e6-2d86e00adfeb",
    "미래가 불안할 때": "32ecce15-bc39-4cf3-95fc-3ea58edb9873",
    "변화를 마주할 때": "b7dcd9ef-60ab-4d1d-88e7-4e27b44e4650",
    "죽음을 생각할 때": "fb403240-91f8-44f9-a11d-7ee4bee74638",
    "삶의 의미를 찾을 때": "acd6f188-eb89-4ade-9f99-305907d7777b",
    "현재를 살고 싶을 때": "03a490c9-9634-4cd1-9e32-29bceb50f133",
}

# ── 기존 authors name→id 매핑 ──
EXISTING_AUTHORS = {}
cur.execute("SELECT id, name FROM authors")
for row in cur.fetchall():
    EXISTING_AUTHORS[row[1]] = row[0]

def get_or_create_author(name_kr, nationality="미상", field_id=None, profession_id=None):
    """기존 저자 찾거나 새로 생성"""
    if name_kr in EXISTING_AUTHORS:
        return EXISTING_AUTHORS[name_kr]
    aid = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO authors (id, name, nationality, field_id, profession_id) VALUES (%s, %s, %s, %s, %s)",
        (aid, name_kr, nationality, field_id, profession_id)
    )
    EXISTING_AUTHORS[name_kr] = aid
    return aid

def impact(upvotes):
    if upvotes > 5000: return 6
    if upvotes > 2000: return 5
    if upvotes > 1000: return 4
    return 3

# ── 명언 데이터 ──
# 제외 대상:
# - "My Great Grandmother..." (저자 불명확)
# - "A phrase that was carved on the walls..." (저자 불명확)
# - "The President of the United States" (문맥상 인용 부적절)
# - "Anonymous" / "Unknown" (저자 불명)
# - "I am a Democrat." - Will Rogers (1935)" (author_name 파싱 실패)
# - "Joe Biden 2020 presidential debate." (저자 파싱 불명확)
# - "George Orwell. 'Why I Write', 1946" (저자 파싱)
# - "Amy Goodman (2016)" → Amy Goodman으로 정리
# - "John Oliver, 2020" → John Oliver로 정리
# - "Robin Williams in 'Man of the Year'" → Robin Williams 기존
# - "Karl Stojka Auschwitz survivor" → Karl Stojka
# - "Marian Turski Auschwitz survivor" → Marian Turski
# - "Dr. Jane Goodall (RIP)" → Jane Goodall
# - "Hippocrates-" → 히포크라테스
# - "Frank Ocean." → Frank Ocean
# - "Dan Hodges." → Dan Hodges
# - "Mike Wawzowski" (허구 캐릭터) → 제외
# - "Steinbck" (Steinbeck 오타, 하지만 실제로는 Ronald Wright 명언) → 제외 (출처 불확실)
# - "W. E. B. Du Bois, 1953" → W. E. B. Du Bois
# - 중복 명언 제거 (Robin Williams 2개, African proverb 2개, Malcolm X 2개, Mark Twain "Most men die" 2개, Theodore Roosevelt 2개)

# Fields/Professions IDs
F_PHILOSOPHY = "f9bf4bf1-12a1-44e6-8a68-49c738a7b5e2"
F_POLITICS = "b0d53c7d-0cbe-476f-b3cb-ec06fff8f8e3"
F_LITERATURE = "2cdd8ad7-0a23-4e64-b93b-c992533242c5"
F_SCIENCE = "b29615ad-0dbf-4e0e-b920-144aa551c9ca"
F_ART = "adf3f414-6362-4c16-b5e1-6cfd0b91bca6"
F_CULTURE = "db2c03fe-25e5-44c4-842a-a2e94761a574"
F_BUSINESS = "b7cdaf72-500a-4b7e-a29b-46b098a1d59b"
F_RELIGION = "3af453e5-eca6-403e-ba5f-17efc4f689f6"
F_HISTORY = "8088f2b8-cf47-4ef8-98fe-51d5f0bd9c1f"
F_PSYCHOLOGY = "f978462c-ec91-4bad-b98a-0a7eac2110f9"

P_PHILOSOPHER = "f154881f-80c2-4cea-9a1d-8ba3fbcd556f"
P_COMEDIAN = "55350bb7-a161-4684-871a-b08f0a533b1e"
P_WRITER = "ba8f678c-3528-4e27-9315-a903a8ee3d1d"
P_ENTREPRENEUR = "be2dc0cc-9355-4002-b107-3a71d5c2e399"
P_JOURNALIST = "dfcc8c25-7904-4401-bcd5-e6f95bf0dbc1"
P_PHYSICIST = "7ad6e70e-c4f9-43e4-b64c-92fde8b03413"
P_ACTOR = "fc462f5c-c84d-4b58-8b3c-f82c30665d57"
P_SCHOLAR = "c4c4aa24-dffc-4a64-a145-ec7cf54ded35"
P_POLITICIAN = "095a6cf0-cded-41fe-8ef0-c3d4e0180e60"
P_THINKER = "2879b5ad-56ae-4921-ab9b-2c59481a251a"
P_MUSICIAN = "7a9e846f-d79a-439a-bc55-13ac3ee80030"
P_SCIENTIST = "2aa07165-7f1f-4f2d-971f-4832e10f39de"
P_ATHLETE = "fd419307-4524-4693-b7da-f4802084d2ce"
P_FOLKLORE = "ca5e7237-1767-4881-918c-e7c0bdf51a06"
P_RELIGIOUS = "ccd25c59-4332-411e-bf7f-00d8286c7075"
P_HISTORIAN = "93507c6f-d6f0-486a-b452-ad2c6038f099"
P_INVENTOR = "a66b8cc4-aaa5-4cbc-a61a-ab1aebfbc4e4"
P_ARTIST = "b878f2bb-a956-4cca-acd5-11682156eebf"

quotes_data = [
    # 1. Mary Pipher - 9862 upvotes
    {
        "text": "젊은 남성들은 강간이 식인 행위만큼이나 상상할 수 없는 일이 되도록 사회화되어야 합니다.",
        "text_original": "Young men need to be socialized in such a way that rape is as unthinkable to them as cannibalism.",
        "author_kr": "메리 파이퍼",
        "nationality": "미국",
        "field_id": F_PSYCHOLOGY,
        "profession_id": P_SCHOLAR,
        "upvotes": 9862,
        "keywords": ["교육", "변화", "공동체"],
        "situations": ["새로운 관점이 필요할 때", "자기 성찰"],
    },
    # 2. Theodore Roosevelt - 8031
    {
        "text": "대통령에 대한 비판이 있어서는 안 된다거나, 옳든 그르든 대통령을 지지해야 한다고 선언하는 것은 비애국적이고 비굴할 뿐 아니라 미국 국민에 대한 도덕적 반역입니다.",
        "text_original": "To announce that there must be no criticism of the President, or that we are to stand by the President, right or wrong, is not only unpatriotic and servile but is morally treasonable to the American public.",
        "author_kr": "시어도어 루스벨트",
        "nationality": "미국",
        "field_id": F_POLITICS,
        "profession_id": P_POLITICIAN,
        "upvotes": 8031,
        "keywords": ["자유", "용기"],
        "situations": ["용기가 필요할 때", "자기 성찰"],
    },
    # 3. Sun Tzu - 6974
    {
        "text": "악한 자는 잿더미 위에 군림하기 위해 자기 나라를 불태울 것이다.",
        "text_original": "An evil man will burn his own nation to the ground to rule over the ashes.",
        "author_kr": "손자",
        "nationality": "중국",
        "field_id": F_HISTORY,
        "profession_id": P_THINKER,
        "upvotes": 6974,
        "keywords": ["지혜", "철학"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    # 4. African proverb - 5859
    {
        "text": "마을에서 품어주지 않은 아이는 온기를 느끼기 위해 마을을 불태울 것이다.",
        "text_original": "The child who is not embraced by the village will burn it down to feel its warmth",
        "author_kr": "아프리카 속담",
        "nationality": "아프리카",
        "field_id": F_CULTURE,
        "profession_id": P_FOLKLORE,
        "upvotes": 5859,
        "keywords": ["공동체", "관계", "교육"],
        "situations": ["관계의 소중함", "새로운 관점이 필요할 때"],
    },
    # 5. Hannah Arendt - 5684
    {
        "text": "인간 공감의 죽음은 문화가 야만으로 빠져들기 직전의 가장 이른 그리고 가장 분명한 징후 중 하나입니다.",
        "text_original": "The death of human empathy is one of the earliest and most telling signs of a culture about to fall into barbarism.",
        "author_kr": "한나 아렌트",
        "nationality": "독일",
        "field_id": F_PHILOSOPHY,
        "profession_id": P_PHILOSOPHER,
        "upvotes": 5684,
        "keywords": ["공동체", "철학", "관계"],
        "situations": ["새로운 관점이 필요할 때", "자기 성찰"],
    },
    # 6. Thomas Jefferson - 4874
    {
        "text": "폭정이 법이 될 때, 반란은 의무가 된다.",
        "text_original": "When tyranny becomes law, rebellion becomes duty.",
        "author_kr": "토머스 제퍼슨",
        "nationality": "미국",
        "field_id": F_POLITICS,
        "profession_id": P_POLITICIAN,
        "upvotes": 4874,
        "keywords": ["자유", "용기", "행동"],
        "situations": ["용기가 필요할 때"],
    },
    # 7. Dave Chappelle - 4566
    {
        "text": "나는 누구든 원하는 사람이 될 권리를 지지합니다. 내 질문은 이것입니다: 당신의 자아상에 내가 어디까지 참여해야 하나요?",
        "text_original": "I support anyone's right to be who they want to be. My question is: to what extent do I have to participate in your self-image?",
        "author_kr": "데이브 샤펠",
        "nationality": "미국",
        "field_id": F_CULTURE,
        "profession_id": P_COMEDIAN,
        "upvotes": 4566,
        "keywords": ["자유", "철학", "자기성찰"],
        "situations": ["자기 성찰", "새로운 관점이 필요할 때"],
    },
    # 8. Anthony Bourdain - 4348
    {
        "text": "미쳤다고 하셔도 좋지만, 내가 파티를 열었는데 나치들이 몰려왔다면 그건 좀 자기 성찰을 해봐야 할 일 아닌가요.",
        "text_original": "Call me crazy, but if I threw a party and a bunch of nazis showed up, it might inspire a little self inspection.",
        "author_kr": "앤서니 보르데인",
        "nationality": "미국",
        "field_id": F_CULTURE,
        "profession_id": P_WRITER,
        "upvotes": 4348,
        "keywords": ["자기성찰", "유머"],
        "situations": ["자기 성찰", "웃음이 필요할 때"],
    },
    # 9. G.K. Chesterton - 4004
    {
        "text": "가난한 사람이야말로 나라에 진정한 이해관계가 있습니다. 부자는 그렇지 않습니다. 그는 요트를 타고 뉴기니로 떠날 수 있으니까요.",
        "text_original": "The poor man really has a stake in the country. The rich man hasn't; he can go away to New Guinea in a yacht. The poor have sometimes objected to being governed badly, the rich have always objected to being governed at all. Aristocrats were always anarchists...",
        "author_kr": "G.K. 체스터턴",
        "nationality": "영국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 4004,
        "keywords": ["공동체", "철학"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    # 10. Turkish Proverb - 3800
    {
        "text": "광대가 궁전에 들어간다고 왕이 되는 것이 아니다. 궁전이 서커스장이 되는 것이다.",
        "text_original": "When a clown moves into a palace, he doesn't become a king. The palace becomes a circus.",
        "author_kr": "터키 속담",
        "nationality": "터키",
        "field_id": F_CULTURE,
        "profession_id": P_FOLKLORE,
        "upvotes": 3800,
        "keywords": ["지혜", "유머"],
        "situations": ["새로운 관점이 필요할 때", "웃음이 필요할 때"],
    },
    # 11. Johnny Depp - 3719
    {
        "text": "사람들은 약해서 우는 것이 아닙니다. 너무 오래 강해야 했기 때문에 우는 것입니다.",
        "text_original": "People Cry, not because they're Weak. It's because they've been Strong for too Long.",
        "author_kr": "조니 뎁",
        "nationality": "미국",
        "field_id": F_ART,
        "profession_id": P_ACTOR,
        "upvotes": 3719,
        "keywords": ["고통", "용기", "회복"],
        "situations": ["절망적일 때", "힘든 상황에서 거리를 두고 싶을 때"],
    },
    # 12. George Carlin - 3449
    {
        "text": "하늘에 보이지 않는 남자가 우주를 창조했다고 말하면 대다수가 믿습니다. 페인트가 젖었다고 하면 직접 만져봐야 확인합니다.",
        "text_original": "Tell people there's an invisible man in the sky who created the universe, and the vast majority will believe you. Tell them the paint is wet, and they have to touch it to be sure.",
        "author_kr": "조지 칼린",
        "nationality": "미국",
        "field_id": F_CULTURE,
        "profession_id": P_COMEDIAN,
        "upvotes": 3449,
        "keywords": ["유머", "철학", "지혜"],
        "situations": ["웃음이 필요할 때", "새로운 관점이 필요할 때"],
    },
    # 13. Robert A. Heinlein - 3198
    {
        "text": "미국은 연예인과 프로 운동선수를 중요한 인물로 착각하는 나라가 되어 버렸다.",
        "text_original": "The United States had become a place where entertainers and professional athletes were mistaken for people of importance.",
        "author_kr": "로버트 하인라인",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 3198,
        "keywords": ["철학", "인생"],
        "situations": ["자기 성찰", "새로운 관점이 필요할 때"],
    },
    # 14. Ricky Gervais - 3153
    {
        "text": "모든 소설과 경전을 없애면 천 년 후에도 여전히 사라진 채일 것입니다. 하지만 모든 과학 저서를 없애면 천 년 안에 모두 다시 나올 것입니다. 모든 실험이 같은 결과를 낼 테니까요.",
        "text_original": "If you took all the works of fiction and holy books and destroyed them, in a 1000 years they would still be gone. But if you took all the works of science, in a 1000 years they would have all come back. Because all the tests would bear the same results.",
        "author_kr": "리키 저베이스",
        "nationality": "영국",
        "field_id": F_CULTURE,
        "profession_id": P_COMEDIAN,
        "upvotes": 3153,
        "keywords": ["과학", "지식"],
        "situations": ["과학적 사고", "지식의 가치"],
    },
    # 15. Robin Williams - 3145
    {
        "text": "가장 슬픈 사람들이 항상 다른 사람들을 행복하게 하려고 가장 열심히 노력한다고 생각합니다. 완전히 무가치하다고 느끼는 것이 어떤 것인지 알기 때문에 다른 누구도 그렇게 느끼게 하고 싶지 않은 것입니다.",
        "text_original": "I think the saddest people always try their hardest to make people happy. Because they know what it feels like to feel absolutely worthless and they don't want anyone else to feel like that.",
        "author_kr": "로빈 윌리엄스",
        "nationality": "미국",
        "field_id": F_ART,
        "profession_id": P_ACTOR,
        "upvotes": 3145,
        "keywords": ["고통", "관계", "공동체"],
        "situations": ["외로울 때", "절망적일 때", "관계의 소중함"],
    },
    # 16. Eric L. Haney - 3038
    {
        "text": "물려받은 부는 쉽게 탕진할 수 있지만, 물려받은 가난은 벗어나기가 거의 불가능한 유산이다.",
        "text_original": "Inherited wealth may be something easily squandered, but inherited poverty is a legacy almost impossible to lose.",
        "author_kr": "에릭 L. 헤이니",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 3038,
        "keywords": ["인생", "공동체"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    # 17. John F. Kennedy - 3035
    {
        "text": "평화적 혁명을 불가능하게 만드는 자들은 폭력적 혁명을 불가피하게 만든다.",
        "text_original": "Those who make peaceful revolution impossible will make violent revolution inevitable.",
        "author_kr": "존 F. 케네디",
        "nationality": "미국",
        "field_id": F_POLITICS,
        "profession_id": P_POLITICIAN,
        "upvotes": 3035,
        "keywords": ["자유", "변화", "용기"],
        "situations": ["변화를 마주할 때", "용기가 필요할 때"],
    },
    # 18. Malcolm X - 3032
    {
        "text": "조심하지 않으면 신문이 당신으로 하여금 억압받는 사람들을 미워하고, 억압하는 사람들을 사랑하게 만들 것이다.",
        "text_original": "If you're not careful, the newspapers will have you hating the people who are being oppressed, and loving the people who are doing the oppressing.",
        "author_kr": "말콤 엑스",
        "nationality": "미국",
        "field_id": F_POLITICS,
        "profession_id": P_THINKER,
        "upvotes": 3032,
        "keywords": ["자유", "지혜"],
        "situations": ["새로운 관점이 필요할 때", "자기 성찰"],
    },
    # 19. Noam Chomsky - 2997
    {
        "text": "거대 기업이 지배하는 사회에서 자유를 논하는 것은 어불성설입니다. 기업 안에 무슨 자유가 있습니까? 위에서 명령을 받고 아래로 전달하는 전체주의 기관입니다.",
        "text_original": "It's ridiculous to talk about freedom in a society dominated by huge corporations. What kind of freedom is there inside a corporation? They're totalitarian institutions - you take orders from above and give them to people below you. There's about as much freedom as under Stalinism.",
        "author_kr": "노엄 촘스키",
        "nationality": "미국",
        "field_id": F_PHILOSOPHY,
        "profession_id": P_SCHOLAR,
        "upvotes": 2997,
        "keywords": ["자유", "철학"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    # 20. Maximilien Robespierre - 2970
    {
        "text": "자유의 비밀은 사람들을 교육하는 데 있고, 폭정의 비밀은 그들을 무지하게 유지하는 데 있다.",
        "text_original": "The secret of freedom lies in educating people, whereas the secret of tyranny is in keeping them ignorant.",
        "author_kr": "막시밀리앙 로베스피에르",
        "nationality": "프랑스",
        "field_id": F_POLITICS,
        "profession_id": P_POLITICIAN,
        "upvotes": 2970,
        "keywords": ["자유", "교육", "지식"],
        "situations": ["배움의 자세", "지식의 가치"],
    },
    # 21. George Carlin - 2888
    {
        "text": "큰 집단 속 어리석은 사람들의 힘을 절대 과소평가하지 마라.",
        "text_original": "Never underestimate the power of stupid people in large groups.",
        "author_kr": "조지 칼린",
        "nationality": "미국",
        "field_id": F_CULTURE,
        "profession_id": P_COMEDIAN,
        "upvotes": 2888,
        "keywords": ["유머", "지혜"],
        "situations": ["웃음이 필요할 때", "새로운 관점이 필요할 때"],
    },
    # 22. Jim Carrey - 2868
    {
        "text": "우울증은 진짜라고 생각합니다. 하지만 운동도 안 하고, 영양가 있는 음식도 안 먹고, 햇빛도 안 쬐고, 긍정적인 것을 접하지도 않고, 주변에 응원해 줄 사람도 없다면 당신은 스스로에게 싸울 기회조차 주고 있지 않은 것입니다.",
        "text_original": "I believe depression is legitimate. But I also believe that if you don't exercise, eat nutritious food, get sunlight, consume positive material, surround yourself with support, then you aren't giving yourself a fighting chance.",
        "author_kr": "짐 캐리",
        "nationality": "캐나다",
        "field_id": F_ART,
        "profession_id": P_ACTOR,
        "upvotes": 2868,
        "keywords": ["행동", "회복", "성장"],
        "situations": ["절망적일 때", "희망이 필요할 때"],
    },
    # 23. Neil deGrasse Tyson - 2748
    {
        "text": "학생들이 시험에서 부정행위를 하는 것은 우리의 학교 시스템이 학생들이 배움을 중시하는 것보다 성적을 더 중시하기 때문이다.",
        "text_original": "When Students cheat on exams it's because our School System values grades more than Students value learning.",
        "author_kr": "닐 디그래스 타이슨",
        "nationality": "미국",
        "field_id": F_SCIENCE,
        "profession_id": P_SCIENTIST,
        "upvotes": 2748,
        "keywords": ["교육", "학습"],
        "situations": ["배움의 자세", "새로운 관점이 필요할 때"],
    },
    # 24. David Foster Wallace - 2702
    {
        "text": "실제로 투표하지 않는다는 것은 존재하지 않습니다. 투표로 투표하거나, 집에 머물며 어떤 열성 지지자의 표 가치를 암묵적으로 두 배로 만들어 주는 것입니다.",
        "text_original": "In reality, there is no such thing as not voting: you either vote by voting, or you vote by staying home and tacitly doubling the value of some Diehard's vote.",
        "author_kr": "데이비드 포스터 월리스",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 2702,
        "keywords": ["행동", "선택", "공동체"],
        "situations": ["인생의 선택", "행동"],
    },
    # 25. Stephen King - 2687
    {
        "text": "예술가가 쓸모없다고 생각한다면, 음악도 책도 시도 영화도 그림도 없이 격리 기간을 보내보세요.",
        "text_original": "If you think artists are useless try to spend your quarantine without music, books, poems, movies and paintings.",
        "author_kr": "스티븐 킹",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 2687,
        "keywords": ["창의성", "감사"],
        "situations": ["감사할 때", "새로운 관점이 필요할 때"],
    },
    # 26. Victor Hugo - 2675
    {
        "text": "부자의 천국은 가난한 자의 지옥으로 만들어진다.",
        "text_original": "The paradise of the rich is made out of the hell of the poor.",
        "author_kr": "빅토르 위고",
        "nationality": "프랑스",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 2675,
        "keywords": ["공동체", "철학"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    # 27. Ralph Waldo Emerson - 2594
    {
        "text": "사람들은 세상에 대한 자신의 의견이 곧 자신의 성격에 대한 고백이라는 것을 깨닫지 못하는 것 같다.",
        "text_original": "People do not seem to realize that their opinion of the world is also a confession of their character",
        "author_kr": "랄프 왈도 에머슨",
        "nationality": "미국",
        "field_id": F_PHILOSOPHY,
        "profession_id": P_PHILOSOPHER,
        "upvotes": 2594,
        "keywords": ["자기성찰", "지혜"],
        "situations": ["자기 성찰"],
    },
    # 28. David W. Orr - 2536
    {
        "text": "지구에는 더 많은 성공한 사람이 필요하지 않습니다. 지구에 절실히 필요한 것은 더 많은 평화의 중재자, 치유자, 복원자, 이야기꾼, 그리고 모든 종류의 사랑하는 사람들입니다.",
        "text_original": "The planet does not need more successful people. The planet desperately needs more peacemakers, healers, restorers, storytellers, and lovers of all kinds.",
        "author_kr": "데이비드 W. 오르",
        "nationality": "미국",
        "field_id": F_SCIENCE,
        "profession_id": P_SCHOLAR,
        "upvotes": 2536,
        "keywords": ["공동체", "사랑", "의미"],
        "situations": ["삶의 의미를 찾을 때", "새로운 관점이 필요할 때"],
    },
    # 29. Louis CK - 2495
    {
        "text": "누군가가 당신이 자기를 아프게 했다고 말할 때, 당신이 안 그랬다고 결정할 권리는 없다.",
        "text_original": "When a person tells you that you hurt them, you don't get to decide that you didn't.",
        "author_kr": "루이 C.K.",
        "nationality": "미국",
        "field_id": F_CULTURE,
        "profession_id": P_COMEDIAN,
        "upvotes": 2495,
        "keywords": ["관계", "자기성찰"],
        "situations": ["관계가 어려울 때", "자기 성찰"],
    },
    # 30. Plato - 2484
    {
        "text": "공공의 일에 대한 무관심의 대가는 악한 자들에게 지배당하는 것이다.",
        "text_original": "The price of apathy towards public affairs is to be ruled by evil men.",
        "author_kr": "플라톤",
        "nationality": "그리스",
        "field_id": F_PHILOSOPHY,
        "profession_id": P_PHILOSOPHER,
        "upvotes": 2484,
        "keywords": ["행동", "공동체", "지혜"],
        "situations": ["게으를 때", "용기가 필요할 때"],
    },
    # 31. Anne Frank - 2456
    {
        "text": "죽은 사람이 산 사람보다 더 많은 꽃을 받는다. 후회가 감사보다 강하기 때문이다.",
        "text_original": "Dead people receive more flowers than the living ones because regret is stronger than gratitude.",
        "author_kr": "안네 프랑크",
        "nationality": "독일",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 2456,
        "keywords": ["감사", "인생", "죽음"],
        "situations": ["감사할 때", "현재를 살고 싶을 때"],
    },
    # 32. Hubert Reeves - 2420
    {
        "text": "인간은 가장 미친 종이다. 보이지 않는 신을 숭배하면서 보이는 자연을 파괴한다. 자신이 파괴하는 이 자연이 자신이 숭배하는 바로 그 신이라는 것을 모른 채.",
        "text_original": "Man is the most insane species. He worships an invisible god and destroys a visible nature. Unaware that this nature he's destroying is this god he's worshipping.",
        "author_kr": "위베르 리브스",
        "nationality": "캐나다",
        "field_id": F_SCIENCE,
        "profession_id": P_SCIENTIST,
        "upvotes": 2420,
        "keywords": ["철학", "자기성찰"],
        "situations": ["새로운 관점이 필요할 때", "자기 성찰"],
    },
    # 33. George Orwell - 2365
    {
        "text": "모든 폭정은 사기와 무력을 통해 지배하지만, 사기가 들통나면 오직 무력에만 의존해야 한다.",
        "text_original": "All tyrannies rule through fraud and force, but once the fraud is exposed they must rely exclusively on force.",
        "author_kr": "조지 오웰",
        "nationality": "영국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 2365,
        "keywords": ["자유", "지혜"],
        "situations": ["용기가 필요할 때"],
    },
    # 34. Desmond Tutu - 2365
    {
        "text": "사람들을 강에서 건져내는 것만 해서는 안 될 때가 옵니다. 상류로 올라가서 왜 사람들이 빠지는지 알아내야 합니다.",
        "text_original": "There comes a point where we need to stop just pulling people out of the river. We need to go upstream and find out why they're falling in.",
        "author_kr": "데즈먼드 투투",
        "nationality": "남아프리카공화국",
        "field_id": F_RELIGION,
        "profession_id": P_RELIGIOUS,
        "upvotes": 2365,
        "keywords": ["지혜", "공동체", "변화"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    # 35. Oscar Wilde - 2313
    {
        "text": "지루한 사람이란 당신에게서 고독을 빼앗으면서 동행은 제공하지 않는 사람이다.",
        "text_original": "A bore is someone who deprives you of solitude without providing you with company.",
        "author_kr": "오스카 와일드",
        "nationality": "아일랜드",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 2313,
        "keywords": ["유머", "관계"],
        "situations": ["웃음이 필요할 때", "관계가 어려울 때"],
    },
    # 36. Mark Twain - 2223
    {
        "text": "투표가 무언가를 바꿀 수 있었다면 그들이 우리에게 투표하게 두지 않았을 것이다.",
        "text_original": "If voting made any difference they wouldn't let us do it.",
        "author_kr": "마크 트웨인",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 2223,
        "keywords": ["유머", "지혜"],
        "situations": ["웃음이 필요할 때"],
    },
    # 37. Muhammad Ali - 2206
    {
        "text": "나에게는 친절하지만 웨이터에게는 무례한 사람을 신뢰하지 않습니다. 내가 그 위치에 있었다면 나에게도 똑같이 했을 것이기 때문입니다.",
        "text_original": "I don't trust anyone who's nice to me but rude to the waiter. Because they would treat me the same way if I were in that position.",
        "author_kr": "무하마드 알리",
        "nationality": "미국",
        "field_id": F_CULTURE,
        "profession_id": P_ATHLETE,
        "upvotes": 2206,
        "keywords": ["관계", "지혜", "겸손"],
        "situations": ["관계의 소중함", "자기 성찰"],
    },
    # 38. Jodi Picoult - 2118
    {
        "text": "외톨이를 만나면, 무슨 말을 하든 그것은 혼자 있는 것을 즐기기 때문이 아닙니다. 세상에 섞이려 했지만 사람들이 계속 실망시켰기 때문입니다.",
        "text_original": "If you meet a loner, no matter what they tell you, it's not because they enjoy solitude. It's because they have tried to blend into the world before, and people continue to disappoint them.",
        "author_kr": "조디 피코",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 2118,
        "keywords": ["고통", "관계", "외로움"],
        "situations": ["외로울 때", "관계가 어려울 때"],
    },
    # 39. Mark Twain - 2081
    {
        "text": "어떤 양의 증거도 바보를 설득하지 못할 것이다.",
        "text_original": "No amount of evidence will ever persuade an idiot",
        "author_kr": "마크 트웨인",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 2081,
        "keywords": ["지혜", "유머"],
        "situations": ["웃음이 필요할 때"],
    },
    # 40. Emery Allen - 2078
    {
        "text": "인생을 완성하기 위해 다른 사람이 필요한 것은 아닙니다. 하지만 솔직히, 당신의 상처를 영혼의 재앙이 아닌 사랑을 부어넣을 틈으로 보는 사람이 입맞춰 줄 때, 그것은 이 세상에서 가장 평온한 일입니다.",
        "text_original": "You don't need another human being to make your life complete, but let's be honest. Having your wounds kissed by someone who doesn't see them as disasters in your soul but cracks to put their love into is the most calming thing in this world.",
        "author_kr": "에머리 앨런",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 2078,
        "keywords": ["사랑", "관계", "회복"],
        "situations": ["사랑을 느낄 때", "사랑의 본질을 고민할 때"],
    },
    # 41. Frank Ocean - 2046
    {
        "text": "행복할 때는 음악을 즐기고, 슬플 때는 가사를 이해하게 된다.",
        "text_original": "When you're happy you enjoy the music. When you're sad you understand the lyrics.",
        "author_kr": "프랭크 오션",
        "nationality": "미국",
        "field_id": F_ART,
        "profession_id": P_MUSICIAN,
        "upvotes": 2046,
        "keywords": ["고통", "행복", "인생"],
        "situations": ["절망적일 때", "일상의 소소함"],
    },
    # 42. Voltaire - 1968
    {
        "text": "터무니없는 것을 믿게 만들 수 있는 자는 잔혹한 행위도 저지르게 만들 수 있다.",
        "text_original": "Those who can make you believe absurdities, can make you commit atrocities.",
        "author_kr": "볼테르",
        "nationality": "프랑스",
        "field_id": F_PHILOSOPHY,
        "profession_id": P_PHILOSOPHER,
        "upvotes": 1968,
        "keywords": ["지혜", "자유", "철학"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    # 43. James Baldwin - 1968
    {
        "text": "우리는 의견이 달라도 서로 사랑할 수 있습니다. 당신의 반대가 나의 억압과 인간성의 부정, 존재할 권리의 부정에 뿌리를 두고 있지 않다면요.",
        "text_original": "We can disagree and still love each other unless your disagreement is rooted in my oppression and denial of my humanity and right to exist.",
        "author_kr": "제임스 볼드윈",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 1968,
        "keywords": ["자유", "관계", "존재"],
        "situations": ["관계가 어려울 때", "용기가 필요할 때"],
    },
    # 44. Frederick Douglass - 1966
    {
        "text": "자유는 자신의 생각과 의견을 말할 권리가 사라진 곳에서는 의미가 없다. 그것은 모든 권리 중 폭군들이 가장 두려워하는 것이다.",
        "text_original": "Liberty is meaningless where the right to utter one's thoughts and opinions has ceased to exist. That, of all rights, is the dread of tyrants. It is the one right which they first of all strike down.",
        "author_kr": "프레더릭 더글러스",
        "nationality": "미국",
        "field_id": F_POLITICS,
        "profession_id": P_THINKER,
        "upvotes": 1966,
        "keywords": ["자유", "용기"],
        "situations": ["용기가 필요할 때"],
    },
    # 45. James Baldwin - 1965
    {
        "text": "사람들이 증오에 그토록 집요하게 매달리는 이유 중 하나는, 증오가 사라지면 고통과 마주해야 한다는 것을 느끼기 때문이라고 생각합니다.",
        "text_original": "I imagine one of the reasons people cling to their hate so stubbornly is because they sense, once hate is gone, they will be forced to deal with pain.",
        "author_kr": "제임스 볼드윈",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 1965,
        "keywords": ["고통", "자기성찰", "철학"],
        "situations": ["자기 성찰", "깊이 이해하고 싶을 때"],
    },
    # 46. Mevlana (Rumi) - 1952
    {
        "text": "하나의 사실로 마흔 명의 학자를 이길 수 있지만, 마흔 개의 사실로도 한 명의 바보를 이길 수는 없다.",
        "text_original": "You can beat 40 scholars with one fact, but you can't beat one idiot with 40 facts.",
        "author_kr": "메블라나(루미)",
        "nationality": "페르시아",
        "field_id": F_PHILOSOPHY,
        "profession_id": P_PHILOSOPHER,
        "upvotes": 1952,
        "keywords": ["지혜", "유머"],
        "situations": ["웃음이 필요할 때", "새로운 관점이 필요할 때"],
    },
    # 47. Keanu Reeves - 1939
    {
        "text": "잔인하게 부서졌으면서도 다른 생명에게 여전히 부드러울 용기가 있다면, 당신은 천사의 마음을 가진 강인한 사람입니다.",
        "text_original": "If you have been brutally broken but still have the courage to be gentle to other living beings, then you're a badass with a heart of an angel",
        "author_kr": "키아누 리브스",
        "nationality": "캐나다",
        "field_id": F_ART,
        "profession_id": P_ACTOR,
        "upvotes": 1939,
        "keywords": ["용기", "회복", "관계"],
        "situations": ["좌절했을 때", "희망이 필요할 때"],
    },
    # 48. Lin Yutang - 1934
    {
        "text": "작은 인간들이 긴 그림자를 드리우기 시작하면, 해가 지고 있다는 뜻이다.",
        "text_original": "When small men begin to cast long shadows, it means the sun is setting.",
        "author_kr": "린위탕",
        "nationality": "중국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 1934,
        "keywords": ["지혜", "철학"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    # 49. Friedrich Nietzsche - 1901
    {
        "text": "당신이 나에게 거짓말한 것이 화나는 게 아닙니다. 이제부터 당신을 믿을 수 없다는 것이 화나는 것입니다.",
        "text_original": "I'm not upset that you lied to me, I'm upset that from now on I can't believe you.",
        "author_kr": "프리드리히 니체",
        "nationality": "독일",
        "field_id": F_PHILOSOPHY,
        "profession_id": P_PHILOSOPHER,
        "upvotes": 1901,
        "keywords": ["관계", "자기성찰"],
        "situations": ["관계가 어려울 때"],
    },
    # 50. Frank Herbert - 1842
    {
        "text": "한때 인간은 자유로워지길 바라며 사고를 기계에 맡겼다. 하지만 그것은 기계를 가진 다른 인간이 그들을 노예로 만드는 것을 허용했을 뿐이다.",
        "text_original": "Once men turned their thinking over to machines in the hope that this would set them free. But that only permitted other men with machines to enslave them.",
        "author_kr": "프랭크 허버트",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 1842,
        "keywords": ["자유", "지혜", "철학"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    # 51. Robin Williams - 1826
    {
        "text": "인생에서 최악의 일은 혼자 끝나는 것이라고 생각했습니다. 아닙니다. 최악은 당신을 외롭게 느끼게 하는 사람들과 함께하는 것입니다.",
        "text_original": "I used to think that the worst thing in life was to end up alone. It's not. The worst thing in life is to end up with people who make you feel alone.",
        "author_kr": "로빈 윌리엄스",
        "nationality": "미국",
        "field_id": F_ART,
        "profession_id": P_ACTOR,
        "upvotes": 1826,
        "keywords": ["관계", "고통", "인생"],
        "situations": ["외로울 때", "관계가 어려울 때"],
    },
    # 52. Heath Ledger - 1816
    {
        "text": "만나는 사람마다 직업이 뭔지, 결혼했는지, 집이 있는지 묻습니다. 마치 인생이 체크리스트인 것처럼. 하지만 아무도 당신이 행복한지는 묻지 않습니다.",
        "text_original": "Everyone you meet always asks if you have a career, are married, or own a house as if life was some kind of grocery list. But no one ever asks you if you are happy",
        "author_kr": "히스 레저",
        "nationality": "호주",
        "field_id": F_ART,
        "profession_id": P_ACTOR,
        "upvotes": 1816,
        "keywords": ["행복", "인생", "자기성찰"],
        "situations": ["삶의 의미를 찾을 때", "자기 성찰"],
    },
    # 53. Christopher Walken - 1812
    {
        "text": "사람들이 죽은 사람을 얼마나 빨리 잊는지 안다면, 남에게 보여주기 위해 사는 것을 그만둘 것이다.",
        "text_original": "If You Know How Quickly People Forget the Dead, You'll Stop Living to Impress People",
        "author_kr": "크리스토퍼 워컨",
        "nationality": "미국",
        "field_id": F_ART,
        "profession_id": P_ACTOR,
        "upvotes": 1812,
        "keywords": ["인생", "죽음", "자기성찰"],
        "situations": ["자기 성찰", "죽음을 생각할 때"],
    },
    # 54. Kurt Vonnegut - 1643
    {
        "text": "수전 손택은 홀로코스트에서 무엇을 배웠냐는 질문에, 어떤 인구든 10%는 무조건 잔인하고 10%는 무조건 자비로우며 나머지 80%는 어느 쪽으로든 움직일 수 있다고 말했습니다.",
        "text_original": "Susan Sontag was asked what she had learned from the Holocaust, and she said that 10% of any population is cruel, no matter what, and that 10% is merciful, no matter what, and that the remaining 80% could be moved in either direction",
        "author_kr": "커트 보네거트",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 1643,
        "keywords": ["철학", "공동체", "인생"],
        "situations": ["새로운 관점이 필요할 때", "깊이 이해하고 싶을 때"],
    },
    # 55. Denis Diderot - 1445
    {
        "text": "마지막 왕이 마지막 사제의 내장으로 교수형에 처해지기 전까지 인간은 자유롭지 않을 것이다.",
        "text_original": "Men will never be free until the last king is strangled with the entrails of the last priest.",
        "author_kr": "드니 디드로",
        "nationality": "프랑스",
        "field_id": F_PHILOSOPHY,
        "profession_id": P_PHILOSOPHER,
        "upvotes": 1445,
        "keywords": ["자유", "철학"],
        "situations": ["용기가 필요할 때"],
    },
    # 56. Denzel Washington - 1379
    {
        "text": "할리우드 파티에서는 '악마'가 도착하기 30분 전에 나와야 합니다.",
        "text_original": "You gotta leave those Hollywood parties 30 minutes before \"The Devil\" arrives.",
        "author_kr": "덴젤 워싱턴",
        "nationality": "미국",
        "field_id": F_ART,
        "profession_id": P_ACTOR,
        "upvotes": 1379,
        "keywords": ["지혜", "선택"],
        "situations": ["인생의 선택"],
    },
    # 57. Mark Twain - 1341
    {
        "text": "대부분의 사람은 27세에 죽는다. 우리는 그저 72세에 묻을 뿐이다.",
        "text_original": "Most men die at 27, we just bury them at 72.",
        "author_kr": "마크 트웨인",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 1341,
        "keywords": ["인생", "변화", "행동"],
        "situations": ["삶의 의미를 찾을 때", "변화를 마주할 때"],
    },
    # 58. Carl Sagan - 1282
    {
        "text": "우리는 아무도 과학과 기술에 대해 이해하지 못하는 사회를 과학과 기술 위에 세워놓았습니다. 이 무지와 힘의 폭발적 혼합물은 조만간 우리 앞에서 폭발할 것입니다.",
        "text_original": "We've arranged a society on science and technology in which nobody understands anything about science and technology, and this combustible mixture of ignorance and power sooner or later is going to blow up in our faces.",
        "author_kr": "칼 세이건",
        "nationality": "미국",
        "field_id": F_SCIENCE,
        "profession_id": P_SCIENTIST,
        "upvotes": 1282,
        "keywords": ["과학", "지식", "교육"],
        "situations": ["과학적 사고", "지식의 가치"],
    },
    # 59. Bertrand Russell - 1263
    {
        "text": "어리석은 사람이 현명한 사람의 말을 전하면 절대 정확하지 않다. 자기가 이해할 수 있는 것으로 무의식적으로 번역하기 때문이다.",
        "text_original": "A stupid man's report of what a clever man says is never accurate, because he unconsciously translates what he hears into something that he can understand.",
        "author_kr": "버트런드 러셀",
        "nationality": "영국",
        "field_id": F_PHILOSOPHY,
        "profession_id": P_PHILOSOPHER,
        "upvotes": 1263,
        "keywords": ["지혜", "지식"],
        "situations": ["깊이 이해하고 싶을 때"],
    },
    # 60. Mike Tyson - 1176
    {
        "text": "소셜 미디어는 사람들이 너무 편하게 남을 모욕하고도 얼굴에 주먹을 맞지 않는 세상을 만들었다.",
        "text_original": "Social media made y'all way too comfortable with disrespecting people and not getting punched in the face for it",
        "author_kr": "마이크 타이슨",
        "nationality": "미국",
        "field_id": F_CULTURE,
        "profession_id": P_ATHLETE,
        "upvotes": 1176,
        "keywords": ["관계", "유머"],
        "situations": ["웃음이 필요할 때", "관계가 어려울 때"],
    },
    # 61. Isaac Asimov - 997
    {
        "text": "반지성주의의 줄기는 우리의 정치와 문화 생활을 관통하는 끈질긴 실이었으며, 민주주의란 '나의 무지가 당신의 지식만큼 좋다'는 거짓 관념에 의해 양육되었습니다.",
        "text_original": "The strain of anti-intellectualism has been a constant thread winding its way through our political and cultural life, nurtured by the false notion that democracy means that \"my ignorance is just as good as your knowledge.",
        "author_kr": "아이작 아시모프",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 997,
        "keywords": ["지식", "교육", "지혜"],
        "situations": ["지식의 가치", "배움의 자세"],
    },
    # 62. Isaac Asimov - 996
    {
        "text": "현재 삶의 가장 슬픈 면은 과학이 지식을 모으는 속도가 사회가 지혜를 모으는 속도보다 빠르다는 것이다.",
        "text_original": "The saddest aspect of life right now is that science gathers knowledge faster than society gathers wisdom.",
        "author_kr": "아이작 아시모프",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 996,
        "keywords": ["과학", "지혜", "지식"],
        "situations": ["과학적 사고", "깊이 이해하고 싶을 때"],
    },
    # 63. Ethan Hawke - 994
    {
        "text": "어렸을 때는 온 세상이 꿈을 좇으라고 격려하는데, 어른이 되면 꿈을 시도하기만 해도 기분 나빠하는 게 이상하지 않나요?",
        "text_original": "Don't you find it odd that when you're a kid, everyone, all the world, encourages you to follow your dreams. But when you're older, somehow they act offended if you even try.",
        "author_kr": "에단 호크",
        "nationality": "미국",
        "field_id": F_ART,
        "profession_id": P_ACTOR,
        "upvotes": 994,
        "keywords": ["도전", "용기", "인생"],
        "situations": ["도전을 망설일 때", "자신감이 없을 때"],
    },
    # 64. Ansel Adams - 976
    {
        "text": "환경을 구하기 위해 우리 자신의 정부와 싸워야 한다는 것은 끔찍한 일이다.",
        "text_original": "It is horrifying that we have to fight our own government to save the environment.",
        "author_kr": "앤설 애덤스",
        "nationality": "미국",
        "field_id": F_ART,
        "profession_id": P_ARTIST,
        "upvotes": 976,
        "keywords": ["용기", "행동"],
        "situations": ["용기가 필요할 때"],
    },
    # 65. Edward Snowden - 935
    {
        "text": "숨길 것이 없으니 사생활 보호에 신경 쓰지 않는다는 것은, 할 말이 없으니 표현의 자유에 신경 쓰지 않는다는 것과 다를 바 없다.",
        "text_original": "Arguing that you don't care about the right to privacy because you have nothing to hide is no different than saying you don't care about free speech because you have nothing to say.",
        "author_kr": "에드워드 스노든",
        "nationality": "미국",
        "field_id": F_POLITICS,
        "profession_id": P_THINKER,
        "upvotes": 935,
        "keywords": ["자유", "지혜"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    # 66. Mark Twain - 910
    {
        "text": "만약 그리스도가 지금 여기에 있다면, 그가 되지 않을 한 가지가 있다 — 기독교인이다.",
        "text_original": "If Christ were here now, there is one thing he would not be — a Christian.",
        "author_kr": "마크 트웨인",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 910,
        "keywords": ["유머", "철학"],
        "situations": ["웃음이 필요할 때", "새로운 관점이 필요할 때"],
    },
    # 67. Thomas Jefferson - 893
    {
        "text": "약간의 자유를 약간의 질서와 맞바꾸려는 사회는 둘 다 잃을 것이며, 둘 다 잃을 자격이 있다.",
        "text_original": "A society that will trade a little liberty for a little order will lose both and deserve neither",
        "author_kr": "토머스 제퍼슨",
        "nationality": "미국",
        "field_id": F_POLITICS,
        "profession_id": P_POLITICIAN,
        "upvotes": 893,
        "keywords": ["자유", "지혜"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    # 68. George Orwell - 830
    {
        "text": "우리는 이제 자명한 것을 다시 말하는 것이 지성인의 첫 번째 의무인 깊이까지 가라앉았다.",
        "text_original": "We have now sunk to a depth at which restatement of the obvious is the first duty of intelligent men",
        "author_kr": "조지 오웰",
        "nationality": "영국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 830,
        "keywords": ["지혜", "용기"],
        "situations": ["용기가 필요할 때"],
    },
    # 69. Chief Seattle - 807
    {
        "text": "우리는 조상으로부터 땅을 물려받은 것이 아니라 우리 아이들에게서 빌린 것이다.",
        "text_original": "We do not inherit the earth from our ancestors; we borrow it from our children",
        "author_kr": "시애틀 추장",
        "nationality": "미국",
        "field_id": F_PHILOSOPHY,
        "profession_id": P_THINKER,
        "upvotes": 807,
        "keywords": ["가족", "지혜", "전통"],
        "situations": ["새로운 관점이 필요할 때", "감사할 때"],
    },
    # 70. Goethe - 793
    {
        "text": "무지한 자들이 제기하는 질문은 현명한 자들이 천 년 전에 답한 것들이다.",
        "text_original": "Ignorant men raise questions that wise men answered a thousand years ago.",
        "author_kr": "요한 볼프강 폰 괴테",
        "nationality": "독일",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 793,
        "keywords": ["지혜", "지식", "학습"],
        "situations": ["배움의 자세", "지식의 가치"],
    },
    # 71. Richard Feynman - 790
    {
        "text": "문제는 사람들이 교육받지 못한 것이 아닙니다. 배운 것을 믿을 만큼만 교육받고, 배운 것에 의문을 가질 만큼은 교육받지 못한 것이 문제입니다.",
        "text_original": "The problem is not people being uneducated. The problem is that people are educated just enough to believe what they have been taught, but not educated enough to question what they have been taught.",
        "author_kr": "리처드 파인만",
        "nationality": "미국",
        "field_id": F_SCIENCE,
        "profession_id": P_PHYSICIST,
        "upvotes": 790,
        "keywords": ["교육", "지식", "과학"],
        "situations": ["배움의 자세", "과학적 사고"],
    },
    # 72. Albert Einstein - 731
    {
        "text": "세상은 악을 행하는 자들에 의해서가 아니라, 아무것도 하지 않고 그들을 지켜보는 자들에 의해 파괴될 것이다.",
        "text_original": "The world will not be destroyed by those who do evil, but by those who watch them without doing anything.",
        "author_kr": "알베르트 아인슈타인",
        "nationality": "독일",
        "field_id": F_SCIENCE,
        "profession_id": P_PHYSICIST,
        "upvotes": 731,
        "keywords": ["행동", "용기", "공동체"],
        "situations": ["용기가 필요할 때", "게으를 때"],
    },
    # 73. Terence McKenna - 691
    {
        "text": "진실은 존재하기 위해 당신의 참여가 필요하지 않다. 허튼소리는 필요하다.",
        "text_original": "The truth does not require your participation in order to exist. Bullshit does.",
        "author_kr": "테렌스 매케나",
        "nationality": "미국",
        "field_id": F_PHILOSOPHY,
        "profession_id": P_THINKER,
        "upvotes": 691,
        "keywords": ["지혜", "철학"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    # 74. Albert Camus - 652
    {
        "text": "두려움에 기반한 존경보다 비열한 것은 없다.",
        "text_original": "Nothing is more despicable than respect based on fear.",
        "author_kr": "알베르 카뮈",
        "nationality": "프랑스",
        "field_id": F_PHILOSOPHY,
        "profession_id": P_PHILOSOPHER,
        "upvotes": 652,
        "keywords": ["용기", "자유", "철학"],
        "situations": ["용기가 필요할 때", "두려울 때"],
    },
    # 75. C.S. Lewis - 615
    {
        "text": "평범한 사람들이 하는 가장 비겁한 일 중 하나는 사실 앞에서 눈을 감는 것이다.",
        "text_original": "One of the most cowardly things ordinary people do is shut their eyes to facts.",
        "author_kr": "C.S. 루이스",
        "nationality": "영국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 615,
        "keywords": ["용기", "지혜"],
        "situations": ["용기가 필요할 때", "자기 성찰"],
    },
    # 76. Jean-Jacques Rousseau - 608
    {
        "text": "왕들은 왜 백성을 불쌍히 여기지 않는가? 자신이 평범한 사람이 될 것이라 기대하지 않기 때문이다. 부자는 왜 가난한 사람에게 가혹한가? 자신이 가난해질 것이라는 두려움이 없기 때문이다.",
        "text_original": "Why have kings no pity on their people? Because they never expect to be ordinary men. Why are the rich so hard on the poor? Because they have no fear of becoming poor. Why do the nobles look down upon the people? Because a nobleman will never be one of the lower classes.",
        "author_kr": "장자크 루소",
        "nationality": "스위스",
        "field_id": F_PHILOSOPHY,
        "profession_id": P_PHILOSOPHER,
        "upvotes": 608,
        "keywords": ["공동체", "철학", "겸손"],
        "situations": ["새로운 관점이 필요할 때", "자기 성찰"],
    },
    # 77. Jon Stewart - 582
    {
        "text": "코미디가 세상을 바꾸지는 못하지만 전조입니다. 우리는 탄광 속의 바나나 껍질입니다. 사회가 위협받을 때 코미디언이 가장 먼저 쫓겨납니다.",
        "text_original": "Comedy doesn't change the world, but it's a bellwether. We're the banana peel in the coal mine. When a society is under threat, comedians are the ones who get sent away first.",
        "author_kr": "존 스튜어트",
        "nationality": "미국",
        "field_id": F_CULTURE,
        "profession_id": P_COMEDIAN,
        "upvotes": 582,
        "keywords": ["유머", "자유"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    # 78. Howard Zinn - 557
    {
        "text": "역사적으로 가장 끔찍한 일들 — 전쟁, 집단학살, 노예제 — 은 불복종이 아닌 복종에서 비롯되었다.",
        "text_original": "Historically, the most terrible things - war, genocide and slavery- have resulted not from disobedience but from obedience",
        "author_kr": "하워드 진",
        "nationality": "미국",
        "field_id": F_HISTORY,
        "profession_id": P_HISTORIAN,
        "upvotes": 557,
        "keywords": ["용기", "자유", "지혜"],
        "situations": ["용기가 필요할 때", "새로운 관점이 필요할 때"],
    },
    # 79. Voltaire - 507
    {
        "text": "많이 아는 사람일수록 말이 적다.",
        "text_original": "The more a man knows, the less he talks.",
        "author_kr": "볼테르",
        "nationality": "프랑스",
        "field_id": F_PHILOSOPHY,
        "profession_id": P_PHILOSOPHER,
        "upvotes": 507,
        "keywords": ["지혜", "겸손"],
        "situations": ["배움의 자세", "자기 성찰"],
    },
    # 80. Bob Marley - 495
    {
        "text": "범죄자가 법을 만드는 세상에서 정의를 찾을 수는 없다.",
        "text_original": "You'll never find justice in a world where criminals make the laws.",
        "author_kr": "밥 말리",
        "nationality": "자메이카",
        "field_id": F_ART,
        "profession_id": P_MUSICIAN,
        "upvotes": 495,
        "keywords": ["자유", "지혜"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    # 81. Hippocrates - 487
    {
        "text": "누군가를 치유하기 전에, 자신을 아프게 하는 것들을 포기할 의지가 있는지 물어보라.",
        "text_original": "Before you heal someone, ask him if he's willing to give up the things that make him sick.",
        "author_kr": "히포크라테스",
        "nationality": "그리스",
        "field_id": F_SCIENCE,
        "profession_id": P_SCHOLAR,
        "upvotes": 487,
        "keywords": ["지혜", "변화", "자기성찰"],
        "situations": ["자기 성찰", "변화를 마주할 때"],
    },
    # 82. Thomas Sowell - 480
    {
        "text": "사람들은 당신이 틀린 것은 용서해도, 당신이 옳은 것은 절대 용서하지 않는다 — 특히 사건이 당신이 옳고 그들이 틀렸음을 증명할 때.",
        "text_original": "People will forgive you for being wrong, but they will never forgive you for being right — especially if events prove you right while proving them wrong.",
        "author_kr": "토머스 소웰",
        "nationality": "미국",
        "field_id": F_PHILOSOPHY,
        "profession_id": P_SCHOLAR,
        "upvotes": 480,
        "keywords": ["지혜", "관계", "인생"],
        "situations": ["관계가 어려울 때", "새로운 관점이 필요할 때"],
    },
    # 83. G.K. Chesterton - 479
    {
        "text": "동화는 아이들에게 용이 존재한다고 말해주지 않는다. 아이들은 이미 용이 존재한다는 것을 안다. 동화는 아이들에게 용을 죽일 수 있다고 말해준다.",
        "text_original": "Fairy tales do not tell children that dragons exist. Children already know that dragons exist. Fairy tales tell children that dragons can be killed.",
        "author_kr": "G.K. 체스터턴",
        "nationality": "영국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 479,
        "keywords": ["용기", "희망"],
        "situations": ["두려울 때", "용기가 필요할 때", "희망이 필요할 때"],
    },
    # 84. Neil deGrasse Tyson - 472
    {
        "text": "과학의 좋은 점은 당신이 믿든 안 믿든 사실이라는 것이다.",
        "text_original": "The good thing about science is that it's true whether or not you believe in it.",
        "author_kr": "닐 디그래스 타이슨",
        "nationality": "미국",
        "field_id": F_SCIENCE,
        "profession_id": P_SCIENTIST,
        "upvotes": 472,
        "keywords": ["과학", "지식"],
        "situations": ["과학적 사고", "지식의 가치"],
    },
    # 85. Ayn Rand - 467
    {
        "text": "현실을 무시할 수는 있지만, 현실을 무시한 결과를 무시할 수는 없다.",
        "text_original": "You can ignore reality, but you can't ignore the consequences of ignoring reality",
        "author_kr": "아인 랜드",
        "nationality": "미국",
        "field_id": F_PHILOSOPHY,
        "profession_id": P_WRITER,
        "upvotes": 467,
        "keywords": ["지혜", "선택", "인생"],
        "situations": ["인생의 선택", "자기 성찰"],
    },
    # 86. George Orwell - 452
    {
        "text": "모든 전쟁 선전, 모든 비명과 거짓말과 증오는 어김없이 싸우지 않는 사람들에게서 나온다.",
        "text_original": "All the war-propaganda, all the screaming and lies and hatred, comes invariably from people who are not fighting.",
        "author_kr": "조지 오웰",
        "nationality": "영국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 452,
        "keywords": ["지혜", "철학"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    # 87. Mark Twain - 438
    {
        "text": "나는 죽음을 두려워하지 않는다. 태어나기 전 수십억 년 동안 죽어 있었지만 조금도 불편하지 않았다.",
        "text_original": "I do not fear death. I had been dead for billions and billions of years before I was born, and had not suffered the slightest inconvenience from it.",
        "author_kr": "마크 트웨인",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 438,
        "keywords": ["죽음", "유머", "철학"],
        "situations": ["죽음을 생각할 때", "웃음이 필요할 때"],
    },
    # 88. Fyodor Dostoyevsky - 424
    {
        "text": "사람들은 때때로 인간의 '짐승 같은' 잔인함에 대해 말하지만, 이는 짐승에게 끔찍하게 부당하고 모욕적이다. 어떤 동물도 인간만큼 잔인할 수는 없다.",
        "text_original": "People speak sometimes about the \"bestial\" cruelty of man, but that is terribly unjust and offensive to beasts, no animal could ever be so cruel as a man, so artfully, so artistically cruel.",
        "author_kr": "표도르 도스토옙스키",
        "nationality": "러시아",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 424,
        "keywords": ["철학", "인생"],
        "situations": ["깊이 이해하고 싶을 때", "새로운 관점이 필요할 때"],
    },
    # 89. George Carlin - 424
    {
        "text": "모든 냉소적인 사람 안에는 실망한 이상주의자가 있다.",
        "text_original": "Inside every cynical person, there is a disappointed idealist.",
        "author_kr": "조지 칼린",
        "nationality": "미국",
        "field_id": F_CULTURE,
        "profession_id": P_COMEDIAN,
        "upvotes": 424,
        "keywords": ["인생", "자기성찰"],
        "situations": ["자기 성찰", "좌절했을 때"],
    },
    # 90. Upton Sinclair - 416
    {
        "text": "급여가 이해하지 못하는 것에 달려 있을 때, 사람에게 무언가를 이해시키기란 어렵다.",
        "text_original": "It is difficult to get a man to understand something when his salary depends upon his not understanding it.",
        "author_kr": "업턴 싱클레어",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 416,
        "keywords": ["지혜", "철학"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    # 91. Adlai Stevenson - 416
    {
        "text": "사람의 크기는 그를 화나게 하는 일의 크기로 알 수 있다.",
        "text_original": "You can tell the size of a man by the size of the thing that makes him mad.",
        "author_kr": "애들레이 스티븐슨",
        "nationality": "미국",
        "field_id": F_POLITICS,
        "profession_id": P_POLITICIAN,
        "upvotes": 416,
        "keywords": ["지혜", "자기성찰", "겸손"],
        "situations": ["자기 성찰"],
    },
    # 92. Mark Twain - 413
    {
        "text": "읽지 않는 사람은 읽을 수 없는 사람에 비해 아무런 이점이 없다.",
        "text_original": "The man who does not read has no advantage over the man who cannot read.",
        "author_kr": "마크 트웨인",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 413,
        "keywords": ["학습", "지식", "교육"],
        "situations": ["배움의 자세", "공부하기 싫을 때"],
    },
    # 93. Will Rogers - 413
    {
        "text": "모든 것이 변하고 있다. 사람들은 코미디언을 진지하게 받아들이고 정치인을 농담으로 여기고 있다.",
        "text_original": "Everything is changing. People are taking their comedians seriously and the politicians as a joke.",
        "author_kr": "윌 로저스",
        "nationality": "미국",
        "field_id": F_CULTURE,
        "profession_id": P_COMEDIAN,
        "upvotes": 413,
        "keywords": ["유머", "변화"],
        "situations": ["웃음이 필요할 때"],
    },
    # 94. Fyodor Dostoyevsky - 412
    {
        "text": "죄수가 탈출하지 못하게 하는 가장 좋은 방법은 그가 감옥에 있다는 것을 모르게 하는 것이다.",
        "text_original": "The best way to keep a prisoner from escaping is to make sure he never knows he's in prison",
        "author_kr": "표도르 도스토옙스키",
        "nationality": "러시아",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 412,
        "keywords": ["자유", "지혜", "철학"],
        "situations": ["새로운 관점이 필요할 때"],
    },
    # 95. George Carlin - 408
    {
        "text": "우리는 소유물은 늘렸지만 가치는 줄였다. 말은 너무 많이 하고, 사랑은 너무 드물게 하며, 증오는 너무 자주 한다. 생계를 꾸리는 법은 배웠지만 삶을 사는 법은 배우지 못했다.",
        "text_original": "We have multiplied our possessions but reduced our values. We talk too much, love too seldom, and hate too often. We've learned how to make a living but not a life. We've added years to life, not life to years.",
        "author_kr": "조지 칼린",
        "nationality": "미국",
        "field_id": F_CULTURE,
        "profession_id": P_COMEDIAN,
        "upvotes": 408,
        "keywords": ["인생", "의미", "자기성찰"],
        "situations": ["삶의 의미를 찾을 때", "자기 성찰"],
    },
    # 96. Tucker Max - 408
    {
        "text": "악마는 빨간 망토에 뿔을 달고 오지 않는다. 당신이 원했던 모든 것의 모습으로 온다.",
        "text_original": "The devil doesn't come dressed in a red cape and pointy horns. He comes as everything you've ever wished for.",
        "author_kr": "터커 맥스",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 408,
        "keywords": ["지혜", "선택"],
        "situations": ["인생의 선택", "두려울 때"],
    },
    # 97. Carl Sagan - 407
    {
        "text": "역사의 가장 슬픈 교훈 중 하나는 이것이다: 충분히 오래 속았다면, 우리는 속임수의 증거를 거부하게 된다. 더 이상 진실을 알고 싶어하지 않는다. 속임수가 우리를 사로잡은 것이다.",
        "text_original": "One of the saddest lessons of history is this: If we've been bamboozled long enough, we tend to reject any evidence of the bamboozle. We're no longer interested in finding out the truth. The bamboozle has captured us...",
        "author_kr": "칼 세이건",
        "nationality": "미국",
        "field_id": F_SCIENCE,
        "profession_id": P_SCIENTIST,
        "upvotes": 407,
        "keywords": ["지혜", "지식", "자기성찰"],
        "situations": ["자기 성찰", "새로운 관점이 필요할 때"],
    },
    # 98. Stephen Hawking - 405
    {
        "text": "지식의 가장 큰 적은 무지가 아니라 지식의 환상이다.",
        "text_original": "The greatest enemy of knowledge is not ignorance; it is the illusion of knowledge.",
        "author_kr": "스티븐 호킹",
        "nationality": "영국",
        "field_id": F_SCIENCE,
        "profession_id": P_PHYSICIST,
        "upvotes": 405,
        "keywords": ["지식", "지혜", "겸손"],
        "situations": ["배움의 자세", "깊이 이해하고 싶을 때"],
    },
    # 99. Isaac Asimov - 404
    {
        "text": "폭력은 무능한 자의 마지막 피난처이다.",
        "text_original": "Violence is the last refuge of the incompetent.",
        "author_kr": "아이작 아시모프",
        "nationality": "미국",
        "field_id": F_LITERATURE,
        "profession_id": P_WRITER,
        "upvotes": 404,
        "keywords": ["지혜", "철학"],
        "situations": ["새로운 관점이 필요할 때"],
    },
]

# P_ARTIST 정의 누락 수정
# ── 실행 ──
import json

inserted = 0
skipped = 0

for q in quotes_data:
    # 중복 체크 (text_original 기반)
    cur.execute("""
        SELECT 1 FROM quotes
        WHERE similarity(text_original, %s) > 0.4
        OR similarity(text, %s) > 0.4
        LIMIT 1
    """, (q["text_original"], q["text"]))
    if cur.fetchone():
        skipped += 1
        print(f"SKIP (중복): {q['text_original'][:60]}...")
        continue

    # 저자 가져오기/생성
    author_id = get_or_create_author(
        q["author_kr"],
        q.get("nationality", "미상"),
        q.get("field_id"),
        q.get("profession_id"),
    )

    # keyword_ids, situation_ids
    kw_ids = [KEYWORD_IDS[k] for k in q["keywords"] if k in KEYWORD_IDS]
    sit_ids = [SITUATION_IDS[s] for s in q["situations"] if s in SITUATION_IDS]

    # keywords, situation JSON (legacy)
    kw_json = json.dumps(q["keywords"], ensure_ascii=False)
    sit_json = json.dumps(q["situations"], ensure_ascii=False)

    # impact_score
    score = impact(q["upvotes"])

    quote_id = str(uuid.uuid4())

    cur.execute("""
        INSERT INTO quotes (id, text, text_original, original_language, author_id,
                            keywords, situation, keyword_ids, situation_ids,
                            impact_score, status, source_reliability)
        VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s, %s, %s)
    """, (
        quote_id,
        q["text"],
        q["text_original"],
        "en",
        author_id,
        kw_json,
        sit_json,
        kw_ids,
        sit_ids,
        score,
        "draft",
        "unknown",
    ))
    inserted += 1
    print(f"INSERT: [{q['author_kr']}] {q['text'][:50]}...")

conn.commit()
cur.close()
conn.close()

print(f"\n=== 완료 ===")
print(f"삽입: {inserted}건")
print(f"스킵(중복): {skipped}건")
print(f"총 처리: {inserted + skipped}건")
