import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def store_chunk(conn, video_id, chunk, embedding):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO video_chunks 
            (video_id, chunk_text, start_time, end_time, embedding)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                video_id,
                chunk["text"],
                chunk["start_time"],
                chunk["end_time"],
                embedding
            )
        )
    conn.commit()