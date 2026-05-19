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
    return [
        e for e in transcript
        if e.text.strip() and not e.text.strip().startswith("[")
    ]
    
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
        