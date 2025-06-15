import os
from datetime import datetime
import logging
from typing import List, Dict
import feedparser
import praw
import yaml
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger(__name__)

# Load credentials from .env file (if available)
load_dotenv()


def load_rss_feeds_from_config(config_path: str = "config/feeds.yaml") -> Dict[str, str]:
    try:
        path = Path(config_path)
        if not path.exists():
            logger.warning(f"Config file {config_path} not found.")
            return {}
        with path.open("r") as f:
            config = yaml.safe_load(f)
            return config.get("rss_feeds", {})
    except Exception as e:
        logger.error(f"Error loading feed config: {e}")
        return {}


def load_reddit_subreddits_from_config(config_path: str = "config/feeds.yaml") -> list[str]:
    try:
        path = Path(config_path)
        if not path.exists():
            logger.warning(f"Config file {config_path} not found.")
            return []
        with path.open("r") as f:
            config = yaml.safe_load(f)
            return config.get("reddit_subreddits", [])
    except Exception as e:
        logger.error(f"Error loading subreddit config: {e}")
        return []


def get_env_or_prompt(var_name: str, prompt_msg: str) -> str:
    """
    Try to get env var, otherwise prompt the user.

    Args:
        var_name (str): The name of the environment variable.
        prompt_msg (str): The message to prompt the user if the variable is not set.
    Returns:
        str: The value of the environment variable or user input.
    """
    return os.getenv(var_name) or input(prompt_msg)

# Initialize Reddit client
reddit = praw.Reddit(
    client_id=get_env_or_prompt("REDDIT_CLIENT_ID", "Enter Reddit client ID: "),
    client_secret=get_env_or_prompt("REDDIT_CLIENT_SECRET", "Enter Reddit client secret: "),
    user_agent=get_env_or_prompt("REDDIT_USER_AGENT", "Enter Reddit user agent: ")
)


def fetch_reddit_posts(subreddits: list[str] = None, limit: int = 5) -> List[Dict]:
    """
    Fetch top posts from one or more subreddits.
    Args:
        subreddits (list[str]): List of subreddit names.
        limit (int): The maximum number of posts to fetch per subreddit.
    Returns:
        List[Dict]: A list of dictionaries containing post details.
    """
    if subreddits is None:
        subreddits = load_reddit_subreddits_from_config()
        if not subreddits:
            subreddits = ["netsec"]  # fallback default

    posts = []
    try:
        for subreddit in subreddits:
            for submission in reddit.subreddit(subreddit).hot(limit=limit):
                posts.append({
                    "id": f"reddit-{submission.id}",
                    "source": f"reddit/{subreddit}",
                    "title": submission.title,
                    "body": submission.selftext or "",
                    "published_at": datetime.utcfromtimestamp(submission.created_utc).isoformat()
                })
    except Exception as e:
        logger.error(f"Error fetching Reddit posts: {e}")
    return posts


def fetch_rss_news(limit_per_feed: int = 5, feeds: dict[str, str] | None = None) -> List[Dict]:
    """
    Fetch recent entries from multiple RSS feeds.
    Args:
        limit_per_feed (int): The maximum number of entries to fetch from each feed.
    Returns:
        List[Dict]: A list of dictionaries containing news items from RSS feeds.
    """
    feeds = feeds or load_rss_feeds_from_config()
    items = []
    for source_name, feed_url in feeds.items():
        try:
            d = feedparser.parse(feed_url)
            for entry in d.entries[:limit_per_feed]:
                published = entry.get("published_parsed")
                published_at = (
                    datetime(*published[:6]).isoformat() if published else datetime.utcnow().isoformat()
                )
                items.append({
                    "id": f"{source_name}-{entry.get('id', entry.get('link'))}",
                    "source": source_name,
                    "title": entry.title,
                    "body": entry.get("summary", ""),
                    "published_at": published_at
                })
        except Exception as e:
            logger.error(f"Error fetching from {source_name}: {e}")
    return items


def fetch_all_sources(include_reddit: bool = True, include_rss: bool = True) -> List[Dict]:
    """
    Fetch news from all sources and return combined list.
    Args:
        include_reddit (bool): Whether to include Reddit posts.
        include_rss (bool): Whether to include RSS feed items.
    Returns:
        List[Dict]: A list of dictionaries containing news items from all sources.
    """
    # TODO: Asynchronous fetching for large number of sources
    items = []
    if include_reddit:
        items += fetch_reddit_posts()
    if include_rss:
        items += fetch_rss_news()
    return items
