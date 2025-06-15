import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler

# Logging configuration
from app.logging_config import configure_logging
configure_logging()
logger = logging.getLogger(__name__)

from app.models import NewsItem
from app.filtering import is_relevant, compute_relevance_score
from app.storage import NewsStorage
from app.ranking import sort_news_items
from app.ingestion import fetch_all_sources

app = FastAPI(title="Mock IT Newsfeed API")

# Initialize storage
storage = NewsStorage()

# Setup templates and static files
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# === Continuous Fetch Job ===
def scheduled_fetch():
    logger.info("🔄 [Scheduled] Fetching and ingesting news...")
    raw_items = fetch_all_sources()

    # Convert dicts to NewsItem models
    typed_items = []
    for raw in raw_items:
        try:
            typed_items.append(NewsItem(**raw))
        except Exception as e:
            logger.info(f"⚠️ Skipped invalid item: {e}")

    relevant = []
    for item in typed_items:
        if is_relevant(item):
            item.relevance_score = compute_relevance_score(item)
            relevant.append(item)

    storage.add_many(relevant)
    logger.info(f"✅ [Scheduled] Ingested {len(relevant)} items")

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_fetch, "interval", minutes=1)
scheduler.start()


# === Routes ===

@app.post("/ingest", status_code=200)
def ingest_items(items: list[NewsItem]):
    """
    Accepts a list of news items, filters them, and stores only the relevant ones.
    """
    if not items:
        return {"message": "No items provided, nothing to ingest.", "accepted": 0, "total": 0}

    relevant = []
    for item in items:
        if is_relevant(item):
            item.relevance_score = compute_relevance_score(item)
            relevant.append(item)

    storage.add_many(relevant)
    return {"accepted": len(relevant), "total": len(items)}


@app.get("/retrieve", response_model=list[NewsItem])
def retrieve_items():
    """
    Returns stored relevant news items sorted by relevance × recency.
    """
    all_items = storage.get_all()
    return sort_news_items(all_items)


@app.post("/reset")
def reset_storage():
    """
    Clears all stored news items.
    """
    storage.clear()
    return {"status": "cleared"}


@app.get("/", response_class=HTMLResponse)
def show_dashboard(request: Request):
    """
    Serves the web dashboard page.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})

