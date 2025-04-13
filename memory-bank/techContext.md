# Technical Context: AI Prospector

## Core Technologies

- **Frontend:** Streamlit (`streamlit`)
- **Backend Logic:** Python
- **Web Crawling/Scraping:** `crawl4ai` library (using Playwright/Browser)
- **Data Handling:** Pandas (`pandas`)
- **AI Query Generation:** Groq API (`groq` library, Llama3-70b model)
- **AI Data Extraction (within `crawl.py`):** Gemini Flash (via `crawl4ai` integration)
- **Process Management:** Python `subprocess` module
- **Concurrency (for Logging):** Python `threading` module

## Development Setup

- Requires Python 3.x.
- Dependencies managed via `requirements.txt`. Install using `pip install -r requirements.txt`.
- Requires environment variables for API keys:
  - `GEMINI_API_KEY`: For data extraction within `crawl.py`.
  - `GROQ_API_KEY`: For AI query generation within `app.py`.
  - These should be stored in a `.env` file (which is loaded by Streamlit/Python environment).
- Run the application using `streamlit run app.py`.

## Technical Constraints & Considerations

- **API Keys:** The application relies on external API keys (Gemini, Groq). Functionality related to these APIs will fail if keys are missing or invalid.
- **Web Scraping Robustness:** Web scraping (especially Google Search and Instagram) can be brittle. Changes to website structure (HTML, CSS selectors) or anti-bot measures can break the crawler (`crawl.py`). The `CSS_SELECTOR` in `crawl.py` might need frequent updates.
- **Rate Limiting:** Both Google Search and the LLM APIs (Groq, Gemini) may have rate limits. Excessive use could lead to temporary blocks or errors. `crawl.py` uses `crawl4ai`'s semaphore for Instagram scraping concurrency control.
- **Process Management:** Running `crawl.py` as a subprocess means it runs independently. Errors within `crawl.py` might not directly crash `app.py` but will be reported in the log.
- **Environment Consistency:** `app.py` uses `sys.executable` to ensure the `crawl.py` subprocess runs with the same Python interpreter and environment, preventing dependency issues.
- **Resource Usage:** Web crawling can be resource-intensive (CPU, memory, network). Running many crawls might impact system performance.
- **Error Handling:** Robust error handling is needed for API calls, file operations (`leads.csv`), subprocess management, and web scraping failures.
