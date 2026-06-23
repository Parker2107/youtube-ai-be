import json

from packaging import tags
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def store_chunk(conn, video_id, chunk, embedding, embedding_small):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO video_chunks 
            (video_id, chunk_text, start_time, end_time, embedding, embedding_small)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                video_id,
                chunk["text"],
                chunk["start_time"],
                chunk["end_time"],
                embedding,
                embedding_small
            )
        )
    conn.commit()
    
def store_video(
    conn,
    video_id,
    title,
    description,
    image_url,
    category_id,
    tags
):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO videos (
                id,
                title,
                description,
                image_url,
                category_id
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                video_id,
                title,
                description,
                image_url,
                category_id,
            ),
        )
        for tag in tags:
            cursor.execute(
                """
                INSERT INTO tags (name)
                VALUES (%s)
                ON CONFLICT (name) DO NOTHING
                """,
                (tag)
            )
        for tag in tags:
            cursor.execute(
                """
                INSERT INTO video_tags (video_id, tag_id)
                SELECT %s, id
                FROM tags
                WHERE name = %s
                ON CONFLICT DO NOTHING
                """,
                (video_id, tag)
            )
    conn.commit()

def store_ner(conn, video_id, chunk_id, result):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO extraction_results (
                video_id,
                chunk_id,
                extraction_json
            )
            VALUES (%s, %s, %s)
            """,
            (
                video_id,
                chunk_id,
                json.dumps(result)
            )
        )
    conn.commit()