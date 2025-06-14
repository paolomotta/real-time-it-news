# real-time-it-news
Real-time newsfeed system that aggregates IT-related news items from selected public sources, filters them for relevance, and provides an easyto-use interface to display the latest updates.


## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/real-time-it-news.git
   cd real-time-it-news
   ```

2. **Create and activate a virtual environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    Alternatively, you can use a Conda environment:
    ```bash
    conda create -n it-newsfeed python=3.11 pip -y 
    conda activate it-newsfeed
    ```

3. **Install dependecies**
    ```bash 
    pip install -r requirements.txt
    ```


## Project Structure

The project is organized into a clear directory structure to separate core components, tests, and documentation:

```
nexthink-it-newsfeed/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── ingestion.py          # Handles ingestion from Reddit and RSS sources
│   ├── filtering.py          # Implements news filtering logic
│   ├── storage.py            # Manages event storage and ranking
│   ├── api.py                # Defines FastAPI endpoints
│   └── models.py             # Contains event data schemas
├── tests/
│   └── test_filtering.py     # Unit tests for filtering logic
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
└──README.md                 # Project documentation
```

