from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import string
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from proxy import proxy_username
from proxy import proxy_password
from pytubefix import YouTube

def get_youtube_object(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    return YouTube(url)

def get_video_title(video_id):
    return(get_youtube_object(video_id).title)

ytt_api = YouTubeTranscriptApi(
    proxy_config=WebshareProxyConfig(
        proxy_username=proxy_username,
        proxy_password=proxy_password,
    )
)

def get_transcript(video_id="mDX_mF3vG7c"):
    # Get only auto-generated English transcript
    try:
        transcript_list = ytt_api.list(video_id)
    except Exception as e:
        print(e)
        print(f"{video_id} failed")
        return

    # print(get_youtube_object(video_id).title)
    transcript = transcript_list.find_generated_transcript(["en"])
    fetched = transcript.fetch()
    text = TextFormatter().format_transcript(fetched)

    # Remove punctuation
    translator = str.maketrans("", "", string.punctuation)
    clean_text = text.translate(translator)
    words = clean_text.split()
    return words