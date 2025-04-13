# Progress: AI Prospector (Initialization)

## What Works

- The `crawl.py` script exists and is capable of:
  - Taking a query via command line.
  - Searching Google.
  - Scraping Instagram profiles found.
  - Extracting data using Gemini.
  - Saving results to `leads.csv`.
- The basic `app.py` exists and can run via Streamlit.
- Memory Bank structure is initialized.

## What's Left to Build / Implement

- **`app.py` Overhaul:**
  - Replace threading with subprocess execution for `crawl.py`.
  - Implement Groq API integration for query generation.
  - Implement real-time log display using threading and subprocess streams.
  - Implement `leads.csv` reading and display using Pandas/Streamlit.
  - Refactor the UI into the planned 5-step flow.
  - Add state management using `st.session_state` for the new features.
  - Implement robust error handling (API calls, file access, subprocess).
- **Dependency Management:** Ensure `requirements.txt` includes `pandas` and `groq`.
- **Testing:** Verify all features work correctly, including edge cases (missing API keys, empty query, crawler errors, empty CSV).

## Current Status

- Initial setup and planning complete.
- Memory Bank files created.
- Ready to begin modifying `app.py` and `requirements.txt`.

## Known Issues / Blockers

- None currently identified, but potential issues include:
  - Web scraping fragility (`crawl.py`).
  - API key availability/validity.
  - Concurrency issues between Streamlit reruns and the logging thread (needs careful implementation).
