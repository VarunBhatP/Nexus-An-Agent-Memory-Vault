from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

#To get the embedding of a given text
def get_embedding(text: str) -> list[float]: 
    return model.encode(text).tolist()

#To compute cosine similarity between two vectors
def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))