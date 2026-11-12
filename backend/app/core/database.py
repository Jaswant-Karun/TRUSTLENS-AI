"""
TRUSTLENS AI - Database Connection Manager
Provides async MongoDB Atlas integration via motor with graceful fallback.
"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from backend.app.core.config import settings
from backend.app.core.logging import logger


class DatabaseManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    is_connected: bool = False

    async def connect(self) -> None:
        """Establishes connection to MongoDB Atlas."""
        try:
            logger.info(f"Connecting to MongoDB Atlas (DB: {settings.MONGODB_DB_NAME})...")
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=settings.MONGODB_TIMEOUT_MS,
            )
            # Ping database to verify connection
            await self.client.admin.command("ping")
            self.db = self.client[settings.MONGODB_DB_NAME]
            self.is_connected = True
            logger.info("Successfully established connection to MongoDB Atlas.")
        except Exception as exc:
            self.is_connected = False
            self.db = None
            logger.warning(
                f"MongoDB connection skipped or unavailable ({exc}). Operating in offline/mock mode."
            )

    async def disconnect(self) -> None:
        """Closes MongoDB client connection."""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("MongoDB client connection closed.")

    def get_database(self) -> Optional[AsyncIOMotorDatabase]:
        return self.db


db_manager = DatabaseManager()

