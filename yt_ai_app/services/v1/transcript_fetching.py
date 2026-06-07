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