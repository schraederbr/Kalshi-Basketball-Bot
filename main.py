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

def get_video_ids():
    video_ids = []
    for playlist_url in playlists:
        playlist = Playlist(playlist_url)
        for video_url in playlist.video_urls:
            q = parse_qs(urlparse(video_url).query)
            vid = q.get("v", [None])[0]
            if vid:
                video_ids.append(vid)
    return video_ids

def main():
    # playlists: list[str] of playlist URLs (must exist in your code)
    # phrase_groups: dict[str, list[str]] mapping label -> phrase variants (must exist in your code)

    video_ids = ["byLVP7bEeRs","DWU9k5tVYSg", "-A-WwK1aVHs"]

    overall_results = {label: 0 for label in phrase_groups}

    for video_id in video_ids:
        words = youtube.get_transcript(video_id=video_id)

        video_results = {}

        for label, variants in phrase_groups.items():
            count = 0
            for variant in variants:
                phrase_words = variant.lower().split()
                count += count_phrase_in_words(words, phrase_words)

            video_results[label] = count
            overall_results[label] += count

        print(f"\nVideo: {video_id}")
        for label, count in video_results.items():
            print(f"{label}: {count}")

    print("\n=== TOTAL ACROSS ALL VIDEOS ===")
    for label, count in overall_results.items():
        print(f"{label}: {count}")


if __name__ == "__main__":
    main()