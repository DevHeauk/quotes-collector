"""
Goodreads Popular Quotes (pages 81~100) -> PostgreSQL goodreads_popularity 테이블 저장.

수집 일시: 2026-04-12
모든 페이지(81~100) 정상 조회 완료.
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
    # ===== Page 81 =====
    ("The soul is healed by being with children.", "Fyodor Dostoevsky", 2850),
    ("Where words leave off, music begins.", "Heinrich Heine", 2850),
    ("It must require bravery to be honest all the time.", "Veronica Roth", 2849),
    ("Words dazzle and deceive because they are mimed by the face. But black words on a white page are the soul laid bare.", "Guy de Maupassant", 2848),
    ("I'd rather die on an adventure than live standing still.", "V.E. Schwab", 2847),
    ("It ain't what they call you, it's what you answer to.", "W.C. Fields", 2845),
    ("I write differently from what I speak, I speak differently from what I think, I think differently from the way I ought to think, and so it all proceeds into deepest darkness.", "Franz Kafka", 2844),
    ("There's nowhere you can be that isn't where you're meant to be.", "John Lennon", 2843),
    ("Curiouser and curiouser!", "Lewis Carroll", 2841),
    ("I kept always two books in my pocket, one to read, one to write in.", "Robert Louis Stevenson", 2841),
    ("Anyone can hide. Facing up to things, working through them, that's what makes you strong.", "Sarah Dessen", 2840),
    ("People change and forget to tell each other.", "Lillian Hellman", 2840),
    ("Stories can conquer fear, you know. They can make the heart bigger.", "Ben Okri", 2839),
    ("To err is human, to forgive, divine.", "Alexander Pope", 2837),
    ("Sometimes things fall apart so that better things can fall together.", "Marilyn Monroe", 2836),
    ("Autumn is a second spring when every leaf is a flower.", "Albert Camus", 2836),
    ("Being entirely honest with oneself is a good exercise.", "Sigmund Freud", 2835),

    # ===== Page 82 =====
    ("Do not think that love in order to be genuine has to be extraordinary. What we need is to love without getting tired.", "Mother Teresa", 2831),
    ("One day you will ask me which is more important? My life or yours? I will say mine and you will walk away not knowing that you are my life.", "Kahlil Gibran", 2830),
    ("Learn from the mistakes of others. You can never live long enough to make them all yourself.", "Groucho Marx", 2827),
    ("Science is not only compatible with spirituality; it is a profound source of spirituality.", "Carl Sagan", 2827),
    ("You only live twice: Once when you are born and once when you look death in the face.", "Ian Fleming", 2827),
    ("Shut your eyes and see.", "James Joyce", 2825),
    ("When I say it's you I like, I'm talking about that part of you that knows that life is far more than anything you can ever see or hear or touch.", "Fred Rogers", 2824),
    ("Kind words can be short and easy to speak, but their echoes are truly endless.", "Mother Teresa", 2824),
    ("I always arrive late at the office, but I make up for it by leaving early.", "Charles Lamb", 2824),
    ("But I love your feet only because they walked upon the earth and upon the wind and upon the waters, until they found me.", "Pablo Neruda", 2822),
    ("You do have a story inside you; it lies articulate and waiting to be written — behind your silence and your suffering.", "Anne Rice", 2821),
    ("People tend to complicate their own lives, as if living weren't already complicated enough.", "Carlos Ruiz Zafón", 2818),
    ("It takes courage to love, but pain through love is the purifying fire which those who love generously know.", "Eleanor Roosevelt", 2818),
    ("Mental pain is less dramatic than physical pain, but it is more common and also more hard to bear.", "C.S. Lewis", 2817),
    ("Between two evils, I always pick the one I never tried before.", "Mae West", 2816),
    ("I like people too much or not at all. I've got to go down deep, to fall into people, to really know them.", "Sylvia Plath", 2815),

    # ===== Page 83 =====
    ("Always be a poet, even in prose.", "Charles Baudelaire", 2809),
    ("You forget what you want to remember, and you remember what you want to forget.", "Cormac McCarthy", 2808),
    ("The advantage of a bad memory is that one enjoys several times the same good things for the first time.", "Friedrich Nietzsche", 2807),
    ("If I am really a part of your dream, you'll come back one day.", "Paulo Coelho", 2806),
    ("When we're incomplete, we're always searching for somebody to complete us.", "Tom Robbins", 2805),
    ("Nothing behind me, everything ahead of me, as is ever so on the road.", "Jack Kerouac", 2804),
    ("I'd rather be hated for who I am, than loved for who I am not.", "Kurt Cobain", 2802),
    ("Parents can only give good advice or put them on the right paths, but the final forming of a person's character lies in their own hands.", "Anne Frank", 2802),
    ("Do not read as children do to enjoy themselves, or, as the ambitious do to educate themselves. No, read to live.", "Gustave Flaubert", 2801),
    ("Ignore those that make you fearful and sad, that degrade you back towards disease and death.", "Rumi", 2799),
    ("Whenever you feel like criticizing any one, just remember that all the people in this world haven't had the advantages that you've had.", "F. Scott Fitzgerald", 2799),
    ("Life starts all over again when it gets crisp in the fall.", "F. Scott Fitzgerald", 2798),
    ("I'd rather die my way than live yours.", "Lauren Oliver", 2798),
    ("The voice of the sea speaks to the soul.", "Kate Chopin", 2797),

    # ===== Page 84 =====
    ("The more I read, the more I acquire, the more certain I am that I know nothing.", "Voltaire", 2785),
    ("All happiness depends on courage and work.", "Honoré de Balzac", 2780),
    ("For me, I am driven by two main philosophies: know more today about the world than I knew yesterday and lessen the suffering of others.", "Neil deGrasse Tyson", 2783),
    ("Silence, I discover, is something you can actually hear.", "Haruki Murakami", 2783),
    ("Scars have the strange power to remind us that our past is real.", "Cormac McCarthy", 2783),
    ("If you liked being a teenager, there's something really wrong with you.", "Stephen King", 2783),
    ("Some walks you have to take alone.", "Suzanne Collins", 2779),
    ("If everybody is thinking alike, then somebody isn't thinking.", "George S. Patton Jr.", 2772),

    # ===== Page 85 =====
    ("Man is the cruelest animal.", "Friedrich Nietzsche", 2762),
    ("I think; therefore I am.", "René Descartes", 2761),
    ("Marriage can wait, education cannot.", "Khaled Hosseini", 2761),
    ("Even after all this time the Sun never says to the Earth, 'You owe me.'", "Hafiz", 2761),
    ("We learn from failure, not from success!", "Bram Stoker", 2761),
    ("Hope is a waking dream.", "Aristotle", 2759),
    ("Books serve to show a man that those original thoughts aren't very new.", "Abraham Lincoln", 2759),
    ("The only real prison is fear, and the only real freedom is freedom from fear.", "Aung San Suu Kyi", 2758),
    ("Fiction is the lie through which we tell the truth.", "Albert Camus", 2758),
    ("The good thing about science is that it's true whether or not you believe in it.", "Neil deGrasse Tyson", 2757),
    ("I have nothing to declare except my genius.", "Oscar Wilde", 2752),
    ("It doesn't matter. I have books, new books, and I can bear anything as long as there are books.", "Jo Walton", 2749),
    ("No great mind has ever existed without a touch of madness.", "Aristotle", 2743),
    ("Anybody can sympathise with the sufferings of a friend, but it requires a very fine nature to sympathise with a friend's success.", "Oscar Wilde", 2747),
    ("At the end of the day, we can endure much more than we think we can.", "Frida Kahlo", 2740),

    # ===== Page 86 =====
    ("The only lies for which we are truly punished are those we tell ourselves.", "V.S. Naipaul", 2735),
    ("Absence diminishes small loves and increases great ones, as the wind blows out the candle and fans the bonfire.", "François de La Rochefoucauld", 2732),
    ("Maybe some people are just meant to be in the same story.", "Jandy Nelson", 2729),
    ("I know of a cure for everything: salt water...in one way or the other. Sweat, or tears, or the salt sea.", "Karen Blixen", 2727),
    ("I'm killing time while I wait for life to shower me with meaning and happiness.", "Bill Watterson", 2726),
    ("The future depends on what you do today.", "Mahatma Gandhi", 2723),
    ("Intelligence plus character-that is the goal of true education.", "Martin Luther King Jr.", 2723),
    ("I am not what happened to me, I am what I choose to become.", "C.G. Jung", 2722),
    ("The things you used to own, now they own you.", "Chuck Palahniuk", 2721),
    ("Courage isn't having the strength to go on - it is going on when you don't have strength.", "Napoléon Bonaparte", 2719),

    # ===== Page 87 =====
    ("Alone. Yes, that's the key word, the most awful word in the English tongue.", "Stephen King", 2715),
    ("A man's face is his autobiography. A woman's face is her work of fiction.", "Oscar Wilde", 2712),
    ("Wanting to be someone else is a waste of the person you are.", "Marilyn Monroe", 2710),
    ("Books are no more threatened by Kindle than stairs by elevators.", "Stephen Fry", 2710),
    ("This is how you do it: you sit down at the keyboard and you put one word after another until its done.", "Neil Gaiman", 2708),
    ("Either you deal with what is the reality, or you can be sure that the reality is going to deal with you.", "Alex Haley", 2707),
    ("Have you ever asked yourself, do monsters make war, or does war make monsters?", "Laini Taylor", 2707),
    ("If you want to get laid, go to college. If you want an education, go to the library.", "Frank Zappa", 2706),
    ("It is nothing to die. It is frightful not to live.", "Victor Hugo", 2703),
    ("The best way to cheer yourself is to cheer somebody else up.", "Albert Einstein", 2703),
    ("Shoot for the moon. Even if you miss, you'll land among the stars.", "Norman Vincent Peale", 2703),

    # ===== Page 88 =====
    ("there is a place in the heart that will never be filled", "Charles Bukowski", 2693),
    ("Trees that are slow to grow bear the best fruit.", "Molière", 2691),
    ("No winter lasts forever; no spring skips its turn.", "Hal Borland", 2689),
    ("It's so much darker when a light goes out than it would have been if it had never shone.", "John Steinbeck", 2689),
    ("What a blessing it is to love books as I love them.", "Thomas Babington Macaulay", 2688),
    ("I am a forest, and a night of dark trees.", "Friedrich Nietzsche", 2682),
    ("I know not all that may be coming, but be it what it will, I'll go to it laughing.", "Herman Melville", 2682),
    ("When will you learn that there isn't a word for everything?", "Nicole Krauss", 2683),
    ("Fashion is a form of ugliness so intolerable that we have to alter it every six months.", "Oscar Wilde", 2684),
    ("Whoever is careless with the truth in small matters cannot be trusted with important matters.", "Albert Einstein", 2681),
    ("The best way to not feel hopeless is to get up and do something.", "Barack Obama", 2681),

    # ===== Page 89 =====
    ("We can't be afraid of change. You may feel very secure in the pond that you are in, but if you never venture out of it, you will never know that there is such a thing as an ocean, a sea.", "C. JoyBell C.", 2668),
    ("When you consider things like the stars, our affairs don't seem to matter very much, do they?", "Virginia Woolf", 2668),
    ("Life is either a daring adventure or nothing at all.", "Helen Keller", 2665),
    ("to love life, to love it even when you have no stomach for it.", "Ellen Bass", 2665),
    ("It isn't what we say or think that defines us, but what we do.", "Jane Austen", 2662),
    ("Do you not see how necessary a world of pains and troubles is to school an intelligence and make it a soul?", "John Keats", 2662),
    ("Don't cry over someone who wouldn't cry over you.", "Lauren Conrad", 2659),
    ("The earth has its music for those who will listen.", "Reginald Vincent Holmes", 2659),
    ("Great minds discuss ideas. Average minds discuss events. Small minds discuss people.", "Henry Thomas Buckle", 2658),
    ("There are two ways of spreading light: to be the candle or the mirror that receives it.", "Edith Wharton", 2656),
    ("It is easy in the world to live after the world's opinion; it is easy in solitude to live after our own; but the great man is he who in the midst of the crowd keeps with perfect sweetness the independence of solitude.", "Ralph Waldo Emerson", 2655),

    # ===== Page 90 =====
    ("To do the useful thing, to say the courageous thing, to contemplate the beautiful thing: that is enough for one man's life.", "T.S. Eliot", 2644),
    ("Freedom lies in being bold.", "Robert Frost", 2644),
    ("You can only be young once. But you can always be immature.", "Pat Monahan", 2644),
    ("Never let anyone make you feel ordinary.", "Taylor Jenkins Reid", 2641),
    ("All a girl really wants is for one guy to prove to her that they are not all the same.", "Marilyn Monroe", 2640),
    ("If you never did you should. These things are fun and fun is good.", "Dr. Seuss", 2640),
    ("There are moments when troubles enter our lives and we can do nothing to avoid them. But they are there for a reason.", "Paulo Coelho", 2638),
    ("If you are distressed by anything external, the pain is not due to the thing itself, but to your estimate of it.", "Marcus Aurelius", 2638),

    # ===== Page 91 =====
    ("There are nights when the wolves are silent and only the moon howls.", "George Carlin", 2627),
    ("Lovers don't finally meet somewhere. They're in each other all along.", "Rumi", 2627),
    ("When I do good, I feel good. When I do bad, I feel bad. That's my religion.", "Abraham Lincoln", 2627),
    ("If you have the words, there's always a chance that you'll find the way.", "Seamus Heaney", 2625),
    ("Laughter is wine for the soul - laughter soft, or loud and deep.", "Sean O'Casey", 2624),
    ("This is a new year. A new beginning. And things will change.", "Taylor Swift", 2621),
    ("Look at everything always as though you were seeing it either for the first or last time.", "Betty Smith", 2620),
    ("The best way out is always through.", "Robert Frost", 2619),
    ("Only a generation of readers will spawn a generation of writers.", "Steven Spielberg", 2618),
    ("Real generosity towards the future lies in giving all to the present.", "Albert Camus", 2617),
    ("As long as she thinks of a man, nobody objects to a woman thinking.", "Virginia Woolf", 2616),
    ("Many people will walk in and out of your life, but only true friends leave footprints.", "Eleanor Roosevelt", 2616),
    ("We do not need magic to transform our world. We carry all the power inside ourselves.", "J.K. Rowling", 2615),

    # ===== Page 92 =====
    ("You can't wait for inspiration. You have to go after it with a club.", "Jack London", 2608),
    ("Luxury is not a necessity to me, but beautiful and good things are.", "Anais Nin", 2608),
    ("The only person you are destined to become is the person you decide to be.", "Ralph Waldo Emerson", 2606),
    ("The past is never where you think you left it.", "Katherine Anne Porter", 2606),
    ("It is better, I think, to grab at the stars than to sit flustered because you know you cannot reach them.", "R.A. Salvatore", 2605),
    ("When you trip over love, it is easy to get up. But when you fall in love, it is impossible to stand again.", "Albert Einstein", 2605),
    ("Be glad. Be good. Be brave.", "Eleanor Hodgman Porter", 2604),
    ("Maybe this world is another planet's hell.", "Aldous Huxley", 2604),
    ("Feminism is the radical notion that women are human beings.", "Cheris Kramarae", 2603),
    ("If I read a book and it makes my whole body so cold no fire can ever warm me, I know that is poetry.", "Emily Dickinson", 2602),
    ("The desire to reach for the stars is ambitious. The desire to reach hearts is wise.", "Maya Angelou", 2599),
    ("Literature is a luxury; fiction is a necessity.", "G.K. Chesterton", 2595),
    ("I am beginning to learn that it is the sweet, simple things of life which are the real ones after all.", "Laura Ingalls Wilder", 2593),
    ("A man is but the product of his thoughts. What he thinks, he becomes.", "Mahatma Gandhi", 2597),
    ("Do not set aside your happiness. Do not wait to be happy in the future. The best time to be happy is always now.", "Roy T. Bennett", 2596),
    ("Name the greatest of all inventors. Accident.", "Mark Twain", 2596),
    ("Literature is a textually transmitted disease, normally contracted in childhood.", "Jane Yolen", 2597),

    # ===== Page 93 =====
    ("I don't mind making jokes, but I don't want to look like one.", "Marilyn Monroe", 2591),
    ("However many holy words you read, however many you speak, what good will they do you if you do not act on upon them?", "Buddha", 2591),
    ("My life has a superb cast, but I cannot figure out the plot.", "Ashleigh Brilliant", 2589),
    ("We dream to give ourselves hope. To stop dreaming - well, that's like saying you can never change your fate.", "Amy Tan", 2588),
    ("The way to get started is to quit talking and begin doing.", "Walt Disney", 2588),
    ("The man who moves a mountain begins by carrying away small stones.", "Confucius", 2586),
    ("All our dreams can come true, if we have the courage to pursue them.", "Walt Disney", 2586),
    ("In one aspect, yes, I believe in ghosts, but we create them. We haunt ourselves.", "Laurie Halse Anderson", 2583),
    ("Another belief of mine: that everyone else my age is an adult, whereas I am merely in disguise.", "Margaret Atwood", 2583),
    ("The longer I live, the more I observe that carrying around anger is the most debilitating to the person who bears it.", "Katharine Graham", 2581),
    ("Music is a higher revelation than all Wisdom & Philosophy.", "Ludwig van Beethoven", 2581),
    ("I love you as certain dark things are loved, secretly, between the shadow and the soul.", "Pablo Neruda", 2578),
    ("The mystery of life isn't a problem to solve, but a reality to experience.", "Frank Herbert", 2576),

    # ===== Page 94 =====
    ("Children learn more from what you are than what you teach.", "W.E.B. Du Bois", 2566),
    ("What draws people to be friends is that they see the same truth.", "C.S. Lewis", 2566),
    ("Now that she had nothing to lose, she was free.", "Paulo Coelho", 2565),
    ("How do I love thee? Let me count the ways. I love thee to the depth and breadth and height my soul can reach.", "Elizabeth Barrett Browning", 2564),
    ("Freedom (n.): To ask nothing. To expect nothing. To depend on nothing.", "Ayn Rand", 2563),
    ("Listen with curiosity. Speak with honesty. Act with integrity.", "Roy T. Bennett", 2562),
    ("There is nothing more deceptive than an obvious fact.", "Arthur Conan Doyle", 2562),
    ("Not everything that is faced can be changed, but nothing can be changed until it is faced.", "James Baldwin", 2559),
    ("The mountains are calling and I must go.", "John Muir", 2556),
    ("Imagination is like a muscle. I found out that the more I wrote, the bigger it got.", "Philip José Farmer", 2555),
    ("With enough courage, you can do without a reputation.", "Margaret Mitchell", 2555),

    # ===== Page 95 =====
    ("But until a person can say deeply and honestly, 'I am what I am today because of the choices I made yesterday,' that person cannot say, 'I choose otherwise.'", "Stephen R. Covey", 2547),
    ("Lord, what fools these mortals be!", "William Shakespeare", 2544),
    ("A short story is a different thing altogether - a short story is like a quick kiss in the dark from a stranger.", "Stephen King", 2544),
    ("We dream in our waking moments, and walk in our sleep.", "Nathaniel Hawthorne", 2543),
    ("So it's true, when all is said and done, grief is the price we pay for love.", "E.A. Bucchianeri", 2543),
    ("The most terrible poverty is loneliness, and the feeling of being unloved.", "Mother Teresa", 2543),
    ("To die, it's easy. But you have to struggle for life.", "Art Spiegelman", 2541),
    ("It was the best of times, it was the worst of times.", "Charles Dickens", 2540),
    ("No one is useless in this world who lightens the burdens of another.", "Charles Dickens", 2536),
    ("Some things in life are out of your control. You can make it a party or a tragedy.", "Nora Roberts", 2536),

    # ===== Page 96 =====
    ("Too many of us are hung up on what we don't have, can't have, or won't ever have.", "Terry McMillan", 2525),
    ("Let no one ever come to you without leaving better and happier.", "Mother Teresa", 2524),
    ("Throw your dreams into space like a kite, and you do not know what it will bring back.", "Anaïs Nin", 2522),
    ("Why do beautiful songs make you sad? Because they aren't true.", "Jonathan Safran Foer", 2521),
    ("After a good dinner one can forgive anybody, even one's own relations.", "Oscar Wilde", 2520),
    ("That which you believe becomes your world.", "Richard Matheson", 2519),
    ("My religion is very simple. My religion is kindness.", "Dalai Lama XIV", 2518),
    ("Nothing takes the taste out of peanut butter quite like unrequited love.", "Charles M. Schulz", 2518),
    ("When you read a book, you hold another's mind in your hands.", "James Burke", 2517),
    ("Don't waste your love on somebody who doesn't value it.", "William Shakespeare", 2516),
    ("Humor is reason gone mad.", "Groucho Marx", 2516),
    ("Of course I'll hurt you. Of course you'll hurt me. Of course we will hurt each other. But this is the very condition of existence.", "Antoine de Saint-Exupéry", 2514),
    ("We do not remember days, we remember moments.", "Jennifer Niven", 2513),

    # ===== Page 97 =====
    ("Always be a first rate version of yourself and not a second rate version of someone else.", "Judy Garland", 2507),
    ("Man often becomes what he believes himself to be. If I keep on saying to myself that I cannot do a certain thing, it is possible that I may end by really becoming incapable of doing it.", "Mahatma Gandhi", 2506),
    ("Sometimes, the best way to help someone is just to be near them.", "Veronica Roth", 2504),
    ("Happiness is not the absence of problems, it's the ability to deal with them.", "Steve Maraboli", 2503),
    ("Every deep thinker is more afraid of being understood than of being misunderstood.", "Friedrich Nietzsche", 2503),
    ("This is where it all begins. Everything starts here, today.", "David Nicholls", 2502),
    ("You may tell a tale that takes up residence in someone's soul, becomes their blood and self and purpose.", "Erin Morgenstern", 2500),
    ("Reading is like thinking, like praying, like talking to a friend, like expressing your ideas.", "Roberto Bolaño", 2500),
    ("Poetry is what gets lost in translation.", "Robert Frost", 2498),
    ("I talk to God but the sky is empty.", "Sylvia Plath", 2496),

    # ===== Page 98 =====
    ("We should meet in another life, we should meet in air, me and you.", "Sylvia Plath", 2490),
    ("You get what anybody gets - you get a lifetime.", "Neil Gaiman", 2490),
    ("We are travelers on a cosmic journey, stardust, swirling and dancing in the eddies and whirlpools of infinity.", "Paulo Coelho", 2489),
    ("People are capable, at any time in their lives, of doing what they dream of.", "Paulo Coelho", 2489),
    ("The mind I love must have wild places.", "Katherine Mansfield", 2486),
    ("To give pleasure to a single heart by a single act is better than a thousand heads bowing in prayer.", "Mahatma Gandhi", 2486),
    ("Dare to live the life you have dreamed for yourself. Go forward and make your dreams come true.", "Ralph Waldo Emerson", 2485),
    ("I'm always happy. Sometimes I just forget.", "Jennifer Egan", 2484),
    ("The starting point of all achievement is DESIRE. Keep this constantly in mind.", "Napoleon Hill", 2484),
    ("The higher we soar the smaller we appear to those who cannot fly.", "Friedrich Nietzsche", 2484),
    ("sex is the consolation you have when you can't have love.", "Gabriel García Márquez", 2483),
    ("We don't need lists of rights and wrongs; we need books, time, and silence.", "Philip Pullman", 2483),
    ("I think and think and think, I've thought myself out of happiness one million times.", "Jonathan Safran Foer", 2482),
    ("Man, when you lose your laugh you lose your footing.", "Ken Kesey", 2481),
    ("If I am not good to myself, how can I expect anyone else to be good to me?", "Maya Angelou", 2479),
    ("Others have seen what is and asked why. I have seen what could be and asked why not.", "Pablo Picasso", 2479),
    ("Learn the rules, break the rules, make up new rules, break the new rules.", "Marvin Bell", 2478),

    # ===== Page 99 =====
    ("Years of love have been forgot, in the hatred of a minute.", "Edgar Allan Poe", 2476),
    ("Help others without any reason and give without the expectation of receiving anything in return.", "Roy T. Bennett", 2475),
    ("It's only those who do nothing that make no mistakes, I suppose.", "Joseph Conrad", 2475),
    ("Life has no remote....get up and change it yourself!", "Mark A. Cooper", 2474),
    ("If everybody minded their own business, the world would go around a great deal faster than it does.", "Lewis Carroll", 2474),
    ("Because when you're scared but you still do it anyway, that's brave.", "Neil Gaiman", 2474),
    ("I like it when a flower or a little tuft of grass grows through a crack in the concrete. It's so heroic.", "George Carlin", 2474),
    ("Silly things do cease to be silly if they are done by sensible people in an impudent way.", "Jane Austen", 2474),
    ("Let others praise ancient times; I am glad I was born in these.", "Ovid", 2473),
    ("In the moment when I truly understand my enemy, understand him well enough to defeat him, then in that very moment I also love him.", "Orson Scott Card", 2473),
    ("My life is a perfect graveyard of buried hopes.", "L.M. Montgomery", 2472),

    # ===== Page 100 =====
    ("Whatever you do, you need courage.", "Ralph Waldo Emerson", 2466),
    ("You're something between a dream and a miracle.", "Elizabeth Barrett Browning", 2465),
    ("History does not always repeat itself. Sometimes it just yells, 'Can't you remember anything I told you?'", "John W. Campbell Jr.", 2463),
    ("May your trails be crooked, winding, lonesome, dangerous, leading to the most amazing view.", "Edward Abbey", 2463),
    ("The unhappiest people in this world, are those who care the most about what other people think.", "C. JoyBell C.", 2463),
    ("Half the world is composed of people who have something to say and can't, and the other half who have nothing to say and keep on saying it.", "Robert Frost", 2463),
    ("If you know the enemy and know yourself, you need not fear the result of a hundred battles.", "Sun Tzu", 2463),
    ("If you try to fail, and succeed, which have you done?", "George Carlin", 2462),
    ("Love makes your soul crawl out from its hiding place.", "Zora Neale Hurston", 2461),
    ("There is no point treating a depressed person as though she were just feeling sad.", "Barbara Kingsolver", 2460),
    ("We are always the same age inside.", "Gertrude Stein", 2459),
    ("I restore myself when I'm alone.", "Marilyn Monroe", 2458),
    ("If we listened to our intellect we'd never have a love affair.", "Ray Bradbury", 2458),
    ("Life doesn't imitate art, it imitates bad television.", "Woody Allen", 2457),
    ("I know some who are constantly drunk on books as other men are drunk on whiskey.", "H.L. Mencken", 2453),
    ("When another person makes you suffer, it is because he suffers deeply within himself.", "Thich Nhat Hanh", 2450),
]


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    inserted = 0
    skipped = 0

    for quote_text, author_name, likes in QUOTES_DATA:
        # 중복 체크
        cur.execute(
            "SELECT 1 FROM goodreads_popularity WHERE quote_text = %s",
            (quote_text,),
        )
        if cur.fetchone():
            skipped += 1
            continue

        quote_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO goodreads_popularity (id, quote_text, author_name, likes)
            VALUES (%s, %s, %s, %s)
            """,
            (quote_id, quote_text, author_name, likes),
        )
        inserted += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"총 데이터 수: {len(QUOTES_DATA)}")
    print(f"새로 저장: {inserted}")
    print(f"중복 스킵: {skipped}")


if __name__ == "__main__":
    main()
