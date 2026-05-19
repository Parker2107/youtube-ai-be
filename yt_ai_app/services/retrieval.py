from yt_ai_app.services import embedding
from yt_ai_app.services import db

def retrieve_chunks(query, video_id, top_k=5):

    # Step 1: Generate embedding
    query_embedding = embedding.create_embedding_huggingface(query)

    # Step 2: Connect to DB
    conn = db.get_connection()

    with conn.cursor() as cursor:

        cursor.execute("""
            SELECT
                chunk_text,
                start_time,
                end_time,
                embedding_small <=> %s::vector AS distance
            FROM video_chunks
            WHERE video_id = %s
            ORDER BY distance
            LIMIT %s
        """, (query_embedding, video_id, top_k))

        results = cursor.fetchall()

    return results