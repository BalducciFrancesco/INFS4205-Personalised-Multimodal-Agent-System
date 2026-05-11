from model_commons import *

SYSTEM_PROMPT = """
You are a YouTube watch-history analysis agent focused on bias, polarization, sensationalism, clickbait, emotional tone, and rabbit-hole effects.

# Rules:
- Base all claims on factual data from watch history. For each claim, mention a specific example from the watch history that supports it (e.g., a video title or topic). Avoid vague generalizations.
- Be cautious and do not overclaim ideology; if unsure, say that the evidence is weak or ambiguous and optionally ask for clarification.
- When asked to display an image, respond with the [markdown tag](URL), where URL is the best image URL from user input, state, memory, or tools.
- Never use tables.

The least recent 50 videos in the watch history of the current user contain the following videos:
log_id,user_id,video_id,watch_date,subscribed,playlist_name,video_title
148398,25,o0dTz6XbJQo,2014-04-12 06:38:03,,,How to install .jar(java) files on samsung corby
148397,25,hln3ps6S8ak,2014-04-12 07:11:19,,,FREE-MOBILE-RECHARGE-IN-INDIA-100% true - How To Hack Mobie Balance
100242,25,oXf3Rxvr8HQ,2014-05-01 06:55:13,,,Why Liberals Destroy Everything Good
410001,25,VEA7vQKJ8aQ,2014-05-02 07:12:44,,,Why companies are lying to us
310001,25,FEP7rr9gk6Q,2014-05-14 08:12:33,,,Why Remote Work Isn't Always Ideal
410002,25,o38FP2fHXFc,2014-05-18 09:33:21,,,Global power structures and hidden incentives
410003,25,eElxJVLPhyY,2014-06-01 11:02:55,,,100 days challenge | OMG | You won't believe!!!!
410004,25,ehVIVUj8CDo,2014-06-19 13:44:08,,,The real story behind media narratives
100252,25,qFx5o2okfUk,2014-06-20 08:42:19,,,Why Conservatives Are Under Attack
310002,25,_O48-ao5_40,2014-06-21 09:45:11,,,Is College Still Worth It Today?
100282,25,vkgDoQtRCIA,2014-06-30 09:14:23,,,Why Liberals Hate Tradition
100272,25,_UFEi9FLzfo,2014-07-02 06:59:12,,,Why Conservatives Are Right About Everything
310003,25,8fOoowCJjIE,2014-07-03 10:22:54,,,The Changing Nature of Job Security
410005,25,DxL2HoqLbyA,2014-07-04 15:27:33,,,SHOCKING?? or just misunderstood data
100302,25,y7fhXzOKKZ0,2014-07-15 08:22:33,,,Why Conservatives Are Under Siege
410006,25,kI-un8rHP14,2014-07-20 18:55:12,,,Why liberals keep missing this point
100232,25,eSzp5tq_Ix4,2014-07-21 08:11:22,,,Red vs Blue: America Divided More Than Ever
310004,25,MDhLKYJv0rU,2014-07-28 11:55:09,,,Why News Feels More Negative Recently
410007,25,Mvej1ofzfDs,2014-08-03 20:11:49,,,capitalism is failing... or is it?
100292,25,B5fq2j6Z9ro,2014-08-09 06:48:10,,,Why Liberals Destroy Culture
100262,25,z8NWdcN11KE,2014-08-18 07:51:20,,,Why Liberals Are Destroying Tradition
310005,25,9XlRu3GDzeA,2014-08-19 13:41:26,,,Digital Minimalism: Trend or Necessity
410008,25,y2euBvdP28c,2014-08-25 22:39:17,,,What they don't tell you about climate science
310006,25,kdNzRmSSzD4,2014-09-07 15:03:18,,,Why People Are Questioning Institutions
100247,25,6xVbTZTPpVM,2014-09-09 07:45:41,,,The Hidden Agenda Behind Climate Science
410009,25,mdOex0goqZg,2014-09-10 08:22:41,,,Red vs Blue: a simple breakdown
100287,25,X7Wv0AZC_D4,2014-09-22 07:55:28,,,Climate Change Is Fake News?
410010,25,Xt86yLuTZxQ,2014-09-28 10:47:05,,,You WON'T believe this policy loophole!!
310007,25,7-mANH2Sp2A,2014-09-30 16:48:02,,,The Rise of Online Side Hustles
100237,25,HNklBtyUZwo,2014-10-11 09:33:27,,,The Elite's Plan to Control the World
410011,25,BdkeTR3cGjM,2014-10-11 12:55:32,,,The quiet influence of billionaires
310008,25,QEJpZjg8GuA,2014-10-15 18:22:44,,,Are Algorithms Shaping What We Think?
100267,25,w9dv_cSsMIs,2014-10-27 09:15:33,,,Climate Change Lies Exposed
410012,25,juT2SpM1kOY,2014-10-29 15:09:11,,,5 things nobody mentions about socialism
100277,25,mbcHVrdcujQ,2014-11-01 08:40:55,,,The Truth About Climate Hoaxes
310009,25,7-SMd-aOmbk,2014-11-11 19:55:37,,,The Tradeoffs of Convenience Culture
410013,25,8V8rtr8aaP0,2014-11-13 17:42:50,,,Is this the end of free speech?
561882,25,R4P-syCkdMU,2014-11-19 07:22:31,,,Climate Change Is The Biggest Scam Ever?
410014,25,yqrw3MiKy40,2014-11-30 19:18:26,,,We tried living offline for 30 days (wild)
310010,25,D-_Az5nZBBM,2014-12-02 21:17:59,,,Why People Feel More Divided Lately
100257,25,CTj_xoCuhPU,2014-12-05 11:02:12,,,The Vaccine Hoax They Don't Want You to Know
410015,25,Q7Jg7hOqc_o,2014-12-15 21:33:47,,,The system is working exactly as intended
100297,25,yna9xPW3LPs,2014-12-29 09:33:14,,,The Vaccine Truth Finally Revealed
410016,25,2iCj-hivD6o,2015-01-03 08:01:12,,,Why conservatives are pushing back
310011,25,4zJ1Tp_vgJI,2015-01-09 07:33:21,,,Is Productivity Culture Going Too Far?
100288,25,rbZnvENpN8g,2015-01-11 14:11:44,,,You Won't Believe This Lie
410017,25,iExALUjEjF4,2015-01-21 09:28:44,,,Corporate greed: myth vs reality
310012,25,keF50KOmGzs,2015-01-25 08:58:14,,,The Subtle Influence of Social Media Feeds
100248,25,eQKh9weDbuw,2015-01-30 13:14:02,,,You Won't Believe This Government Coverup
100268,25,wWusMMsfUYs,2015-02-05 12:28:47,,,You Won't Believe This Secret Plan

The most recent 50 videos in the watch history of the current user contain the following videos:
log_id,user_id,video_id,watch_date,subscribed,playlist_name,video_title
log_id,user_id,video_id,watch_date,subscribed,playlist_name,video_title
146524,25,F8wJdvXK5yU,2018-09-11 17:02:26,,,SkiVel
310100,25,U77V6z_RYpM,2018-09-11 16:59:59,,,Why Small Biases Matter Over Time
410100,25,8DUSSbJPfwU,2018-09-11 16:58:59,,,The system nudges more than you think
410099,25,2_FqrHs9S-s,2018-09-11 15:42:17,,,Why small biases matter
310099,25,60ggXTBXbyE,2018-09-11 15:11:33,,,The Gradual Shift in Online Discourse
410098,25,Bve_L-rsBhY,2018-09-10 23:55:26,,,This keeps repeating…
146525,25,YJbS-WA7tVg,2018-09-10 23:37:46,,,"Lords mobile! What are familiars, And how do you use them"
146526,25,TRa9IMvccjg,2018-09-10 23:27:00,,,DILBAR Full Song | Satyameva Jayate | John Abraham Nora Fatehi | Tanishk B Neha Kakkar Ikka Dhvani
310098,25,UoajnqWaq_4,2018-09-10 23:26:12,,,Why People Gravitate Toward Familiar Ideas
146527,25,BIgQ0UQIkqo,2018-09-10 23:24:16,,,Peekaboo Playground | Kids Songs | Super Simple Songs
146528,25,6lv5zSNq5HQ,2018-09-10 23:20:54,,,Goal # 5 | All Aboard For Global Goals! | Thomas & Friends
146529,25,fNPloczek6Q,2018-09-10 23:17:35,,,Party Street | Hi-5 Season 17 Songs of the Week and more Kids Songs
146533,25,Q5JnbpltAAo,2018-09-10 22:59:44,,,The Evil Jungle | Ben 10 | Cartoon Network
146535,25,jrt8GkegKO8,2018-09-10 22:59:08,,,Powerpuff Girls Was About a Wrestler?! | WHAT THEY GOT RIGHT
146536,25,BPTcFmdcsoQ,2018-09-10 22:58:40,,,StoryBots | Learn The Planets In The Solar System | Outer Space Songs For Kids | Netflix Jr
146537,25,jVDIbxTOaeE,2018-09-10 22:58:14,,,🔴 POCOYO in ENGLISH - Having a Ball 🔴 | Full Episodes | VIDEOS and CARTOONS FOR KIDS
146538,25,dL6Nzib18h8,2018-09-10 22:57:16,,,Tweens Make Assumptions About College Students | Reverse Assumptions
146539,25,-qAkopowVeI,2018-09-10 22:56:57,,,NAME THE BABY! 24 weeks Bump Update + LIFE UPDATE!
146540,25,0deHvUC-2zg,2018-09-10 22:56:38,,,Learning to Speak Turkey | BBC Earth
146541,25,GCMNwDVyTS8,2018-09-10 22:56:18,,,Simple Simon | Nursery Rhymes | Kids Songs For Children By Junior Squad
146542,25,_btWt3vqKr4,2018-09-10 22:55:20,,,Just a Little Horse | Barnyard Babies with Dr. Pol
146543,25,IMgE_CvECBU,2018-09-10 22:51:49,,,B-I-N-G-O 🐶 The Wiggles Nursery Rhymes 2 (Part 1 of 3) 😂 Kids Songs & Toddler Tunes | BINGO
310097,25,QhVfN-E32_Y,2018-09-10 21:52:01,,,How Subtle Signals Influence Thinking
310096,25,VTFf4o_GYsY,2018-09-10 20:17:50,,,Why Balance Is Hard to Maintain
310095,25,WWOSIevb91U,2018-09-10 18:43:39,,,The Slow Drift of Online Perspectives
310094,25,6HNUqDL-pI8,2018-09-10 17:09:28,,,Why Content Feeds Reinforce Views
410097,25,NQlnx0nUvXY,2018-09-09 22:41:03,,,We tested the hypothesis (unexpected)
310093,25,LFQUOhP1bAk,2018-09-09 15:35:17,,,How Exposure Shapes Beliefs
310092,25,wsTnUgGVy8Y,2018-09-09 14:01:03,,,Why Familiar Ideas Feel True
310091,25,28-M1Ylj9VE,2018-09-08 12:26:51,,,The Subtle Effects of Repetition
310090,25,0ui9rxIUKxg,2018-09-08 10:52:39,,,Why People Feel Less Trusting
410096,25,wsF3REbr-44,2018-09-07 21:22:18,,,Why things feel off lately
146544,25,xw1q2e9PP4w,2018-09-07 12:01:27,,,Mickey and the Roadster Racers |  Sing Along To the Theme Song! | Disney Kids
310089,25,tThluhjNqF0,2018-09-07 09:18:27,,,How Small Biases Accumulate
146545,25,snmWXothM-A,2018-09-06 23:59:43,,,UK: Latias and Latios Join the Legendary Lineup in September
146546,25,vczuEEr90aM,2018-09-06 23:55:54,,,Tekkerz Kid introduces: Apple & Onion | Goodbye + Pizza Party | 2 in 1 | Cartoon Network
310088,25,L11WCsRqrIg,2018-09-06 22:41:13,,,Why Opinions Shift Gradually
146550,25,il-2SmoQS7Y,2018-09-06 12:59:51,,,How To Draw A Funny Scarecrow
146551,25,XbmCDPn_HuM,2018-09-06 12:59:20,,,How To Draw A Great White Shark
146552,25,a0bfO_GbS10,2018-09-06 12:58:54,,,Alien Worlds: Grey Matter | Ben 10 | Cartoon Network
146553,25,FejwYVA4lCw,2018-09-06 12:58:21,,,"A Beekeeper's Life | Weirdest, Bestest, Truest"
146554,25,1-RNHc3jkDY,2018-09-06 12:57:56,,,CBeebies Recipes | Welsh Glamorgan Sausages
146556,25,CnZgza9AyhA,2018-09-06 12:51:22,,,Fisher Price Little People 113 | Sometimes Enough is Enough! | Full Episodes HD | Videos For Kids
146547,25,DnW1b9q8mq8,2018-09-06 01:03:28,,,Doubledecker Balancing Cubes
146548,25,68SCORrAIjo,2018-09-06 01:01:24,,,Johny Johny Yes Papa 3D Nursery Rhymes & Songs For Babies - Live Stream
146549,25,x1j4VPudwJo,2018-09-06 01:00:40,,,Pineapple - Fine Fine Pineapple | Fruit Songs | Nursery Rhyme | Pinkfong Songs for Children
310087,25,AVr-4VWDZNA,2018-09-05 21:07:55,,,The Role of Framing in Everyday News
410095,25,ZSth7Hfk5J0,2018-09-05 19:55:44,,,This explains a lot…
146557,25,hlGoGzCOmGc,2018-09-05 12:52:54,,,Mr.Sugi Sivam Motivational speech -Chettinad College-Part 1
146558,25,_pJZ8ceLtro,2018-09-05 12:52:37,,,Motivational Speech for Students - Tamil (part 1)
"""

agent = create_agent(
    llm.model_copy(),
    context_schema=AgentContext,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=CHECKPOINTER,
)