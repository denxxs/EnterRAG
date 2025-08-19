from typing import List
import numpy as np
from openai import OpenAI
from app.config.settings import settings

_client = None


def get_openai_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def embed_texts(texts: List[str]) -> List[np.ndarray]:
    client = get_openai_client()
    resp = client.embeddings.create(model=settings.embedding_model, input=texts)
    return [np.array(d.embedding) for d in resp.data]


def stream_chat(messages):
    client = get_openai_client()
    return client.chat.completions.create(model=settings.chat_model, messages=messages, stream=True)


def chat_once(messages):
    client = get_openai_client()
    return client.chat.completions.create(model=settings.chat_model, messages=messages)
