import re
import logging
from app.models import NewsItem

logger = logging.getLogger(__name__)

# TODO: Using an LLM for semantic understanding would be ideal

# Weighted keywords indicating relevance
KEYWORD_SCORES = {
    "ransomware": 5,
    "breach": 4,
    "CVE": 3,
    "critical vulnerability": 5,
    "exploit": 3,
    "ddos": 4,
    "leak": 3,
    "zero-day": 5,
    "patch": 2,
    "mitigation": 2,
    "outage": 3
}

# Regex patterns for boosting scores based on structure
PATTERN_BONUSES = [
    (r"CVE-\d{4}-\d+", 3),            # CVE references
    (r"\bAWS\b.*\boutage\b", 2),      # AWS outage
    (r"\bGoogle\b.*\bbreach\b", 2),   # Org + incident
    (r"\bexploit\s+released\b", 3)    # Escalating threats
]

# Optional: weight based on source reliability
SOURCE_WEIGHTS = {
    "reddit": 1.0,
    "arstechnica": 1.2,
    "tomshardware": 1.1,
    "mock": 1.0
}


def compute_relevance_score(item: NewsItem) -> float:
    """
    Calculate a weighted relevance score for a news item based on content and source.
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
    """
    score = compute_relevance_score(item)
    relevant = score >= threshold
    logger.debug(f"Item '{item.id}' relevance: {score} (threshold: {threshold}) -> {'relevant' if relevant else 'not relevant'}")
    return score >= threshold
