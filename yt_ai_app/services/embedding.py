from openai import OpenAI
import random
import os

def create_embedding(text):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return res.data[0].embedding

def get_fake_embedding(dim=1536):
    return [random.random() for _ in range(dim)]


# 13340ug02