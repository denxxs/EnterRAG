from __future__ import annotations

import logging
from typing import Dict, List, Optional

from bson.objectid import ObjectId  # provided by pymongo (bundled with pymongo)
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from app.config.settings import settings

logger = logging.getLogger(__name__)


_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        if not settings.mongodb_uri:
            raise RuntimeError("MONGODB_URI is not set in environment")
        _client = MongoClient(settings.mongodb_uri, server_api=ServerApi("1"))
        try:
            _client.admin.command("ping")
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.exception("Error connecting to MongoDB")
            raise
    return _client


def insert_pdf_data(data: Dict) -> Optional[str]:
    client = get_client()
    db = client.enterrag_db
    collection = db.pdf_data
    result = collection.insert_one(data)
    return str(result.inserted_id)


def fetch_pdf_data(limit: int = 100, include_id: bool = True) -> List[Dict]:
    client = get_client()
    db = client.enterrag_db
    collection = db.pdf_data
    projection = None if include_id else {"_id": 0}
    docs = list(collection.find({}, projection).limit(limit))
    # Ensure ObjectId is stringified for Streamlit display
    if include_id:
        for d in docs:
            if isinstance(d.get("_id"), ObjectId):
                d["_id"] = str(d["_id"])  # type: ignore
    return docs


def update_pdf_document(document_id: str, updated_document: Dict) -> bool:
    client = get_client()
    db = client.enterrag_db
    collection = db.pdf_data
    updated = dict(updated_document)
    updated.pop("_id", None)
    result = collection.update_one({"_id": ObjectId(document_id)}, {"$set": updated})
    logger.info("MongoDB update modified_count=%s", result.modified_count)
    return result.modified_count > 0
