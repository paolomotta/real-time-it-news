from datetime import datetime, timedelta, timezone
from app.models import NewsItem
from app.storage import NewsStorage

from datetime import datetime, timedelta, timezone
from app.models import NewsItem
from app.storage import NewsStorage

def make_item(id, source, minutes_ago=0):
    now = datetime.now(timezone.utc)
    return NewsItem(
        id=id,
        title=f"Title {id}",
        source=source,
        published_at=now - timedelta(minutes=minutes_ago)
    )

def test_add_and_get_all():
    store = NewsStorage()
    store.clear()
    item1 = make_item("1", "A")
    item2 = make_item("2", "A", minutes_ago=10)
    store.add(item1)
    store.add(item2)
    assert len(store.get_all()) == 2

def test_add_duplicate():
    store = NewsStorage()
    store.clear()
    item = make_item("1", "A")
    store.add(item)
    store.add(item)
    assert len(store.get_all()) == 1

def test_add_many_skips_duplicates():
    store = NewsStorage()
    store.clear()
    item = make_item("dup", "src")
    store.add_many([item, item])
    assert len(store.get_all()) == 1

def test_get_by_source_case_insensitive():
    store = NewsStorage()
    store.clear()
    item1 = make_item("1", "TechCrunch")
    item2 = make_item("2", "techcrunch")
    store.add(item1)
    store.add(item2)
    result = store.get_by_source("TECHCRUNCH")
    assert len(result) == 2

def test_get_since_filters_old_items():
    store = NewsStorage()
    store.clear()
    old_item = make_item("old", "src", minutes_ago=61)
    new_item = make_item("new", "src")
    store.add_many([old_item, new_item])
    recent = store.get_since(60)
    assert len(recent) == 1
    assert recent[0].id == "new"

def test_clear_removes_all_items():
    store = NewsStorage()
    store.clear()
    store.add(make_item("1", "A"))
    store.add(make_item("2", "B"))
    store.clear()
    assert store.get_all() == []