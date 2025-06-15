from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.models import NewsItem
from app.filtering import is_relevant, compute_relevance_score
from app.storage import NewsStorage
from app.ranking import sort_news_items

app = FastAPI(title="Mock IT Newsfeed API")

# Initialize storage
storage = NewsStorage()

# Mount templates and static directories
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.post("/ingest", status_code=200)
def ingest_items(items: list[NewsItem]):
    """
    Accepts a list of news items, filters them, and stores only the relevant ones.
    """
    if not items:
        raise HTTPException(status_code=400, detail="No items provided.")

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
    Returns stored relevant news items sorted by relevance x recency.
    """
    all_items = storage.get_all()
    return sort_news_items(all_items)

@app.post("/reset")
def reset_storage():
    storage.clear()
    return {"status": "cleared"}

@app.get("/", response_class=HTMLResponse)
def show_dashboard(request: Request):
    """
    Serves the web dashboard page.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})
