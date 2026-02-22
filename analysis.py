import os
import re

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

def load_texts_from_folder(folder_path):
    texts = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            path = os.path.join(folder_path, filename)
            with open(path, "r", encoding="utf-8") as f:
                texts.append(f.read().lower())
    return texts

def phrase_present(text, variants):
    for variant in variants:
        pattern = r"\b" + re.escape(variant.lower()) + r"\b"
        if re.search(pattern, text):
            return True
    return False

def analyze_texts(texts, phrase_groups):
    total_texts = len(texts)
    results = {}

    for group_name, variants in phrase_groups.items():
        count = 0
        for text in texts:
            if phrase_present(text, variants):
                count += 1

        percent = (count / total_texts) * 100 if total_texts > 0 else 0
        results[group_name] = (count, percent)

    return results


if __name__ == "__main__":
    transcripts_folder = "transcripts"
    texts = load_texts_from_folder(transcripts_folder)

    stats = analyze_texts(texts, phrase_groups)

    print(f"Total transcripts analyzed: {len(texts)}\n")
    for phrase, (count, percent) in stats.items():
        print(f"{phrase}: {count} texts ({percent:.2f}%)")