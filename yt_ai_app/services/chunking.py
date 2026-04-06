import tiktoken

def chunk_transcript(transcript, max_tokens=200, overlap=100):
    enc = tiktoken.get_encoding("cl100k_base")

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