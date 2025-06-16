import os
import logging
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import praw
import yaml
from dotenv import load_dotenv
from feedfinder2 import find_feeds

logger = logging.getLogger(__name__)

# Load credentials from .env file (if available)
load_dotenv()


def load_config_key(key: str, config_path: str = "config/feeds.yaml", default=None):
    """
    Load a specific key from a YAML config file, returning a default if missing.
    """
    if default is None:
        default = {}
    try:
        path = Path(config_path)
        if not path.exists():
            logger.warning(f"Config file {config_path} not found.")
            return default
        with path.open("r") as f:
            config = yaml.safe_load(f)
            value = config.get(key, default) if config else default
            if value is None:
                return default
            return value
    except Exception as e:
        logger.error(f"Error loading config key '{key}': {e}")
        return default


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


def fetch_reddit_posts(subreddits: list[str] | None = None, limit: int = 10) -> list[dict[str, any]]:
    """
    Fetch top posts from one or more subreddits.
    Args:
        subreddits (list[str]): List of subreddit names.
        limit (int): The maximum number of posts to fetch per subreddit.
    Returns:
        List[Dict]: A list of dictionaries containing post details.
    """

    if subreddits is None:
        subreddits = load_config_key("reddit_subreddits", default=[])

    posts = []
    try:
        for subreddit in subreddits:
            for submission in reddit.subreddit(subreddit).hot(limit=limit):
                posts.append({
                    "id": f"reddit-{submission.id}",
                    "source": f"reddit/{subreddit}",
                    "title": submission.title,
                    "body": submission.selftext or "",
                    "published_at": datetime.fromtimestamp(submission.created_utc, tz=timezone.utc).isoformat()
                })
    except Exception as e:
        logger.error(f"Error fetching Reddit posts: {e}")
    return posts


def fetch_website_news(feeds: dict[str, str] | None = None, limit_per_feed: int = 10) -> list[dict[str, any]]:
    """
    Fetch recent entries from multiple websites. If a feed value is a homepage URL, try to auto-discover the RSS feed.
    Args:
        feeds (dict[str, str]): Dictionary of feed names and URLs. If None, loads from config.
        limit_per_feed (int): Maximum number of items to fetch from each feed.
    Returns:
        List[Dict]: A list of dictionaries containing feed items.
    """

    if feeds is None:
        feeds = load_config_key("websites", default={})
    items = []

    for source_name, url in feeds.items():
        try:
            # Discover feed URLs if not an RSS URL
            feed_urls = [url]
            if not url.endswith(".xml") and "feed" not in url:
                discovered = find_feeds(url)
                if discovered:
                    logger.debug(f"Discovered RSS feed(s) for {source_name}: {discovered}")
                    feed_urls = discovered
                else:
                    logger.warning(f"No RSS feeds found for {source_name} at {url}")
                    continue

            for feed_url in feed_urls:
                d = feedparser.parse(feed_url)
                for entry in d.entries[:limit_per_feed]:
                    published = entry.get("published_parsed")
                    published_at = (
                        datetime(*published[:6]).isoformat() if published else datetime.now(datetime.timezone.utc).isoformat()
                    )
                    items.append({
                        "id": f"{source_name}-{entry.get('id', entry.get('link'))}",
                        "source": source_name,
                        "title": entry.title,
                        "body": entry.get("summary", ""),
                        "published_at": published_at
                    })

        except Exception as e:
            logger.error(f"Error fetching from {source_name} ({url}): {e}")

    return items


def fetch_all_sources(include_reddit: bool = True, include_rss: bool = True) -> list[dict[str, any]]:
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
        items += fetch_website_news()
    return items
