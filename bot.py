import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

CHANNEL_ID = "UCErgcFPND-Hagk8PkNIJvww"
COMMENT_TEXT = """⭐ لدعم القناة والاطلاع على المحتوى الحصري
https://www.youtube.com/channel/UCErgcFPND-Hagk8PkNIJvww/join

ما رأيك في الحلقة؟"""

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

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

response = youtube.search().list(
    part="snippet",
    channelId=CHANNEL_ID,
    order="date",
    maxResults=10,
    type="video"
).execute()

video_id = None

for item in response.get("items", []):
    candidate = item["id"]["videoId"]

    comments = youtube.commentThreads().list(
        part="snippet",
        videoId=candidate,
        maxResults=20,
        textFormat="plainText"
    ).execute()

    already_commented = False

    for c in comments.get("items", []):
        text = c["snippet"]["topLevelComment"]["snippet"].get("textDisplay", "")
        if "لدعم القناة" in text:
            already_commented = True
            break

    if not already_commented:
        video_id = candidate
        break

if not video_id:
    print("لم يتم العثور على فيديو جديد بدون تعليق.")
    raise SystemExit(0)

youtube.commentThreads().insert(
    part="snippet",
    body={
        "snippet": {
            "videoId": video_id,
            "topLevelComment": {
                "snippet": {
                    "textOriginal": COMMENT_TEXT
                }
            }
        }
    }
).execute()

print(f"تم نشر التعليق على الفيديو: {video_id}")
