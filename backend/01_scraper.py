import requests
import json
import csv
from dotenv import load_dotenv
import os
import time
import sys

# Increase CSV field size limit
csv.field_size_limit(10_000_000)

load_dotenv()

API_KEY = os.getenv("SUPADATA_API_KEY")
API_URL = "https://api.supadata.ai/v1/youtube/transcript"
INPUT_FILE = "backend/videos.txt"
OUTPUT_FILE = "backend/transcripts.csv"
RETRY_COUNT = 1
RETRY_DELAY = 5  # seconds


def read_video_urls(file_path, limit=150):
    """Read the first `limit` video URLs from a text file."""
    with open(file_path, "r") as file:
        return [line.strip() for line in file.readlines()][:limit]


def fetch_transcript(video_url):
    """Fetch transcript for a given YouTube video URL with retries."""
    headers = {"x-api-key": API_KEY}
    params = {"url": video_url, "text": "true"}

    for attempt in range(RETRY_COUNT):
        response = requests.get(API_URL, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Attempt {attempt + 1} failed for {video_url}: {response.status_code}"
            )
            time.sleep(RETRY_DELAY)

    print(f"Failed to fetch transcript for {video_url} after {RETRY_COUNT} attempts.")
    return None


def load_existing_data(file_path):
    """Load existing data from the CSV file to prevent duplicates."""
    if not os.path.exists(file_path):
        return set()

    existing_urls = set()
    with open(file_path, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header
        for row in reader:
            if row:
                existing_urls.add(row[0])
    return existing_urls


def save_to_csv(url, transcript_data, file_path):
    """Save a single transcript entry to the CSV file, checking for duplicates."""
    existing_urls = load_existing_data(file_path)

    if url in existing_urls:
        print(f"Skipping {url}, already in CSV.")
        return

    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if os.stat(file_path).st_size == 0:
            writer.writerow(
                ["Video URL", "Language", "Transcript", "Available Languages"]
            )
        writer.writerow(
            [
                url,
                transcript_data.get("lang", "N/A"),
                transcript_data.get("content", "N/A"),
                ", ".join(transcript_data.get("availableLangs", [])),
            ]
        )


def main():
    video_urls = read_video_urls(INPUT_FILE)

    for url in video_urls:
        if url in load_existing_data(OUTPUT_FILE):
            print(f"Skipping {url}, already processed.")
            continue

        transcript_data = fetch_transcript(url)
        if transcript_data:
            save_to_csv(url, transcript_data, OUTPUT_FILE)
            print(f"Saved transcript for {url}")


if __name__ == "__main__":
    main()
