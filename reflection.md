# 💬 Discussion 

## Requirements

### **1. Data Aggregation & Ingestion Strategy**

The core ingestion logic is implemented in [`app/ingestion.py`](app/ingestion.py). The design follows a modular approach to make it easy to add or remove news sources.

- **Reddit Integration:**  
  The system uses the PRAW library to fetch posts from IT-focused subreddits. Subreddits are configured in [`config/feeds.yaml`](config/feeds.yaml) under the `reddit_subreddits` key, making it easy to add or remove subreddits without code changes.

- **Website/RSS Integration:**  
  IT news websites are specified in the same config file under the `websites` key. The ingestion logic uses `feedparser` and `feedfinder2` to auto-discover and parse RSS feeds from these sites. This allows for flexible addition of new sources by simply updating the YAML config.

- **Extensibility:**  
  The [`load_config_key`](app/ingestion.py) function abstracts configuration loading, so new source types can be added with minimal changes. The main fetch functions—[`fetch_reddit_posts`](app/ingestion.py) and [`fetch_website_news`](app/ingestion.py)—are independent and can be extended or replaced as needed.

- **Continuous Fetching:**  
  The ingestion process is scheduled to run periodically (see [`app/api.py`](app/api.py)), ensuring the news feed stays up to date.

- **Synthetic Batch Support:**  
  The API is designed to accept synthetic batches via the `/ingest` endpoint, supporting the test harness requirements.

This modular structure ensures that new sources can be integrated by updating configuration files, without modifying the core ingestion code. 


### **2. Content Filtering**

To ensure that only news items relevant to IT managers are surfaced (e.g., outages, security incidents, major vulnerabilities), I implemented a rule-based filtering mechanism in [`app/filtering.py`](app/filtering.py).

**Approach:**

- **Keyword Scoring:**  
  Each news item is scored based on the presence of weighted keywords (e.g., "ransomware", "breach", "outage") in its title and body. The weights are defined in [`config/relevance_config.yaml`](config/relevance_config.yaml), allowing easy adjustment and extension.

- **Pattern Bonuses:**  
  Additional points are awarded if the news item matches certain regular expression patterns (e.g., CVE identifiers, phrases like "exploit released"). This helps capture structured signals of high relevance that may not be covered by simple keywords.

- **Source Weighting:**  
  Each source (e.g., Reddit, Ars Technica) can be assigned a reliability weight, so items from more trusted or relevant sources are scored higher.

- **Thresholding:**  
  Only items whose computed relevance score exceeds a configurable threshold are considered relevant and stored.

**Justification:**

This rule-based approach is transparent, auditable, and highly configurable. It enables rapid iteration and tuning based on feedback. While not as nuanced as a machine learning model, it is robust for the assignment's scope and ensures that only items with clear IT management relevance are included. The configuration-driven design also makes it easy to adapt the filter as new threats or topics emerge.

**Reflection and Alternatives:**

Initially, I experimented with a language model (LLM)-based approach for semantic filtering. However, despite prompt engineering, I encountered too many false positives and false negatives. With more time, it might have been possible to identify or fine-tune a model better suited to this specific domain. For this assignment, I reverted to the rule-based solution for its stability, transparency, and ease of control. In the future, a hybrid or fine-tuned LLM-based filter could further improve relevance detection, as discussed in the "Future Work" section.


### **3. User Interface**

To fulfill the requirement for a simple user interface, I implemented a lightweight web dashboard using FastAPI and Jinja2 templates. The dashboard is served at the root endpoint (`/`) and is styled with a custom CSS file for clarity and readability.

**Key Features:**

- **Live News Feed:**  
  The dashboard displays all filtered news items, ranked by a combination of relevance and recency. News items are fetched from the `/retrieve` API endpoint and updated automatically every 10 seconds using JavaScript, ensuring users always see the latest relevant news.

- **Clear Presentation:**  
  Each news item shows its title, source, publication time, and summary/body. The design uses a clean layout and color scheme to highlight important information and improve readability.

This approach provides a user-friendly and accessible way for IT managers to stay informed about the most relevant and recent IT news, without requiring any command-line interaction or complex setup.


### 4. **Automated Evaluation Interface (Mock Newsfeed API)**

The Mock Newsfeed API is implemented using **FastAPI**, a modern Python web framework that provides automatic data validation, OpenAPI documentation, and high performance. Below are the key technical aspects of the solution:

- **Data Model:**  
  All news items are represented using a Pydantic `NewsItem` model (`app/models.py`). This ensures strict validation of incoming data for required fields (`id`, `source`, `title`, `published_at`) and correct types, with automatic error responses for malformed input.

- **In-Memory Storage with Persistence:**  
  News items are managed by a `NewsStorage` class (`app/storage.py`), which stores relevant items in memory and can persist them to disk as a JSON file. This allows for fast access and easy reset during tests, while also supporting durability between runs if needed.

- **/ingest Endpoint:**  
  - Accepts a JSON array of news items via POST.
  - Each item is parsed and validated as a `NewsItem`.
  - The filtering logic (`is_relevant` and `compute_relevance_score` from `app/filtering.py`) is applied to each item.
  - Only items passing the relevance threshold are stored, with their computed relevance score.
  - Returns a JSON acknowledgment with the number of accepted and total items.
  - Example response:  
    ```json
    {"accepted": 3, "total": 5}
    ```

- **/retrieve Endpoint:**  
  - Returns all stored, relevant news items as a JSON array.
  - Items are sorted using the `sort_news_items` function (`app/ranking.py`), which orders by descending relevance score, then by recency (`published_at`), and finally by ID for deterministic results.
  - The endpoint uses FastAPI’s response model feature to ensure the output matches the expected schema.

- **/reset Endpoint:**  
  - Accepts a POST request.
  - Calls the `clear()` method on the storage backend, removing all stored news items.
  - Returns a simple JSON status message.
  - This endpoint is critical for automated testing, as it allows the test harness to ensure a clean state before each test run.

- **Statelessness:**  
  - The API does not use sessions or per-client state. All state is global and can be reset via `/reset`.
  - Each endpoint operates independently, and the system’s state is fully determined by the sequence of `/reset`, `/ingest`, and `/retrieve` calls.

- **Language Agnosticism:**  
  - The API uses standard HTTP verbs (POST, GET) and JSON for all data exchange.
  - No client-specific logic or language bindings are required; any tool or language that can make HTTP requests and parse JSON can interact with the API.

- **Deterministic Behavior:**  
  - The combination of strict input validation, stateless design, and deterministic sorting ensures that for a given batch of input events, the output of `/retrieve` is always the same. This is essential for automated test harnesses to assert correctness.

- **Error Handling:**  
  - Invalid or malformed items are skipped with a log message, but do not cause the entire batch to fail.
  - FastAPI’s automatic validation provides clear error messages for incorrect payloads.

This technical design ensures the API is robust, easy to test, and fully compatible with automated evaluation workflows.


### **5. Bonus: Evaluating Efficiency and Correctness**

**Correctness:**
- **Unit and Integration Tests:**  
  I would implement unit tests for the filtering and ranking logic, using both real and synthetic news items to ensure that only relevant items are accepted and that the ranking is deterministic and correct.
- **Automated Test Harness:**  
  The provided `/ingest`, `/retrieve`, and `/reset` endpoints allow automated scripts to inject controlled batches of events and verify that only the expected items are returned, in the correct order.
- **Manual Spot Checks:**  
  Periodically reviewing the dashboard output and logs helps catch edge cases or misclassifications not covered by automated tests.

**Efficiency:**
- **Profiling and Benchmarking:**  
  I would use Python profiling tools (e.g., `cProfile`, FastAPI’s built-in timing, or custom logging) to measure the time taken for ingestion, filtering, and retrieval, especially under large batches.
- **Scalability Testing:**  
  By simulating large ingestion batches and high-frequency retrievals, I can observe memory usage and response times, ensuring the system remains responsive.
- **Algorithmic Review:**  
  The filtering and ranking algorithms are linear in the number of items, which is efficient for the expected workload. For larger scales, I would consider optimizing storage and indexing.

**Summary:**  
Combining automated tests, profiling, and manual review ensures both the correctness and efficiency of the news retrieval and filtering process. The stateless API and deterministic ranking further support reliable and repeatable evaluation


### **6. Dockerization & Deployment**

To simplify setup and deployment, the project includes a `Dockerfile` and a `docker-compose.yml` file. Dockerization allows the entire application, along with its dependencies and environment, to be packaged into a portable container image. This ensures that the app runs consistently across different machines and environments, eliminating issues related to dependency conflicts or OS differences.

**Key Benefits:**
- **Reproducibility:** The Docker image encapsulates all dependencies, so the app will behave the same way everywhere.
- **Ease of Deployment:** With Docker Compose, the application can be started with a single command (`docker compose up`), making it easy for others to run or test the project without manual setup.
- **Isolation:** The app runs in its own container, isolated from the host system and other applications.
- **Scalability:** Docker makes it straightforward to scale the service or deploy it in cloud environments.


---
# 🚀 Future Work


### Asynchronous Fetching

Currently, the `ingestion.py` script fetches news from RSS feeds and Reddit subreddits sequentially, meaning each network request (for each feed or subreddit) is performed one after the other. This approach is simple but can be slow, especially as the number of sources grows, because the script waits for each request to finish before starting the next. 
**Asynchronous fetching** would allow the script to initiate multiple network requests concurrently, significantly reducing the total time required to gather news from all sources. For example, using Python's `asyncio` library along with asynchronous HTTP clients (such as `aiohttp` for RSS feeds and `asyncpraw` for Reddit), the script could fetch from many feeds and subreddits at the same time. This would make the ingestion process much faster and more scalable, especially when aggregating from dozens of sources.


### LLM-Based and Embedding-Based Filtering

The current keyword-matching approach, while simple and fast, has several notable limitations:

- It requires manual identification of all potentially relevant keywords, which is both time-consuming and error-prone.
- It struggles with false positives and false negatives due to its lack of semantic understanding.
- It tends to favor longer texts, as the likelihood of matching keywords increases with length, leading to a bias in relevance scoring.

To overcome these limitations, future versions of the system could incorporate more advanced NLP techniques:

- **LLM-Based Filtering:**  
  A large language model (LLM), such as GPT-4, could be used to classify the relevance of news items based on their semantic content. This would enable the detection of subtle or implied security threats that keyword-based filters might miss. For reliable testing and reproducibility, the LLM should operate under fixed conditions—such as a consistent prompt, zero temperature, and a locked model version—and return binary relevance decisions.

- **Embedding and Transformer-Based Filtering:**  
  Alternatively, or in combination with LLMs, transformer models (such as BERT or Sentence Transformers) could be used to generate vector embeddings of news items. These embeddings can be compared to vectors representing relevant topics or example incidents using cosine similarity, enabling semantic filtering without relying solely on generative models. This approach can capture nuanced relationships and improve recall and precision over simple keyword matching.

A hybrid approach—combining LLM-based classification, embeddings, and traditional rule-based methods—could further enhance the accuracy and robustness of relevance detection, while maintaining transparency and control.

### Database Storage

Currently, the `NewsStorage` class in `storage.py` uses an in-memory Python dictionary to store news items and persists them to a local JSON file (`.data/news_store.json`). This approach is simple and sufficient for prototyping or small-scale use, but it has several limitations:

- **Scalability:** As the number of news items grows, reading and writing the entire JSON file becomes inefficient and slow.
- **Query Flexibility:** Filtering and querying news items (e.g., by time, source, or keyword) is limited and must be done in memory, which is not efficient for large datasets.
- **Data Integrity:** There is no transactional support, so a crash during a write operation could corrupt the storage file.

**Future Work:**  
For a production environment, I would replace the JSON file with a proper database such as SQLite or PostgreSQL. When deploying with Docker, it is important to store the database file or configure the database server to use a persistent volume outside the container. This ensures that data is not lost when containers are rebuilt or restarted, and allows for easier backup and migration.


### Editable install 

For a more robust setup, we could create a `setup.py` or `pyproject.toml` and install the app as a package. However, at the moment this feature has been skipped because not considered relevant for the purpose of the assignment.

### Authentication and Rate Limiting (if deployed)
If this were deployed as a real-time API:

- Add basic auth or API key support.
- Rate-limit ingestion to prevent abuse or overload.

