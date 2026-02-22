from kalshi import kalshi
import youtube
import re
from pytubefix import Playlist
from urllib.parse import urlparse, parse_qs
import string
import os

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
            #2025-2026
            "https://www.youtube.com/playlist?list=PLSrXjFYZsRuPS6Fow6qsDfsR8SfUhicxU", 
            #2024-2025
            "https://www.youtube.com/watch?v=2rOrYSl6xjk&list=PLSrXjFYZsRuPiXisybt_mXAhKp0itSi2e", 
            #2023-2024
            "https://www.youtube.com/watch?v=5nZxF204_eQ&list=PLSrXjFYZsRuNPH9H5Z0y4woc1vtA_9Ly7",
            #2022-2023
            "https://www.youtube.com/watch?v=WKdFpCvk-pI&list=PLSrXjFYZsRuMu8DHzvgdFnC6TgGdx-dwD",
            #2020-2021
            "https://www.youtube.com/watch?v=NeBs81IlBdI&list=PLSrXjFYZsRuOcB6iTYlUKsuoTkNHpDhlz"]

def save_video_ids(video_ids, filepath=VIDEO_ID_FILE):
    existing_ids = set()

    # Load existing IDs if file exists
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                existing_ids.add(line.strip())

    # Append only new IDs
    new_ids = [vid for vid in video_ids if vid not in existing_ids]

    if new_ids:
        with open(filepath, "a") as f:
            for vid in new_ids:
                f.write(vid + "\n")

    return new_ids

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

def save_transcript(video_id, words, folder="transcripts"):
    # Ensure directory exists
    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, f"{video_id}.txt")

    # Join tokenized words back into readable text
    text = " ".join(words)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

def get_video_ids(max_videos=1100):
    existing_ids = []

    # Load existing IDs
    if os.path.exists(VIDEO_ID_FILE):
        with open(VIDEO_ID_FILE, "r") as f:
            existing_ids = [line.strip() for line in f if line.strip()]

    # If no max specified, just return what's already stored
    if max_videos is None:
        return existing_ids

    # If already have enough, return first max_videos
    if len(existing_ids) >= max_videos:
        print("Existing_ids" + str(existing_ids))
        return existing_ids[:max_videos]

    needed = max_videos - len(existing_ids)
    existing_set = set(existing_ids)
    new_ids = []

    # Fetch additional IDs
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

    # Append new IDs to file
    if new_ids:
        with open(VIDEO_ID_FILE, "a") as f:
            for vid in new_ids:
                f.write(vid + "\n")
    print("Existing_ids" + str(existing_ids))
    print("New_ids" + str(existing_ids))
    return existing_ids + new_ids

def load_transcript(video_id, folder="transcripts"):
    filepath = os.path.join(folder, f"{video_id}.txt")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Transcript file not found for {video_id}")

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Normalize similarly to your original transcript format
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    words = text.split()

    return words

def get_or_load_transcript(video_id, folder="transcripts"):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"{video_id}.txt")

    # Load if cached
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            words = f.read().split()
        # If file exists but is empty/corrupt, treat as missing and refetch
        if words:
            return words

    # Fetch (your youtube.get_transcript may return None)
    words = youtube.get_transcript(video_id)
    if not words:
        # Do not create/update cache file
        return None

    # Save exactly what get_transcript returns
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(" ".join(words))

    return words

def main():
    video_ids = get_video_ids()
    print(video_ids)

    youtube_objects = []

    videos_with_phrase = {label: 0 for label in phrase_groups}
    processed_videos = 0

    for video_id in video_ids:
        print(video_id)
        # yt_object = youtube.get_youtube_object(video_id)
        # youtube_objects.append(yt_object)
        # print(yt_object.title)

        words = get_or_load_transcript(video_id)
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

    total_videos = processed_videos
    print(f"Total Videos With Transcripts: {total_videos}")
    if total_videos == 0:
        print("No usable transcripts found.")
        return

    import pdb; pdb.set_trace()

    print("\n=== PROBABILITY PHRASE APPEARS IN A VIDEO ===")
    results_string = ""
    for label in phrase_groups:
        probability = videos_with_phrase[label] / total_videos
        results_string += f"{label}: {probability:.2%} ({videos_with_phrase[label]}/{total_videos})\n"
        
    print(results_string)



    with open(RESULTS_FILE, "a") as f:
        f.write(results_string)



if __name__ == "__main__":
    main()