from django.test import TestCase
from dotenv import load_dotenv
from yt_ai_app.services.v1 import embedding
from yt_ai_app.services.v2 import ingestion
from yt_ai_app.services import db
from yt_ai_app.services.v2 import ner

class IngestionTests(TestCase):
    def test_ingestion(self):
        load_dotenv()
        url1 = "https://www.youtube.com/watch?v=Hc0aqOEU2w8"
        url2 = "https://www.youtube.com/watch?v=8HBDE-msUjw"
        
        video_id = ingestion.extract_video_id(url2)
        self.assertEqual(video_id, "8HBDE-msUjw")
        
        if (video_id):
            conn = db.get_connection()
        
            video_data = ingestion.extract_metadata(url2)
            db.store_video(conn, video_data["video_id"], video_data["title"], video_data["description"], video_data["image_url"], video_data["category_id"], video_data["tags"])
        
            transcript_data = ingestion.get_transcript(video_id)
            self.assertIsNotNone(transcript_data)
            chunks = ingestion.semantic_chunking_with_timestamps(transcript_data)
        
            for chunk in chunks:
                embedding_data = embedding.get_fake_embedding()
                embedding_small = embedding.create_embedding_huggingface(chunk["text"])
                db.store_chunk(conn, video_id, chunk, embedding_data, embedding_small)

            print(f"Total semantic chunks: {len(chunks)}")
            json = ner.create_relations(chunks[0]["text"])
            db.store_ner(conn, video_id, 0, json)