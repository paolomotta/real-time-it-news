import pytest
import time
from unittest.mock import patch, MagicMock
from app import ingestion

# Sample config structure matching the new ingestion.py
FAKE_RSS_FEED = {
    "websites": {
        "mocksource": "http://mocksource.com"
    },
    "reddit_subreddits": ["netsec"]
}

@patch("app.ingestion.yaml.safe_load", return_value=FAKE_RSS_FEED)
@patch("pathlib.Path.exists", return_value=True)
def test_websites_from_config(mock_exists, mock_yaml):
    feeds = ingestion.load_websites_from_config()
    assert "mocksource" in feeds
    assert feeds["mocksource"] == "http://mocksource.com"

@patch("app.ingestion.yaml.safe_load", return_value=FAKE_RSS_FEED)
@patch("pathlib.Path.exists", return_value=True)
def test_load_reddit_subreddits_from_config(mock_exists, mock_yaml):
    subreddits = ingestion.load_reddit_subreddits_from_config()
    assert "netsec" in subreddits

@patch("app.ingestion.os.getenv", return_value=None)
@patch("builtins.input", return_value="dummy_value")
def test_get_env_or_prompt_fallback(mock_input, mock_getenv):
    val = ingestion.get_env_or_prompt("TEST_VAR", "Prompt:")
    assert val == "dummy_value"

@patch("app.ingestion.feedparser.parse")
@patch("app.ingestion.find_feeds", return_value=["http://rss.test/feed.xml"])
@patch("app.ingestion.load_websites_from_config", return_value={"mocksource": "http://rss.test"})
def test_fetch_rss_news(mock_load_config, mock_find_feeds, mock_feedparser):
    published_time = time.struct_time((2025, 6, 15, 12, 0, 0, 0, 0, 0))

    mock_entry = MagicMock()
    mock_entry.title = "Mock News"
    mock_entry.summary = "Important summary"
    mock_entry.get.side_effect = lambda key, default=None: {
        "id": "1234",
        "link": "http://mocksource.com/article",
        "summary": "Important summary",
        "published_parsed": published_time,
    }.get(key, default)

    mock_feed = MagicMock()
    mock_feed.entries = [mock_entry]
    mock_feedparser.return_value = mock_feed

    news = ingestion.fetch_rss_news()
    assert isinstance(news, list)
    assert len(news) == 1
    assert news[0]["title"] == "Mock News"
    assert news[0]["source"] == "mocksource"

@patch("app.ingestion.reddit")
@patch("app.ingestion.load_reddit_subreddits_from_config", return_value=["netsec"])
def test_fetch_reddit_posts(mock_subs, mock_reddit):
    mock_post = MagicMock()
    mock_post.id = "abc123"
    mock_post.title = "Reddit Security News"
    mock_post.selftext = "Details inside"
    mock_post.created_utc = 1750000000

    mock_reddit.subreddit.return_value.hot.return_value = [mock_post]

    posts = ingestion.fetch_reddit_posts()
    assert isinstance(posts, list)
    assert len(posts) == 1
    assert posts[0]["source"].startswith("reddit")

@patch("app.ingestion.fetch_rss_news", return_value=[{"id": "rss-1", "source": "mock", "title": "rss", "published_at": "2025-06-15T00:00:00"}])
@patch("app.ingestion.fetch_reddit_posts", return_value=[{"id": "reddit-1", "source": "reddit", "title": "reddit", "published_at": "2025-06-15T00:00:00"}])
def test_fetch_all_sources(mock_reddit, mock_rss):
    items = ingestion.fetch_all_sources()
    assert isinstance(items, list)
    assert len(items) == 2
