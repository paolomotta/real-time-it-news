import tempfile
import os
from datetime import datetime, timedelta
from app.models import NewsItem
from app.storage import NewsStorage

def test_news_storage():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tf:
        test_path = tf.name

    try:
        now = datetime.utcnow()
        item1 = NewsItem(id="1", title="First", source="A", published_at=now)
        item2 = NewsItem(id="2", title="Second", source="A", published_at=now - timedelta(minutes=10))

        store = NewsStorage(persistence_file=test_path)
        store.clear()
        store.add(item1)
        store.add(item2)
        store.add(item1)  # duplicate

        assert len(store.get_all()) == 2
        assert len(store.get_by_source("A")) == 2
        assert len(store.get_since(30)) == 2  # Only item1 and item2

        store.clear()
        assert len(store.get_all()) == 0
    finally:
        os.unlink(test_path)


def test_persistence_across_sessions(tmp_path):
    file = tmp_path / "store.json"

    now = datetime.utcnow()
    item = NewsItem(id="abc", title="Test", source="source", published_at=now)

    store1 = NewsStorage(persistence_file=str(file))
    store1.clear()
    store1.add(item)

    # Create a new instance to simulate a reload
    store2 = NewsStorage(persistence_file=str(file))
    items = store2.get_all()
    assert len(items) == 1
    assert items[0].id == "abc"



def test_get_by_source_case_insensitive(tmp_path):
    store = NewsStorage(persistence_file=str(tmp_path / "store.json"))
    store.clear()

    now = datetime.utcnow()
    item1 = NewsItem(id="1", title="Item 1", source="TechCrunch", published_at=now)
    item2 = NewsItem(id="2", title="Item 2", source="techcrunch", published_at=now)

    store.add(item1)
    store.add(item2)

    result = store.get_by_source("TECHCRUNCH")
    assert len(result) == 2



def test_get_since_filters_old_items(tmp_path):
    store = NewsStorage(persistence_file=str(tmp_path / "store.json"))
    store.clear()

    now = datetime.utcnow()
    old_item = NewsItem(id="old", title="Old", source="src", published_at=now - timedelta(minutes=61))
    new_item = NewsItem(id="new", title="New", source="src", published_at=now)

    store.add_many([old_item, new_item])

    recent = store.get_since(60)
    assert len(recent) == 1
    assert recent[0].id == "new"



def test_add_many_skips_duplicates(tmp_path):
    store = NewsStorage(persistence_file=str(tmp_path / "store.json"))
    store.clear()

    now = datetime.utcnow()
    item = NewsItem(id="dup", title="Same", source="src", published_at=now)

    store.add_many([item, item])
    all_items = store.get_all()
    assert len(all_items) == 1


def test_load_from_missing_file(tmp_path, caplog):
    path = tmp_path / "nonexistent.json"
    store = NewsStorage(persistence_file=str(path))

    assert store.get_all() == []