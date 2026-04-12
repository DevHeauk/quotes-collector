"""
Goodreads Popular Quotes (pages 61~80) -> PostgreSQL goodreads_popularity 테이블 저장.

수집 일시: 2026-04-12
페이지 78은 timeout으로 스킵.
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
    # ===== Page 61 =====
    ("Your beliefs become your thoughts, Your thoughts become your words, Your words become your actions, Your actions become your habits, Your habits become your values, Your values become your destiny.", "Mahatma Gandhi", 3496),
    ("Creativity is intelligence having fun.", "Albert Einstein", 3494),
    ("Remember, remember, this is now, and now, and now. Live it, feel it, cling to it.", "Sylvia Plath", 3491),
    ("Today was good. Today was fun. Tomorrow is another one.", "Dr. Seuss", 3491),
    ("People shouldn't be afraid of their government. Governments should be afraid of their people.", "Alan Moore", 3488),
    ("Never give up... No one knows what's going to happen next.", "L. Frank Baum", 3487),
    ("My soul is from elsewhere, I'm sure of that, and I intend to end up there.", "Jalal ad-Din Muhammad ar-Rumi", 3482),
    ("Those who know do not speak. Those who speak do not know.", "Lao Tzu", 3480),
    ("A dream you dream alone is only a dream. A dream you dream together is reality.", "John Lennon", 3475),
    ("If I'd observed all the rules I'd never have got anywhere.", "Marilyn Monroe", 3473),
    ("My library is an archive of longings.", "Susan Sontag", 3469),
    ("No matter what he does, every person on earth plays a central role in the history of the world.", "Paulo Coelho", 3469),

    # ===== Page 62 =====
    ("Never interrupt your enemy when he is making a mistake.", "Napoleon Bonaparte", 3448),
    ("When the heart speaks, the mind finds it indecent to object.", "Milan Kundera", 3445),
    ("You yourself, as much as anybody in the entire universe, deserve your love and affection.", "Sharon Salzberg", 3444),
    ("Tell me and I forget, teach me and I may remember, involve me and I learn.", "Benjamin Franklin", 3438),
    ("Is there no way out of the mind?", "Sylvia Plath", 3437),
    ("silence is the language of god, all else is poor translation.", "Rumi", 3432),
    ("It's the questions we can't answer that teach us the most. They teach us how to think.", "Patrick Rothfuss", 3431),
    ("Though my soul may set in darkness, it will rise in perfect light; I have loved the stars too fondly to be fearful of the night.", "Sarah Williams", 3431),
    ("There was another life that I might have had, but I am having this one.", "Kazuo Ishiguro", 3418),
    ("Books are a way to live a thousand lives\u2014or to find strength in a very long one.", "V.E. Schwab", 3421),
    ("For whatever we lose, it's always our self we find in the sea.", "e.e. cummings", 3420),

    # ===== Page 63 =====
    ("The beauty of a woman is not in the clothes she wears, the figure that she carries, or the way she combs her hair. The beauty of a woman is seen in her eyes, because that is the doorway to her heart, the place where love resides. True beauty in a woman is reflected in her soul.", "Audrey Hepburn", 3387),
    ("They who can give up essential liberty to obtain a little temporary safety deserve neither liberty nor safety.", "Benjamin Franklin", 3386),
    ("Art enables us to find ourselves and lose ourselves at the same time.", "Thomas Merton", 3384),
    ("When I had nothing to lose, I had everything. When I stopped being who I am, I found myself.", "Paulo Coelho", 3382),
    ("You're alive only once, as far as we know, and what could be worse than getting to the end of your life and realizing you hadn't lived it?", "Edward Albee", 3381),
    ("There is greatness in doing something you hate for the sake of someone you love.", "Shmuley Boteach", 3380),
    ("Confidence is ignorance. If you're feeling cocky, it's because there's something you don't know.", "Eoin Colfer", 3380),
    ("You have to know what you stand for, not just what you stand against.", "Laurie Halse Anderson", 3378),
    ("Just because you fail once, it doesn't mean you're going to fail at everything. Keep trying and always believe in yourself.", "Marilyn Monroe", 3377),
    ("Our memory is a more perfect world than the universe: it gives back life to those who no longer exist.", "Guy de Maupassant", 3377),
    ("Success makes so many people hate you. I wish it wasn't that way.", "Marilyn Monroe", 3376),
    ("Have a heart that never hardens, and a temper that never tires, and a touch that never hurts.", "Charles Dickens", 3373),
    ("You can have it all. Just not all at once.", "Oprah Winfrey", 3373),
    ("The library is inhabited by spirits that come out of the pages at night.", "Isabel Allende", 3371),

    # ===== Page 64 =====
    ("The purpose of life is to live it, to taste experience to the utmost, to reach out eagerly and without fear for newer and richer experience.", "Eleanor Roosevelt", 3351),
    ("A child can teach an adult three things: to be happy for no reason, to always be busy with something, and to know how to demand with all his might that which he desires.", "Paulo Coelho", 3349),
    ("We need, in love, to practice only this: letting each other go. For holding on comes easily; we do not need to learn it.", "Rainer Maria Rilke", 3348),
    ("I wanted a perfect ending. Now I've learned, the hard way, that some poems don't rhyme, and some stories don't have a clear beginning, middle, and end.", "Gilda Radner", 3347),
    ("A girl should be two things: who and what she wants.", "Coco Chanel", 3347),
    ("Man only likes to count his troubles; he doesn't calculate his happiness.", "Fyodor Dostoevsky", 3346),
    ("Life isn't finding shelter in the storm. It's about learning to dance in the rain.", "Sherrilyn Kenyon", 3344),
    ("How nice -- to feel nothing, and still get full credit for being alive.", "Kurt Vonnegut", 3342),
    ("Quotation is a serviceable substitute for wit.", "Oscar Wilde", 3339),
    ("That which can be asserted without evidence, can be dismissed without evidence.", "Christopher Hitchens", 3337),
    ("Nothing in the world is ever completely wrong. Even a stopped clock is right twice a day.", "Paulo Coelho", 3334),
    ("In a time of destruction, create something.", "Maxine Hong Kingston", 3333),
    ("A book lying idle on a shelf is wasted ammunition.", "Henry Miller", 3333),

    # ===== Page 65 =====
    ("If you end up with a boring miserable life because you listened to your mom, your dad, your teacher, your priest, or some guy on television telling you how to do your shit, then you deserve it.", "Frank Zappa", 3315),
    ("Older men declare war. But it is youth that must fight and die.", "Herbert Hoover", 3315),
    ("Lack of direction, not lack of time, is the problem. We all have twenty-four hour days.", "Zig Ziglar", 3312),
    ("And thus the heart will break, yet brokenly live on.", "George Gordon Byron", 3311),
    ("Keep in mind that people change, but the past doesn't.", "Becca Fitzpatrick", 3309),
    ("Don't spend time beating on a wall, hoping to transform it into a door.", "Coco Chanel", 3309),
    ("What's the good of living if you don't try a few things?", "Charles M. Schulz", 3308),
    ("Change will not come if we wait for some other person, or if we wait for some other time. We are the ones we've been waiting for. We are the change that we seek.", "Barack Obama", 3307),
    ("Books are the carriers of civilization. They are companions, teachers, magicians, bankers of the treasures of the mind. Books are humanity in print.", "Barbara W. Tuchman", 3305),
    ("Kindness is a language which the deaf can hear and the blind can see.", "Mark Twain", 3305),
    ("Time doesn't heal emotional pain, you need to learn how to let go.", "Roy T. Bennett", 3304),
    ("We rip out so much of ourselves to be cured of things faster than we should that we go bankrupt by the age of thirty and have less to offer each time we start with someone new. But to feel nothing so as not to feel anything - what a waste!", "Andr\u00e9 Aciman", 3302),
    ("All parents damage their children. It cannot be helped. Youth, like pristine glass, absorbs the prints of its handlers. Some parents smudge, others crack, a few shatter childhoods completely into jagged little pieces, beyond repair.", "Mitch Albom", 3302),
    ("God can't give us peace and happiness apart from Himself because there is no such thing.", "C.S. Lewis", 3300),
    ("Every book, every volume you see here, has a soul. The soul of the person who wrote it and of those who read it and lived and dreamed with it. Every time a book changes hands, every time someone runs his eyes down its pages, its spirit grows and strengthens.", "Carlos Ruiz Zaf\u00f3n", 3298),
    ("You should never be surprised when someone treats you with respect, you should expect it.", "Sarah Dessen", 3296),
    ("Do not be afraid; our fate cannot be taken from us; it is a gift.", "Dante Alighieri", 3296),
    ("Atheism turns out to be too simple. If the whole universe has no meaning, we should never have found out that it has no meaning.", "C.S. Lewis", 3292),
    ("Expose yourself to your deepest fear; after that, fear has no power, and the fear of freedom shrinks and vanishes. You are free.", "Jim Morrison", 3291),
    ("Learn to value yourself, which means: fight for your happiness.", "Ayn Rand", 3290),
    ("When I get lonely these days, I think: So BE lonely. Learn your way around loneliness. Make a map of it. Sit with it, for once in your life. Welcome to the human experience. But never again use another person's body or emotions as a scratching post for your own unfulfilled yearnings.", "Elizabeth Gilbert", 3290),
    ("When you find your path, you must not be afraid. You need to have sufficient courage to make mistakes. Disappointment, defeat, and despair are the tools God uses to show us the way.", "Paulo Coelho", 3293),

    # ===== Page 66 =====
    ("Trust is like a mirror, you can fix it if it's broken, but you can still see the crack in that mother fucker's reflection.", "Lady Gaga", 3282),
    ("It's all in the view. That's what I mean about forever, too. For any one of us our forever could end in an hour, or a hundred years from now. You never know for sure, so you'd better make every second count.", "Sarah Dessen", 3278),
    ("Cry. Forgive. Learn. Move on. Let your tears water the seeds of your future happiness.", "Steve Maraboli", 3277),
    ("No persons are more frequently wrong, than those who will not admit they are wrong.", "Fran\u00e7ois de La Rochefoucauld", 3276),
    ("The world is indeed comic, but the joke is on mankind.", "H. P. Lovecraft", 3272),
    ("A word after a word after a word is power.", "Margaret Atwood", 3272),
    ("So please, oh please, we beg, we pray, go throw your TV set away, and in its place you can install, a lovely bookshelf on the wall.", "Roald Dahl", 3259),
    ("If people refuse to look at you in a new light and they can only see you for what you were, only see you for the mistakes you've made, if they don't realize that you are not your mistakes, then they have to go.", "Steve Maraboli", 3259),
    ("Let our scars fall in love.", "Galway Kinnell", 3259),
    ("It is a good rule after reading a new book, never to allow yourself another new one till you have read an old one in between.", "C.S. Lewis", 3259),
    ("The saddest people I've ever met in life are the ones who don't care deeply about anything at all. Passion and satisfaction go hand in hand, and without them, any happiness is only temporary, because there's nothing to make it last.", "Nicholas Sparks", 3258),
    ("Without suffering, there'd be no compassion.", "Nicholas Sparks", 3258),

    # ===== Page 67 =====
    ("You are not your job, you're not how much money you have in the bank. You are not the car you drive. You're not the contents of your wallet. You are not your fucking khakis. You are all singing, all dancing crap of the world.", "Chuck Palahniuk", 3245),
    ("Therefore, dear Sir, love your solitude and try to sing out with the pain it causes you.", "Rainer Maria Rilke", 3244),
    ("Love and a cough cannot be concealed. Even a small cough. Even a small love.", "Anne Sexton", 3243),
    ("You shall know the truth and the truth shall make you mad.", "Aldous Huxley", 3243),
    ("If there's a single lesson that life teaches us, it's that wishing doesn't make it so.", "Lev Grossman", 3241),
    ("Don't let the bastards grind you down.", "Margaret Atwood", 3241),
    ("They say time heals all wounds, but that presumes the source of the grief is finite.", "Cassandra Clare", 3239),
    ("Here is a lesson in creative writing. First rule: Do not use semicolons.", "Kurt Vonnegut", 3239),
    ("Worry never robs tomorrow of its sorrow, but only saps today of its strength.", "A.J. Cronin", 3238),
    ("Who, being loved, is poor?", "Oscar Wilde", 3238),
    ("There is more to sex appeal than just measurements. I don't need a bedroom to prove my womanliness.", "Audrey Hepburn", 3237),
    ("Fear is a phoenix. You can watch it burn a thousand times and still it will return.", "Leigh Bardugo", 3235),
    ("I know I am but summer to your heart, and not the full four seasons of the year.", "Edna St. Vincent Millay", 3234),
    ("You can't stop the future. You can't rewind the past. The only way to learn the secret is to press play.", "Jay Asher", 3234),
    ("Nothing in the world is more dangerous than sincere ignorance and conscientious stupidity.", "Martin Luther King Jr.", 3234),
    ("Of all the words of mice and men, the saddest are, It might have been.", "Kurt Vonnegut", 3233),
    ("The greatest enemy of knowledge is not ignorance, it is the illusion of knowledge.", "Daniel J. Boorstin", 3233),
    ("I want to grow old without facelifts. I want to have the courage to be loyal to the face I have made.", "Marilyn Monroe", 3233),
    ("Talk sense to a fool and he calls you foolish.", "Euripides", 3232),

    # ===== Page 68 =====
    ("Courage is found in unlikely places.", "J.R.R. Tolkien", 3221),
    ("the free soul is rare, but you know it when you see it - basically because you feel good, very good, when you are near or with them.", "Charles Bukowski", 3219),
    ("When you are content to be simply yourself and don't compare or compete, everyone will respect you.", "Lao Tzu", 3219),
    ("I drink to make other people more interesting.", "Ernest Hemingway", 3218),
    ("I imagine one of the reasons people cling to their hates so stubbornly is because they sense, once hate is gone, they will be forced to deal with pain.", "James Baldwin", 3217),
    ("Scared is what you're feeling. Brave is what you're doing.", "Emma Donoghue", 3215),
    ("Time is the longest distance between two places.", "Tennessee Williams", 3215),
    ("When people talk, listen completely. Most people never listen.", "Ernest Hemingway", 3213),
    ("Even in the Future the Story Begins with Once Upon a Time.", "Marissa Meyer", 3210),
    ("Words are unpredictable creatures. No gun, sword, army or king will ever be more powerful than a sentence.", "Tahereh Mafi", 3209),

    # ===== Page 69 =====
    ("One of the advantages of being disorganized is that one is always having surprising discoveries.", "A.A. Milne", 3194),
    ("It is good to have an end to journey toward; but it is the journey that matters, in the end.", "Ursula K. Le Guin", 3194),
    ("A house without books is like a room without windows.", "Horace Mann", 3193),
    ("Don't compromise yourself - you're all you have.", "John Grisham", 3192),
    ("Happiness is holding someone in your arms and knowing you hold the whole world.", "Orhan Pamuk", 3191),
    ("Open your heart. Someone will come. Someone will come for you. But first you must open your heart.", "Kate DiCamillo", 3191),
    ("Do your little bit of good where you are; it's those little bits of good put together that overwhelm the world.", "Desmond Tutu", 3191),
    ("The heart has its reasons which reason knows not.", "Blaise Pascal", 3191),
    ("We take for granted the very things that most deserve our gratitude.", "Cynthia Ozick", 3188),
    ("I have the simplest tastes. I am always satisfied with the best.", "Oscar Wilde", 3187),
    ("I don't think of all the misery, but of the beauty that still remains.", "Anne Frank", 3186),
    ("Strange as it may seem, I still hope for the best, even though the best, like an interesting piece of mail, so rarely arrives, and even when it does it can be lost so easily.", "Lemony Snicket", 3184),
    ("Our mothers always remain the strangest, craziest people we've ever met.", "Marguerite Duras", 3182),
    ("Crying is for plain women. Pretty women go shopping.", "Oscar Wilde", 3180),
    ("Memories, even your most precious ones, fade surprisingly quickly. But I don't go along with that. The memories I value most, I don't ever see them fading.", "Kazuo Ishiguro", 3180),

    # ===== Page 70 =====
    ("Love can change a person the way a parent can change a baby- awkwardly, and often with a great deal of mess.", "Lemony Snicket", 3168),
    ("And so I try to be kind to everything I see, and in everything I see, I see him.", "Hanya Yanagihara", 3167),
    ("those who escape hell however never talk about it and nothing much bothers them after that.", "Charles Bukowski", 3167),
    ("Never make someone a priority when all you are to them is an option.", "Maya Angelou", 3165),
    ("Come sleep with me: We won't make Love, Love will make us.", "Julio Cort\u00e1zar", 3165),
    ("Can you understand? Someone, somewhere, can you understand me a little, love me a little?", "Sylvia Plath", 3165),
    ("Sell your cleverness and buy bewilderment.", "Rumi", 3158),
    ("She refused to be bored chiefly because she wasn't boring.", "Zelda Fitzgerald", 3155),
    ("The real voyage of discovery consists not in seeking new landscapes, but in having new eyes.", "Marcel Proust", 3155),
    ("True love is usually the most inconvenient kind.", "Kiera Cass", 3153),
    ("Where you used to be, there is a hole in the world, which I find myself constantly walking around in.", "Edna St. Vincent Millay", 3152),

    # ===== Page 71 =====
    ("The more you know who you are, and what you want, the less you let things upset you.", "Stephanie Perkins", 3130),
    ("You are all the colors in one, at full brightness.", "Jennifer Niven", 3129),
    ("Time was passing like a hand waving from a train I wanted to be on. I hope you never have to think about anything as much as I think about you.", "Jonathan Safran Foer", 3127),
    ("Try a little harder to be a little better.", "Gordon B. Hinckley", 3122),
    ("There is only one page left to write on. I will fill it with words of only one syllable. I love. I have loved. I will love.", "Dodie Smith", 3121),
    ("Tears are words that need to be written.", "Paulo Coelho", 3120),
    ("What do we live for, if it is not to make life less difficult for each other?", "George Eliot", 3118),
    ("You must not lose faith in humanity. Humanity is like an ocean; if a few drops of the ocean are dirty, the ocean does not become dirty.", "Mahatma Gandhi", 3116),
    ("Art washes away from the soul the dust of everyday life.", "Pablo Picasso", 3114),

    # ===== Page 72 =====
    ("You are not entitled to your opinion. You are entitled to your informed opinion. No one is entitled to be ignorant.", "Harlan Ellison", 3103),
    ("Reading brings us unknown friends", "Honor\u00e9 de Balzac", 3102),
    ("Friendship marks a life even more deeply than love. Love risks degenerating into obsession, friendship is never anything but sharing.", "Elie Wiesel", 3101),
    ("It's not worth doing something unless someone, somewhere, would much rather you weren't doing it.", "Terry Pratchett", 3101),
    ("Be thankful for everything that happens in your life; it's all an experience.", "Roy T. Bennett", 3100),
    ("Until you make the unconscious conscious, it will direct your life and you will call it fate.", "C.G. Jung", 3094),
    ("Whatever you're meant to do, do it now. The conditions are always impossible.", "Doris Lessing", 3093),
    ("I am different, not less.", "Temple Grandin", 3092),
    ("If you work really hard, and you're kind, amazing things will happen.", "Conan O'Brien", 3092),
    ("The longer and more carefully we look at a funny story, the sadder it becomes.", "Nikolai Gogol", 3091),
    ("I haven't been everywhere, but it's on my list.", "Susan Sontag", 3091),
    ("Animals are my friends...and I don't eat my friends.", "George Bernard Shaw", 3091),
    ("The trouble is not that I am single and likely to stay single, but that I am lonely and likely to stay lonely.", "Charlotte Bront\u00eb", 3089),
    ("The pleasure of all reading is doubled when one lives with another who shares the same books.", "Katherine Mansfield", 3088),
    ("I like it when somebody gets excited about something. It's nice.", "J.D. Salinger", 3087),
    ("From childhood's hour I have not been. As others were, I have not seen. As others saw, I could not awaken.", "Edgar Allan Poe", 3087),

    # ===== Page 73 =====
    ("There is no place like home.", "L. Frank Baum", 3084),
    ("I'm sick of just liking people. I wish to God I could meet somebody I could respect.", "J.D. Salinger", 3084),
    ("I myself have never been able to find out precisely what feminism is: I only know that people call me a feminist whenever I express sentiments that differentiate me from a doormat.", "Rebecca West", 3082),
    ("I love books, by the way, way more than movies. Movies tell you what to think. A good book lets you choose a few thoughts for yourself.", "Karen Marie Moning", 3075),
    ("There are two means of refuge from the misery of life \u2014 music and cats.", "Albert Schweitzer", 3075),
    ("God, but life is loneliness, despite all the opiates, despite the shrill tinsel gaiety of parties with no purpose.", "Sylvia Plath", 3074),
    ("It is a far, far better thing that I do, than I have ever done; it is a far, far better rest that I go to than I have ever known.", "Charles Dickens", 3074),
    ("Children have never been very good at listening to their elders, but they have never failed to imitate them.", "James Baldwin", 3068),
    ("No one ever told me that grief felt so like fear.", "C.S. Lewis", 3068),
    ("I am too intelligent, too demanding, and too resourceful for anyone to be able to take charge of me entirely. No one knows me or loves me completely. I have only myself.", "Simone de Beauvoir", 3065),
    ("I meant what I said and I said what I meant. An elephant's faithful one-hundred percent!", "Dr. Seuss", 3065),
    ("Ask not what you can do for your country. Ask what's for lunch.", "Orson Welles", 3065),

    # ===== Page 74 =====
    ("You never change your life until you step out of your comfort zone; change begins at the end of your comfort zone.", "Roy T. Bennett", 3051),
    ("As a woman I have no country. As a woman I want no country. As a woman, my country is the whole world.", "Virginia Woolf", 3051),
    ("When the snows fall and the white winds blow, the lone wolf dies but the pack survives.", "George R.R. Martin", 3049),
    ("Remain true to yourself, child. If you know your own heart, you will always have one friend who does not lie.", "Marion Zimmer Bradley", 3048),
    ("If you love what you do and are willing to do what it takes, it's within your reach.", "Steve Wozniak", 3046),
    ("I must be a mermaid, Rango. I have no fear of depths and a great fear of shallow living.", "Ana\u00efs Nin", 3043),
    ("Maybe some people just aren't meant to be in our lives forever. Maybe some people are just passing through.", "Danielle Steel", 3040),
    ("The truth will set you free. But not until it is finished with you.", "David Foster Wallace", 3036),
    ("There are so many ways to be brave in this world. Sometimes it is nothing more than gritting your teeth through pain.", "Veronica Roth", 3036),
    ("It's the job that's never started as takes longest to finish.", "J.R.R. Tolkien", 3032),
    ("Open your eyes and see what you can with them before they close forever.", "Anthony Doerr", 3031),

    # ===== Page 75 =====
    ("It gives me strength to have somebody to fight for; I can never fight for myself, but, for others, I can kill.", "Emilie Autumn", 3014),
    ("Tomorrow may be hell, but today was a good writing day, and on the good writing days nothing else matters.", "Neil Gaiman", 3014),
    ("Do not let the memories of your past limit the potential of your future. There are no limits to what you can achieve on your journey through life, except in your mind.", "Roy T. Bennett", 3013),
    ("Those who have a 'why' to live, can bear with almost any 'how'.", "Viktor E. Frankl", 3013),
    ("It is easy to love people in memory; the hard thing is to love them when they are there in front of you.", "John Updike", 3013),
    ("Lost love is still love. It takes a different form, that's all. You can't see their smile or bring them food or tousle their hair or move them around a dance floor. But when those senses weaken another heightens. Memory. Memory becomes your partner.", "Mitch Albom", 3013),
    ("Boring damned people. All over the earth. Propagating more boring damned people. What a horror show.", "Charles Bukowski", 3010),
    ("It takes something more than intelligence to act intelligently.", "Fyodor Dostoevsky", 3009),
    ("One word frees us of all the weight and pain of life: That word is love.", "Sophocles", 3007),
    ("Your visions will become clear only when you can look into your own heart. Who looks outside, dreams; who looks inside, awakes.", "C.G. Jung", 3006),
    ("Adults are just obsolete children and the hell with them.", "Dr. Seuss", 3004),

    # ===== Page 76 =====
    ("The brick walls are there for a reason. The brick walls are not there to keep us out. The brick walls are there to give us a chance to show how badly we want something.", "Randy Pausch", 2992),
    ("Blessed are the hearts that can bend; they shall never be broken.", "Albert Camus", 2991),
    ("Very few of us are what we seem.", "Agatha Christie", 2990),
    ("Whenever you feel like criticizing any one, just remember that all the people in this world haven't had the advantages that you've had.", "F. Scott Fitzgerald", 2990),
    ("The love of learning, the sequestered nooks, And all the sweet serenity of books", "Henry Wadsworth Longfellow", 2989),
    ("Trust your heart if the seas catch fire, live by love though the stars walk backward.", "E.E. Cummings", 2986),
    ("The way you get meaning into your life is to devote yourself to loving others, devote yourself to your community around you, and devote yourself to creating something that gives you purpose and meaning.", "Mitch Albom", 2986),
    ("You can make anything by writing.", "C.S. Lewis", 2986),
    ("The purpose of a storyteller is not to tell you how to think, but to give you questions to think upon.", "Brandon Sanderson", 2984),
    ("When I was about eight, I decided that the most wonderful thing, next to a human being, was a book.", "Margaret Walker", 2980),
    ("The trouble is if you don't spend your life yourself, other people spend it for you.", "Peter Shaffer", 2979),
    ("It's not always necessary to be strong, but to feel strong.", "Jon Krakauer", 2979),
    ("A library is infinity under a roof.", "Gail Carson Levine", 2978),
    ("If you have enough book space, I don't want to talk to you.", "Terry Pratchett", 2978),
    ("I used to dream about escaping my ordinary life, but my life was never ordinary. I had simply failed to notice how extraordinary it was.", "Ransom Riggs", 2977),
    ("Waste no more time arguing about what a good man should be. Be one.", "Marcus Aurelius", 2977),
    ("A woman's heart should be so hidden in God that a man has to seek Him just to find her.", "Maya Angelou", 2977),
    ("Let the improvement of yourself keep you so busy that you have no time to criticize others.", "Roy T. Bennett", 2976),
    ("The greatness of a man is not in how much wealth he acquires, but in his integrity and his ability to affect those around him positively.", "Bob Marley", 2976),

    # ===== Page 77 =====
    ("We sometimes encounter people, even perfect strangers, who begin to interest us at first sight, somehow suddenly, all at once, before a word has been spoken.", "Fyodor Dostoevsky", 2966),
    ("Black holes are where God divided by zero.", "Albert Einstein", 2966),
    ("The mark of the immature man is that he wants to die nobly for a cause, while the mark of the mature man is that he wants to live humbly for one.", "J.D. Salinger", 2964),
    ("The only thing necessary for the triumph of evil is for good men to do nothing.", "Edmund Burke", 2963),
    ("Some people have a way with words, and other people...oh, uh, not have way.", "Steve Martin", 2962),
    ("My alone feels so good, I'll only have you if you're sweeter than my solitude.", "Warsan Shire", 2961),
    ("You want to know about anybody? See what books they read, and how they've been read...", "Keri Hulme", 2961),
    ("If I had my life to live over again, I would have made a rule to read some poetry and listen to some music at least once every week.", "Charles Darwin", 2961),
    ("Selfishness is not living as one wishes to live, it is asking others to live as one wishes to live.", "Oscar Wilde", 2961),
    ("Is man merely a mistake of God's? Or God merely a mistake of man?", "Friedrich Nietzsche", 2959),
    ("To love another person is to see the face of God.", "Victor Hugo", 2957),
    ("Somewhere over the rainbow, skies are blue, and the dreams that you dare to dream really do come true.", "E.Y. Harburg", 2950),
    ("There must be those among whom we can sit down and weep and still be counted as warriors.", "Adrienne Rich", 2950),
    ("Sometimes even to live is an act of courage.", "Seneca", 2947),
    ("Never be bullied into silence. Never allow yourself to be made a victim. Accept no one's definition of your life, but define yourself.", "Harvey Fierstein", 2947),
    ("When everything goes to hell, the people who stand by you without flinching -- they are your family.", "Jim Butcher", 2946),

    # ===== Page 78 ===== (SKIPPED - timeout)

    # ===== Page 79 =====
    ("The major problem\u2014one of the major problems, for there are several\u2014one of the many major problems with governing people is that of whom you get to do it; or rather of who manages to get people to let them do it to them. To summarize: it is a well-known fact that those people who must want to rule people are, ipso facto, those least suited to do it. To summarize the summary: anyone who is capable of getting themselves made President should on no account be allowed to do the job.", "Douglas Adams", 2910),
    ("I am only responsible for my own heart, you offered yours up for the smashing my darling. Only a fool would give out such a vital organ", "Ana\u00efs Nin", 2908),
    ("Education: the path from cocky ignorance to miserable uncertainty.", "Mark Twain", 2906),
    ("Remember if people talk behind your back, it only means you are two steps ahead.", "Fannie Flagg", 2905),
    ("If the moon smiled, she would resemble you. You leave the same impression of something beautiful, but annihilating.", "Sylvia Plath", 2904),
    ("I hate to advocate drugs, alcohol, violence, or insanity to anyone, but they've always worked for me.", "Hunter S. Thompson", 2904),
    ("We are all someone's monster.", "Leigh Bardugo", 2903),
    ("It is one of life's bitterest truths that bedtime so often arrives just when things are really getting interesting.", "Lemony Snicket", 2903),
    ("Books have to be heavy because the whole world's inside them.", "Cornelia Funke", 2903),
    ("All I have seen teaches me to trust the Creator for all I have not seen.", "Ralph Waldo Emerson", 2901),
    ("Life before Death. Strength before Weakness. Journey before Destination.", "Brandon Sanderson", 2900),
    ("When you laugh, laugh like hell. And when you get angry, get good and angry. Try to be alive. You will be dead soon enough.", "William Saroyan", 2898),
    ("But if thought corrupts language, language can also corrupt thought.", "George Orwell", 2898),
    ("A man who dares to waste one hour of time has not discovered the value of life.", "Charles Darwin", 2898),
    ("You are not rich until you have a rich heart.", "Roy T. Bennett", 2897),

    # ===== Page 80 =====
    ("The more one judges, the less one loves.", "Honor\u00e9 de Balzac", 2886),
    ("No book can be appreciated until it has been slept with and dreamed over.", "Eugene Field", 2885),
    ("If you're too open-minded; your brains will fall out.", "Lawrence Ferlinghetti", 2884),
    ("In your light I learn how to love. In your beauty, how to make poems.", "Rumi", 2884),
    ("One person's craziness is another person's reality.", "Tim Burton", 2882),
    ("Better a cruel truth than a comfortable delusion.", "Edward Abbey", 2880),
    ("Nothing in life is to be feared, it is only to be understood.", "Marie Curie", 2879),
    ("Evil is always possible. And goodness is eternally difficult.", "Anne Rice", 2873),
    ("We are each our own devil, and we make this world our hell.", "Oscar Wilde", 2864),
    ("The earth laughs in flowers.", "Ralph Waldo Emerson", 2864),
    ("Things need not have happened to be true. Tales and dreams endure.", "Neil Gaiman", 2864),
    ("Only people capable of loving strongly can suffer great sorrow.", "Leo Tolstoy", 2863),
    ("To choose doubt as philosophy is akin to choosing immobility as transportation.", "Yann Martel", 2862),
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
