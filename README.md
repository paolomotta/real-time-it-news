# 📡 real-time-it-news
Aggregates and filters cybersecurity and IT-related news from Reddit and public RSS feeds, applies intelligent filtering, and serves the latest updates through a FastAPI interface.

## 🚀 Features

✅ Fetches news from Reddit and RSS feeds

✅ Filters for relevant IT incidents (e.g. CVEs, breaches, zero-days)

✅ Scores and ranks items by importance × recency

✅ REST API for ingestion, retrieval, and reset

✅ Easily testable and extendable

✅ Dockerized for easy deployment


## 🧰 Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/real-time-it-news.git
   cd real-time-it-news
   ```

2. **Create and activate a virtual environment**
    ```bash
    python3 -m venv news
    source news/bin/activate
    ```
    Alternatively, you can use a Conda environment:
    ```bash
    conda create -n news python=3.11 pip -y 
    conda activate news
    ```

3. **Install dependecies**
    ```bash 
    pip install -r requirements.txt
    ```

4. **Configure Reddit API Access** 

    To fetch news from Reddit, you need Reddit API credentials. Follow these steps:
    - Go to https://www.reddit.com/prefs/apps
    - Scroll down and click **“Create App”** or **“Create Another App”**
    - Fill in the form:
        - **Name**: `real-time-it-news`
        - **App Type**: `script`
        - **Redirect URI**: `http://localhost:8080`
    - After creating the app, you will receive:
        - `client_id` (under the app name)
        - `client_secret` (called secret)


5. **Set up environment variables**

    - Copy the example environment file to create your own configuration:
      ```bash
      cp .env.example .env
      ```
    - Open the newly created `.env` file and fill in your Reddit API credentials:
      ```env
      REDDIT_CLIENT_ID=your_client_id_here
      REDDIT_CLIENT_SECRET=your_client_secret_here
      REDDIT_USER_AGENT=real-time-it-news by u/your_reddit_username
      ```
    - Save the file. The application will automatically load these variables at runtime.

6. **Configure the RSS Feeds**

    The application uses a YAML file to specify which RSS feeds to aggregate.
    Open `config/feeds.yaml` in a text editor and add or modify the RSS feeds you want to include.


## Configuration: Relevance Scoring

The filtering logic is governed by a YAML file located at `config/relevance_config.yaml`. It defines:

- **Keyword scores**: Terms that increase an article’s relevance (e.g., `"exploit": 3`)
- **Regex patterns**: Structural patterns with additional weight
- **Source weights**: How trustworthy/relevant a source is considered

This allows you to adjust filtering behavior without modifying the code.

Example:

```yaml
keyword_scores:
  ransomware: 5
  breach: 4
  critical vulnerability: 5

pattern_bonuses:
  - pattern: CVE-\d{4}-\d+
    bonus: 3

source_weights:
  reddit: 1.0
  arstechnica: 1.2
  mock: 1.0
```

## 🏁 Running the Application

Start the FastAPI server with:

```bash
uvicorn app.api:app --reload
```


## 📦 Docker Support

**Build the image:**
```bash
docker build -t it-news-app .
```

**Run the container**:
```bash
docker run -p 8000:8000 --env-file .env it-news-app
```

Or use **Docker Compose**:
```bash
docker-compose up --build
```

⚠️ Ensure Docker is installed and your user has permission to access the Docker daemon (e.g., add your user to the docker group).


## 🧪 Testing

Run all tests with:

```bash
pytest
```

Test coverage includes:

- API endpoints (api.py)

- Filtering logic (filtering.py)

- Relevance scoring (ranking.py)

- Storage persistence (storage.py)

- Data validation (models.py)

- Ingestion integration (ingestion.py)

## Project Structure

The project is organized into a clear directory structure to separate core components, tests, and documentation:

```
real-time-it-news/
├── app/
│   ├── api.py              # FastAPI endpoints
│   ├── filtering.py        # Keyword + semantic filtering logic
│   ├── ingestion.py        # Reddit + RSS ingestion
│   ├── models.py           # Pydantic schemas
│   ├── ranking.py          # Importance × recency sorting
│   └── storage.py          # Persistent JSON-based storage
├── tests/                  # Unit + integration tests
│   ├── test_api.py
│   ├── test_storage.py
│   ├── test_filtering.py
│   ├── test_ranking.py
│   ├── test_models.py
│   └── test_ingestion.py
├── config/
│   ├── feeds.yaml              # Subreddits and RSS sources
│   ├── relevance_config.yaml   # Keyword, pattern, and source weight configuration for filtering
├── .env.example            # Example environment variables
├── Dockerfile              # Docker container setup
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Project dependencies
├── README.md               # This file
└── future_work.md          # Notes on trade-offs and future work
```

