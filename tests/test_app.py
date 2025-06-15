import pytest
from fastapi.testclient import TestClient
from app.api import app
from app.models import NewsItem
from app.filtering import is_relevant, compute_relevance_score

# Create a TestClient instance for making requests to the FastAPI app
client = TestClient(app)


# === Auto-used fixture to reset storage before/after each test ===
@pytest.fixture(autouse=True)
def clear_storage():
    client.post("/reset")
    yield
    client.post("/reset")

@pytest.fixture
def sample_news():
    return [
        {
            "id": "1",
            "title": "Apple rolls out urgent security patch",
            "body": "Fixes flaws actively exploited in the wild.",
            "source": "Source B",
            "published_at": "2025-06-15T16:10:00Z"
        },
        {
            "id": "2",
            "title": "Zero-day exploit in Microsoft Edge",
            "body": "New vulnerability affects latest version.",
            "source": "Source A",
            "published_at": "2025-06-15T16:00:00Z"
        },
    ]


# === Test for /ingest Endpoint ===
def test_ingest_news(sample_news):
    response = client.post("/ingest", json=sample_news)
    assert response.status_code == 200
    assert response.json()["accepted"] == 2  # Assuming both items are accepted
    assert response.json()["total"] == 2

def test_ingest_empty_list():
    response = client.post("/ingest", json=[])
    assert response.status_code == 200
    assert response.json()["accepted"] == 0  # No items accepted
    assert response.json()["total"] == 0  # No items provided

def test_ingest_invalid_item():
    # Test invalid item with missing required fields
    invalid_news = [{"id": "3", "title": "Invalid News", "published_at": "2025-06-15T16:20:00Z"}]
    response = client.post("/ingest", json=invalid_news)
    assert response.status_code == 422 # Should return validation error


def test_duplicate_ingestion(sample_news):
    client.post("/ingest", json=sample_news)
    client.post("/ingest", json=sample_news)  # Duplicate

    response = client.get("/retrieve")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2 # Should still only have 2 unique items after duplicate ingestion


# === Test for /retrieve Endpoint ===
def test_retrieve_news(sample_news):
    # First, ingest the sample news
    client.post("/ingest", json=sample_news)

    # Retrieve the news
    response = client.get("/retrieve")
    assert response.status_code == 200
    data = response.json()

    # Verify the number of news items
    assert len(data) == 2  # We added 2 items in the test
    assert data[0]["id"] == "2"  # Check that the first item has the correct ID and it is the first ordered by relevance


# === Test for /reset Endpoint ===
def test_reset_storage():
    # Ingest some news first
    sample_news = [{"id": "1", "title": "Sample News", "source": "Source A", "published_at": "2025-06-15T16:00:00Z"}]
    client.post("/ingest", json=sample_news)

    # Reset the storage
    response = client.post("/reset")
    assert response.status_code == 200

    # Ensure the storage is cleared
    response = client.get("/retrieve")
    assert len(response.json()) == 0  # Storage should now be empty


# === Test for Business Logic ===

# Test the relevance filtering
def test_is_relevant():
    news_item = NewsItem(id="1", title="Critical vulnerability, need quick fix.", source="Source A", published_at="2025-06-15T16:00:00Z")
    
    # Assuming that is_relevant returns a boolean value
    assert is_relevant(news_item) is True 

# Test relevance score calculation
def test_compute_relevance_score():
    news_item = NewsItem(id="1", title="Critical vulnerability, need quick fix.", source="Source A", published_at="2025-06-15T16:00:00Z")
    
    # Assuming the relevance score is a numerical value
    score = compute_relevance_score(news_item)
    assert isinstance(score, (int, float))  # Ensure it returns a number
    assert score > 0  # Ensure a positive score
