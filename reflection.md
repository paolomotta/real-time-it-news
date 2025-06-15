## Future Work

### Asynchronous Fetching

Currently, the `ingestion.py` script fetches news from RSS feeds and Reddit subreddits sequentially, meaning each network request (for each feed or subreddit) is performed one after the other. This approach is simple but can be slow, especially as the number of sources grows, because the script waits for each request to finish before starting the next.

**Asynchronous fetching** would allow the script to initiate multiple network requests concurrently, significantly reducing the total time required to gather news from all sources. For example, using Python's `asyncio` library along with asynchronous HTTP clients (such as `aiohttp` for RSS feeds and `asyncpraw` for Reddit), the script could fetch from many feeds and subreddits at the same time. This would make the ingestion process much faster and more scalable, especially when aggregating from dozens of sources.


### LLM-Based Filtering
A future iteration of the system could use a language model (e.g., GPT-4) to classify the relevance of news items using semantic understanding. This would allow detection of subtle or implied threats not easily captured by keyword matching. For testability, the model would need to operate deterministically (fixed prompt, temperature=0, same model version) and only make binary relevance decisions per item. An hybrid approach can also be used.

### Database Storage

Currently, the `NewsStorage` class in `storage.py` uses an in-memory Python dictionary to store news items and persists them to a local JSON file (`news_store.json`). This approach is simple and sufficient for prototyping or small-scale use, but it has several limitations:

- **Scalability:** As the number of news items grows, reading and writing the entire JSON file becomes inefficient and slow.
- **Query Flexibility:** Filtering and querying news items (e.g., by time, source, or keyword) is limited and must be done in memory, which is not efficient for large datasets.
- **Data Integrity:** There is no transactional support, so a crash during a write operation could corrupt the storage file.

**Future Work:**  
For a production environment, I would replace the JSON file with a proper database such as SQLite or PostgreSQL.


### Editable install 

For a more robust setup, we could create a `setup.py` or `pyproject.toml` and install the app as a package. However, at the moment this feature has been skipped because not considered relevant for the purpose of the assignment.

### Authentication and Rate Limiting (if deployed)
If this were deployed as a real-time API:

- Add basic auth or API key support.
- Rate-limit ingestion to prevent abuse or overload.