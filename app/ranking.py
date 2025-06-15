from app.models import NewsItem

def sort_news_items(items: list[NewsItem]) -> list[NewsItem]:
    """
    Sort news items by:
    1. Descending relevance score
    2. Descending published_at timestamp
    3. Lexicographical ID order (tie-breaker)
    """
    return sorted(
        items,
        key=lambda item: (
            -item.relevance_score if item.relevance_score is not None else 0,
            -item.published_at.timestamp(),
            item.id
        )
    )