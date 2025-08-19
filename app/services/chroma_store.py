from __future__ import annotations

from typing import List

import chromadb
from chromadb import PersistentClient

from app.config.settings import settings
from app.services.openai_client import embed_texts


_client = None


def get_client() -> chromadb.Client:
    global _client
    if _client is None:
        if settings.chroma_persist_dir:
            _client = PersistentClient(path=settings.chroma_persist_dir)
        else:
            _client = chromadb.Client()
    return _client


def get_or_create_collection(name: str):
    client = get_client()
    return client.get_or_create_collection(name=name)


def add_texts(collection_name: str, chunks: List[str], ids: List[str]):
    collection = get_or_create_collection(collection_name)
    embeddings = embed_texts(chunks)
    collection.add(documents=chunks, embeddings=[e.tolist() for e in embeddings], ids=ids)


def query(collection_name: str, query_text: str, k: int = 3) -> List[str]:
    collection = get_or_create_collection(collection_name)
    emb = embed_texts([query_text])[0]
    results = collection.query(query_embeddings=[emb.tolist()], n_results=k)
    return results["documents"][0] if results and results.get("documents") else []
