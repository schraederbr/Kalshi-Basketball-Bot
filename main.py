import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
import string
from urllib.parse import urlparse, parse_qs
from pytubefix import Playlist

import youtube

VIDEO_ID_FILE = "video_ids.txt"
RESULTS_FILE = "results.txt"

phrase_groups = {
    "ankle": ["ankle"],
    "double double": ["double double"],
    "recruit": ["recruit", "recruited", "recruitment"],
    "all american": ["all american", "all america", "all-american", "all-america", "allamerican", "allamerica"],
    "airball": ["airball", "air ball", "air-ball", "airballs", "air balls", "air-balls", "airballed", "air-balled"],
    "elbow": ["elbow"],
    "draft": ["draft", "drafted"],
    "transfer": ["transfer", "transferred"],
}

playlists = [
    "https://www.youtube.com/playlist?list=PLSrXjFYZsRuPS6Fow6qsDfsR8SfUhicxU",
    "https://www.youtube.com/watch?v=2rOrYSl6xjk&list=PLSrXjFYZsRuPiXisybt_mXAhKp0itSi2e",
    "https://www.youtube.com/watch?v=5nZxF204_eQ&list=PLSrXjFYZsRuNPH9H5Z0y4woc1vtA_9Ly7",
    "https://www.youtube.com/watch?v=WKdFpCvk-pI&list=PLSrXjFYZsRuMu8DHzvgdFnC6TgGdx-dwD",
    "https://www.youtube.com/watch?v=NeBs81IlBdI&list=PLSrXjFYZsRuOcB6iTYlUKsuoTkNHpDhlz",
]

def count_phrase_in_words(words, phrase_words):
    n = len(phrase_words)
    if n == 0:
        return 0
    if n == 1:
        target = phrase_words[0]
        return sum(1 for w in words if w == target)

    total = 0
    for i in range(len(words) - n + 1):
        if words[i:i+n] == phrase_words:
            total += 1
    return total

def get_video_ids(max_videos=1100):
    existing_ids = []

    if os.path.exists(VIDEO_ID_FILE):
        with open(VIDEO_ID_FILE, "r") as f:
            existing_ids = [line.strip() for line in f if line.strip()]

    if max_videos is None:
        return existing_ids

    if len(existing_ids) >= max_videos:
        return existing_ids[:max_videos]

    needed = max_videos - len(existing_ids)
    existing_set = set(existing_ids)
    new_ids = []

    for playlist_url in playlists:
        playlist = Playlist(playlist_url)
        for video_url in playlist.video_urls:
            vid = parse_qs(urlparse(video_url).query).get("v", [None])[0]
            if vid and vid not in existing_set:
                new_ids.append(vid)
                existing_set.add(vid)
                if len(new_ids) >= needed:
                    break
        if len(new_ids) >= needed:
            break

    if new_ids:
        with open(VIDEO_ID_FILE, "a") as f:
            for vid in new_ids:
                f.write(vid + "\n")

    return existing_ids + new_ids

def _load_cached_words(video_id, folder):
    filepath = os.path.join(folder, "{}.txt".format(video_id))
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        words = f.read().split()
    return words if words else None

def _save_cached_words(video_id, words, folder):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, "{}.txt".format(video_id))
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(" ".join(words))

async def get_or_load_transcript_async(video_id, loop, executor, sem, folder="transcripts"):
    cached = _load_cached_words(video_id, folder)
    if cached:
        return (video_id, cached)

    # Limit concurrent network calls
    async with sem:
        words = await loop.run_in_executor(
            executor,
            youtube.get_transcript,  # blocking call
            video_id
        )

    if not words:
        return (video_id, None)

    _save_cached_words(video_id, words, folder)
    return (video_id, words)

async def main_async(max_videos=1100, concurrency=10):
    video_ids = get_video_ids(max_videos=max_videos)
    print("Video count:", len(video_ids))

    videos_with_phrase = {label: 0 for label in phrase_groups}
    processed_videos = 0

    loop = asyncio.get_event_loop()
    sem = asyncio.Semaphore(concurrency)

    # Thread pool for blocking HTTP work
    executor = ThreadPoolExecutor(max_workers=concurrency)

    try:
        tasks = [
            get_or_load_transcript_async(vid, loop, executor, sem)
            for vid in video_ids
        ]

        for fut in asyncio.as_completed(tasks):
            video_id, words = await fut
            if not words:
                continue

            processed_videos += 1

            for label, variants in phrase_groups.items():
                found_in_this_video = False
                for variant in variants:
                    phrase_words = variant.lower().split()
                    if count_phrase_in_words(words, phrase_words) > 0:
                        found_in_this_video = True
                        break
                if found_in_this_video:
                    videos_with_phrase[label] += 1

    finally:
        executor.shutdown(wait=True)

    total_videos = processed_videos
    print("Total Videos With Transcripts:", total_videos)
    if total_videos == 0:
        print("No usable transcripts found.")
        return

    results_string = ""
    for label in phrase_groups:
        probability = float(videos_with_phrase[label]) / float(total_videos)
        results_string += "{}: {:.2%} ({}/{})\n".format(
            label, probability, videos_with_phrase[label], total_videos
        )

    print(results_string)
    with open(RESULTS_FILE, "a") as f:
        f.write(results_string)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_async(max_videos=1100, concurrency=20))

if __name__ == "__main__":
    main()