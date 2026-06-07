import tiktoken
import re
from nltk.tokenize import sent_tokenize

enc = tiktoken.get_encoding("cl100k_base")

def preprocess_transcript(transcript):
    """
    Preprocesses transcript text by removing >> characters and normalizing whitespace.
    """
    text = transcript.replace(">>", "")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_transcript(transcript, max_tokens=200, overlap=100):

    chunks = []
    current_chunk = []
    current_tokens = 0
    start_time = None
    print("Total tokens:", sum(len(enc.encode(e.text)) for e in transcript))
    cleaned_transcript = clean_transcript(transcript)
    for entry in cleaned_transcript:
        # print(f"Processing entry: {entry}")
        text = entry.text
        tokens = len(enc.encode(text))

        if start_time is None:
            start_time = entry.start

        # If adding this exceeds limit → finalize chunk
        if current_tokens + tokens > max_tokens:
            end_time = entry.start + entry.duration
            chunks.append({
                "text": " ".join(current_chunk),
                "start_time": start_time,
                "end_time": end_time
            })

            # overlap: keep last few entries
            current_chunk = current_chunk[-3:]
            current_tokens = sum(len(enc.encode(t)) for t in current_chunk)
            start_time = entry.start

        current_chunk.append(text)
        current_tokens += tokens

    # Final chunk
    if current_chunk:
        chunks.append({
            "text": " ".join(current_chunk),
            "start_time": start_time,
            "end_time": cleaned_transcript[-1].start + cleaned_transcript[-1].duration
        })

    return chunks

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

def semantic_chunking(transcript, max_tokens=200):
    sentences = sent_tokenize(transcript)
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for sentence in sentences:
        # Skip sentences with less than 3 words
        if len(sentence.split()) < 3:
            continue
            
        tokens = len(enc.encode(sentence))
        
        # If adding this sentence exceeds limit → finalize chunk
        if current_tokens + tokens > max_tokens and current_chunk:
            chunks.append(" ".join(current_chunk))
            
            # overlap: keep last sentence
            current_chunk = [current_chunk[-1]]
            current_tokens = len(enc.encode(current_chunk[0]))
        
        current_chunk.append(sentence)
        current_tokens += tokens
    
    # Final chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks
        