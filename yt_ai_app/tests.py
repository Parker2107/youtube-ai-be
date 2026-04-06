from django.test import TestCase
from yt_ai_app.services import transcript
from yt_ai_app.services import chunking
from yt_ai_app.services import embedding
from yt_ai_app.services import db

class TranscriptTests(TestCase):

    def test_extract_video_id(self):
        url1 = "https://www.youtube.com/watch?v=Hc0aqOEU2w8"
        url2 = "https://youtu.be/dQw4w9WgXcQ"
        url3 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s"
        url4 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley"

        self.assertEqual(transcript.extract_video_id(url1), "Hc0aqOEU2w8")
        self.assertEqual(transcript.extract_video_id(url2), "dQw4w9WgXcQ")
        self.assertEqual(transcript.extract_video_id(url3), "dQw4w9WgXcQ")
        self.assertEqual(transcript.extract_video_id(url4), "dQw4w9WgXcQ")

    def test_get_transcript(self):
        transcript.get_transcript("Hc0aqOEU2w8")
        
class ChunkingTests(TestCase):

    def test_chunk_transcript(self):
        url1 = "https://www.youtube.com/watch?v=Hc0aqOEU2w8"
        
        video_id = transcript.extract_video_id(url1)
        if (video_id):
            transcript_data = transcript.get_transcript(video_id)
        else:
            raise Exception("Failed to extract video ID, cannot proceed with fetching transcript.")
        if (transcript_data):
            chunks = chunking.chunk_transcript(transcript_data)
        else:
            raise Exception("Transcript data is None, cannot proceed with chunking.")
        
        if chunks:
            print("Chunks created successfully:")
            print(f"Total chunks: {len(chunks)}")
            for i, chunk in enumerate(chunks):
                print(f"Chunk {i+1}: {chunk}")
        else:
            raise Exception("No chunks were created, check the chunking.py file.")
        
class StoringTests(TestCase):

    def test_store_chunk(self):
        url = "https://www.youtube.com/watch?v=Hc0aqOEU2w8"

        video_id = transcript.extract_video_id(url)
        if (video_id):
            transcript_data = transcript.get_transcript(video_id)
            chunks = chunking.chunk_transcript(transcript_data)

            conn = db.get_connection()

            for chunk in chunks:
                embedding_data = embedding.get_fake_embedding()
                db.store_chunk(conn, video_id, chunk, embedding_data)

            print("Stored successfully!")
        else:
            raise Exception("Failed to extract video ID, cannot proceed with fetching transcript and storing chunks.")