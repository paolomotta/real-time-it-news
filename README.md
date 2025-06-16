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
   git clone https://github.com/paolomotta/real-time-it-news.git
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

    To fetch news from Reddit, the system requires Reddit API credentials. If you haven’t already:

    #### 🧾 Create a Reddit Account
    - Sign up at [https://www.reddit.com/register](https://www.reddit.com/register)

    #### ⚙️ Register a Reddit Developer App
    Once logged in:

    1. Visit the Reddit developer dashboard:  
      👉 [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)

    2. If you haven’t created any apps yet, click the `“Are you a developer? Create an app...”` button at the top left of the page.  
      If you already have apps, scroll to the bottom and click `“Create another app...”`.

    3. Fill out the form:
      - **Name**: `real-time-it-news` (or any descriptive name)
      - **App Type**: Select **script**
      - **Description**: _(optional)_
      - **Redirect URI**: `http://localhost:8080` (required, even if unused)

    4. Click `Create app`

    After submitting, you will be provided with:
    - **Client ID** → displayed just below your app name
    - **Client Secret** → labeled as “secret”
    - **User Agent** → a string identifying your app (e.g., `real-time-it-news by u/your_reddit_username`)

    You’ll need to add these to your `.env` file in the next step.



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

You can start the application **either from the command line** (locally) **or using Docker**.


### 🖥️ Option 1: Run Locally

Start the FastAPI server with:

```bash
uvicorn app.api:app --reload
```

The API will be available at http://localhost:8000.
### 🐳 Option 2: Run with Docker

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

The API will be available at http://localhost:8000.

⚠️ Ensure Docker is installed and [your user has permission to access the Docker daemon](https://stackoverflow.com/questions/48957195/how-to-fix-docker-permission-denied) (e.g., add your user to the docker group).


### 🐳 Installing Docker (if needed)

If you don’t have Docker installed, follow the official instructions for your operating system:

- [Get Docker for Windows, Mac, or Linux](https://docs.docker.com/get-docker/)

After installation, you can verify from terminal that Docker is working by running:

```bash
docker --version
```

If you want to use Docker Compose, you may also need to install it separately. See [Install Docker Compose](https://docs.docker.com/compose/install/) for details.



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

## 🗂️ Project Structure

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

