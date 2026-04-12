"""
Goodreads Popular Quotes (pages 41~60) -> PostgreSQL goodreads_popularity 테이블 저장.

수집 일시: 2026-04-12
페이지 44는 timeout으로 스킵됨.
소설 속 대화는 제외하고, 독립적인 명언/격언만 포함.
"""

import uuid
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "user": "youheaukjun",
    "database": "quotes_db",
}

QUOTES_DATA = [
    # ===== Page 41 =====
    ("When the power of love overcomes the love of power, the world will know peace.", "Jimi Hendrix", 4597),
    ("A good library will never be too neat, or too dusty, because somebody will always be in it, taking books off the shelves and staying up late reading them.", "Lemony Snicket", 4593),
    ("No matter how much suffering you went through, you never wanted to let go of those memories.", "Haruki Murakami", 4591),
    ("The one thing that doesn't abide by majority rule is a person's conscience.", "Harper Lee", 4575),
    ("The function of prayer is not to influence God, but rather to change the nature of the one who prays.", "Søren Kierkegaard", 4575),
    ("Why didn't I learn to treat everything like it was the last time. My greatest regret was how much I believed in the future.", "Jonathan Safran Foer", 4573),
    ("People think that intimacy is about sex. But intimacy is about truth. When you realize you can tell someone your truth, when you can show yourself to them, when you stand in front of them bare and their response is 'you're safe with me'- that's intimacy.", "Taylor Jenkins Reid", 4570),
    ("I go to seek a Great Perhaps.", "François Rabelais", 4568),
    ("The Chinese use two brush strokes to write the word 'crisis.' One brush stroke stands for danger; the other for opportunity. In a crisis, be aware of the danger--but recognize the opportunity.", "John F. Kennedy", 4567),
    ("History will be kind to me for I intend to write it.", "Winston S. Churchill", 4566),
    ("After nourishment, shelter and companionship, stories are the thing we need most in the world.", "Philip Pullman", 4563),
    ("Forever is composed of nows.", "Emily Dickinson", 4560),
    ("If you're lonely when you're alone, you're in bad company.", "Jean-Paul Sartre", 4552),
    ("All the world's a stage, And all the men and women merely players; They have their exits and their entrances; And one man in his time plays many parts, His acts being seven ages.", "William Shakespeare", 4548),
    ("Reading is escape, and the opposite of escape; it's a way to make contact with reality after a day of making things up, and it's a way of making contact with someone else's imagination after a day that's all too real.", "Nora Ephron", 4536),
    ("To burn with desire and keep quiet about it is the greatest punishment we can bring on ourselves.", "Federico García Lorca", 4526),
    ("I dream my painting and I paint my dream.", "Vincent van Gogh", 4526),

    # ===== Page 42 =====
    ("I'm so glad I live in a world where there are Octobers.", "L.M. Montgomery", 4512),
    ("Hate the sin, love the sinner.", "Mahatma Gandhi", 4510),
    ("Great spirits have always encountered violent opposition from mediocre minds.", "Albert Einstein", 4510),
    ("When we are no longer able to change a situation, we are challenged to change ourselves.", "Viktor E. Frankl", 4504),
    ("Never close your lips to those whom you have already opened your heart.", "Charles Dickens", 4504),
    ("Nobody ever figures out what life is all about, and it doesn't matter. Explore the world.", "Richard P. Feynman", 4503),
    ("When we are tired, we are attacked by ideas we conquered long ago.", "Friedrich Nietzsche", 4478),
    ("Dance, when you're broken open. Dance, if you've torn the bandage off.", "Rumi", 4475),
    ("Life is to be enjoyed, not endured.", "Gordon B. Hinckley", 4488),

    # ===== Page 43 =====
    ("You are imperfect, permanently and inevitably flawed. And you are beautiful.", "Amy Bloom", 4446),
    ("Trees are poems the earth writes upon the sky, We fell them down and turn them into paper, That we may record our emptiness.", "Kahlil Gibran", 4444),
    ("Someone I loved once gave me a box full of darkness. It took me years to understand that this too, was a gift.", "Mary Oliver", 4440),
    ("If you're losing your soul and you know it, then you've still got a soul left to lose.", "Charles Bukowski", 4425),
    ("You can't be happy unless you're unhappy sometimes.", "Lauren Oliver", 4420),
    ("One ought, every day at least, to hear a little song, read a good poem, see a fine picture, and, if it were possible, to speak a few reasonable words.", "Johann Wolfgang von Goethe", 4409),
    ("If you obey all of the rules, you miss all of the fun.", "Katharine Hepburn", 4409),
    ("This is your life and its ending one moment at a time.", "Chuck Palahniuk", 4408),
    ("One cannot think well, love well, sleep well, if one has not dined well.", "Virginia Woolf", 4406),
    ("No amount of regretting can change the past, and no amount of worrying can change the future.", "Roy T. Bennett", 4399),

    # ===== Page 44: SKIPPED (timeout) =====

    # ===== Page 45 =====
    ("Don't take life too seriously. Punch it in the face when it needs a good hit. Laugh at it.", "Colleen Hoover", 4291),
    ("All great and precious things are lonely.", "John Steinbeck", 4291),
    ("When a man is denied the right to live the life he believes in, he has no choice but to become an outlaw.", "Nelson Mandela", 4290),
    ("When someone leaves, it's because someone else is about to arrive.", "Paulo Coelho", 4287),
    ("A random act of kindness, no matter how small, can make a tremendous impact on someone else's life.", "Roy T. Bennett", 4283),
    ("Any fool can be happy. It takes a man with real heart to make beauty out of the stuff that makes us weep.", "Clive Barker", 4283),
    ("I want to do with you what spring does with the cherry trees.", "Pablo Neruda", 4282),
    ("You were born with wings, why prefer to crawl through life?", "Rumi", 4281),
    ("The happiness of your life depends upon the quality of your thoughts.", "Marcus Aurelius", 4273),
    ("I can resist anything except temptation.", "Oscar Wilde", 4273),
    ("The greater the love, the greater the tragedy when it's over.", "Nicholas Sparks", 4270),

    # ===== Page 46 =====
    ("So be sure when you step, Step with care and great tact. And remember that life's A Great Balancing Act.", "Dr. Seuss", 4230),
    ("You speak an infinite deal of nothing.", "William Shakespeare", 4229),
    ("The secret of health for both mind and body is not to mourn for the past, nor to worry about the future, but to live the present moment wisely and earnestly.", "Bukkyo Dendo Kyokai", 4227),
    ("Literature is the most agreeable way of ignoring life.", "Fernando Pessoa", 4225),
    ("The first draft of anything is shit.", "Ernest Hemingway", 4221),
    ("People demand freedom of speech as a compensation for the freedom of thought which they seldom use.", "Søren Kierkegaard", 4221),
    ("Always do sober what you said you'd do drunk. That will teach you to keep your mouth shut.", "Ernest Hemingway", 4212),
    ("There are years that ask questions and years that answer.", "Zora Neale Hurston", 4212),
    ("An expert is a person who has made all the mistakes that can be made in a very narrow field.", "Niels Bohr", 4210),
    ("What you do, the way you think, makes you beautiful.", "Scott Westerfeld", 4209),
    ("Confront the dark parts of yourself, and work to banish them with illumination and forgiveness.", "August Wilson", 4208),
    ("As if you were on fire from within. The moon lives in the lining of your skin.", "Pablo Neruda", 4208),
    ("After silence, that which comes nearest to expressing the inexpressible is music.", "Aldous Huxley", 4208),
    ("Stories may well be lies, but they are good lies that say true things.", "Neil Gaiman", 4206),

    # ===== Page 47 =====
    ("What makes the desert beautiful is that somewhere it hides a well.", "Antoine de Saint-Exupéry", 4181),
    ("If you do not tell the truth about yourself you cannot tell it about other people.", "Virginia Woolf", 4174),
    ("We should consider every day lost on which we have not danced at least once.", "Friedrich Nietzsche", 4166),
    ("The world breaks everyone, and afterward, many are strong at the broken places.", "Ernest Hemingway", 4163),
    ("Many a book is like a key to unknown chambers within the castle of one's own self.", "Franz Kafka", 4159),
    ("Life appears to me too short to be spent in nursing animosity or registering wrongs.", "Charlotte Brontë", 4159),
    ("Letting go means to come to the realization that some people are a part of your history, but not a part of your destiny.", "Steve Maraboli", 4158),
    ("It's been my experience that you can nearly always enjoy things if you make up your mind firmly that you will.", "L.M. Montgomery", 4152),
    ("The world was hers for the reading.", "Betty Smith", 4151),
    ("I dream. Sometimes I think that's the only right thing to do.", "Haruki Murakami", 4147),
    ("It is a great thing to start life with a small number of really good books which are your very own.", "Arthur Conan Doyle", 4147),
    ("They say when you are missing someone that they are probably feeling the same, but I don't think it's possible for you to miss me as much as I'm missing you right now.", "Edna St. Vincent Millay", 4146),
    ("Understanding is the first step to acceptance, and only with acceptance can there be recovery.", "J.K. Rowling", 4141),

    # ===== Page 48 =====
    ("The beginning of love is the will to let those we love be perfectly themselves, the resolution not to twist them to fit our own image.", "Thomas Merton", 4123),
    ("It is only with the heart that one can see rightly; what is essential is invisible to the eye.", "Antoine de Saint-Exupéry", 4119),
    ("We waste time looking for the perfect lover, instead of creating the perfect love.", "Tom Robbins", 4115),
    ("Never lose hope. Storms make people stronger and never last forever.", "Roy T. Bennett", 4110),
    ("It doesn't interest me what you do for a living. I want to know what you ache for.", "Oriah Mountain Dreamer", 4110),
    ("Words are easy, like the wind; faithful friends are hard to find.", "William Shakespeare", 4108),
    ("It is forbidden to kill; therefore all murderers are punished unless they kill in large numbers and to the sound of trumpets.", "Voltaire", 4104),
    ("The bravest people are the ones who don't mind looking like cowards.", "T.H. White", 4100),
    ("Don't waste your time with explanations: people only hear what they want to hear.", "Paulo Coelho", 4098),
    ("A cynic is a man who knows the price of everything, and the value of nothing.", "Oscar Wilde", 4098),
    ("Live in the sunshine, swim the sea, drink the wild air.", "Ralph Waldo Emerson", 4097),
    ("You might be poor, your shoes might be broken, but your mind is a palace.", "Frank McCourt", 4093),
    ("I never change, I simply become more myself.", "Joyce Carol Oates", 4083),

    # ===== Page 49 =====
    ("Great things happen to those who don't stop believing, trying, learning, and being grateful.", "Roy T. Bennett", 4052),
    ("Everything we hear is an opinion, not a fact. Everything we see is a perspective, not the truth.", "Marcus Aurelius", 4050),
    ("I am made of memories.", "Madeline Miller", 4049),
    ("You don't remember what happened. What you remember becomes what happened.", "John Green", 4043),
    ("The past has no power over the present moment.", "Eckhart Tolle", 4040),
    ("Don't part with your illusions. When they are gone you may still exist, but you have ceased to live.", "Mark Twain", 4037),
    ("Wherever you go becomes a part of you somehow.", "Anita Desai", 4031),
    ("You need to learn how to select your thoughts just the same way you select your clothes every day.", "Elizabeth Gilbert", 4031),
    ("Don't feel sorry for yourself. Only assholes do that.", "Haruki Murakami", 4028),
    ("If a book about failures doesn't sell, is it a success?", "Jerry Seinfeld", 4021),
    ("The very least you can do in your life is figure out what you hope for. And the most you can do is live inside that hope.", "Barbara Kingsolver", 4021),
    ("You will lose someone you can't live without, and your heart will be badly broken, and the bad news is that you never completely get over the loss.", "Anne Lamott", 4017),
    ("There are three types of lies -- lies, damn lies, and statistics.", "Benjamin Disraeli", 4014),
    ("Do not fear failure but rather fear not trying.", "Roy T. Bennett", 4012),

    # ===== Page 50 =====
    ("Don't you think it's better to be extremely happy for a short while, even if you lose it, than to be just okay for your whole life?", "Audrey Niffenegger", 3986),
    ("Though nobody can go back and make a new beginning... Anyone can start over and make a new ending.", "Chico Xavier", 3980),
    ("I cannot teach anybody anything. I can only make them think.", "Socrates", 3978),
    ("Behind every exquisite thing that existed, there was something tragic.", "Oscar Wilde", 3976),
    ("Men are afraid that women will laugh at them. Women are afraid that men will kill them.", "Margaret Atwood", 3973),
    ("If you treat an individual as he is, he will remain how he is. But if you treat him as if he were what he ought to be and could be, he will become what he ought to be and could be.", "Johann Wolfgang von Goethe", 3960),
    ("We must be willing to let go of the life we planned so as to have the life that is waiting for us.", "Joseph Campbell", 3959),
    ("Growing apart doesn't change the fact that for a long time we grew side by side; our roots will always be tangled. I'm glad for that.", "Ally Condie", 3954),
    ("And when at last you find someone to whom you feel you can pour out your soul, you stop in shock at the words you utter-- they are so rusty, so ugly, so meaningless and feeble from being kept in the small cramped dark inside you so long.", "Sylvia Plath", 3950),

    # ===== Page 51 =====
    ("You will do foolish things, but do them with enthusiasm.", "Colette", 3939),
    ("I can shake off everything as I write; my sorrows disappear, my courage is reborn.", "Anne Frank", 3934),
    ("That it will never come again is what makes life so sweet.", "Emily Dickinson", 3933),
    ("If you want to be a writer, you must do two things above all others: read a lot and write a lot.", "Stephen King", 3931),
    ("Happiness is only real when shared.", "Jon Krakauer", 3930),
    ("Appear weak when you are strong, and strong when you are weak.", "Sun Tzu", 3919),
    ("There is no exquisite beauty without some strangeness in the proportion.", "Edgar Allan Poe", 3912),
    ("When it is dark enough, you can see the stars.", "Ralph Waldo Emerson", 3910),

    # ===== Page 52 =====
    ("Love is an untamed force. When we try to control it, it destroys us. When we try to imprison it, it enslaves us. When we try to understand it, it leaves us feeling lost and confused.", "Paulo Coelho", 3880),
    ("Life is a shipwreck, but we must not forget to sing in the lifeboats.", "Voltaire", 3878),
    ("Reading furnishes the mind only with materials of knowledge; it is thinking that makes what we read ours.", "John Locke", 3878),
    ("The only way to get rid of temptation is to yield to it.", "Oscar Wilde", 3874),
    ("Do I contradict myself? Very well then I contradict myself, (I am large, I contain multitudes.)", "Walt Whitman", 3872),
    ("Is 'fat' really the worst thing a human being can be? Is 'fat' worse than 'vindictive', 'jealous', 'shallow', 'vain', 'boring' or 'cruel'? Not to me.", "J.K. Rowling", 3870),
    ("All women become like their mothers. That is their tragedy. No man does, and that is his.", "Oscar Wilde", 3869),
    ("If we wait for the moment when everything, absolutely everything is ready, we shall never begin.", "Ivan Turgenev", 3860),
    ("Everything that irritates us about others can lead us to an understanding of ourselves.", "C.G. Jung", 3856),
    ("There are three rules for writing a novel. Unfortunately, no one knows what they are.", "W. Somerset Maugham", 3850),
    ("Don't feel bad for one moment about doing what brings you joy.", "Sarah J. Maas", 3843),
    ("A ship is safe in harbor, but that's not what ships are for.", "John A. Shedd", 3842),
    ("Never say 'no' to adventures. Always say 'yes,' otherwise you'll lead a very dull life.", "Ian Fleming", 3839),

    # ===== Page 53 =====
    ("I cannot make you understand. I cannot make anyone understand what is happening inside me.", "Franz Kafka", 3818),
    ("You wanna fly, you got to give up the shit that weighs you down.", "Toni Morrison", 3817),
    ("If you ask me what I came to do in this world, I, an artist, will answer you: I am here to live out loud.", "Émile Zola", 3816),
    ("Money can't buy happiness, but it can make you awfully comfortable while you're being miserable.", "Clare Boothe Luce", 3814),
    ("Failure is the condiment that gives success its flavor.", "Truman Capote", 3813),
    ("Always find opportunities to make someone smile, and to offer random acts of kindness in everyday life.", "Roy T. Bennett", 3810),
    ("Raise your words, not voice. It is rain that grows flowers, not thunder.", "Rumi", 3810),
    ("Rivers know this: there is no hurry. We shall get there some day.", "A.A. Milne", 3808),
    ("The only way to get through life is to laugh your way through it. You either have to laugh or cry.", "Marjorie Pay Hinckley", 3808),
    ("She read books as one would breathe air, to fill up and live.", "Annie Dillard", 3799),
    ("So many things are possible just as long as you don't know they're impossible.", "Norton Juster", 3795),

    # ===== Page 54 =====
    ("When people don't express themselves, they die one piece at a time.", "Laurie Halse Anderson", 3777),
    ("You couldn't relive your life, skipping the awful parts, without losing what made it worthwhile. You had to accept it as a whole--like the world, or the person you loved.", "Stewart O'Nan", 3771),
    ("Tears shed for another person are not a sign of weakness. They are a sign of a pure heart.", "José N. Harris", 3771),
    ("I'm not young enough to know everything.", "J.M. Barrie", 3768),
    ("A good traveler has no fixed plans and is not intent on arriving.", "Lao Tzu", 3767),
    ("I am not afraid of storms, for I am learning how to sail my ship.", "Louisa May Alcott", 3765),
    ("A purpose of human life, no matter who is controlling it, is to love whoever is around to be loved.", "Kurt Vonnegut", 3764),
    ("Everybody talks about wanting to change things and help and fix, but ultimately all you can do is fix yourself. And that's a lot. Because if you can fix yourself, it has a ripple effect.", "Rob Reiner", 3754),
    ("I've found that there is always some beauty left -- in nature, sunshine, freedom, in yourself; these can all help you.", "Anne Frank", 3754),
    ("If you don't know, the thing to do is not to get scared, but to learn.", "Ayn Rand", 3754),
    ("Every one of us is, in the cosmic perspective, precious. If a human disagrees with you, let him live. In a hundred billion galaxies, you will not find another.", "Carl Sagan", 3754),

    # ===== Page 55 =====
    ("To be great is to be misunderstood.", "Ralph Waldo Emerson", 3738),
    ("Biology gives you a brain. Life turns it into a mind.", "Jeffrey Eugenides", 3736),
    ("Sometimes, the smallest things take up the most room in your heart.", "A.A. Milne", 3734),
    ("In life, unlike chess, the game continues after checkmate.", "Isaac Asimov", 3732),
    ("Books are easily destroyed. But words will live as long as people can remember them.", "Tahereh Mafi", 3730),
    ("I regret that it takes a life to learn how to live.", "Jonathan Safran Foer", 3724),
    ("I believe a strong woman may be stronger than a man, particularly if she happens to have love in her heart. I guess a loving woman is indestructible.", "John Steinbeck", 3721),
    ("I came from a real tough neighborhood. Once a guy pulled a knife on me. I knew he wasn't a professional, the knife had butter on it.", "Rodney Dangerfield", 3720),
    ("All the secrets of the world are contained in books. Read at your own risk.", "Lemony Snicket", 3718),
    ("Success is stumbling from failure to failure with no loss of enthusiasm.", "Winston S. Churchill", 3717),
    ("If you don't like someone's story, write your own.", "Chinua Achebe", 3712),
    ("Letting go doesn't mean that you don't care about someone anymore. It's just realizing that the only person you really have control over is yourself.", "Deborah Reber", 3710),

    # ===== Page 56 =====
    ("A single dream is more powerful than a thousand realities.", "Nathaniel Hawthorne", 3699),
    ("Clothes make the man. Naked people have little or no influence on society.", "Mark Twain", 3699),
    ("A book is really like a lover. It arranges itself in your life in a way that is beautiful.", "Maurice Sendak", 3697),
    ("It's often just enough to be with someone. I don't need to touch them. Not even talk.", "Marilyn Monroe", 3697),
    ("A writer is someone for whom writing is more difficult than it is for other people.", "Thomas Mann", 3693),
    ("There is no mistaking a real book when one meets it. It is like falling in love.", "Christopher Morley", 3689),
    ("There are good days and hard days for me -- even now. Don't let the hard days win.", "Sarah J. Maas", 3688),
    ("The most common way people give up their power is by thinking they don't have any.", "Alice Walker", 3684),
    ("The capacity for friendship is God's way of apologizing for our families.", "Jay McInerney", 3683),
    ("Books say: She did this because. Life says: She did this. Books are where things are explained to you; life is where things aren't.", "Julian Barnes", 3685),

    # ===== Page 57 =====
    ("Still round the corner there may wait a new road or a secret gate...", "J.R.R. Tolkien", 3655),
    ("You will find that it is necessary to let things go; simply for the reason that they are heavy.", "C. JoyBell C.", 3652),
    ("I'm tough, I'm ambitious, and I know exactly what I want. If that makes me a bitch, okay.", "Madonna", 3650),
    ("Kindred spirits are not so scarce as I used to think.", "L.M. Montgomery", 3647),
    ("Real loneliness is not necessarily limited to when you are alone.", "Charles Bukowski", 3647),
    ("Don't Gain The World & Lose Your Soul, Wisdom Is Better Than Silver Or Gold.", "Bob Marley", 3644),
    ("let me live, love, and say it well in good sentences.", "Sylvia Plath", 3640),
    ("Maybe everyone can live beyond what they're capable of.", "Markus Zusak", 3637),
    ("You can't depend on your eyes when your imagination is out of focus.", "Mark Twain", 3635),
    ("I like good strong words that mean something.", "Louisa May Alcott", 3634),
    ("Knowledge speaks, but wisdom listens.", "Jimi Hendrix", 3632),
    ("Do you want to know who you are? Don't ask. Act! Action will delineate and define you.", "Thomas Jefferson", 3631),
    ("It's amazing how a little tomorrow can make up for a whole lot of yesterday.", "John Guare", 3630),
    ("It is my belief that the truth is generally preferable to lies.", "J.K. Rowling", 3631),

    # ===== Page 58 =====
    ("Even strength must bow to wisdom sometimes.", "Rick Riordan", 3615),
    ("The moon is a loyal companion. It never leaves. It's always there, watching, steadfast, knowing us in our light and dark moments, changing forever just as we do.", "Tahereh Mafi", 3611),
    ("People can lose their lives in libraries. They ought to be warned.", "Saul Bellow", 3611),
    ("A learning experience is one of those things that says, 'You know that thing you just did? Don't do that.'", "Douglas Adams", 3608),
    ("Believe nothing you hear, and only one half that you see.", "Edgar Allan Poe", 3607),
    ("being alone never felt right. sometimes it felt good, but it never felt right.", "Charles Bukowski", 3605),
    ("The only way that we can live, is if we grow. The only way that we can grow is if we change. The only way that we can change is if we learn.", "C. JoyBell C.", 3604),
    ("Love the life you live. Live the life you love.", "Bob Marley", 3604),
    ("Isn't it enough to see that a garden is beautiful without having to believe that there are fairies at the bottom of it too?", "Douglas Adams", 3603),
    ("The world is full of magic things, patiently waiting for our senses to grow sharper.", "W.B. Yeats", 3599),
    ("Children begin by loving their parents; as they grow older they judge them; sometimes they forgive them.", "Oscar Wilde", 3599),
    ("Let's think the unthinkable, let's do the undoable. Let us prepare to grapple with the ineffable itself, and see if we may not eff it after all.", "Douglas Adams", 3598),
    ("You realize that our mistrust of the future makes it hard to give up the past.", "Chuck Palahniuk", 3596),

    # ===== Page 59 =====
    ("It is easier to forgive an enemy than to forgive a friend.", "William Blake", 3576),
    ("I've been homesick for countries I've never been, and longed to be where I couldn't be.", "John Cheever", 3575),
    ("To love oneself is the beginning of a lifelong romance.", "Oscar Wilde", 3575),
    ("Anyone who falls in love is searching for the missing pieces of themselves.", "Haruki Murakami", 3574),
    ("It does not matter how slowly you go as long as you do not stop.", "Confucius", 3574),
    ("If you want to keep a secret, you must also hide it from yourself.", "George Orwell", 3573),
    ("There is no such thing as bad people. We're all just people who sometimes do bad things.", "Colleen Hoover", 3571),
    ("Fools talk, cowards are silent, wise men listen.", "Carlos Ruiz Zafón", 3570),
    ("If you don't read the newspaper, you're uninformed. If you read it, you're mis-informed.", "Mark Twain", 3564),
    ("People who deny the existence of dragons are often eaten by dragons. From within.", "Ursula K. Le Guin", 3560),

    # ===== Page 60 =====
    ("Only the dead have seen the end of war.", "Plato", 3545),
    ("What you do makes a difference, and you have to decide what kind of difference you want to make.", "Jane Goodall", 3543),
    ("There are books of which the backs and covers are by far the best parts.", "Charles Dickens", 3541),
    ("Pain insists upon being attended to. God whispers to us in our pleasures, speaks in our consciences, but shouts in our pains.", "C.S. Lewis", 3539),
    ("A good book is an event in my life.", "Stendhal", 3538),
    ("Don't be so humble - you are not that great.", "Golda Meir", 3535),
    ("Trying to define yourself is like trying to bite your own teeth.", "Alan W. Watts", 3532),
    ("May the forces of evil become confused on the way to your house.", "George Carlin", 3521),
    ("Light thinks it travels faster than anything but it is wrong. No matter how fast light travels, it finds the darkness has always got there first.", "Terry Pratchett", 3518),
    ("But how could you live and have no story to tell?", "Fyodor Dostoevsky", 3515),
    ("In the beginning there was nothing, which exploded.", "Terry Pratchett", 3514),
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
    print("조회 성공 페이지: 41, 42, 43, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60 (19개)")
    print("조회 실패 페이지: 44 (timeout)")


if __name__ == "__main__":
    main()
