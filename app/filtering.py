import re
import logging
import yaml
from app.models import NewsItem

logger = logging.getLogger(__name__)

def load_relevance_config(config_path="config/relevance_config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

_config = load_relevance_config()
KEYWORD_SCORES = _config["keyword_scores"]
PATTERN_BONUSES = [(entry["pattern"], entry["bonus"]) for entry in _config["pattern_bonuses"]]
SOURCE_WEIGHTS = _config["source_weights"]
THRESHOLD = _config.get("threshold", 2.0)  # Default to 2.0 if not set

def compute_relevance_score(item: NewsItem) -> float:
    content = f"{item.title} {item.body or ''}".lower()
    score = 0

    keyword_scores = KEYWORD_SCORES if KEYWORD_SCORES is not None else {}
    pattern_bonuses = PATTERN_BONUSES if PATTERN_BONUSES is not None else []
    source_weights = SOURCE_WEIGHTS if SOURCE_WEIGHTS is not None else {}

    for keyword, weight in keyword_scores.items():
        if keyword in content:
            logger.debug(f"Keyword '{keyword}' matched in item '{item.id}' (+{weight})")
            score += weight

    for pattern, bonus in pattern_bonuses:
        if re.search(pattern, content, flags=re.IGNORECASE):
            logger.debug(f"Pattern '{pattern}' matched in item '{item.id}' (+{bonus})")
            score += bonus

    source_weight = source_weights.get(item.source.lower(), 1.0)
    final_score = score * source_weight
    logger.debug(f"Item '{item.id}' base score: {score}, source weight: {source_weight}, final score: {final_score}")
    return final_score

def is_relevant(item: NewsItem, threshold: float = None) -> bool:
    """
    Return True if the item is considered relevant based on a score threshold.
    Args:
        item (NewsItem): The news item to evaluate.
        threshold (float, optional): The score threshold for relevance. If None, uses config value.
    Returns:
        bool: True if the item is relevant, False otherwise.
    """
    if threshold is None:
        threshold = THRESHOLD
    score = compute_relevance_score(item)
    relevant = score >= threshold
    logger.debug(f"Item '{item.id}' relevance: {score} (threshold: {threshold}) -> {'relevant' if relevant else 'not relevant'}")
    return relevant
