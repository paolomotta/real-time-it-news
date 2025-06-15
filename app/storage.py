import json
import logging
from pathlib import Path
from threading import Lock
from datetime import datetime, timedelta
from app.models import NewsItem

# TODO: In a production environment, I would consider using a database like SQLite or PostgreSQL, now skipped for time limits.
class NewsStorage:
    def __init__(self, persistence_file: str = "news_store.json"):
        self._store: dict[str, NewsItem] = {}
        self._file = Path(persistence_file)
        self._lock = Lock()
        self.load_from_file()

    def add(self, item: NewsItem) -> None:
        with self._lock:
            self._store[item.id] = item
            self.save_to_file()

    def add_many(self, items: list[NewsItem]) -> None:
        with self._lock:
            for item in items:
                self._store[item.id] = item
            self.save_to_file()

    def get_all(self) -> list[NewsItem]:
        with self._lock:
            return list(self._store.values())

    def get_by_source(self, source: str) -> list[NewsItem]:
        with self._lock:
            return [item for item in self._store.values() if item.source.lower() == source.lower()]

    def get_since(self, minutes_ago: int) -> list[NewsItem]:
        cutoff = datetime.utcnow() - timedelta(minutes=minutes_ago)
        with self._lock:
            return [item for item in self._store.values() if item.published_at >= cutoff]

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
            self.save_to_file()

    def save_to_file(self) -> None:
        try:
            with self._file.open("w") as f:
                json.dump([item.dict() for item in self._store.values()], f, default=str, indent=2)
        except Exception as e:
            print(f"Error saving storage file: {e}")

    def load_from_file(self) -> None:
        if not self._file.exists():
            return
        try:
            with self._file.open("r") as f:
                items = json.load(f)
                self._store = {item["id"]: NewsItem(**item) for item in items}
        except Exception as e:
            logging.error(f"Error loading storage file: {e}")
