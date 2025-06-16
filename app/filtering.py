import re
import logging
import yaml
from app.models import NewsItem

logger = logging.getLogger(__name__)

# TODO: Using an LLM for semantic understanding would be ideal


def load_relevance_config(config_path="config/relevance_config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

_config = load_relevance_config()
KEYWORD_SCORES = _config["keyword_scores"] # Weighted keywords indicating relevance
PATTERN_BONUSES = [(entry["pattern"], entry["bonus"]) for entry in _config["pattern_bonuses"]] # Regex patterns for boosting scores based on structure
SOURCE_WEIGHTS = _config["source_weights"] # Optional: weight based on source reliability


def compute_relevance_score(item: NewsItem) -> float:
    """
    Calculate a weighted relevance score for a news item based on content and source.
    The score is based on keyword matches, regex patterns, and source reliability.
    Args:
        item (NewsItem): The news item to evaluate.
    Returns:
        float: The computed relevance score.
    """
    content = f"{item.title} {item.body or ''}".lower()
    score = 0

    # Score keyword matches
    for keyword, weight in KEYWORD_SCORES.items():
        if keyword in content:
            logger.debug(f"Keyword '{keyword}' matched in item '{item.id}' (+{weight})")
            score += weight

    # Apply bonus points for regex pattern matches
    for pattern, bonus in PATTERN_BONUSES:
        if re.search(pattern, content, flags=re.IGNORECASE):
            logger.debug(f"Pattern '{pattern}' matched in item '{item.id}' (+{bonus})")
            score += bonus

    # Adjust based on source weight
    source_weight = SOURCE_WEIGHTS.get(item.source.lower(), 1.0)
    final_score = score * source_weight
    logger.debug(f"Item '{item.id}' base score: {score}, source weight: {source_weight}, final score: {final_score}")
    return final_score


def is_relevant(item: NewsItem, threshold: float = 2.0) -> bool:
    """
    Return True if the item is considered relevant based on a score threshold.
    Args:
        item (NewsItem): The news item to evaluate.
        threshold (float): The score threshold for relevance.
    Returns:
        bool: True if the item is relevant, False otherwise.
    """
    score = compute_relevance_score(item)
    relevant = score >= threshold
    logger.debug(f"Item '{item.id}' relevance: {score} (threshold: {threshold}) -> {'relevant' if relevant else 'not relevant'}")
    return score >= threshold
