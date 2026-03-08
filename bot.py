import os
import random
import re
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

CHANNEL_ID = "UCErgcFPND-Hagk8PkNIJvww"

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# -----------------------------
# التعليقات
# -----------------------------

SHORT_COMMENTS = [

"""📌 لو المقطع شدّك، تابع المحتوى الكامل من هنا:
الرابط الرسمي:
https://www.youtube.com/channel/UCErgcFPND-Hagk8PkNIJvww

اكتب رأيك في أقل من 5 كلمات 👇""",

"""⚡ شورت سريع… لكن القصة الكاملة دائمًا أعمق.
لدعم القناة ومتابعة المحتوى الحصري:
الرابط الرسمي:
https://www.youtube.com/channel/UCErgcFPND-Hagk8PkNIJvww/join

هل تتفق أم لا؟ 👇""",

"""🎯 لو أعجبك هذا الشورت، فالمقاطع الكاملة على القناة ستهمك أكثر.
تابع القناة من هنا:
الرابط الرسمي:
https://www.youtube.com/channel/UCErgcFPND-Hagk8PkNIJvww

ما أول انطباع عندك؟ 👇""",

"""🔥 محتوى مختصر ومباشر… وللمزيد من التفاصيل والحصريات:
الرابط الرسمي:
https://www.youtube.com/channel/UCErgcFPND-Hagk8PkNIJvww/join

هل تريد شورتات أكثر بهذا الأسلوب؟ 👇"""
]

SHORT_VIDEO_COMMENTS = [

"""📌 إذا شاهدت هذا المقطع، فلا تفوّت بقية المحتوى على القناة.
تابعنا من هنا:
الرابط الرسمي:
https://www.youtube.com/channel/UCErgcFPND-Hagk8PkNIJvww

ما أهم نقطة لفتت انتباهك؟ 👇""",

"""🎯 هذا النوع من المقاطع يختصر الفكرة بسرعة، لكن التفاصيل الكاملة دائمًا تستحق المتابعة.
ولدعم القناة:
الرابط الرسمي:
https://www.youtube.com/channel/UCErgcFPND-Hagk8PkNIJvww/join

شاركنا رأيك 👇""",

"""⭐ لو وصلك محتوى المقطع، ساعدنا نستمر ونوصل أكثر.
تابع القناة من هنا:
الرابط الرسمي:
https://www.youtube.com/channel/UCErgcFPND-Hagk8PkNIJvww

هل تتفق مع طرح الفيديو؟ 👇""",

"""🧭 مقطع قصير… لكن فيه رسالة مهمة.
لدعم القناة ومتابعة المحتوى الحصري:
الرابط الرسمي:
https://www.youtube.com/channel/UCErgcFPND-Hagk8PkNIJvww/join

اكتب لنا رأيك بصراحة 👇"""
]

LONG_VIDEO_COMMENTS = [

"""📌 إذا وصلت إلى هنا، فالمقطع أكيد يستحق المشاهدة حتى النهاية.
تابع القناة من هنا:
الرابط الرسمي:
https://www.youtube.com/channel/UCErgcFPND-Hagk8PkNIJvww

ما أبرز نقطة خرجت بها من هذا المقطع؟ 👇""",

"""🎥 المقاطع الكاملة تصنع الفرق، لأنها تشرح ما لا يظهر في المقاطع السريعة.
ولدعم القناة:
الرابط الرسمي:
https://www.youtube.com/channel/UCErgcFPND-Hagk8PkNIJvww/join

ما تقييمك لهذا المقطع من 10؟ 👇""",

"""🧠 لو شاهدت المقطع كاملًا، فأنت فعلًا مهتم بالمحتوى الجاد.
تابع المزيد من هنا:
الرابط الرسمي:
https://www.youtube.com/channel/UCErgcFPND-Hagk8PkNIJvww

ما أكثر جزئية أثرت فيك؟ 👇""",

"""📍 هذا المقطع جزء من صورة أكبر، ومتابعتك المستمرة تصنع فارقًا.
لدعم القناة والوصول إلى المحتوى الحصري:
الرابط الرسمي:
https://www.youtube.com/channel/UCErgcFPND-Hagk8PkNIJvww/join

قل لنا: ما أهم سؤال تركه هذا المقطع عندك؟ 👇"""
]

BOT_SIGNATURE = "الرابط الرسمي:"


# -----------------------------
# تحويل مدة الفيديو
# -----------------------------

def iso_duration_to_seconds(duration):

    pattern = re.compile(
        r'PT'
        r'(?:(\d+)H)?'
        r'(?:(\d+)M)?'
        r'(?:(\d+)S)?'
    )

    match = pattern.match(duration)

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    return hours * 3600 + minutes * 60 + seconds


# -----------------------------
# اختيار التعليق المناسب
# -----------------------------

def choose_comment(duration):

    if duration < 90:
        return random.choice(SHORT_COMMENTS)

    elif duration < 240:
        return random.choice(SHORT_VIDEO_COMMENTS)

    else:
        return random.choice(LONG_VIDEO_COMMENTS)


# -----------------------------
# التأكد من وجود تعليق سابق
# -----------------------------

def already_commented(youtube, video_id):

    comments = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=50,
        textFormat="plainText"
    ).execute()

    for item in comments.get("items", []):
        text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]

        if BOT_SIGNATURE in text:
            return True

    return False


# -----------------------------
# الاتصال بيوتيوب
# -----------------------------

creds = Credentials(
    None,
    refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.environ["YOUTUBE_CLIENT_ID"],
    client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
    scopes=SCOPES,
)

creds.refresh(Request())

youtube = build("youtube", "v3", credentials=creds)


# -----------------------------
# جلب أحدث الفيديوهات
# -----------------------------

search = youtube.search().list(
    part="snippet",
    channelId=CHANNEL_ID,
    order="date",
    maxResults=10,
    type="video"
).execute()

video_ids = [item["id"]["videoId"] for item in search["items"]]


videos = youtube.videos().list(
    part="contentDetails",
    id=",".join(video_ids)
).execute()


video_map = {}

for item in videos["items"]:

    duration = iso_duration_to_seconds(item["contentDetails"]["duration"])

    video_map[item["id"]] = duration


target_video = None
target_comment = None


for vid in video_ids:

    if already_commented(youtube, vid):
        continue

    duration = video_map[vid]

    target_video = vid
    target_comment = choose_comment(duration)

    break


if not target_video:
    print("لا يوجد فيديو جديد للتعليق عليه")
    exit()


youtube.commentThreads().insert(
    part="snippet",
    body={
        "snippet": {
            "videoId": target_video,
            "topLevelComment": {
                "snippet": {
                    "textOriginal": target_comment
                }
            }
        }
    }
).execute()

print("تم نشر التعليق بنجاح")
