import pytest
from datetime import datetime, timedelta
from app.models import NewsItem
from app.ranking import sort_news_items

@pytest.fixture
def unsorted_news_items():
    now = datetime.utcnow()
    return [
        NewsItem(id="b", title="Item B", source="test", published_at=now - timedelta(minutes=2), relevance_score=5.0),
        NewsItem(id="a", title="Item A", source="test", published_at=now - timedelta(minutes=1), relevance_score=5.0),
        NewsItem(id="c", title="Item C", source="test", published_at=now - timedelta(minutes=3), relevance_score=4.0),
        NewsItem(id="d", title="Item D", source="test", published_at=now - timedelta(minutes=2), relevance_score=None),
    ]

def test_sort_news_items_by_relevance_and_recency(unsorted_news_items):
    sorted_items = sort_news_items(unsorted_news_items)
    ids = [item.id for item in sorted_items]

    # a and b have highest relevance score (5.0), a is more recent
    # c has lower score (4.0)
    # d has no score, treated as 0
    assert ids == ["a", "b", "c", "d"]

def test_sort_with_equal_scores_and_dates():
    now = datetime.utcnow()
    items = [
        NewsItem(id="z", title="Z", source="test", published_at=now, relevance_score=2.0),
        NewsItem(id="x", title="X", source="test", published_at=now, relevance_score=2.0),
        NewsItem(id="y", title="Y", source="test", published_at=now, relevance_score=2.0),
    ]
    sorted_items = sort_news_items(items)
    ids = [item.id for item in sorted_items]

    # Tie on score and time → sort by id
    assert ids == ["x", "y", "z"]
