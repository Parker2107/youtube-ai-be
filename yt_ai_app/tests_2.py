from django.test import TestCase
from yt_ai_app.services.v2 import ingestion

class IngestionTests(TestCase):
    def test_ingestion(self):
        url1 = "https://www.youtube.com/watch?v=Hc0aqOEU2w8"
        video_id = ingestion.extract_video_id(url1)
        self.assertEqual(video_id, "Hc0aqOEU2w8")
        if (video_id):
            transcript_data = ingestion.get_transcript(video_id)
            self.assertIsNotNone(transcript_data)
            chunks = ingestion.semantic_chunking_with_timestamps(transcript_data)
            print(f"Total semantic chunks: {len(chunks)}")
        