from kalshi import kalshi
import youtube
import re
from pytubefix import Playlist
from urllib.parse import urlparse, parse_qs
import string

phrase_groups = {
    "ankle": ["ankle", "ankles"],
    "double double": ["double double", "double-double", "double doubles", "double-doubles"],
    "recruit": ["recruit", "recruits", "recruited", "recruiting"],
    "all american": ["all american", "all-american", "all americans", "all-americans"],
    "airball": ["airball", "air ball", "air-ball", "airballs", "air balls", "air-balls"],
    "elbow": ["elbow", "elbows", "elbowed", "elbowing"],
    "draft": ["draft", "drafts", "drafted", "drafting"],
    "transfer": ["transfer", "transfers", "transferred", "transferring"],
}

playlists = ["https://www.youtube.com/playlist?list=PLSrXjFYZsRuPS6Fow6qsDfsR8SfUhicxU"]

def count_phrase_in_words(words, phrase_words):
    # Count occurrences of phrase_words as a contiguous sequence in words
    n = len(phrase_words)
    if n == 0:
        return 0
    if n == 1:
        target = phrase_words[0]
        return sum(1 for w in words if w == target)

    total = 0
    for i in range(len(words) - n + 1):
        if words[i : i + n] == phrase_words:
            total += 1
    return total

def get_video_ids(max=20):
    video_ids = []
    for playlist_url in playlists:
        playlist = Playlist(playlist_url)
        for video_url in playlist.video_urls:
            vid = parse_qs(urlparse(video_url).query).get("v", [None])[0]
            if vid:
                video_ids.append(vid)
                if len(video_ids) >= max:
                    return video_ids
    return video_ids

def main():
    # playlists: list[str] of playlist URLs (must exist in your code)
    # phrase_groups: dict[str, list[str]] mapping label -> phrase variants (must exist in your code)

    # video_ids = ["byLVP7bEeRs","DWU9k5tVYSg", "-A-WwK1aVHs"]
    video_ids = get_video_ids()
    print(video_ids)

    total_videos = len(video_ids)
    if total_videos == 0:
        print("No videos found.")
        return

    youtube_objects = []

    videos_with_phrase = {label: 0 for label in phrase_groups}

    for video_id in video_ids:
        yt_object = youtube.get_youtube_object(video_id)
        youtube_objects.append(yt_object)
        print(yt_object.title)
        words = youtube.get_transcript(video_id)

        for label, variants in phrase_groups.items():
            found_in_this_video = False

            for variant in variants:
                phrase_words = variant.lower().split()
                if count_phrase_in_words(words, phrase_words) > 0:
                    found_in_this_video = True
                    break  # stop once found

            if found_in_this_video:
                videos_with_phrase[label] += 1

    print("\n=== PROBABILITY PHRASE APPEARS IN A VIDEO ===")
    for label in phrase_groups:
        probability = videos_with_phrase[label] / total_videos
        print(f"{label}: {probability:.2%} ({videos_with_phrase[label]}/{total_videos})")


if __name__ == "__main__":
    main()