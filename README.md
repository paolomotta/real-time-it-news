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
    Open `feeds.yaml` in a text editor and add or modify the RSS feeds you want to include.

## Project Structure

The project is organized into a clear directory structure to separate core components, tests, and documentation:

```
real-time-it-news/
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

