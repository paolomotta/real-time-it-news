import pytest
from datetime import datetime
from pydantic import ValidationError
from app.models import NewsItem

def test_valid_news_item():
    item = NewsItem(
        id="reddit-abc123",
        source="reddit",
        title="Test vulnerability",
        body="Details of the test",
        published_at="2025-06-14T09:00:00Z"
    )
    assert item.id == "reddit-abc123"
    assert item.source == "reddit"
    assert isinstance(item.published_at, datetime)
    assert item.body == "Details of the test"
    assert item.relevance_score is None  # Default behavior

def test_optional_body_defaults_to_empty_string():
    item = NewsItem(
        id="rss-xyz456",
        source="arstechnica",
        title="Another news headline",
        published_at="2025-06-14T10:00:00Z"
    )
    assert item.body == ""

def test_missing_required_field_raises_error():
    with pytest.raises(ValidationError) as exc_info:
        NewsItem(
            id="broken",
            source="reddit",
            published_at="2025-06-14T11:00:00Z"
        )
    assert "title" in str(exc_info.value)

def test_invalid_timestamp_format():
    with pytest.raises(ValidationError):
        NewsItem(
            id="invalid-date",
            source="reddit",
            title="Bad date format",
            published_at="14-06-2025"
        )

def test_extra_field_ignored_or_raises():
    with pytest.raises(ValidationError):
        NewsItem(
            id="extra-field",
            source="reddit",
            title="Title here",
            published_at="2025-06-14T09:00:00Z",
            extra_field="unexpected"
        )
