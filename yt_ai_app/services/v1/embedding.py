from sentence_transformers import SentenceTransformer
from openai import OpenAI
import random
import os

model = SentenceTransformer('all-MiniLM-L6-v2')

def create_embedding_openai(text):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return res.data[0].embedding

def create_embedding_huggingface(text):
    
    embedding = model.encode(text)
    return embedding.tolist()

def get_fake_embedding(dim=1536):
    return [random.random() for _ in range(dim)]