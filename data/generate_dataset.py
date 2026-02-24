"""
Generate a synthetic YouTube-style spam comments dataset.
Modeled after the YouTube Spam Collection Dataset (~2000 comments).
Columns: COMMENT_ID, AUTHOR, DATE, CONTENT, CLASS (1=spam, 0=ham)
"""

import csv
import random
import os
import uuid
from datetime import datetime, timedelta

# ─── Spam Templates ─────────────────────────────────────────────────────────
SPAM_TEMPLATES = [
    # Scam links
    "Check out this amazing deal at {link}",
    "Free iPhones! Go to {link} now!!!",
    "I made $5000 in one week! Visit {link}",
    "Want free followers? Click {link}",
    "Get rich quick! {link}",
    "OMG this actually works!! {link} 💰💰💰",
    "Subscribe to my channel {link} for free gifts!",
    "Hey check my channel out {link}",
    "Visit {link} to get 1000 free subscribers!",
    "Earn money online easily! {link}",
    "I just got a free PS5 from {link}!!!",
    "Win a $1000 gift card at {link}",
    "FREE ROBUX! Go to {link} right now!",
    "Click here for free V-Bucks {link}",
    "Best deals ever at {link} 🔥🔥🔥",
    # Fake promotions
    "Sub4Sub anyone??? Subscribe to me and I'll subscribe back!!!",
    "PLEASE SUBSCRIBE TO MY CHANNEL I NEED 1000 SUBS",
    "Like if you agree! Sub to my channel for more!",
    "First comment! Check my channel out plz!",
    "Who's watching in 2024? Sub to me btw",
    "I bet you can't subscribe to my channel!",
    "Check out my new song on my channel!!!",
    "My channel is better than this one lol subscribe",
    "SUBSCRIBE OR BAD LUCK FOR 7 YEARS!!!",
    "If you see this, you HAVE to subscribe to me!",
    # Bot patterns
    "Nice video! 👍 Check out my content too!",
    "Great content! Visit my page for similar stuff!",
    "Love this! I make similar videos, check me out!",
    "Amazing! I just uploaded something even better!",
    "Wow this is so good! My channel has more like this!",
    "Awesome video bro! Sub to me I sub back!",
    "This is fire! 🔥 Check my profile!",
    "So inspiring! I posted a reaction on my channel!",
    # Adult/inappropriate spam
    "Hot singles in your area at {link}",
    "Meet beautiful people at {link} 😍",
    "Adult content at {link} 🔞",
    "Dating site {link} join free today!",
    # Crypto/financial spam
    "BITCOIN is going to $100k! Buy now at {link}",
    "I turned $100 into $50,000 with crypto! DM me",
    "Invest in {link} before it's too late!!!",
    "NFT drop happening now! {link} 🚀🚀🚀",
    "Double your money with {link}",
    "My trading bot made me rich {link}",
    "Forex signals for free! Check {link}",
    "Passive income secrets revealed at {link}",
]

SPAM_LINKS = [
    "http://bit.ly/fReEstUfF",
    "http://tinyurl.com/fr33g1fts",
    "http://scamsite.xyz/free",
    "http://get-rich-fast.com",
    "http://www.fakepromo.net",
    "http://freelikesfollowers.com",
    "http://bitcoin-profit.io",
    "http://earn-money-now.biz",
    "http://click4cash.net",
    "http://subscribe2win.com",
    "https://t.co/xYzAbCdEf",
    "http://goo.gl/spam123",
]

# ─── Ham (legitimate) Templates ─────────────────────────────────────────────
HAM_TEMPLATES = [
    "Great video, really enjoyed it!",
    "This tutorial was super helpful, thanks!",
    "I've been looking for this information everywhere. Thank you!",
    "Can you make a video about {topic}?",
    "This is the best explanation I've found on YouTube",
    "I learned so much from this, thank you!",
    "Watching this for my exam tomorrow, wish me luck!",
    "You explain things so clearly, keep it up!",
    "This channel deserves more subscribers",
    "I've been following your channel for years now, love the content",
    "The editing on this video is amazing",
    "Could you do a follow-up on this topic?",
    "I tried this and it actually worked! Thanks!",
    "This helped me with my homework",
    "My teacher recommended this video to us",
    "I shared this with all my friends",
    "Rewatching this because it's so good",
    "The background music is so calming",
    "I disagree with some points but overall good video",
    "What software do you use for editing?",
    "This came at the perfect time, I was just struggling with this",
    "Please do more videos like this!",
    "I have a question about the part at {time}",
    "Love the way you break down complex topics",
    "Finally someone who explains this properly!",
    "You should collab with {creator}",
    "This is better than my university lectures lol",
    "I've watched all your videos, you're the best!",
    "The quality of your content keeps getting better",
    "Just discovered this channel, where have you been all my life?",
    "This video changed my perspective on things",
    "Can you recommend any books on this topic?",
    "I take notes while watching your videos",
    "Notification squad! 🔔",
    "Early gang! Love your content",
    "This is pure gold! 💛",
    "Thank you for making this free",
    "I was confused about this but now I understand",
    "You make learning fun!",
    "Subscribed after watching just one video",
    "The examples you use are so relatable",
    "I wish my teachers explained things like you do",
    "Such an underrated channel",
    "Beautifully produced video as always",
    "The animation at {time} was really cool",
    "I tried this recipe and my family loved it!",
    "Your travel vlogs are always so beautiful",
    "How long did it take you to film this?",
    "Really appreciate the effort you put into these videos",
    "Looking forward to the next one!",
    "This is my favorite YouTube channel",
    "I sent this to my friend who needed to hear this",
    "Thank you for being so honest and genuine",
    "This restored my faith in YouTube content",
    "I cried watching this, so beautiful",
    "Your dog is so cute! What breed is it?",
    "The cinematography is stunning",
    "More people need to see this video",
    "I love how you included both sides of the argument",
    "What camera do you use?",
    "This popped up in my recommendations and I'm glad it did",
    "Short and informative, just how I like it",
    "I have a project due next week and this is saving me",
    "You explained in 10 minutes what my textbook couldn't in 100 pages",
]

HAM_TOPICS = [
    "machine learning", "cooking", "photography", "gaming", "fitness",
    "music production", "web development", "digital art", "history",
    "science", "math", "psychology", "philosophy", "travel", "nature",
]

HAM_TIMES = [
    "3:42", "5:18", "1:05", "7:30", "10:22", "2:15", "8:47", "4:33",
    "6:10", "0:45", "9:55", "11:20", "12:08", "3:00", "7:15",
]

HAM_CREATORS = [
    "MrBeast", "Veritasium", "3Blue1Brown", "Kurzgesagt", "MKBHD",
    "Linus Tech Tips", "Mark Rober", "CGP Grey", "SmarterEveryDay",
]

SPAM_AUTHORS = [
    "FreeGiftBot", "Sub4SubKing", "MoneyMaker2024", "ClickHere4Free",
    "CryptoGuru99", "FollowerFactory", "LikeBot3000", "PromoKing",
    "SpamMaster", "ViralQueen", "RichQuick", "GiveawayBot",
    "FakeAccount001", "BotUser_xz", "SubscribeNow123",
]

HAM_AUTHORS = [
    "Alex Johnson", "Maria Garcia", "James Smith", "Emily Chen",
    "David Kim", "Sarah Williams", "Michael Brown", "Jessica Lee",
    "Daniel Martinez", "Amanda Wilson", "Chris Taylor", "Lisa Anderson",
    "Ryan Thomas", "Nicole Jackson", "Brandon White", "Samantha Harris",
    "Kevin Clark", "Rachel Lewis", "Jason Robinson", "Megan Walker",
    "Tyler Hall", "Lauren Allen", "Andrew Young", "Stephanie King",
    "Matthew Wright", "Ashley Lopez", "Joshua Hill", "Kayla Scott",
    "Ethan Green", "Olivia Adams", "musiclover_42", "gamer_pro",
    "study_buddy", "tech_nerd", "bookworm_99", "fitness_fan",
    "art_creator", "foodie_life", "travel_addict", "science_geek",
]


def generate_spam_comment():
    """Generate a single spam comment."""
    template = random.choice(SPAM_TEMPLATES)
    link = random.choice(SPAM_LINKS)
    comment = template.format(link=link)
    
    # Randomly add extra spam features
    if random.random() < 0.3:
        comment = comment.upper()
    if random.random() < 0.2:
        comment += " " + "".join(random.choices(["🔥", "💰", "🎁", "👇", "⬇️", "🚀", "💯", "😱", "🤑"], k=random.randint(2, 5)))
    if random.random() < 0.15:
        comment += "!!!" * random.randint(1, 3)
    
    return comment


def generate_ham_comment():
    """Generate a single legitimate comment."""
    template = random.choice(HAM_TEMPLATES)
    topic = random.choice(HAM_TOPICS)
    time = random.choice(HAM_TIMES)
    creator = random.choice(HAM_CREATORS)
    comment = template.format(topic=topic, time=time, creator=creator)
    return comment


def generate_dataset(n_total=2000, spam_ratio=0.45, output_path=None):
    """
    Generate the full dataset.
    
    Args:
        n_total: Total number of comments
        spam_ratio: Proportion of spam comments (0.0 to 1.0)
        output_path: Path to save the CSV file
    """
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "comments.csv")
    
    n_spam = int(n_total * spam_ratio)
    n_ham = n_total - n_spam
    
    records = []
    base_date = datetime(2023, 1, 1)
    
    # Generate spam comments
    for i in range(n_spam):
        record = {
            "COMMENT_ID": str(uuid.uuid4())[:12],
            "AUTHOR": random.choice(SPAM_AUTHORS) + (str(random.randint(1, 999)) if random.random() < 0.5 else ""),
            "DATE": (base_date + timedelta(days=random.randint(0, 700), hours=random.randint(0, 23))).strftime("%Y-%m-%dT%H:%M:%S"),
            "CONTENT": generate_spam_comment(),
            "CLASS": 1,
        }
        records.append(record)
    
    # Generate ham comments
    for i in range(n_ham):
        record = {
            "COMMENT_ID": str(uuid.uuid4())[:12],
            "AUTHOR": random.choice(HAM_AUTHORS),
            "DATE": (base_date + timedelta(days=random.randint(0, 700), hours=random.randint(0, 23))).strftime("%Y-%m-%dT%H:%M:%S"),
            "CONTENT": generate_ham_comment(),
            "CLASS": 0,
        }
        records.append(record)
    
    # Shuffle
    random.shuffle(records)
    
    # Write CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["COMMENT_ID", "AUTHOR", "DATE", "CONTENT", "CLASS"])
        writer.writeheader()
        writer.writerows(records)
    
    print(f"✅ Generated {n_total} comments ({n_spam} spam, {n_ham} ham)")
    print(f"   Saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_dataset()
