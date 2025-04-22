import os
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings

DB_PATH = "./db/faiss/"

def store_chunks(chunks, embeddings: Embeddings, user_id: str):
    user_path = os.path.join(DB_PATH, f"{user_id}_index")
    os.makedirs(user_path, exist_ok=True)

    vectordb = FAISS.from_documents(chunks, embeddings)
    vectordb.save_local(user_path)
    return f"Stored {len(chunks)} chunks for user {user_id}"

def load_vectordb(user_id: str, embeddings: Embeddings):
    user_path = os.path.join(DB_PATH, f"{user_id}_index")
    vectordb = FAISS.load_local(user_path, embeddings)
    return vectordb
