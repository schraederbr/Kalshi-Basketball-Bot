from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import string
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from proxy import proxy_username
from proxy import proxy_password

ytt_api = YouTubeTranscriptApi(
    proxy_config=WebshareProxyConfig(
        proxy_username=proxy_username,
        proxy_password=proxy_password,
    )
)

def get_transcript(video_id="mDX_mF3vG7c"):
    # Get only auto-generated English transcript
    transcript_list = ytt_api.list(video_id)
    transcript = transcript_list.find_generated_transcript(["en"])
    fetched = transcript.fetch()
    text = TextFormatter().format_transcript(fetched)

    # Remove punctuation
    translator = str.maketrans("", "", string.punctuation)
    clean_text = text.translate(translator)
    words = clean_text.split()
    return words