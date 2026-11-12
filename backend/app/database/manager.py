"""
TRUSTLENS AI - MongoDB Connection Manager
Provides async MongoDB Atlas integration via motor with in-memory resilient fallback.
Guarantees zero crashes if MongoDB is unreachable.
"""

from typing import Optional, Dict, Any, List
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from backend.app.config.settings import settings
from backend.app.core.logging import logger


class InMemoryCollectionFallback:
    """In-memory collection mock for testing and offline development."""
    def __init__(self, name: str):
        self.name = name
        self.documents: Dict[str, Dict[str, Any]] = {}

    async def insert_one(self, doc: Dict[str, Any]):
        doc_id = str(doc.get("_id") or doc.get("id") or len(self.documents) + 1)
        doc["_id"] = doc_id
        self.documents[doc_id] = doc
        class Result:
            inserted_id = doc_id
        return Result()

    async def find_one(self, query: Dict[str, Any]):
        for doc in self.documents.values():
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                return doc
        return None

    def find(self, query: Optional[Dict[str, Any]] = None, sort: Optional[List] = None):
        query = query or {}
        matches = []
        for doc in self.documents.values():
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                matches.append(doc)

        class Cursor:
            def __init__(self, docs):
                self.docs = docs

            def sort(self, *args, **kwargs):
                return self

            def skip(self, n: int):
                self.docs = self.docs[n:]
                return self

            def limit(self, n: int):
                self.docs = self.docs[:n]
                return self

            async def to_list(self, length: Optional[int] = None):
                if length is not None:
                    return self.docs[:length]
                return self.docs

            def __aiter__(self):
                self._iter = iter(self.docs)
                return self

            async def __anext__(self):
                try:
                    return next(self._iter)
                except StopIteration:
                    raise StopAsyncIteration

        return Cursor(matches)

    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = False):
        doc = await self.find_one(query)
        if doc:
            if "$set" in update:
                doc.update(update["$set"])
            if "$inc" in update:
                for k, v in update["$inc"].items():
                    doc[k] = doc.get(k, 0) + v
        elif upsert:
            new_doc = {**query}
            if "$set" in update:
                new_doc.update(update["$set"])
            await self.insert_one(new_doc)

    async def count_documents(self, query: Optional[Dict[str, Any]] = None) -> int:
        cursor = self.find(query)
        docs = await cursor.to_list(None)
        return len(docs)

    async def create_index(self, *args, **kwargs):
        pass


class InMemoryDatabaseFallback:
    def __init__(self):
        self.collections: Dict[str, InMemoryCollectionFallback] = {}

    def __getitem__(self, name: str) -> InMemoryCollectionFallback:
        if name not in self.collections:
            self.collections[name] = InMemoryCollectionFallback(name)
        return self.collections[name]


class DatabaseManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    is_connected: bool = False
    _fallback_db = InMemoryDatabaseFallback()

    async def connect(self) -> None:
        """Establishes connection to MongoDB Atlas or initializes resilient fallback."""
        try:
            logger.info(f"Connecting to MongoDB Atlas at {settings.MONGODB_URI.split('@')[-1]} (DB: {settings.MONGODB_DB_NAME})...")
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=settings.MONGODB_TIMEOUT_MS,
            )
            # Verify connectivity via admin ping
            await self.client.admin.command("ping")
            self.db = self.client[settings.MONGODB_DB_NAME]
            self.is_connected = True
            logger.info("Successfully connected to MongoDB Atlas.")
        except Exception as exc:
            self.is_connected = False
            self.db = None
            logger.warning(
                f"MongoDB Atlas unreachable ({exc.__class__.__name__}). Operating in resilient in-memory mode."
            )

    async def disconnect(self) -> None:
        """Closes MongoDB connection cleanly."""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("MongoDB Atlas connection closed.")

    def get_collection(self, collection_name: str):
        """Returns motor collection if connected, else returns in-memory fallback collection."""
        if self.is_connected and self.db is not None:
            return self.db[collection_name]
        return self._fallback_db[collection_name]


db_manager = DatabaseManager()


def get_db():
    return db_manager
