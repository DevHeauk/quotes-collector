"""
goodreads_popularity에는 있지만 quotes 테이블에 없는 인기 명언을
quotes 형식에 맞게 추가하는 스크립트.

소설/영화 캐릭터 대사는 제외하고, 저자 본인의 독립적인 명언만 포함.
"""

import uuid
import psycopg2
import json

DB_CONFIG = {
    "host": "localhost",
    "user": "youheaukjun",
    "database": "quotes_db",
}

# ── 키워드 ID 맵 ──
KW = {
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

# ── 상황 ID 맵 ──
SIT = {
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

# ── 저자 이름 매핑 (Goodreads 이름 → DB 한국어 이름) ──
AUTHOR_NAME_MAP = {
    "Albert Einstein": "알베르트 아인슈타인",
    "Marcus Tullius Cicero": "키케로",
    "Mark Twain": "마크 트웨인",
    "Oscar Wilde": "오스카 와일드",
    "Friedrich Nietzsche": "프리드리히 니체",
    "Eleanor Roosevelt": "엘리노어 루스벨트",
    "Pablo Neruda": "파블로 네루다",
    "Lao Tzu": "노자",
    "Ralph Waldo Emerson": "랄프 왈도 에머슨",
    "Maya Angelou": "마야 안젤루",
    "Mother Teresa": "마더 테레사",
    "Pablo Picasso": "파블로 피카소",
    "George Bernard Shaw": "조지 버나드 쇼",
    "Abraham Lincoln": "에이브러햄 링컨",
    "Mahatma Gandhi": "마하트마 간디",
    "Martin Luther King Jr.": "마틴 루터 킹 주니어",
    "William Shakespeare": "윌리엄 셰익스피어",
    "Haruki Murakami": "무라카미 하루키",
    "Paulo Coelho": "파울로 코엘료",
    "Helen Keller": "헬렌 켈러",
    "Leo Tolstoy": "레프 톨스토이",
    "Fyodor Dostoevsky": "표도르 도스토옙스키",
    "Kahlil Gibran": "칼릴 지브란",
    "Leonardo da Vinci": "레오나르도 다빈치",
    "Albert Camus": "알베르 카뮈",
    "Robert Frost": "로버트 프로스트",
    "Aristotle": "아리스토텔레스",
    "Victor Hugo": "빅토르 위고",
    "Anne Frank": "안네 프랑크",
    "Confucius": "공자",
    "Benjamin Franklin": "벤저민 프랭클린",
    "Winston Churchill": "윈스턴 처칠",
    "Winston S. Churchill": "윈스턴 처칠",
    "Thomas Jefferson": "토머스 제퍼슨",
    "Sigmund Freud": "지그문트 프로이트",
    "Dale Carnegie": "데일 카네기",
    "Oprah Winfrey": "오프라 윈프리",
    "C.S. Lewis": "C.S. 루이스",
    "Ernest Hemingway": "어니스트 헤밍웨이",
    "Mae West": "메이 웨스트",
    "Audrey Hepburn": "오드리 헵번",
    "George Orwell": "조지 오웰",
    "Niccolò Machiavelli": "니콜로 마키아벨리",
    "Antoine de Saint-Exupéry": "앙투안 드 생텍쥐페리",
    "Rumi": "루미",
    "William Faulkner": "윌리엄 포크너",
    "Francis Bacon": "프랜시스 베이컨",
    "Ray Bradbury": "레이 브래드버리",
    "John Lennon": "존 레논",
}

# ── 소설/영화 캐릭터 대사로 제외할 항목 ──
# J.K. Rowling (해리포터 대사), Suzanne Collins (헝거게임), J.R.R. Tolkien (반지의 제왕),
# Lemony Snicket (소설 시리즈), George R.R. Martin (왕좌의 게임),
# John Green (소설), Chuck Palahniuk (파이트 클럽 등),
# Lewis Carroll (이상한 나라의 앨리스), S.E. Hinton (소설),
# Patrick Rothfuss (소설), Marie Lu (소설), Neil Gaiman (소설 대사),
# Vladimir Nabokov (소설 대사), Arthur Conan Doyle (셜록 홈즈),
# Stephen King (소설 대사), Kurt Vonnegut / Jr. (소설 대사),
# F. Scott Fitzgerald (소설 대사), Charles M. Schulz (만화 캐릭터 대사)
FICTIONAL_EXCLUSIONS = {
    # J.K. Rowling - 해리포터 대사
    "If you want to know what a man's like, take a good look at how he treats his inferiors, not his equals.",
    "It is our choices, Harry, that show what we truly are, far more than our abilities.",
    "It does not do to dwell on dreams and forget to live.",
    "It takes a great deal of bravery to stand up to our enemies, but just as much to stand up to our friends.",
    # J.R.R. Tolkien - 반지의 제왕 대사
    "All that is gold does not glitter, Not all those who wander are lost.",
    "Not all those who wander are lost.",
    "If more of us valued food and cheer and song above hoarded gold, it would be a merrier world.",
    # Suzanne Collins - 헝거게임 대사
    "I wish I could freeze this moment, right here, right now and live in it forever.",
    # George R.R. Martin - 왕좌의 게임 대사
    "Never forget what you are, for surely the world will not.",
    # John Green - 소설 대사
    "The only way out of the labyrinth of suffering is to forgive.",
    # Chuck Palahniuk - 파이트 클럽 등 소설 대사
    "It's only after we've lost everything that we're free to do anything.",
    "We all die. The goal isn't to live forever, the goal is to create something that will.",
    "Nothing of me is original. I am the combined effort of everyone I've ever known.",
    "What I want is to be needed. What I need is to be indispensable to somebody.",
    # Lewis Carroll - 이상한 나라의 앨리스 대사
    "It's no use going back to yesterday, because I was a different person then.",
    # Lemony Snicket - 소설 시리즈 대사
    "Never trust anyone who has not brought a book with them.",
    "People aren't either wicked or noble. They're like chef's salads, with good things and bad things chopped and mixed together in a vinaigrette of confusion and conflict.",
    "Everyone should be able to do one card trick, tell two jokes, and recite three poems, in case they are ever trapped in an elevator.",
    # S.E. Hinton - 소설 대사
    "I lie to myself all the time. But I never believe me.",
    # Patrick Rothfuss - 소설 대사
    "There are three things all wise men fear: the sea in storm, a night with no moon, and the anger of a gentle man.",
    # Marie Lu - 소설 대사
    "Each day means a new twenty-four hours. Each day means everything's possible again.",
    # Stephen King - 소설 대사
    "Books are a uniquely portable magic.",
    "Get busy living or get busy dying.",
    # Kurt Vonnegut / Jr. - 소설 대사
    "We are what we pretend to be, so we must be careful about what we pretend to be.",
    "I want to stand as close to the edge as I can without going over.",
    # F. Scott Fitzgerald - 소설 대사
    "So we beat on, boats against the current, borne back ceaselessly into the past.",
    "The loneliest moment in someone's life is when they are watching their whole world fall apart, and all they can do is stare blankly.",
    # George Orwell - 소설 대사
    "All animals are equal, but some animals are more equal than others.",
    # William Shakespeare - 연극 대사
    "The fool doth think he is wise, but the wise man knows himself to be a fool.",
    "Hell is empty and all the devils are here.",
    "Be not afraid of greatness. Some are born great, some achieve greatness, and some have greatness thrust upon them.",
    "It is not in the stars to hold our destiny but in ourselves.",
    # Charles M. Schulz - 만화 캐릭터(스누피) 대사
    "All you need is love. But a little chocolate now and then doesn't hurt.",
    # Neil Gaiman - 소설 대사
    "Life is a disease: sexually transmitted, and invariably fatal.",
    # Vladimir Nabokov - 소설 대사
    "It was love at first sight, at last sight, at ever and ever sight.",
    # Arthur Conan Doyle - 셜록 홈즈 대사
    "When you have eliminated all which is impossible, then whatever remains, however improbable, must be the truth.",
    # Daphne du Maurier - 소설 대사
    "But luxury has never appealed to me, I like simple things, books, being alone, or with somebody who understands.",
    # Terry Pratchett - 소설 대사
    "It is said that your life flashes before your eyes just before you die. That is true, it's called Life.",
    "Stories of imagination tend to upset those without one.",
    # Ursula K. Le Guin - 소설 대사
    "Love doesn't just sit there, like a stone, it has to be made, like bread; remade all the time, made new.",
    # Douglas Coupland - 소설 대사
    "Remember: the time you feel lonely is the time you most need to be by yourself. Life's cruelest irony.",
    # Arthur C. Clarke - SF 소설 대사
    "Two possibilities exist: either we are alone in the Universe or we are not. Both are equally terrifying.",
}

# ── 명언 데이터: (text_original, text_ko, author_goodreads, likes, keywords, situations) ──
QUOTES_DATA = [
    (
        "I'm selfish, impatient and a little insecure. I look at the world and I want it all. I know I'm not the only one.",
        "나는 이기적이고, 참을성이 없고, 조금은 불안하다. 실수도 하고, 통제할 수 없을 때도 있다. 하지만 나를 최악의 모습으로 감당하지 못한다면, 최고의 나를 누릴 자격도 없다.",
        "Marilyn Monroe", 165443,
        ["자기성찰", "자신감", "존재"],
        ["자기 성찰", "자신감이 없을 때"],
    ),
    (
        "So many books, so little time.",
        "책은 너무 많고, 시간은 너무 적다.",
        "Frank Zappa", 152011,
        ["지식", "학습", "시간"],
        ["배움의 자세", "지식의 가치"],
    ),
    (
        "Two things are infinite: the universe and human stupidity; and I'm not sure about the universe.",
        "두 가지가 무한하다. 우주와 인간의 어리석음. 다만 우주에 대해서는 확신이 없다.",
        "Albert Einstein", 148677,
        ["지혜", "유머", "과학"],
        ["웃음이 필요할 때", "새로운 관점이 필요할 때"],
    ),
    (
        "A room without books is like a body without a soul.",
        "책이 없는 방은 영혼 없는 육체와 같다.",
        "Marcus Tullius Cicero", 135765,
        ["지식", "학습", "교육"],
        ["배움의 자세", "지식의 가치"],
    ),
    (
        "Be who you are and say what you feel, because those who mind don't matter, and those who matter don't mind.",
        "있는 그대로의 너 자신이 되어라. 그리고 느끼는 대로 말하라. 신경 쓰는 사람은 중요하지 않고, 중요한 사람은 신경 쓰지 않는다.",
        "Bernard M. Baruch", 130396,
        ["자신감", "용기", "존재"],
        ["자신감이 없을 때", "자기 성찰"],
    ),
    (
        "You've gotta dance like there's nobody watching, love like you'll never be hurt, sing like there's nobody listening, and live like it's heaven on earth.",
        "아무도 보지 않는 것처럼 춤추고, 절대 상처받지 않을 것처럼 사랑하고, 아무도 듣지 않는 것처럼 노래하고, 이곳이 천국인 것처럼 살아라.",
        "William W. Purkey", 129130,
        ["인생", "자유", "행복"],
        ["현재를 살고 싶을 때", "삶의 의미를 찾을 때"],
    ),
    (
        "You know you're in love when you can't fall asleep because reality is finally better than your dreams.",
        "잠이 오지 않는다면 사랑에 빠진 것이다. 현실이 마침내 꿈보다 아름다워졌기 때문이다.",
        "Dr. Seuss", 127437,
        ["사랑", "행복"],
        ["사랑을 느낄 때"],
    ),
    (
        "You only live once, but if you do it right, once is enough.",
        "인생은 한 번뿐이지만, 제대로 살면 한 번으로 충분하다.",
        "Mae West", 119312,
        ["인생", "의미", "행동"],
        ["삶의 의미를 찾을 때", "현재를 살고 싶을 때"],
    ),
    (
        "In three words I can sum up everything I've learned about life: it goes on.",
        "세 단어로 인생에서 배운 모든 것을 요약할 수 있다: 삶은 계속된다.",
        "Robert Frost", 109497,
        ["인생", "회복", "희망"],
        ["좌절했을 때", "희망이 필요할 때"],
    ),
    (
        "Imperfection is beauty, madness is genius and it's better to be absolutely ridiculous than absolutely boring.",
        "불완전함이 아름다움이고, 광기가 천재성이며, 완전히 우스꽝스러운 것이 완전히 지루한 것보다 낫다.",
        "Marilyn Monroe", 50010,
        ["자신감", "존재", "창의성"],
        ["자신감이 없을 때", "새로운 관점이 필요할 때"],
    ),
    (
        "Good friends, good books, and a sleepy conscience: this is the ideal life.",
        "좋은 친구, 좋은 책, 그리고 졸린 양심. 이것이 이상적인 삶이다.",
        "Mark Twain", 47086,
        ["우정", "인생", "유머"],
        ["일상의 소소함", "웃음이 필요할 때"],
    ),
    (
        "We are all in the gutter, but some of us are looking at the stars.",
        "우리 모두 시궁창에 있지만, 그중 일부는 별을 바라보고 있다.",
        "Oscar Wilde", 46593,
        ["희망", "인생", "초월"],
        ["절망적일 때", "희망이 필요할 때"],
    ),
    (
        "Whenever you find yourself on the side of the majority, it is time to reform (or pause and reflect).",
        "스스로가 다수의 편에 서 있다면, 멈추고 다시 생각해 볼 때이다.",
        "Mark Twain", 43948,
        ["자기성찰", "지혜", "변화"],
        ["자기 성찰", "새로운 관점이 필요할 때"],
    ),
    (
        "Yesterday is history, tomorrow is a mystery, today is a gift of God, which is why we call it the present.",
        "어제는 역사이고, 내일은 미스터리이며, 오늘은 신의 선물이다. 그래서 우리는 오늘을 '선물(present)'이라고 부른다.",
        "Bill Keane", 42812,
        ["시간", "감사", "인생"],
        ["현재를 살고 싶을 때", "감사할 때"],
    ),
    (
        "It is not a lack of love, but a lack of friendship that makes unhappy marriages.",
        "불행한 결혼을 만드는 것은 사랑의 부족이 아니라 우정의 부족이다.",
        "Friedrich Nietzsche", 42493,
        ["사랑", "우정", "관계"],
        ["사랑의 본질을 고민할 때", "관계가 어려울 때"],
    ),
    (
        "The man who does not read has no advantage over the man who cannot read.",
        "책을 읽지 않는 사람은 읽을 수 없는 사람보다 나을 것이 없다.",
        "Mark Twain", 41042,
        ["지식", "학습", "교육"],
        ["배움의 자세", "공부하기 싫을 때"],
    ),
    (
        "A woman is like a tea bag; you never know how strong it is until it's in hot water.",
        "여자는 티백과 같다. 뜨거운 물에 들어가기 전까지는 얼마나 강한지 알 수 없다.",
        "Eleanor Roosevelt", 40781,
        ["용기", "자신감", "도전"],
        ["용기가 필요할 때", "도전을 망설일 때"],
    ),
    (
        "I love you without knowing how, or when, or from where.",
        "나는 당신을 사랑합니다. 어떻게, 언제, 어디서부터인지도 모른 채.",
        "Pablo Neruda", 39943,
        ["사랑"],
        ["사랑을 느낄 때", "사랑의 본질을 고민할 때"],
    ),
    (
        "Being deeply loved by someone gives you strength, while loving someone deeply gives you courage.",
        "누군가에게 깊이 사랑받으면 힘이 생기고, 누군가를 깊이 사랑하면 용기가 생긴다.",
        "Lao Tzu", 34837,
        ["사랑", "용기"],
        ["사랑의 본질을 고민할 때", "용기가 필요할 때"],
    ),
    (
        "You have brains in your head. You have feet in your shoes. You can steer yourself any direction you choose.",
        "너에게는 머리가 있고, 발이 있다. 너는 네가 선택한 어떤 방향으로든 스스로를 이끌 수 있다.",
        "Dr. Seuss", 33885,
        ["선택", "자신감", "자유"],
        ["인생의 선택", "자신감이 없을 때"],
    ),
    (
        "For every minute you are angry you lose sixty seconds of happiness.",
        "화를 내는 1분마다 60초의 행복을 잃는다.",
        "Ralph Waldo Emerson", 33017,
        ["행복", "시간", "자기성찰"],
        ["자기 성찰", "현재를 살고 싶을 때"],
    ),
    (
        "I love deadlines. I love the whooshing noise they make as they go by.",
        "나는 마감을 좋아한다. 마감이 지나갈 때 내는 '휙' 하는 소리가 좋다.",
        "Douglas Adams", 32157,
        ["유머", "시간"],
        ["웃음이 필요할 때"],
    ),
    (
        "I'm not upset that you lied to me, I'm upset that from now on I can't believe you.",
        "네가 나에게 거짓말한 것이 화나는 게 아니라, 이제부터 너를 믿을 수 없다는 것이 화가 난다.",
        "Friedrich Nietzsche", 31649,
        ["관계", "철학"],
        ["관계가 어려울 때"],
    ),
    (
        "There is no greater agony than bearing an untold story inside you.",
        "내 안에 말하지 못한 이야기를 품고 사는 것보다 더 큰 고통은 없다.",
        "Maya Angelou", 31566,
        ["고통", "존재", "용기"],
        ["자기 성찰", "용기가 필요할 때"],
    ),
    (
        "If you judge people, you have no time to love them.",
        "사람들을 판단하면, 그들을 사랑할 시간이 없다.",
        "Mother Teresa", 31384,
        ["사랑", "관계", "겸손"],
        ["관계의 소중함", "관계가 어려울 때"],
    ),
    (
        "If you only read the books that everyone else is reading, you can only think what everyone else is thinking.",
        "다른 사람들이 읽는 책만 읽으면, 다른 사람들이 생각하는 것만 생각하게 된다.",
        "Haruki Murakami", 31287,
        ["지식", "창의성", "자기성찰"],
        ["새로운 관점이 필요할 때", "깊이 이해하고 싶을 때"],
    ),
    (
        "Love is that condition in which the happiness of another person is essential to your own.",
        "사랑이란 다른 사람의 행복이 나 자신의 행복에 필수적인 상태이다.",
        "Robert A. Heinlein", 30841,
        ["사랑", "행복"],
        ["사랑의 본질을 고민할 때"],
    ),
    (
        "Everything you can imagine is real.",
        "상상할 수 있는 모든 것은 현실이다.",
        "Pablo Picasso", 30008,
        ["창의성"],
        ["창의적 사고"],
    ),
    (
        "I have always imagined that Paradise will be a kind of library.",
        "나는 항상 천국이 일종의 도서관일 것이라 상상해왔다.",
        "Jorge Luis Borges", 29739,
        ["지식", "학습"],
        ["배움의 자세", "지식의 가치"],
    ),
    (
        "We don't see things as they are, we see them as we are.",
        "우리는 사물을 있는 그대로 보지 않는다. 우리 자신의 눈으로 본다.",
        "Anais Nin", 28850,
        ["자기성찰", "철학", "지혜"],
        ["자기 성찰", "새로운 관점이 필요할 때"],
    ),
    (
        "Sometimes the questions are complicated and the answers are simple.",
        "때로는 질문은 복잡하지만, 답은 단순하다.",
        "Dr. Seuss", 28151,
        ["지혜", "철학"],
        ["깊이 이해하고 싶을 때"],
    ),
    (
        "Life isn't about finding yourself. Life is about creating yourself.",
        "인생은 자신을 찾는 것이 아니라 자신을 만들어가는 것이다.",
        "George Bernard Shaw", 27337,
        ["인생", "성장", "자기성찰"],
        ["삶의 의미를 찾을 때", "자기 성찰"],
    ),
    (
        "Today you are You, that is truer than true. There is no one alive who is Youer than You.",
        "오늘 너는 너다. 이것은 진실보다 더 진실하다. 살아 있는 누구도 너보다 더 '너'일 수 없다.",
        "Dr. Seuss", 25808,
        ["자신감", "존재"],
        ["자신감이 없을 때", "자기 성찰"],
    ),
    (
        "Logic will get you from A to Z; imagination will get you everywhere.",
        "논리는 A에서 Z까지 데려다줄 것이다. 상상력은 어디든 데려다줄 것이다.",
        "Albert Einstein", 24723,
        ["창의성", "지혜"],
        ["창의적 사고", "새로운 관점이 필요할 때"],
    ),
    (
        "The truth is, everyone is going to hurt you. You just got to find the ones worth suffering for.",
        "사실, 모든 사람이 당신에게 상처를 줄 것이다. 당신은 그저 고통받을 가치가 있는 사람을 찾으면 된다.",
        "Bob Marley", 24452,
        ["관계", "고통", "사랑"],
        ["관계의 소중함", "관계가 어려울 때"],
    ),
    (
        "Folks are usually about as happy as they make their minds up to be.",
        "사람들은 대체로 마음먹은 만큼만 행복하다.",
        "Abraham Lincoln", 23779,
        ["행복", "선택", "자기성찰"],
        ["인생의 선택", "자기 성찰"],
    ),
    (
        "The more that you read, the more things you will know. The more that you learn, the more places you'll go.",
        "더 많이 읽을수록 더 많이 알게 되고, 더 많이 배울수록 더 많은 곳에 갈 수 있다.",
        "Dr. Seuss", 23676,
        ["학습", "지식", "성장"],
        ["배움의 자세", "지식의 가치"],
    ),
    (
        "Not all of us can do great things. But we can do small things with great love.",
        "우리 모두가 위대한 일을 할 수 있는 것은 아니다. 하지만 작은 일을 위대한 사랑으로 할 수 있다.",
        "Mother Teresa", 22712,
        ["사랑", "겸손", "행동"],
        ["일상의 소소함", "삶의 의미를 찾을 때"],
    ),
    (
        "If I had a flower for every time I thought of you, I could walk through my garden forever.",
        "당신을 생각할 때마다 꽃 한 송이를 얻었다면, 나는 영원히 정원을 거닐 수 있을 것이다.",
        "Alfred Tennyson", 21850,
        ["사랑"],
        ["사랑을 느낄 때"],
    ),
    (
        "To love at all is to be vulnerable.",
        "사랑한다는 것 자체가 상처받기 쉬워지는 것이다.",
        "C.S. Lewis", 20582,
        ["사랑", "용기", "고통"],
        ["사랑의 본질을 고민할 때", "용기가 필요할 때"],
    ),
    (
        "The books that the world calls immoral are books that show the world its own shame.",
        "세상이 부도덕하다고 부르는 책들은 세상 자신의 수치를 보여주는 책들이다.",
        "Oscar Wilde", 20232,
        ["지식", "철학", "자기성찰"],
        ["새로운 관점이 필요할 때"],
    ),
    (
        "And, when you want something, all the universe conspires in helping you to achieve it.",
        "무언가를 간절히 원할 때, 온 우주가 그것을 이룰 수 있도록 도와준다.",
        "Paulo Coelho", 20155,
        ["희망", "목표", "운명"],
        ["희망이 필요할 때", "목표가 멀게 느껴질 때"],
    ),
    (
        "The reason I talk to myself is because I'm the only one whose answers I accept.",
        "내가 나 자신에게 말하는 이유는, 내 답을 받아들이는 사람이 나뿐이기 때문이다.",
        "George Carlin", 19796,
        ["유머", "자기성찰"],
        ["웃음이 필요할 때", "자기 성찰"],
    ),
    (
        "There is nothing to writing. All you do is sit down at a typewriter and bleed.",
        "글쓰기란 별것 아니다. 타자기 앞에 앉아서 피를 흘리면 된다.",
        "Ernest Hemingway", 19422,
        ["창의성", "노력", "고통"],
        ["창의적 사고"],
    ),
    (
        "Our deepest fear is not that we are inadequate. Our deepest fear is that we are powerful beyond measure.",
        "우리의 가장 깊은 두려움은 부족하다는 것이 아니다. 가장 깊은 두려움은 우리가 측량할 수 없을 만큼 강력하다는 것이다.",
        "Marianne Williamson", 18052,
        ["자신감", "용기", "성장"],
        ["자신감이 없을 때", "두려울 때"],
    ),
    (
        "The truth is rarely pure and never simple.",
        "진실은 좀처럼 순수하지 않고, 결코 단순하지 않다.",
        "Oscar Wilde", 17407,
        ["지혜", "철학"],
        ["깊이 이해하고 싶을 때"],
    ),
    (
        "It takes courage to grow up and become who you really are.",
        "성장하여 진정한 자신이 되는 데는 용기가 필요하다.",
        "E.E. Cummings", 17052,
        ["용기", "성장", "자기성찰"],
        ["용기가 필요할 때", "자기 성찰"],
    ),
    (
        "Tis better to have loved and lost than never to have loved at all.",
        "사랑하고 잃는 것이 전혀 사랑하지 않은 것보다 낫다.",
        "Alfred Lord Tennyson", 15968,
        ["사랑", "고통", "용기"],
        ["사랑의 본질을 고민할 때"],
    ),
    (
        "Music expresses that which cannot be put into words and that which cannot remain silent.",
        "음악은 말로 표현할 수 없지만 침묵할 수도 없는 것을 표현한다.",
        "Victor Hugo", 13921,
        ["창의성", "초월"],
        ["창의적 사고"],
    ),
    (
        "Those who don't believe in magic will never find it.",
        "마법을 믿지 않는 사람은 결코 그것을 찾지 못할 것이다.",
        "Roald Dahl", 13799,
        ["희망", "창의성"],
        ["희망이 필요할 때", "새로운 관점이 필요할 때"],
    ),
    (
        "An eye for an eye will only make the whole world blind.",
        "눈에는 눈은 온 세상을 눈멀게 할 뿐이다.",
        "Mahatma Gandhi", 13705,
        ["지혜", "관계", "철학"],
        ["새로운 관점이 필요할 때"],
    ),
    (
        "I speak to everyone in the same way, whether he is the garbage man or the president of the university.",
        "나는 누구에게나 같은 방식으로 말한다. 쓰레기 수거원이든 대학 총장이든.",
        "Albert Einstein", 13439,
        ["겸손", "관계"],
        ["관계의 소중함"],
    ),
    (
        "How wonderful it is that nobody need wait a single moment before starting to improve the world.",
        "세상을 더 나은 곳으로 만들기 위해 단 한 순간도 기다릴 필요가 없다는 것은 얼마나 멋진 일인가.",
        "Anne Frank", 13394,
        ["희망", "행동", "변화"],
        ["새로운 시작", "희망이 필요할 때"],
    ),
    (
        "I would rather walk with a friend in the dark, than alone in the light.",
        "밝은 곳을 혼자 걷기보다 어둠 속을 친구와 함께 걷겠다.",
        "Helen Keller", 13330,
        ["우정", "관계"],
        ["관계의 소중함", "외로울 때"],
    ),
    (
        "Happiness is when what you think, what you say, and what you do are in harmony.",
        "행복이란 생각하는 것, 말하는 것, 행하는 것이 조화를 이루는 상태이다.",
        "Mahatma Gandhi", 12755,
        ["행복", "자기성찰", "행동"],
        ["자기 성찰", "삶의 의미를 찾을 때"],
    ),
    (
        "Keep away from people who try to belittle your ambitions. Small people always do that, but the really great make you feel that you, too, can become great.",
        "당신의 포부를 과소평가하려는 사람들에게서 멀리하라. 소인은 항상 그렇게 하지만, 진정으로 위대한 사람은 당신도 위대해질 수 있다고 느끼게 해준다.",
        "Mark Twain", 12752,
        ["관계", "성장", "자신감"],
        ["자신감이 없을 때", "관계가 어려울 때"],
    ),
    (
        "One is loved because one is loved. No reason is needed for loving.",
        "사랑받는 것은 사랑받기 때문이다. 사랑에는 이유가 필요 없다.",
        "Paulo Coelho", 12596,
        ["사랑"],
        ["사랑의 본질을 고민할 때"],
    ),
    (
        "Everyone thinks of changing the world, but no one thinks of changing himself.",
        "누구나 세상을 바꿀 생각을 하지만, 아무도 자기 자신을 바꿀 생각은 하지 않는다.",
        "Leo Tolstoy", 12575,
        ["변화", "자기성찰"],
        ["자기 성찰", "변화를 마주할 때"],
    ),
    (
        "Well-behaved women seldom make history.",
        "얌전한 여성은 좀처럼 역사를 만들지 않는다.",
        "Laurel Thatcher Ulrich", 12562,
        ["용기", "도전", "변화"],
        ["도전을 망설일 때", "용기가 필요할 때"],
    ),
    (
        "Above all, don't lie to yourself.",
        "무엇보다 자기 자신에게 거짓말하지 마라.",
        "Fyodor Dostoevsky", 11924,
        ["자기성찰", "용기"],
        ["자기 성찰"],
    ),
    (
        "Most people are other people. Their thoughts are someone else's opinions, their lives a mimicry, their passions a quotation.",
        "대부분의 사람들은 다른 사람이다. 그들의 생각은 남의 의견이고, 그들의 삶은 모방이며, 그들의 열정은 인용에 불과하다.",
        "Oscar Wilde", 11922,
        ["자기성찰", "존재", "철학"],
        ["자기 성찰", "새로운 관점이 필요할 때"],
    ),
    (
        "It's the friends you can call up at 4 a.m. that matter.",
        "중요한 것은 새벽 4시에 전화할 수 있는 친구다.",
        "Marlene Dietrich", 11853,
        ["우정", "관계"],
        ["관계의 소중함"],
    ),
    (
        "You don't have to burn books to destroy a culture. Just get people to stop reading them.",
        "문화를 파괴하기 위해 책을 태울 필요 없다. 사람들이 읽지 않게 만들면 된다.",
        "Ray Bradbury", 11743,
        ["지식", "교육", "변화"],
        ["지식의 가치", "배움의 자세"],
    ),
    (
        "Nothing is impossible, the word itself says I'm possible!",
        "불가능한 것은 없다. '불가능(impossible)'이라는 단어 자체가 '나는 가능하다(I'm possible)'고 말하고 있다!",
        "Audrey Hepburn", 11532,
        ["희망", "자신감", "동기부여"],
        ["자신감이 없을 때", "희망이 필요할 때"],
    ),
    (
        "Never doubt that a small group of thoughtful, committed, citizens can change the world. Indeed, it is the only thing that ever has.",
        "소수의 사려 깊고 헌신적인 시민이 세상을 바꿀 수 있다는 것을 결코 의심하지 마라. 실제로 세상을 바꾼 것은 항상 그런 사람들이었다.",
        "Margaret Mead", 11498,
        ["변화", "공동체", "행동"],
        ["변화를 마주할 때", "희망이 필요할 때"],
    ),
    (
        "The only people for me are the mad ones, the ones who are mad to live, mad to talk, mad to be saved.",
        "내게 맞는 사람은 미친 사람들뿐이다. 삶에 미치고, 말에 미치고, 구원에 미친 사람들.",
        "Jack Kerouac", 11482,
        ["인생", "자유", "존재"],
        ["삶의 의미를 찾을 때"],
    ),
    (
        "Facts do not cease to exist because they are ignored.",
        "사실은 무시한다고 해서 존재하지 않는 것이 아니다.",
        "Aldous Huxley", 10557,
        ["지혜", "철학"],
        ["새로운 관점이 필요할 때"],
    ),
    (
        "A clever person solves a problem. A wise person avoids it.",
        "영리한 사람은 문제를 해결하고, 현명한 사람은 문제를 피한다.",
        "Albert Einstein", 9509,
        ["지혜", "철학"],
        ["깊이 이해하고 싶을 때"],
    ),
    (
        "Out beyond ideas of wrongdoing and rightdoing there is a field. I'll meet you there.",
        "옳고 그름이라는 관념 너머에 들판이 있다. 그곳에서 만나자.",
        "Rumi", 9471,
        ["초월", "사랑", "철학"],
        ["새로운 관점이 필요할 때", "삶의 의미를 찾을 때"],
    ),
    (
        "First they ignore you. Then they ridicule you. And then they attack you and want to burn you. And then they build monuments to you.",
        "처음에는 무시하고, 다음에는 조롱하고, 그 다음에는 공격한다. 그리고 마지막에는 당신에게 기념비를 세운다.",
        "Nicholas Klein", 9396,
        ["끈기", "용기", "변화"],
        ["좌절했을 때", "포기하고 싶을 때"],
    ),
    (
        "When someone shows you who they are believe them the first time.",
        "누군가 자신이 어떤 사람인지 보여줄 때, 처음부터 믿어라.",
        "Maya Angelou", 9393,
        ["관계", "지혜"],
        ["관계가 어려울 때"],
    ),
    (
        "There are two basic motivating forces: fear and love.",
        "두 가지 기본적인 동기 부여의 힘이 있다: 두려움과 사랑.",
        "John Lennon", 9366,
        ["사랑", "동기부여", "철학"],
        ["삶의 의미를 찾을 때"],
    ),
    (
        "Tell me, what is it you plan to do with your one wild and precious life?",
        "말해보세요, 이 거칠고 소중한 단 하나의 인생으로 당신은 무엇을 할 건가요?",
        "Mary Oliver", 9306,
        ["인생", "선택", "의미"],
        ["삶의 의미를 찾을 때", "인생의 선택"],
    ),
    (
        "Pain and suffering are always inevitable for a large intelligence and a deep heart.",
        "고통과 괴로움은 큰 지성과 깊은 마음을 가진 사람에게 항상 불가피하다.",
        "Fyodor Dostoevsky", 9252,
        ["고통", "지혜", "존재"],
        ["힘든 상황에서 거리를 두고 싶을 때"],
    ),
    (
        "These woods are lovely, dark and deep. But I have promises to keep, and miles to go before I sleep.",
        "이 숲은 아름답고, 어둡고, 깊다. 하지만 나에게는 지켜야 할 약속이 있고, 잠들기 전에 가야 할 먼 길이 있다.",
        "Robert Frost", 9172,
        ["인생", "목표", "끈기"],
        ["꾸준함이 필요할 때", "목표가 멀게 느껴질 때"],
    ),
    (
        "Some books should be tasted, some devoured, but only a few should be chewed and digested thoroughly.",
        "어떤 책은 맛보고, 어떤 책은 삼키되, 소수의 책만 씹어서 완전히 소화해야 한다.",
        "Francis Bacon", 8662,
        ["지식", "학습", "지혜"],
        ["배움의 자세", "깊이 이해하고 싶을 때"],
    ),
    (
        "Those who dream by day are cognizant of many things which escape those who dream only by night.",
        "낮에 꿈꾸는 사람은 밤에만 꿈꾸는 사람이 놓치는 많은 것들을 안다.",
        "Edgar Allan Poe", 8631,
        ["창의성", "희망", "목표"],
        ["창의적 사고", "목표가 멀게 느껴질 때"],
    ),
    (
        "The wound is the place where the Light enters you.",
        "상처는 빛이 당신에게 들어오는 곳이다.",
        "Rumi", 7872,
        ["고통", "회복", "초월"],
        ["실패했을 때", "희망이 필요할 때"],
    ),
    (
        "You have enemies? Good. That means you've stood up for something, sometime in your life.",
        "적이 있는가? 좋다. 그것은 인생에서 한 번이라도 무언가를 위해 일어섰다는 뜻이다.",
        "Winston Churchill", 7802,
        ["용기", "도전"],
        ["용기가 필요할 때", "좌절했을 때"],
    ),
    (
        "Once you learn to read, you will be forever free.",
        "읽는 법을 배우면, 영원히 자유로워진다.",
        "Frederick Douglass", 7691,
        ["자유", "학습", "교육"],
        ["배움의 자세", "지식의 가치"],
    ),
    (
        "Think of all the beauty still left around you and be happy.",
        "당신 주변에 여전히 남아 있는 모든 아름다움을 생각하고 행복해하세요.",
        "Anne Frank", 7687,
        ["행복", "감사", "희망"],
        ["감사할 때", "희망이 필요할 때"],
    ),
    (
        "God created war so that Americans would learn geography.",
        "신은 미국인들이 지리를 배우도록 전쟁을 만들었다.",
        "Mark Twain", 7543,
        ["유머"],
        ["웃음이 필요할 때"],
    ),
    (
        "A human being is a part of the whole called by us universe, a part limited in time and space.",
        "인간은 우리가 '우주'라고 부르는 전체의 일부이며, 시간과 공간에 한정된 존재이다.",
        "Albert Einstein", 7522,
        ["존재", "철학", "과학"],
        ["삶의 의미를 찾을 때"],
    ),
    (
        "What is a friend? A single soul dwelling in two bodies.",
        "친구란 무엇인가? 두 몸에 깃든 하나의 영혼이다.",
        "Aristotle", 7453,
        ["우정", "관계"],
        ["관계의 소중함"],
    ),
    (
        "Those who find ugly meanings in beautiful things are corrupt without being charming.",
        "아름다운 것에서 추한 의미를 찾는 사람은 매력 없이 타락한 것이다.",
        "Oscar Wilde", 7450,
        ["지혜", "철학"],
        ["새로운 관점이 필요할 때"],
    ),
    (
        "Take responsibility of your own happiness, never put it in other people's hands.",
        "자신의 행복을 스스로 책임져라. 절대 남의 손에 맡기지 마라.",
        "Roy T. Bennett", 7393,
        ["행복", "자기성찰", "선택"],
        ["자기 성찰", "인생의 선택"],
    ),
    (
        "Nobody realizes that some people expend tremendous energy merely to be normal.",
        "어떤 사람들이 단지 평범해지기 위해 엄청난 에너지를 쏟는다는 것을 아무도 모른다.",
        "Albert Camus", 7375,
        ["존재", "고통", "자기성찰"],
        ["힘든 상황에서 거리를 두고 싶을 때", "자기 성찰"],
    ),
    (
        "Accept yourself, love yourself, and keep moving forward.",
        "자신을 받아들이고, 자신을 사랑하고, 계속 앞으로 나아가라.",
        "Roy T. Bennett", 7369,
        ["자신감", "성장", "동기부여"],
        ["자신감이 없을 때", "포기하고 싶을 때"],
    ),
    (
        "Waiting is painful. Forgetting is painful. But not knowing which to do is the worst kind of suffering.",
        "기다림은 고통스럽다. 잊는 것도 고통스럽다. 하지만 어느 쪽을 해야 할지 모르는 것이 최악의 고통이다.",
        "Paulo Coelho", 7363,
        ["고통", "선택", "인생"],
        ["인생의 선택", "절망적일 때"],
    ),
    (
        "I cannot live without books.",
        "나는 책 없이는 살 수 없다.",
        "Thomas Jefferson", 7347,
        ["지식", "학습"],
        ["배움의 자세", "지식의 가치"],
    ),
    (
        "There is always some madness in love. But there is also always some reason in madness.",
        "사랑에는 항상 약간의 광기가 있다. 하지만 광기 속에도 항상 약간의 이성이 있다.",
        "Friedrich Nietzsche", 7290,
        ["사랑", "철학"],
        ["사랑의 본질을 고민할 때"],
    ),
    (
        "what matters most is how well you walk through the fire",
        "가장 중요한 것은 불 속을 얼마나 잘 걸어가느냐이다.",
        "Charles Bukowski", 7212,
        ["용기", "끈기", "인생"],
        ["힘든 상황에서 거리를 두고 싶을 때", "포기하고 싶을 때"],
    ),
    (
        "Never be bullied into silence. Never allow yourself to be made a victim. Accept no one's definition of your life; define yourself.",
        "협박에 굴복하여 침묵하지 마라. 자신이 희생자가 되도록 허락하지 마라. 누구의 인생 정의도 받아들이지 말고, 스스로를 정의하라.",
        "Robert Frost", 7197,
        ["자신감", "용기", "자유"],
        ["용기가 필요할 때", "자신감이 없을 때"],
    ),
    (
        "Love is so short, forgetting is so long.",
        "사랑은 너무 짧고, 잊음은 너무 길다.",
        "Pablo Neruda", 7174,
        ["사랑", "시간", "고통"],
        ["사랑의 본질을 고민할 때"],
    ),
    (
        "I can be changed by what happens to me. But I refuse to be reduced by it.",
        "나에게 일어나는 일에 의해 변할 수는 있다. 하지만 그것에 의해 작아지는 것은 거부한다.",
        "Maya Angelou", 7163,
        ["회복", "용기", "성장"],
        ["실패했을 때", "좌절했을 때"],
    ),
    (
        "Respect other people's feelings. It might mean nothing to you, but it could mean everything to them.",
        "다른 사람의 감정을 존중하라. 당신에게는 아무것도 아닐 수 있지만, 그들에게는 전부일 수 있다.",
        "Roy T. Bennett", 7162,
        ["관계", "겸손"],
        ["관계의 소중함", "관계가 어려울 때"],
    ),
    (
        "Man is least himself when he talks in his own person. Give him a mask, and he will tell you the truth.",
        "인간은 자기 자신으로 말할 때 가장 진실하지 않다. 가면을 주면, 진실을 말할 것이다.",
        "Oscar Wilde", 7144,
        ["자기성찰", "철학", "존재"],
        ["자기 성찰", "깊이 이해하고 싶을 때"],
    ),
    (
        "Should I kill myself, or have a cup of coffee?",
        "자살해야 할까, 아니면 커피를 한 잔 마셔야 할까?",
        "Albert Camus", 7143,
        ["철학", "존재", "유머"],
        ["삶의 의미를 찾을 때"],
    ),
    (
        "If you can't fly then run, if you can't run then walk, if you can't walk then crawl, but whatever you do you have to keep moving forward.",
        "날 수 없다면 뛰어라, 뛸 수 없다면 걸어라, 걸을 수 없다면 기어라. 무엇을 하든 계속 앞으로 나아가야 한다.",
        "Martin Luther King Jr.", 7099,
        ["끈기", "동기부여", "행동"],
        ["포기하고 싶을 때", "꾸준함이 필요할 때"],
    ),
    (
        "Try not to become a man of success. Rather become a man of value.",
        "성공한 사람이 되려고 하지 말고, 가치 있는 사람이 되려고 하라.",
        "Albert Einstein", 7087,
        ["성공", "의미", "자기성찰"],
        ["삶의 의미를 찾을 때", "자기 성찰"],
    ),
    (
        "We are all different. Don't judge, understand instead.",
        "우리는 모두 다르다. 판단하지 말고, 대신 이해하라.",
        "Roy T. Bennett", 7025,
        ["관계", "겸손", "지혜"],
        ["관계가 어려울 때", "새로운 관점이 필요할 때"],
    ),
    (
        "I generally avoid temptation unless I can't resist it.",
        "나는 대체로 유혹을 피한다. 거부할 수 없는 유혹이 아니라면.",
        "Mae West", 7022,
        ["유머", "인생"],
        ["웃음이 필요할 때"],
    ),
    (
        "Either write something worth reading or do something worth writing.",
        "읽을 만한 가치가 있는 것을 쓰거나, 쓸 만한 가치가 있는 것을 하라.",
        "Benjamin Franklin", 6900,
        ["행동", "의미", "동기부여"],
        ["삶의 의미를 찾을 때", "게으를 때"],
    ),
    (
        "I was gratified to be able to answer promptly, and I did. I said I didn't know.",
        "즉시 대답할 수 있어서 기뻤다. 그래서 대답했다. 모른다고.",
        "Mark Twain", 6894,
        ["유머", "겸손", "지혜"],
        ["웃음이 필요할 때"],
    ),
    (
        "Accept who you are. Unless you're a serial killer.",
        "있는 그대로의 자신을 받아들여라. 연쇄 살인범이 아닌 이상.",
        "Ellen DeGeneres", 6885,
        ["유머", "자신감"],
        ["웃음이 필요할 때", "자신감이 없을 때"],
    ),
    (
        "Stop acting so small. You are the universe in ecstatic motion.",
        "그렇게 작은 척 하지 마라. 너는 황홀경 속에 움직이는 우주다.",
        "Rumi", 6872,
        ["자신감", "초월", "존재"],
        ["자신감이 없을 때", "삶의 의미를 찾을 때"],
    ),
    (
        "You must have chaos within you to give birth to a dancing star.",
        "춤추는 별을 낳으려면 내면에 혼돈이 있어야 한다.",
        "Friedrich Nietzsche", 6855,
        ["창의성", "존재", "철학"],
        ["창의적 사고"],
    ),
    (
        "Turn your wounds into wisdom.",
        "상처를 지혜로 바꿔라.",
        "Oprah Winfrey", 6854,
        ["지혜", "회복", "성장"],
        ["실패했을 때", "좌절했을 때"],
    ),
    (
        "The important thing is not to stop questioning. Curiosity has its own reason for existence.",
        "중요한 것은 질문을 멈추지 않는 것이다. 호기심에는 그 자체로 존재 이유가 있다.",
        "Albert Einstein", 6831,
        ["과학", "학습", "지혜"],
        ["과학적 사고", "배움의 자세"],
    ),
    (
        "Life is too short to waste your time on people who don't respect, appreciate, and value you.",
        "당신을 존중하지도, 감사하지도, 소중히 여기지도 않는 사람에게 시간을 낭비하기에 인생은 너무 짧다.",
        "Roy T. Bennett", 6813,
        ["인생", "관계", "시간"],
        ["관계가 어려울 때"],
    ),
    (
        "No tears in the writer, no tears in the reader. No surprise in the writer, no surprise in the reader.",
        "작가에게 눈물이 없다면 독자에게도 눈물이 없다. 작가에게 놀라움이 없다면 독자에게도 놀라움이 없다.",
        "Robert Frost", 6803,
        ["창의성", "노력"],
        ["창의적 사고"],
    ),
    (
        "Painting is poetry that is seen rather than felt, and poetry is painting that is felt rather than seen.",
        "회화는 느끼기보다 보는 시이고, 시는 보기보다 느끼는 회화이다.",
        "Leonardo da Vinci", 6752,
        ["창의성"],
        ["창의적 사고"],
    ),
    (
        "The simple things are also the most extraordinary things, and only the wise can see them.",
        "단순한 것이 가장 비범한 것이기도 하며, 현명한 사람만이 그것을 볼 수 있다.",
        "Paulo Coelho", 6740,
        ["지혜", "겸손"],
        ["일상의 소소함", "깊이 이해하고 싶을 때"],
    ),
    (
        "I wonder how many people I've looked at all my life and never seen.",
        "평생 바라보면서도 한 번도 제대로 보지 못한 사람이 얼마나 될까 궁금하다.",
        "John Steinbeck", 6733,
        ["관계", "자기성찰"],
        ["자기 성찰", "관계의 소중함"],
    ),
    (
        "You gain strength, courage and confidence by every experience in which you really stop to look fear in the face.",
        "두려움을 정면으로 바라보는 모든 경험에서 힘과 용기와 자신감을 얻는다.",
        "Eleanor Roosevelt", 6709,
        ["용기", "자신감", "성장"],
        ["두려울 때", "용기가 필요할 때"],
    ),
    (
        "Live the Life of Your Dreams: Be brave enough to live the life of your dreams according to your vision and purpose.",
        "꿈꾸는 삶을 살아라: 자신의 비전과 목적에 따라 꿈의 삶을 살 만큼 용감해져라.",
        "Roy T. Bennett", 6701,
        ["용기", "목표", "동기부여"],
        ["도전을 망설일 때", "목표가 멀게 느껴질 때"],
    ),
    (
        "Everyone sees what you appear to be, few experience what you really are.",
        "누구나 당신의 겉모습을 보지만, 진짜 당신을 경험하는 사람은 거의 없다.",
        "Niccolò Machiavelli", 6693,
        ["자기성찰", "지혜", "존재"],
        ["자기 성찰"],
    ),
    (
        "What happens when people open their hearts? They get better.",
        "사람들이 마음을 열면 어떻게 되는가? 더 나아진다.",
        "Haruki Murakami", 6689,
        ["관계", "회복", "성장"],
        ["관계가 어려울 때", "희망이 필요할 때"],
    ),
    (
        "Above all, be the heroine of your life, not the victim.",
        "무엇보다 자신의 인생의 주인공이 되어라, 희생자가 아니라.",
        "Nora Ephron", 6526,
        ["자신감", "용기", "인생"],
        ["자신감이 없을 때", "인생의 선택"],
    ),
    (
        "Whatever it is you're seeking won't come in the form you're expecting.",
        "당신이 찾고 있는 것이 무엇이든, 기대하는 형태로 오지 않을 것이다.",
        "Haruki Murakami", 6487,
        ["인생", "지혜", "변화"],
        ["새로운 관점이 필요할 때"],
    ),
    (
        "Why fit in when you were born to stand out?",
        "어울리려고 왜 애쓰는가? 너는 돋보이기 위해 태어났는데.",
        "Dr. Seuss", 6475,
        ["자신감", "존재"],
        ["자신감이 없을 때"],
    ),
    (
        "I have great faith in fools - self-confidence my friends will call it.",
        "나는 바보들에게 큰 믿음이 있다. 친구들은 그것을 자신감이라고 부를 것이다.",
        "Edgar Allan Poe", 6467,
        ["유머", "자신감"],
        ["웃음이 필요할 때"],
    ),
    (
        "That's the thing about books. They let you travel without moving your feet.",
        "책이란 그런 것이다. 발을 움직이지 않고도 여행하게 해준다.",
        "Jhumpa Lahiri", 6463,
        ["지식", "학습"],
        ["배움의 자세", "지식의 가치"],
    ),
    (
        "Don't waste your time in anger, regrets, worries, and grudges. Life is too short to be unhappy.",
        "분노, 후회, 걱정, 원한에 시간을 낭비하지 마라. 불행하기에 인생은 너무 짧다.",
        "Roy T. Bennett", 6448,
        ["행복", "시간", "자기성찰"],
        ["자기 성찰", "현재를 살고 싶을 때"],
    ),
    (
        "You must stay drunk on writing so reality cannot destroy you.",
        "글쓰기에 취해 있어야 한다. 그래야 현실이 당신을 파괴하지 못한다.",
        "Ray Bradbury", 6446,
        ["창의성", "끈기"],
        ["창의적 사고"],
    ),
    (
        "Prayer is not asking. It is a longing of the soul. It is daily admission of one's weakness. It is better in prayer to have a heart without words than words without a heart.",
        "기도는 요청이 아니다. 영혼의 갈망이다. 자신의 약함을 매일 인정하는 것이다. 기도에서는 말 없는 마음이 마음 없는 말보다 낫다.",
        "Mahatma Gandhi", 6427,
        ["겸손", "초월", "자기성찰"],
        ["자기 성찰"],
    ),
    (
        "One day, in retrospect, the years of struggle will strike you as the most beautiful.",
        "훗날 돌이켜보면, 고군분투한 세월이 가장 아름다웠음을 알게 될 것이다.",
        "Sigmund Freud", 6423,
        ["끈기", "성장", "희망"],
        ["좌절했을 때", "과거를 돌아볼 때"],
    ),
    (
        "There are worse crimes than burning books. One of them is not reading them.",
        "책을 태우는 것보다 더 나쁜 죄가 있다. 그중 하나는 읽지 않는 것이다.",
        "Joseph Brodsky", 6412,
        ["지식", "교육"],
        ["배움의 자세", "지식의 가치"],
    ),
    (
        "I do not fear death. I had been dead for billions and billions of years before I was born, and had not suffered the slightest inconvenience from it.",
        "나는 죽음을 두려워하지 않는다. 태어나기 전 수십억 년 동안 죽어 있었지만, 그로 인한 불편은 조금도 없었다.",
        "Mark Twain", 6397,
        ["죽음", "유머", "철학"],
        ["죽음을 생각할 때", "웃음이 필요할 때"],
    ),
    (
        "I think God, in creating man, somewhat overestimated his ability.",
        "신은 인간을 창조하면서 그의 능력을 다소 과대평가한 것 같다.",
        "Oscar Wilde", 6387,
        ["유머", "철학"],
        ["웃음이 필요할 때"],
    ),
    (
        "If you love somebody, let them go, for if they return, they were always yours. If they don't, they never were.",
        "누군가를 사랑한다면 보내주어라. 돌아온다면 그 사람은 항상 당신의 것이었고, 돌아오지 않는다면 처음부터 당신의 것이 아니었다.",
        "Kahlil Gibran", 6386,
        ["사랑", "자유"],
        ["사랑의 본질을 고민할 때"],
    ),
    (
        "You cannot swim for new horizons until you have courage to lose sight of the shore.",
        "해안을 시야에서 놓칠 용기가 없다면, 새로운 수평선을 향해 헤엄칠 수 없다.",
        "William Faulkner", 6319,
        ["용기", "도전", "변화"],
        ["도전을 망설일 때", "두려울 때"],
    ),
    (
        "I never travel without my diary. One should always have something sensational to read in the train.",
        "나는 일기장 없이 여행하지 않는다. 기차에서 읽을 만한 센세이셔널한 것이 항상 있어야 하니까.",
        "Oscar Wilde", 6305,
        ["유머"],
        ["웃음이 필요할 때"],
    ),
    (
        "If you are going through hell, keep going.",
        "지옥을 지나고 있다면, 계속 걸어라.",
        "Winston S. Churchill", 6293,
        ["용기", "끈기", "회복"],
        ["포기하고 싶을 때", "힘든 상황에서 거리를 두고 싶을 때"],
    ),
    (
        "It isn't what you have or who you are or where you are or what you are doing that makes you happy or unhappy. It is what you think about it.",
        "당신을 행복하거나 불행하게 만드는 것은 가진 것, 당신이 누구인지, 어디에 있는지, 무엇을 하는지가 아니다. 그것에 대해 어떻게 생각하느냐가 중요하다.",
        "Dale Carnegie", 6285,
        ["행복", "자기성찰", "선택"],
        ["자기 성찰", "인생의 선택"],
    ),
    (
        "Angry people are not always wise.",
        "화난 사람이 항상 현명한 것은 아니다.",
        "Jane Austen", 6257,
        ["지혜", "자기성찰"],
        ["자기 성찰"],
    ),
    (
        "As usual, there is a great woman behind every idiot.",
        "늘 그렇듯, 모든 바보 뒤에는 위대한 여성이 있다.",
        "John Lennon", 6251,
        ["유머", "사랑", "관계"],
        ["웃음이 필요할 때"],
    ),
    (
        "I have found the paradox, that if you love until it hurts, there can be no more hurt, only more love.",
        "아플 때까지 사랑하면 더 이상 아픔은 없고, 오직 더 많은 사랑만 있다는 역설을 발견했다.",
        "Daphne Rae", 6247,
        ["사랑", "고통", "초월"],
        ["사랑의 본질을 고민할 때"],
    ),
    (
        "Don't let the expectations and opinions of other people affect your decisions. It's your life, not theirs.",
        "다른 사람의 기대와 의견이 당신의 결정에 영향을 주지 않게 하라. 당신의 인생이지, 그들의 인생이 아니다.",
        "Roy T. Bennett", 6204,
        ["선택", "자유", "자신감"],
        ["인생의 선택", "자신감이 없을 때"],
    ),
    (
        "Love does not consist of gazing at each other, but in looking outward together in the same direction.",
        "사랑은 서로를 바라보는 것이 아니라, 함께 같은 방향을 바라보는 것이다.",
        "Antoine de Saint-Exupéry", 6202,
        ["사랑", "관계"],
        ["사랑의 본질을 고민할 때", "관계의 소중함"],
    ),
    (
        "Time flies like an arrow; fruit flies like a banana.",
        "시간은 화살처럼 날아간다. 과일파리는 바나나를 좋아한다.",
        "Anthony G. Oettinger", 6192,
        ["유머", "시간"],
        ["웃음이 필요할 때"],
    ),
    (
        "When a man gives his opinion, he's a man. When a woman gives her opinion, she's a bitch.",
        "남자가 의견을 말하면 남자답다고 하고, 여자가 의견을 말하면 까다롭다고 한다.",
        "Bette Davis", 6173,
        ["용기", "자유"],
        ["용기가 필요할 때", "새로운 관점이 필요할 때"],
    ),
    (
        "Even if you cannot change all the people around you, you can change the people you choose to be around.",
        "주변의 모든 사람을 바꿀 수는 없지만, 함께하기로 선택한 사람은 바꿀 수 있다.",
        "Roy T. Bennett", 6160,
        ["관계", "선택"],
        ["관계가 어려울 때", "인생의 선택"],
    ),
    (
        "Being crazy isn't enough.",
        "미쳐있는 것만으로는 충분하지 않다.",
        "Dr. Seuss", 6147,
        ["유머", "창의성"],
        ["웃음이 필요할 때"],
    ),
    (
        "To be a Christian means to forgive the inexcusable because God has forgiven the inexcusable in you.",
        "기독교인이 된다는 것은 용서할 수 없는 것을 용서하는 것이다. 신이 당신 안의 용서할 수 없는 것을 용서했기 때문이다.",
        "C.S. Lewis", 6141,
        ["겸손", "관계"],
        ["관계가 어려울 때"],
    ),
    (
        "By three methods we may learn wisdom: First, by reflection, which is noblest; Second, by imitation, which is easiest; and third by experience, which is the bitterest.",
        "세 가지 방법으로 지혜를 배울 수 있다. 첫째 성찰, 가장 고귀하다. 둘째 모방, 가장 쉽다. 셋째 경험, 가장 쓰라리다.",
        "Confucius", 6124,
        ["지혜", "학습", "자기성찰"],
        ["배움의 자세", "자기 성찰"],
    ),
    (
        "I cannot remember the books I've read any more than the meals I have eaten; even so, they have made me.",
        "내가 먹은 식사를 기억할 수 없듯이 읽은 책들도 기억할 수 없다. 그래도 그것들이 나를 만들었다.",
        "Ralph Waldo Emerson", 6113,
        ["학습", "성장", "지식"],
        ["배움의 자세"],
    ),
    (
        "I like living. I have sometimes been wildly, despairingly, acutely miserable, racked with sorrow; but through it all I still know quite certainly that just to be alive is a grand thing.",
        "나는 사는 것이 좋다. 때로는 미칠 듯이, 절망적으로, 극심하게 비참했지만, 그 모든 것을 겪고도 살아 있다는 것만으로도 위대하다는 것을 확실히 안다.",
        "Agatha Christie", 6095,
        ["인생", "희망", "감사"],
        ["절망적일 때", "감사할 때"],
    ),
    (
        "Reading was my escape and my comfort, my consolation, my stimulant of choice: reading for the pure pleasure of it.",
        "독서는 나의 도피이자 위안이었고, 나의 위로이자 내가 선택한 자극제였다. 순수한 즐거움을 위한 독서.",
        "Paul Auster", 6092,
        ["학습", "지식"],
        ["배움의 자세"],
    ),
]


def get_impact_score(likes):
    if likes > 100000:
        return 10
    elif likes > 50000:
        return 9
    elif likes > 30000:
        return 8
    elif likes > 20000:
        return 7
    elif likes > 10000:
        return 6
    elif likes > 5000:
        return 5
    else:
        return 4


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # 기존 저자 캐시
    cur.execute("SELECT id, name FROM authors")
    existing_authors = {row[1]: row[0] for row in cur.fetchall()}

    saved = 0
    skipped_fictional = 0
    skipped_dup = 0

    for q in QUOTES_DATA:
        text_original = q[0]
        text_ko = q[1]
        author_goodreads = q[2]
        likes = q[3]
        kw_names = q[4]
        sit_names = q[5]

        # 소설/영화 대사 제외
        if text_original in FICTIONAL_EXCLUSIONS:
            skipped_fictional += 1
            continue

        # 중복 체크 (text_original 기준)
        cur.execute(
            "SELECT 1 FROM quotes WHERE text_original = %s LIMIT 1",
            (text_original,),
        )
        if cur.fetchone():
            skipped_dup += 1
            continue

        # 저자 매칭
        author_ko = AUTHOR_NAME_MAP.get(author_goodreads, None)
        author_id = None

        if author_ko and author_ko in existing_authors:
            author_id = existing_authors[author_ko]
        elif author_ko is None:
            # 매핑이 없는 경우, DB에서 직접 검색해본다
            # 여기서는 새로 생성
            author_id = _create_author(cur, author_goodreads, existing_authors)
        else:
            # 매핑은 있지만 DB에 없는 경우
            author_id = _create_author_with_ko_name(
                cur, author_ko, author_goodreads, existing_authors
            )

        # 키워드/상황 JSONB 및 ID 배열
        keyword_ids = [KW[k] for k in kw_names if k in KW]
        situation_ids = [SIT[s] for s in sit_names if s in SIT]
        keywords_jsonb = json.dumps(
            [{"id": KW[k], "name": k} for k in kw_names if k in KW],
            ensure_ascii=False,
        )
        situation_jsonb = json.dumps(
            [{"id": SIT[s], "name": s} for s in sit_names if s in SIT],
            ensure_ascii=False,
        )

        impact_score = get_impact_score(likes)
        quote_id = str(uuid.uuid4())

        cur.execute(
            """INSERT INTO quotes
            (id, text, text_original, original_language, author_id,
             keywords, situation, keyword_ids, situation_ids,
             status, source_reliability, impact_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                quote_id,
                text_ko,
                text_original,
                "en",
                author_id,
                keywords_jsonb,
                situation_jsonb,
                keyword_ids,
                situation_ids,
                "draft",
                "attributed",
                impact_score,
            ),
        )
        saved += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"저장 완료: {saved}개")
    print(f"소설/영화 대사 제외: {skipped_fictional}개")
    print(f"중복 스킵: {skipped_dup}개")
    print(f"총 처리: {saved + skipped_fictional + skipped_dup}개")


# ── 저자 생성 헬퍼 ──

# Goodreads 이름 → (한국어 이름, nationality, birth_year, profession, field)
NEW_AUTHOR_INFO = {
    "Bernard M. Baruch": ("버나드 바루크", "US", 1870, "정치가", "정치"),
    "William W. Purkey": ("윌리엄 퍼키", "US", 1929, "학자", "심리학"),
    "Dr. Seuss": ("닥터 수스", "US", 1904, "작가", "문학"),
    "Bill Keane": ("빌 킨", "US", 1922, "예술가", "예술"),
    "Robert A. Heinlein": ("로버트 하인라인", "US", 1907, "작가", "문학"),
    "Jorge Luis Borges": ("호르헤 루이스 보르헤스", "AR", 1899, "작가", "문학"),
    "Anais Nin": ("아나이스 닌", "FR", 1903, "작가", "문학"),
    "Douglas Adams": ("더글러스 애덤스", "GB", 1952, "작가", "문학"),
    "Bob Marley": ("밥 말리", "JM", 1945, "음악가", "예술"),
    "Alfred Tennyson": ("앨프레드 테니슨", "GB", 1809, "시인", "문학"),
    "George Carlin": ("조지 칼린", "US", 1937, "코미디언", "예술"),
    "Marianne Williamson": ("마리안 윌리엄슨", "US", 1952, "작가", "종교"),
    "E.E. Cummings": ("E.E. 커밍스", "US", 1894, "시인", "문학"),
    "Alfred Lord Tennyson": ("앨프레드 테니슨", "GB", 1809, "시인", "문학"),
    "Roald Dahl": ("로알드 달", "GB", 1916, "작가", "문학"),
    "Frederick Douglass": ("프레더릭 더글러스", "US", 1818, "사상가", "정치"),
    "Jack Kerouac": ("잭 케루악", "US", 1922, "작가", "문학"),
    "Aldous Huxley": ("올더스 헉슬리", "GB", 1894, "작가", "문학"),
    "Marlene Dietrich": ("마를레네 디트리히", "DE", 1901, "배우", "예술"),
    "Margaret Mead": ("마거릿 미드", "US", 1901, "학자", "역사"),
    "Nicholas Klein": ("니콜라스 클라인", "US", 1870, "사상가", "정치"),
    "Mary Oliver": ("메리 올리버", "US", 1935, "시인", "문학"),
    "Laurel Thatcher Ulrich": ("로렐 대처 울리치", "US", 1938, "학자", "역사"),
    "Charles Bukowski": ("찰스 부코스키", "US", 1920, "시인", "문학"),
    "Edgar Allan Poe": ("에드거 앨런 포", "US", 1809, "작가", "문학"),
    "Roy T. Bennett": ("로이 T. 베넷", "US", 1939, "작가", "문학"),
    "Ellen DeGeneres": ("엘런 드제너러스", "US", 1958, "코미디언", "예술"),
    "Nora Ephron": ("노라 에프론", "US", 1941, "작가", "문학"),
    "John Steinbeck": ("존 스타인벡", "US", 1902, "작가", "문학"),
    "Jhumpa Lahiri": ("줌파 라히리", "GB", 1967, "작가", "문학"),
    "Sylvia Plath": ("실비아 플라스", "US", 1932, "시인", "문학"),
    "Joseph Brodsky": ("요시프 브로츠키", "RU", 1940, "시인", "문학"),
    "Anthony G. Oettinger": ("앤서니 외팅거", "US", 1929, "학자", "기술"),
    "Bette Davis": ("베트 데이비스", "US", 1908, "배우", "예술"),
    "Jane Austen": ("제인 오스틴", "GB", 1775, "작가", "문학"),
    "Daphne Rae": ("다프네 레이", "IN", 1928, "작가", "종교"),
    "Agatha Christie": ("아가사 크리스티", "GB", 1890, "작가", "문학"),
    "Paul Auster": ("폴 오스터", "US", 1947, "작가", "문학"),
    "Frank Zappa": ("프랭크 자파", "US", 1940, "음악가", "예술"),
    "Henry Ward Beecher": ("헨리 워드 비처", "US", 1813, "종교 지도자", "종교"),
    "W.C. Fields": ("W.C. 필즈", "US", 1880, "코미디언", "예술"),
}

PROFESSION_IDS = {
    "기업가": "be2dc0cc-9355-4002-b107-3a71d5c2e399",
    "방송인": "9805bd7c-ea4f-4cd6-99e4-2beee27d5e8b",
    "언론인": "dfcc8c25-7904-4401-bcd5-e6f95bf0dbc1",
    "운동선수": "fd419307-4524-4693-b7da-f4802084d2ce",
    "배우": "fc462f5c-c84d-4b58-8b3c-f82c30665d57",
    "시인": "52fd5077-365b-4382-bdce-17ebcd07c053",
    "예술가": "b878f2bb-a956-4cca-acd5-11682156eebf",
    "음악가": "7a9e846f-d79a-439a-bc55-13ac3ee80030",
    "작가": "ba8f678c-3528-4e27-9315-a903a8ee3d1d",
    "코미디언": "55350bb7-a161-4684-871a-b08f0a533b1e",
    "패션 디자이너": "d74937c1-0f0c-4dfd-8e43-23ab39ef6b79",
    "종교 지도자": "ccd25c59-4332-411e-bf7f-00d8286c7075",
    "경영학자": "e00cdfb1-2bf0-4b4e-ba05-e0e85bb04c18",
    "사상가": "2879b5ad-56ae-4921-ab9b-2c59481a251a",
    "심리학자": "ad212b15-b763-41ae-9356-78b18d302e2c",
    "역사가": "93507c6f-d6f0-486a-b452-ad2c6038f099",
    "철학자": "f154881f-80c2-4cea-9a1d-8ba3fbcd556f",
    "학자": "c4c4aa24-dffc-4a64-a145-ec7cf54ded35",
    "과학자": "2aa07165-7f1f-4f2d-971f-4832e10f39de",
    "물리학자": "7ad6e70e-c4f9-43e4-b64c-92fde8b03413",
    "발명가": "a66b8cc4-aaa5-4cbc-a61a-ab1aebfbc4e4",
    "수학자": "1472f438-8f97-4519-878e-18d813ebc3d2",
    "의사": "1781b3b6-ee77-4142-b338-2ae2f5713846",
    "군인": "79b80e10-ca64-4ffe-909d-ef445f69a09e",
    "정치가": "095a6cf0-cded-41fe-8ef0-c3d4e0180e60",
}

FIELD_IDS = {
    "경영": "b7cdaf72-500a-4b7e-a29b-46b098a1d59b",
    "과학": "b29615ad-0dbf-4e0e-b920-144aa551c9ca",
    "기술": "bd38c164-3a54-4054-835c-198365db65b3",
    "문학": "2cdd8ad7-0a23-4e64-b93b-c992533242c5",
    "문화": "db2c03fe-25e5-44c4-842a-a2e94761a574",
    "심리학": "f978462c-ec91-4bad-b98a-0a7eac2110f9",
    "역사": "8088f2b8-cf47-4ef8-98fe-51d5f0bd9c1f",
    "예술": "adf3f414-6362-4c16-b5e1-6cfd0b91bca6",
    "정치": "b0d53c7d-0cbe-476f-b3cb-ec06fff8f8e3",
    "종교": "3af453e5-eca6-403e-ba5f-17efc4f689f6",
    "철학": "f9bf4bf1-12a1-44e6-8a68-49c738a7b5e2",
}


def _create_author(cur, goodreads_name, existing_authors):
    """새 저자 생성 (Goodreads 이름으로)"""
    info = NEW_AUTHOR_INFO.get(goodreads_name)
    if info:
        ko_name, nat, birth, prof_name, field_name = info
    else:
        # 정보를 알 수 없는 경우 기본값
        ko_name = goodreads_name
        nat = "US"
        birth = None
        prof_name = "작가"
        field_name = "문학"

    author_id = str(uuid.uuid4())
    prof_id = PROFESSION_IDS.get(prof_name)
    field_id = FIELD_IDS.get(field_name)

    # 한국어 이름으로 이미 존재하는지 재확인
    if ko_name in existing_authors:
        return existing_authors[ko_name]

    cur.execute(
        """INSERT INTO authors (id, name, nationality, birth_year, profession_id, field_id)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        (author_id, ko_name, nat, birth, prof_id, field_id),
    )
    existing_authors[ko_name] = author_id
    print(f"  새 저자 생성: {ko_name} ({goodreads_name})")
    return author_id


def _create_author_with_ko_name(cur, ko_name, goodreads_name, existing_authors):
    """한국어 이름은 정해져 있지만 DB에 없는 경우"""
    info = NEW_AUTHOR_INFO.get(goodreads_name)
    if info:
        _, nat, birth, prof_name, field_name = info
    else:
        nat = "US"
        birth = None
        prof_name = "작가"
        field_name = "문학"

    author_id = str(uuid.uuid4())
    prof_id = PROFESSION_IDS.get(prof_name)
    field_id = FIELD_IDS.get(field_name)

    cur.execute(
        """INSERT INTO authors (id, name, nationality, birth_year, profession_id, field_id)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        (author_id, ko_name, nat, birth, prof_id, field_id),
    )
    existing_authors[ko_name] = author_id
    print(f"  새 저자 생성: {ko_name} ({goodreads_name})")
    return author_id


if __name__ == "__main__":
    main()
