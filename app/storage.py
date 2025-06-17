import json
from pathlib import Path
from threading import Lock
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.models import NewsItem

import logging
logger = logging.getLogger(__name__)

# TODO: In a production environment, I would consider using a database like SQLite or PostgreSQL, now skipped for time limits.
class NewsStorage:
    def __init__(self, persistence_file: str = ".data/news_store.json"):
        # Ensure .data directory exists
        data_dir = Path(persistence_file).parent
        data_dir.mkdir(parents=True, exist_ok=True)
        self._store: dict[str, NewsItem] = {}
        self._file = Path(persistence_file)
        self._lock = Lock()
        self.load_from_file()

    def add(self, item: NewsItem) -> None:
        with self._lock:
            if item.id not in self._store:  # Check if the item already exists
                self._store[item.id] = item
                self.save_to_file()
                logger.info(f"Stored news item: {item.id}")
            else:
                logger.debug(f"Skipped duplicate news item: {item.id}")

    def add_many(self, items: list[NewsItem]) -> None:
        with self._lock:
            newly_added = 0
            for item in items:
                if item.id not in self._store:  # Check if the item already exists
                    self._store[item.id] = item
                    newly_added += 1
            if newly_added > 0:
                self.save_to_file()
            logger.info(f"Stored {newly_added} new news items out of {len(items)}.")

    def get_all(self) -> list[NewsItem]:
        with self._lock:
            logger.debug("Retrieving all news items.")
            return list(self._store.values())

    def get_by_source(self, source: str) -> list[NewsItem]:
        with self._lock:
            return [item for item in self._store.values() if item.source.lower() == source.lower()]

    def get_since(self, minutes_ago: int) -> list[NewsItem]:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
        with self._lock:
            return [item for item in self._store.values() if item.published_at >= cutoff]

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
            self.save_to_file()
        logger.info("Cleared all news items from storage.")

    def save_to_file(self) -> None:
        try:
            with self._file.open("w") as f:
                json.dump([item.model_dump() for item in self._store.values()], f, default=str, indent=2)
                logger.debug(f"Saved {len(self._store)} news items to {self._file}.")
        except Exception as e:
            logger.error(f"Error saving storage file: {e}")

    def load_from_file(self) -> None:
        if not self._file.exists():
            logger.info(f"Storage file {self._file} does not exist. Starting with empty store.")
            return
        try:
            with self._file.open("r") as f:
                items = json.load(f)
                self._store = {item["id"]: NewsItem(**item) for item in items}
            logger.info(f"Loaded {len(self._store)} news items from {self._file}.")
        except Exception as e:
            logging.error(f"Error loading storage file: {e}")
