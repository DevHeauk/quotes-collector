"""
Goodreads Popular Quotes (pages 21~40) -> PostgreSQL goodreads_popularity 테이블 저장.

수집 일시: 2026-04-12
소설 속 대화는 제외하고, 독립적인 명언/격언만 포함.
"""

import uuid
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "user": "youheaukjun",
    "database": "quotes_db",
}

# likes가 None인 항목은 페이지 마지막 항목으로 likes 수 파싱 실패한 경우 -> 제외하지 않고 0으로 처리
# 소설 속 대화/캐릭터 대사는 수동으로 필터링하여 제외함

QUOTES_DATA = [
    # ===== Page 21 =====
    ("I want to stand as close to the edge as I can without going over.", "Kurt Vonnegut Jr.", 7568),
    ("God created war so that Americans would learn geography.", "Mark Twain", 7543),
    ("A human being is a part of the whole called by us universe...", "Albert Einstein", 7522),
    ("She was a girl who knew how to be happy even when she was sad.", "Marilyn Monroe", 7460),
    ("What is a friend? A single soul dwelling in two bodies.", "Aristotle", 7453),
    ("Those who find ugly meanings in beautiful things are corrupt...", "Oscar Wilde", 7450),
    ("Where is human nature so weak as in the bookstore?", "Henry Ward Beecher", 7419),
    ("If at first you don't succeed, try, try again. Then quit.", "W.C. Fields", 7411),
    ("The very essence of romance is uncertainty.", "Oscar Wilde", 7399),
    ("Take responsibility of your own happiness, never put it in other people's hands.", "Roy T. Bennett", 7393),
    ("Nobody realizes that some people expend tremendous energy merely to be normal.", "Albert Camus", 7375),
    ("Accept yourself, love yourself, and keep moving forward.", "Roy T. Bennett", 7369),
    ("Waiting is painful. Forgetting is painful. But not knowing which to do is the worst kind of suffering.", "Paulo Coelho", 7363),
    ("I cannot live without books.", "Thomas Jefferson", 7347),
    ("I can't imagine a man really enjoying a book and reading it only once.", "C.S. Lewis", 7331),
    ("The unexamined life is not worth living.", "Socrates", 7292),
    ("There is always some madness in love. But there is also always some reason in madness.", "Friedrich Nietzsche", 7290),

    # ===== Page 22 =====
    ("People aren't either wicked or noble. They're like chef's salads, with good things and bad things chopped and mixed together in a vinaigrette of confusion and conflict.", "Lemony Snicket", 7213),
    ("what matters most is how well you walk through the fire", "Charles Bukowski", 7212),
    ("Never be bullied into silence. Never allow yourself to be made a victim. Accept no one's definition of your life; define yourself.", "Robert Frost", 7197),
    ("Love is so short, forgetting is so long.", "Pablo Neruda", 7174),
    ("Everything in the world is about sex except sex. Sex is about power.", "Oscar Wilde", 7172),
    ("I can be changed by what happens to me. But I refuse to be reduced by it.", "Maya Angelou", 7163),
    ("Respect other people's feelings. It might mean nothing to you, but it could mean everything to them.", "Roy T. Bennett", 7162),
    ("Man is least himself when he talks in his own person. Give him a mask, and he will tell you the truth.", "Oscar Wilde", 7144),
    ("Should I kill myself, or have a cup of coffee?", "Albert Camus", 7143),
    ("If you can't fly then run, if you can't run then walk, if you can't walk then crawl, but whatever you do you have to keep moving forward.", "Martin Luther King Jr.", 7099),
    ("Try not to become a man of success. Rather become a man of value.", "Albert Einstein", 7087),
    ("We are all different. Don't judge, understand instead.", "Roy T. Bennett", 7025),
    ("I generally avoid temptation unless I can't resist it.", "Mae West", 7022),
    ("It is not in the stars to hold our destiny but in ourselves.", "William Shakespeare", 7005),

    # ===== Page 23 =====
    ("Either write something worth reading or do something worth writing.", "Benjamin Franklin", 6900),
    ("I love to see a young girl go out and grab the world by the lapels. Life's a bitch. You've got to go out and kick ass.", "Maya Angelou", 6898),
    ("I was gratified to be able to answer promptly, and I did. I said I didn't know.", "Mark Twain", 6894),
    ("Accept who you are. Unless you're a serial killer.", "Ellen DeGeneres", 6885),
    ("Stop acting so small. You are the universe in ecstatic motion.", "Rumi", 6872),
    ("Two possibilities exist: either we are alone in the Universe or we are not. Both are equally terrifying.", "Arthur C. Clarke", 6861),
    ("You must have chaos within you to give birth to a dancing star.", "Friedrich Nietzsche", 6855),
    ("Turn your wounds into wisdom.", "Oprah Winfrey", 6854),
    ("The important thing is not to stop questioning. Curiosity has its own reason for existence.", "Albert Einstein", 6831),
    ("Life is too short to waste your time on people who don't respect, appreciate, and value you.", "Roy T. Bennett", 6813),
    ("Kiss me, and you will see how important I am.", "Sylvia Plath", 6810),
    ("No tears in the writer, no tears in the reader. No surprise in the writer, no surprise in the reader.", "Robert Frost", 6803),
    ("When you have eliminated all which is impossible, then whatever remains, however improbable, must be the truth.", "Arthur Conan Doyle", 6792),

    # ===== Page 24 =====
    ("Painting is poetry that is seen rather than felt, and poetry is painting that is felt rather than seen.", "Leonardo da Vinci", 6752),
    ("The simple things are also the most extraordinary things, and only the wise can see them.", "Paulo Coelho", 6740),
    ("I wonder how many people I've looked at all my life and never seen.", "John Steinbeck", 6733),
    ("It is said that your life flashes before your eyes just before you die. That is true, it's called Life.", "Terry Pratchett", 6730),
    ("You gain strength, courage and confidence by every experience in which you really stop to look fear in the face.", "Eleanor Roosevelt", 6709),
    ("Live the Life of Your Dreams: Be brave enough to live the life of your dreams according to your vision and purpose.", "Roy T. Bennett", 6701),
    ("Everyone sees what you appear to be, few experience what you really are.", "Niccolò Machiavelli", 6693),
    ("What happens when people open their hearts? They get better.", "Haruki Murakami", 6689),
    ("Stories of imagination tend to upset those without one.", "Terry Pratchett", 6689),
    ("Love doesn't just sit there, like a stone, it has to be made, like bread; remade all the time, made new.", "Ursula K. Le Guin", 6669),
    ("Each day means a new twenty-four hours. Each day means everything's possible again.", "Marie Lu", 6678),

    # ===== Page 25 =====
    ("Above all, be the heroine of your life, not the victim.", "Nora Ephron", 6526),
    ("What matters in life is not what happens to you but what you remember and how you remember it.", "Gabriel García Márquez", 6516),
    ("But luxury has never appealed to me, I like simple things, books, being alone, or with somebody who understands.", "Daphne du Maurier", 6493),
    ("Whatever it is you're seeking won't come in the form you're expecting.", "Haruki Murakami", 6487),
    ("Why fit in when you were born to stand out?", "Dr. Seuss", 6475),
    ("I lie to myself all the time. But I never believe me.", "S.E. Hinton", 6468),
    ("I have great faith in fools - self-confidence my friends will call it.", "Edgar Allan Poe", 6467),
    ("That's the thing about books. They let you travel without moving your feet.", "Jhumpa Lahiri", 6463),
    ("Don't waste your time in anger, regrets, worries, and grudges. Life is too short to be unhappy.", "Roy T. Bennett", 6448),
    ("Life is a disease: sexually transmitted, and invariably fatal.", "Neil Gaiman", 6446),
    ("You must stay drunk on writing so reality cannot destroy you.", "Ray Bradbury", 6446),
    ("One day, in retrospect, the years of struggle will strike you as the most beautiful.", "Sigmund Freud", 6423),
    ("There are worse crimes than burning books. One of them is not reading them.", "Joseph Brodsky", 6412),
    ("I do not fear death. I had been dead for billions and billions of years before I was born, and had not suffered the slightest inconvenience from it.", "Mark Twain", 6397),
    ("I think God, in creating man, somewhat overestimated his ability.", "Oscar Wilde", 6387),
    ("If you love somebody, let them go, for if they return, they were always yours. If they don't, they never were.", "Kahlil Gibran", 6386),
    ("Remember: the time you feel lonely is the time you most need to be by yourself. Life's cruelest irony.", "Douglas Coupland", 6383),
    ("Prayer is not asking. It is a longing of the soul. It is daily admission of one's weakness. It is better in prayer to have a heart without words than words without a heart.", "Mahatma Gandhi", 6427),
    ("Everyone should be able to do one card trick, tell two jokes, and recite three poems, in case they are ever trapped in an elevator.", "Lemony Snicket", 6427),

    # ===== Page 26 =====
    ("There are three things all wise men fear: the sea in storm, a night with no moon, and the anger of a gentle man.", "Patrick Rothfuss", 6328),
    ("You cannot swim for new horizons until you have courage to lose sight of the shore.", "William Faulkner", 6319),
    ("I never travel without my diary. One should always have something sensational to read in the train.", "Oscar Wilde", 6305),
    ("If you are going through hell, keep going.", "Winston S. Churchill", 6293),
    ("Education is the most powerful weapon which you can use to change the world.", "Nelson Mandela", 6287),
    ("It isn't what you have or who you are or where you are or what you are doing that makes you happy or unhappy. It is what you think about it.", "Dale Carnegie", 6285),
    ("Nothing of me is original. I am the combined effort of everyone I've ever known.", "Chuck Palahniuk", 6273),
    ("Angry people are not always wise.", "Jane Austen", 6257),
    ("As usual, there is a great woman behind every idiot.", "John Lennon", 6251),
    ("I have found the paradox, that if you love until it hurts, there can be no more hurt, only more love.", "Daphne Rae", 6247),

    # ===== Page 27 =====
    ("Don't let the expectations and opinions of other people affect your decisions. It's your life, not theirs.", "Roy T. Bennett", 6204),
    ("Love does not consist of gazing at each other, but in looking outward together in the same direction.", "Antoine de Saint-Exupéry", 6202),
    ("Time flies like an arrow; fruit flies like a banana.", "Anthony G. Oettinger", 6192),
    ("When a man gives his opinion, he's a man. When a woman gives her opinion, she's a bitch.", "Bette Davis", 6173),
    ("Even if you cannot change all the people around you, you can change the people you choose to be around.", "Roy T. Bennett", 6160),
    ("What I want is to be needed. What I need is to be indispensable to somebody.", "Chuck Palahniuk", 6158),
    ("Being crazy isn't enough.", "Dr. Seuss", 6147),
    ("To be a Christian means to forgive the inexcusable because God has forgiven the inexcusable in you.", "C.S. Lewis", 6141),
    ("By three methods we may learn wisdom: First, by reflection, which is noblest; Second, by imitation, which is easiest; and third by experience, which is the bitterest.", "Confucius", 6124),
    ("It was love at first sight, at last sight, at ever and ever sight.", "Vladimir Nabokov", 6119),
    ("I cannot remember the books I've read any more than the meals I have eaten; even so, they have made me.", "Ralph Waldo Emerson", 6113),
    ("I like living. I have sometimes been wildly, despairingly, acutely miserable, racked with sorrow; but through it all I still know quite certainly that just to be alive is a grand thing.", "Agatha Christie", 6095),
    ("Reading was my escape and my comfort, my consolation, my stimulant of choice: reading for the pure pleasure of it.", "Paul Auster", 6092),
    ("I don't want to die without any scars.", "Chuck Palahniuk", 6085),
    ("You cannot control the behavior of others, but you can always choose how you respond to it.", "Roy T. Bennett", 6077),
    ("Every child is an artist. The problem is how to remain an artist once he grows up.", "Pablo Picasso", 6075),
    ("To define is to limit.", "Oscar Wilde", 6072),
    ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt", 6063),
    ("A girl should be two things: classy and fabulous.", "Coco Chanel", 6059),

    # ===== Page 28 =====
    ("Loyalty to country ALWAYS. Loyalty to government, when it deserves it.", "Mark Twain", 6016),
    ("You have power over your mind - not outside events. Realize this, and you will find strength.", "Marcus Aurelius", 6015),
    ("And, in the end the love you take is equal to the love you make.", "Paul McCartney", 6009),
    ("I love people who make me laugh. I honestly think it's the thing I like most, to laugh. It cures a multitude of ills. It's probably the most important thing in a person.", "Audrey Hepburn", 6009),
    ("Be patient toward all that is unsolved in your heart and try to love the questions themselves, like locked rooms and like books that are now written in a very foreign tongue.", "Rainer Maria Rilke", 6004),
    ("Don't tell me the moon is shining; show me the glint of light on broken glass.", "Anton Chekhov", 5990),
    ("Books are like mirrors: if a fool looks in, you cannot expect a genius to look out.", "J.K. Rowling", 5986),
    ("More smiling, less worrying. More compassion, less judgment. More blessed, less stressed. More love, less hate.", "Roy T. Bennett", 5984),
    ("My tastes are simple: I am easily satisfied with the best.", "Winston S. Churchill", 5980),
    ("I will not say: do not weep; for not all tears are an evil.", "J.R.R. Tolkien", 5944),
    ("And now these three remain: faith, hope and love. But the greatest of these is love.", "Anonymous", 5934),
    ("You do not write your life with words...You write it with actions. What you think is not important. It is only important what you do.", "Patrick Ness", 5926),
    ("Simplicity, patience, compassion. These three are your greatest treasures.", "Lao Tzu", 5920),

    # ===== Page 29 =====
    ("He who has a why to live for can bear almost any how.", "Friedrich Nietzsche", 5881),
    ("In the case of good books, the point is not to see how many of them you can get through, but rather how many can get through to you.", "Mortimer J. Adler", 5878),
    ("She generally gave herself very good advice, (though she very seldom followed it).", "Lewis Carroll", 5878),
    ("She is too fond of books, and it has turned her brain.", "Louisa May Alcott", 5877),
    ("The fact that we live at the bottom of a deep gravity well, on the surface of a gas covered planet going around a nuclear fireball 90 million miles away and think this to be normal is obviously some indication of how skewed our perspective tends to be.", "Douglas Adams", 5866),
    ("There are too many books I haven't read, too many places I haven't seen, too many memories I haven't kept long enough.", "Irwin Shaw", 5865),
    ("People generally see what they look for, and hear what they listen for.", "Harper Lee", 5863),
    ("Sometimes people don't want to hear the truth because they don't want their illusions destroyed.", "Friedrich Nietzsche", 5862),
    ("What you seek is seeking you.", "Mawlana Jalal-al-Din Rumi", 5857),
    ("Let there be spaces in your togetherness, And let the winds of the heavens dance between you. Love one another but make not a bond of love: Let it rather be a moving sea between the shores of your souls.", "Kahlil Gibran", 5851),
    ("I was never really insane except upon occasions when my heart was touched.", "Edgar Allan Poe", 5834),
    ("Life should not be a journey to the grave with the intention of arriving safely in a pretty and well preserved body, but rather to skid in broadside in a cloud of smoke, thoroughly used up, totally worn out, and loudly proclaiming \"Wow! What a Ride!\"", "Hunter S. Thompson", 5830),
    ("The nicest thing for me is sleep, then at least I can dream.", "Marilyn Monroe", 5807),
    ("The most important things are the hardest to say. They are the things you get ashamed of, because words diminish them -- words shrink things that seemed limitless when they were in your head to no more than living size when they're brought out.", "Stephen King", 5805),
    ("I am not sure exactly what heaven will be like, but I know that when we die and it comes time for God to judge us, He will not ask, 'How many good things have you done in your life?' rather He will ask, 'How much love did you put into what you did?'", "Mother Teresa", 5778),
    ("The worst part of holding the memories is not the pain. It's the loneliness of it. Memories need to be shared.", "Lois Lowry", 5774),

    # ===== Page 30 =====
    ("Books are the mirrors of the soul.", "Virginia Woolf", 5695),
    ("Everyone seems to have a clear idea of how other people should lead their lives, but none about his or her own.", "Paulo Coelho", 5691),
    ("Fantasy is escapist, and that is its glory. If a soldier is imprisioned by the enemy, don't we consider it his duty to escape?", "J.R.R. Tolkien", 5689),
    ("I think... if it is true that there are as many minds as there are heads, then there are as many kinds of love as there are hearts.", "Leo Tolstoy", 5686),
    ("What is hell? I maintain that it is the suffering of being unable to love.", "Fyodor Dostoevsky", 5681),
    ("Love is a fire. But whether it is going to warm your hearth or burn down your house, you can never tell.", "Joan Crawford", 5676),
    ("Unbeing dead isn't being alive.", "E.E. Cummings", 5671),
    ("Don't judge each day by the harvest you reap but by the seeds that you plant.", "Robert Louis Stevenson", 5660),
    ("Life's under no obligation to give us what we expect.", "Margaret Mitchell", 5649),
    ("The past is a place of reference, not a place of residence; the past is a place of learning, not a place of living.", "Roy T. Bennett", 5645),
    ("Nobody likes being alone that much. I don't go out of my way to make friends, that's all. It just leads to disappointment.", "Haruki Murakami", 5639),
    ("Nobody can hurt me without my permission.", "Mahatma Gandhi", 5635),

    # ===== Page 31 =====
    ("Find what you love and let it kill you.", "Kinky Friedman", 5562),
    ("The best and most beautiful things cannot be seen or touched.", "Helen Keller", 5558),
    ("The most painful thing is losing yourself in loving someone too much.", "Ernest Hemingway", 5553),
    ("Words are the most powerful drug used by mankind.", "Rudyard Kipling", 5550),
    ("The truth does not change according to our ability to stomach it.", "Flannery O'Connor", 5546),
    ("None of us really changes over time. We only become more fully what we are.", "Anne Rice", 5541),
    ("Life becomes easier when we can see the good in other people.", "Roy T. Bennett", 5535),
    ("Let everything happen to you. No feeling is final.", "Rainer Maria Rilke", 5528),
    ("Without deviation from the norm, progress is not possible.", "Frank Zappa", 5525),
    ("Let us be grateful to people who make us happy.", "Marcel Proust", 5519),
    ("It is amazing how complete is the delusion that beauty is goodness.", "Leo Tolstoy", 5518),
    ("The world we created is a process of our thinking.", "Albert Einstein", 5514),
    ("Wrinkles should indicate where the smiles have been.", "Mark Twain", 5506),
    ("Let no man pull you so low as to hate him.", "Martin Luther King Jr.", 5481),
    ("Music was my refuge. I could crawl into the space between the notes.", "Maya Angelou", 5479),

    # ===== Page 32 =====
    ("Everything is possible. The impossible just takes longer.", "Dan Brown", 5449),
    ("Nothing is so painful to the human mind as a great and sudden change.", "Mary Wollstonecraft Shelley", 5446),
    ("Blessed is he who expects nothing, for he shall never be disappointed.", "Alexander Pope", 5434),
    ("Nowadays people know the price of everything and the value of nothing.", "Oscar Wilde", 5431),
    ("It's not denial. I'm just selective about the reality I accept.", "Bill Watterson", 5430),
    ("Friendship is the hardest thing in the world to explain. It's not something you learn in school. But if you haven't learned the meaning of friendship, you really haven't learned anything.", "Muhammad Ali", 5428),
    ("Why, sometimes I've believed as many as six impossible things before breakfast.", "Lewis Carroll", 5426),
    ("Do what is right, not what is easy nor what is popular.", "Roy T. Bennett", 5422),
    ("None but ourselves can free our minds.", "Bob Marley", 5420),
    ("Do not fear to be eccentric in opinion, for every opinion now accepted was once eccentric.", "Bertrand Russell", 5417),
    ("If you want to be happy, do not dwell in the past, do not worry about the future, focus on living fully in the present.", "Roy T. Bennett", 5401),

    # ===== Page 33 =====
    ("It is the time you have wasted for your rose that makes your rose so important.", "Antoine de Saint-Exupéry", 5355),
    ("Dwell on the beauty of life. Watch the stars, and see yourself running with them.", "Marcus Aurelius", 5355),
    ("This moment will just be another story someday.", "Stephen Chbosky", 5344),
    ("When love is not madness it is not love.", "Pedro Calderon de la Barca", 5335),
    ("The journey of a thousand miles begins with a single step.", "Lao Tzu", 5329),
    ("All I ever wanted was to reach out and touch another human being not just with my hands but with my heart.", "Tahereh Mafi", 5320),
    ("Clouds come floating into my life, no longer to carry rain or usher storm, but to add color to my sunset sky.", "Rabindranath Tagore", 5315),
    ("God has no religion.", "Mahatma Gandhi", 5306),
    ("We are not necessarily doubting that God will do the best for us; we are wondering how painful the best will turn out to be.", "C.S. Lewis", 5303),

    # ===== Page 34 =====
    ("Who said nights were for sleep?", "Marilyn Monroe", 5249),
    ("The most beautiful people we have known are those who have known defeat, known suffering, known struggle, known loss, and have found their way out of the depths.", "Elisabeth Kübler-Ross", 5246),
    ("Sometimes our light goes out, but is blown again into instant flame by an encounter with another human being.", "Albert Schweitzer", 5222),
    ("Keep Going. Your hardest times often lead to the greatest moments of your life.", "Roy T. Bennett", 5216),
    ("When a new day begins, dare to smile gratefully.", "Steve Maraboli", 5216),
    ("It is more fun to talk with someone who doesn't use long, difficult words.", "A.A. Milne", 5205),
    ("When life gives you lemons, squirt someone in the eye.", "Cathy Guisewite", 5201),
    ("There may be times when we are powerless to prevent injustice, but there must never be a time when we fail to protest.", "Elie Wiesel", 5180),
    ("Beware; for I am fearless, and therefore powerful.", "Mary Wollstonecraft Shelley", 5176),
    ("The things you do for yourself are gone when you are gone, but the things you do for others remain as your legacy.", "Kalu Ndukwe Kalu", 5174),

    # ===== Page 35 =====
    ("The true soldier fights not because he hates what is in front of him, but because he loves what is behind him.", "G.K. Chesterton", 5137),
    ("Knowing others is intelligence; knowing yourself is true wisdom. Mastering others is strength; mastering yourself is true power.", "Lao Tzu", 5137),
    ("We know what we are, but not what we may be.", "William Shakespeare", 5119),
    ("Think left and think right and think low and think high. Oh, the thinks you can think up if only you try!", "Dr. Seuss", 5118),
    ("Everybody is identical in their secret unspoken belief that way deep down they are different from everyone else.", "David Foster Wallace", 5112),
    ("There are no facts, only interpretations.", "Friedrich Nietzsche", 5111),
    ("Women who seek to be equal with men lack ambition.", "Timothy Leary", 5111),
    ("I wanted the whole world or nothing.", "Charles Bukowski", 5108),
    ("I don't want to be at the mercy of my emotions. I want to use them, to enjoy them, and to dominate them.", "Oscar Wilde", 5100),

    # ===== Page 36 =====
    ("A poem begins as a lump in the throat, a sense of wrong, a homesickness, a lovesickness.", "Robert Frost", 5069),
    ("A painter should begin every canvas with a wash of black, because all things in nature are dark except where exposed by the light.", "Leonardo da Vinci", 5058),
    ("The only way to find true happiness is to risk being completely cut open.", "Chuck Palahniuk", 5054),
    ("There is no surer foundation for a beautiful friendship than a mutual taste in literature.", "P.G. Wodehouse", 5047),
    ("If I were not a physicist, I would probably be a musician. I often think in music. I live my daydreams in music.", "Albert Einstein", 5045),
    ("Even the darkest night will end and the sun will rise.", "Victor Hugo", 5044),
    ("Live to the point of tears.", "Albert Camus", 5034),
    ("Poets have been mysteriously silent on the subject of cheese.", "G.K. Chesterton", 5019),
    ("There is a stubbornness about me that never can bear to be frightened at the will of others.", "Jane Austen", 5017),
    ("And now that you don't have to be perfect, you can be good.", "John Steinbeck", 5017),

    # ===== Page 37 =====
    ("Weeds are flowers, too, once you get to know them.", "A.A. Milne", 4939),
    ("The man of knowledge must be able not only to love his enemies but also to hate his friends.", "Friedrich Nietzsche", 4938),
    ("It's enough for me to be sure that you and I exist at this moment.", "Gabriel García Márquez", 4933),
    ("A woman has to live her life, or live to repent not having lived it.", "D.H. Lawrence", 4929),
    ("A woman's heart should be so hidden in God that a man has to seek Him just to find her.", "Max Lucado", 4917),
    ("Pain is temporary. Quitting lasts forever.", "Lance Armstrong", 4907),
    ("Don't be afraid of your fears. They're not there to scare you. They're there to let you know that something is worth it.", "C. JoyBell C.", 4906),
    ("Do I not destroy my enemies when I make them my friends?", "Abraham Lincoln", 4903),
    ("Make improvements, not excuses. Seek respect, not attention.", "Roy T. Bennett", 4901),
    ("You never fail until you stop trying.", "Albert Einstein", 4890),
    ("The most important kind of freedom is to be what you really are. You trade in your reality for a role. You trade in your sense for an act. You give up your ability to feel, and in exchange, put on a mask.", "Jim Morrison", 4890),
    ("To the stars who listen—and the dreams that are answered.", "Sarah J. Maas", 4891),

    # ===== Page 38 =====
    ("Walk as if you are kissing the Earth with your feet.", "Thich Nhat Hanh", 4846),
    ("All the darkness in the world cannot extinguish the light of a single candle.", "St. Francis Of Assisi", 4844),
    ("There comes a time when one must take a position that is neither safe, nor politic, nor popular, but he must take it because conscience tells him it is right.", "Martin Luther King Jr.", 4842),
    ("It's not the load that breaks you down, it's the way you carry it.", "Lou Holtz", 4838),
    ("Some say the world will end in fire, Some say in ice. From what I've tasted of desire, I hold with those who favor fire.", "Robert Frost", 4837),
    ("I think we dream so we don't have to be apart for so long. If we're in each other's dreams, we can be together all the time.", "A.A. Milne", 4833),
    ("And that's the thing about people who mean everything they say. They think everyone else does too.", "Khaled Hosseini", 4833),
    ("It's kind of fun to do the impossible.", "Walt Disney", 4832),
    ("Everything can be taken from a man but one thing: the last of the human freedoms—to choose one's attitude in any given set of circumstances, to choose one's own way.", "Viktor E. Frankl", 4828),
    ("Start each day with a positive thought and a grateful heart.", "Roy T. Bennett", 4816),
    ("Books are for people who wish they were somewhere else.", "Mark Twain", 4811),
    ("There is no real ending. It's just the place where you stop the story.", "Frank Herbert", 4809),
    ("But in the end one needs more courage to live than to kill himself.", "Albert Camus", 4788),
    ("A classic is a book that has never finished saying what it has to say.", "Italo Calvino", 4785),

    # ===== Page 39 =====
    ("Love is an irresistible desire to be irresistibly desired.", "Robert Frost", 4750),
    ("Everything tells me that I am about to make a wrong decision, but making mistakes is just part of life.", "Paulo Coelho", 4747),
    ("Treat everyone with politeness and kindness, not because they are nice, but because you are.", "Roy T. Bennett", 4730),
    ("Be grateful for what you already have while you pursue your goals.", "Roy T. Bennett", 4724),
    ("I read a book one day and my whole life was changed.", "Orhan Pamuk", 4723),
    ("All endings are also beginnings. We just don't know it at the time.", "Mitch Albom", 4727),

    # ===== Page 40 =====
    ("It is a curious thought, but it is only when you see people looking ridiculous that you realize just how much you love them.", "Agatha Christie", 4679),
    ("The more I see, the less I know for sure.", "John Lennon", 4673),
    ("Tell your heart that the fear of suffering is worse than the suffering itself. And that no heart has ever suffered when it goes in search of its dreams.", "Paulo Coelho", 4673),
    ("Reading one book is like eating one potato chip.", "Diane Duane", 4669),
    ("No thief, however skillful, can rob one of knowledge, and that is why knowledge is the best and safest treasure to acquire.", "L. Frank Baum", 4660),
    ("The individual has always had to struggle to keep from being overwhelmed by the tribe. If you try it, you will be lonely often, and sometimes frightened. But no price is too high to pay for the privilege of owning yourself.", "Friedrich Nietzsche", 4650),
    ("Judge a man by his questions rather than by his answers.", "Voltaire", 4637),
    ("We all have our time machines, don't we. Those that take us back are memories...And those that carry us forward, are dreams.", "H.G. Wells", 4629),
    ("Learn what is to be taken seriously and laugh at the rest.", "Hermann Hesse", 4622),
]


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # 테이블 생성 (없으면)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS goodreads_popularity (
            id VARCHAR(36) PRIMARY KEY,
            quote_text TEXT NOT NULL,
            author_name VARCHAR(255) NOT NULL,
            likes INT NOT NULL,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

    saved = 0
    skipped = 0

    for quote_text, author_name, likes in QUOTES_DATA:
        # likes가 None이면 0으로 처리
        if likes is None:
            likes = 0

        # 중복 체크
        cur.execute(
            "SELECT 1 FROM goodreads_popularity WHERE quote_text = %s",
            (quote_text,),
        )
        if cur.fetchone():
            skipped += 1
            continue

        row_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO goodreads_popularity (id, quote_text, author_name, likes)
            VALUES (%s, %s, %s, %s)
            """,
            (row_id, quote_text, author_name, likes),
        )
        saved += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"총 데이터 수: {len(QUOTES_DATA)}")
    print(f"신규 저장: {saved}")
    print(f"중복 스킵: {skipped}")


if __name__ == "__main__":
    main()
