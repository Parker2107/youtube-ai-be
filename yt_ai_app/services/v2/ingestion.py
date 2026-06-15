import re
import os
from dotenv import load_dotenv
import requests
from nltk.tokenize import sent_tokenize
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url: str):
    if "watch?v=" in url:
        return url.split("watch?v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None


def get_transcript(video_id: str):
    ytt_api = YouTubeTranscriptApi()
    try:
        # langs = ytt_api.list(video_id)
        transcript = ytt_api.fetch(video_id, preserve_formatting=True, languages=['en'])
        return transcript
    except Exception as e:
        print("Error fetching transcript:", e)
        return None
    
def get_full_transcript_text(transcript_data):
    if not transcript_data:
        return ""
    full_text = " ".join([entry.text for entry in transcript_data])
    return full_text

def clean_transcript(transcript):
    """
    Cleans transcript entries by removing unwanted content and normalizing text.
    Removes >> characters, normalizes whitespace, and filters out non-content entries.
    """
    cleaned = []
    for entry in transcript:
        text = entry.text.strip()
        
        # Skip empty entries and non-speech markers
        if not text or text.startswith("["):
            continue
        
        # Remove speaker indicators and normalize whitespace
        text = text.replace(">>", "")
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Skip if text became empty after cleaning
        if not text:
            continue
        
        # Create new entry with cleaned text
        entry.text = text
        cleaned.append(entry)
    
    return cleaned


def semantic_chunking_with_timestamps(transcript_data, target_tokens=100, overlap_sentences=2):
    """
    Builds semantic chunks while preserving timestamps.

    Strategy:
    1. Reconstruct proper sentences from transcript fragments
    2. Track timestamps per sentence
    3. Chunk sentences semantically
    4. Preserve chunk timestamps
    """

    cleaned_transcript = clean_transcript(transcript_data)

    full_text = ""
    char_mappings = []
    current_pos = 0

    for segment in cleaned_transcript:
        text = segment.text.strip()

        if not text:
            continue

        # Add space if needed
        if full_text:
            full_text += " "
            current_pos += 1

        start_char = current_pos
        full_text += text
        current_pos += len(text)
        end_char = current_pos

        char_mappings.append({
            "start_char": start_char,
            "end_char": end_char,
            "start_time": segment.start,
            "end_time": segment.start + segment.duration
        })

    sentences = sent_tokenize(full_text)
    sentence_data = []
    search_pos = 0
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        sentence_start = full_text.find(sentence, search_pos)
        if sentence_start == -1:
            continue
        sentence_end = sentence_start + len(sentence)
        search_pos = sentence_end
        matching_segments = []
        for mapping in char_mappings:
            overlaps = not (
                sentence_end < mapping["start_char"]
                or sentence_start > mapping["end_char"]
            )
            if overlaps:
                matching_segments.append(mapping)

        if not matching_segments:
            continue

        sentence_data.append({
            "text": sentence,
            "start_time": matching_segments[0]["start_time"],
            "end_time": matching_segments[-1]["end_time"]
        })

    chunks = []

    current_chunk_sentences = []
    current_token_count = 0

    for sentence in sentence_data:

        token_count = len(sentence["text"].split())

        # finalize chunk if limit exceeded
        if (
            current_chunk_sentences
            and current_token_count + token_count > target_tokens
        ):

            chunk_text = " ".join(
                s["text"] for s in current_chunk_sentences
            )

            chunks.append({
                "text": chunk_text,
                "start_time": current_chunk_sentences[0]["start_time"],
                "end_time": current_chunk_sentences[-1]["end_time"]
            })

            # overlap
            overlap = current_chunk_sentences[-overlap_sentences:]
            current_chunk_sentences = overlap.copy()
            current_token_count = sum(
                len(s["text"].split())
                for s in current_chunk_sentences
            )

        current_chunk_sentences.append(sentence)
        current_token_count += token_count

    if current_chunk_sentences:

        chunk_text = " ".join(
            s["text"] for s in current_chunk_sentences
        )

        chunks.append({
            "text": chunk_text,
            "start_time": current_chunk_sentences[0]["start_time"],
            "end_time": current_chunk_sentences[-1]["end_time"]
        })

    return chunks

def extract_metadata(url: str):
    """
    Extracts metadata from a YouTube URL.
    Returns a dictionary with video_id, title, and description.
    """
    load_dotenv()
    YT_API_KEY = os.getenv("YT_API_KEY")
    print(f"YT_API_KEY: {YT_API_KEY}")  # Debugging line to check if the API key is loaded correctly
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={
            "part":"snippet,contentDetails,statistics",
            "id": video_id,
            "key": YT_API_KEY
        }
    )
    print(response.json())
    return ({
        "video_id": video_id,
        "title": response.json()["items"][0]["snippet"]["title"],
        "description": response.json()["items"][0]["snippet"]["description"],
        "image_url": response.json()["items"][0]["snippet"]["thumbnails"]["high"]["url"], #For future, we can make it [standard][url] or [maxres][url] based on availability and space
        "category_id": response.json()["items"][0]["snippet"]["categoryId"],
        "tags": response.json()["items"][0]["snippet"].get("tags", [])
    })
    
# extract_metadata("https://www.youtube.com/watch?v=Hc0aqOEU2w8")