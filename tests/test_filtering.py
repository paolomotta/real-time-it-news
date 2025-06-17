import pytest
from app.filtering import compute_relevance_score, is_relevant
from app.models import NewsItem
from datetime import datetime, timezone

# Sample news items
@pytest.fixture
def high_relevance_item():
    return NewsItem(
        id="test-001",
        title="Critical zero-day vulnerability in Microsoft Exchange exploited",
        body="Attackers released an exploit. CVE-2025-12345 issued. Patch now.",
        source="arstechnica",
        published_at=datetime.now(timezone.utc)
    )

@pytest.fixture
def low_relevance_item():
    return NewsItem(
        id="test-002",
        title="Company updates terms of service",
        body="The new TOS will be effective starting August 1.",
        source="reddit",
        published_at=datetime.now(timezone.utc)
    )

# === TEST: compute_relevance_score ===

def test_score_high_relevance(high_relevance_item):
    score = compute_relevance_score(high_relevance_item)
    assert score > 5, "Expected high relevance score for critical incident"

def test_score_low_relevance(low_relevance_item):
    score = compute_relevance_score(low_relevance_item)
    assert score < 2, "Expected low relevance score for generic update"

# === TEST: is_relevant ===

def test_is_relevant_true(high_relevance_item):
    assert is_relevant(high_relevance_item) is True

def test_is_relevant_false(low_relevance_item):
    assert is_relevant(low_relevance_item) is False
