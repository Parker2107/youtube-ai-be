from django.test import TestCase
from yt_ai_app.services import retrieval, transcript_fetching
from yt_ai_app.services import chunking
from yt_ai_app.services import embedding
from yt_ai_app.services import db
from yt_ai_app.services import retrieval

class TranscriptTests(TestCase):

    def test_extract_video_id(self):
        url1 = "https://www.youtube.com/watch?v=Hc0aqOEU2w8"
        url2 = "https://youtu.be/dQw4w9WgXcQ"
        url3 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s"
        url4 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley"

        self.assertEqual(transcript_fetching.extract_video_id(url1), "Hc0aqOEU2w8")
        self.assertEqual(transcript_fetching.extract_video_id(url2), "dQw4w9WgXcQ")
        self.assertEqual(transcript_fetching.extract_video_id(url3), "dQw4w9WgXcQ")
        self.assertEqual(transcript_fetching.extract_video_id(url4), "dQw4w9WgXcQ")

    def test_get_transcript(self):
        transcript_data = transcript_fetching.get_transcript("Hc0aqOEU2w8")
        print(transcript_fetching.get_full_transcript_text(transcript_data))
        
class ChunkingTests(TestCase):

    def test_chunk_transcript(self):
        url1 = "https://www.youtube.com/watch?v=Hc0aqOEU2w8"
        
        video_id = transcript_fetching.extract_video_id(url1)
        if (video_id):
            transcript_data = transcript_fetching.get_transcript(video_id)
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
        
    def test_semantic_chunking(self):
        url1 = "https://www.youtube.com/watch?v=Hc0aqOEU2w8"
        
        video_id = transcript_fetching.extract_video_id(url1)
        if (video_id):
            transcript_data = transcript_fetching.get_transcript(video_id)
            chunks = chunking.semantic_chunking_with_timestamps(transcript_data)
            print(f"Total semantic chunks: {len(chunks)}")
            for i, chunk in enumerate(chunks):
                print(f"Semantic Chunk {i+1}: {chunk}")
        else:
            raise Exception("Failed to extract video ID, cannot proceed with fetching transcript and semantic chunking.")
        
class StoringTests(TestCase):

    def test_store_chunk(self):
        url = "https://www.youtube.com/watch?v=Hc0aqOEU2w8"

        video_id = transcript_fetching.extract_video_id(url)
        if (video_id):
            transcript_data = transcript_fetching.get_transcript(video_id)
            chunks = chunking.chunk_transcript(transcript_data)

            conn = db.get_connection()

            for chunk in chunks:
                embedding_data = embedding.get_fake_embedding()
                embedding_small = embedding.create_embedding_huggingface(chunk["text"])
                db.store_chunk(conn, video_id, chunk, embedding_data, embedding_small)

            print("Stored successfully!")
        else:
            raise Exception("Failed to extract video ID, cannot proceed with fetching transcript and storing chunks.")

    def test_store_semantic_chunks(self):
        url = "https://www.youtube.com/watch?v=Hc0aqOEU2w8"

        video_id = transcript_fetching.extract_video_id(url)
        if (video_id):
            transcript_data = transcript_fetching.get_transcript(video_id)
            semantic_chunks = chunking.semantic_chunking_with_timestamps(transcript_data)

            conn = db.get_connection()

            for chunk in semantic_chunks:
                embedding_data = embedding.get_fake_embedding()
                embedding_small = embedding.create_embedding_huggingface(chunk["text"])
                db.store_chunk(conn, video_id, chunk, embedding_data, embedding_small)

            print(f"Stored {len(semantic_chunks)} semantic chunks successfully!")
        else:
            raise Exception("Failed to extract video ID, cannot proceed with fetching transcript and storing semantic chunks.")
        
class RetrievalTests(TestCase):

    def test_retrieve_chunks(self):
        query = "What is the video about?"
        results = retrieval.retrieve_chunks(query=query, video_id="Hc0aqOEU2w8", top_k=5)

        if results:
            print("Retrieved chunks successfully:")
            for i, res in enumerate(results):
                print(f"Result {i+1}: {res}")
        else:
            raise Exception("No results retrieved, check the retrieval.py file.")   