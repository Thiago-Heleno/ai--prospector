# System Patterns: AI Prospector

## Architecture Overview

The application follows a simple two-part architecture:

1.  **Streamlit Frontend (`app.py`):** Handles user interaction, input gathering, AI query generation (optional), process initiation, log display, and results presentation. It acts as the control center.
2.  **Crawler Backend (`crawl.py`):** A separate Python script responsible for the heavy lifting of web crawling and data extraction. It's executed as an independent subprocess managed by `app.py`.

```mermaid
graph LR
    User --> App[Streamlit App (app.py)];
    App -- Optional --> Groq[Groq API (Query Gen)];
    App -- Manages --> Crawler[Crawler Process (crawl.py)];
    Crawler -- Searches --> Google;
    Crawler -- Scrapes --> Instagram;
    Crawler -- Extracts Data --> Gemini[Gemini API (Extraction)];
    Crawler -- Writes --> CSV[leads.csv];
    App -- Reads --> CSV;
    App -- Displays Logs/Results --> User;
    Crawler -- Streams Logs --> App;
```

## Key Design Patterns & Approaches

- **Process Separation:** The core crawling logic is decoupled from the UI by running `crawl.py` in a separate process using `subprocess.Popen`. This prevents the potentially long-running and resource-intensive crawl from blocking the Streamlit UI.
- **Asynchronous Execution (Subprocess):** `subprocess.Popen` allows `app.py` to start `crawl.py` and continue running without waiting for it to complete immediately.
- **Background Log Monitoring:** A separate `threading.Thread` is used within `app.py` to read the `stdout` of the `crawl.py` subprocess in a non-blocking way, allowing logs to be displayed in near real-time.
- **State Management:** Streamlit's `st.session_state` is used extensively in `app.py` to maintain the application's state across reruns, including user inputs, generated queries, logs, subprocess status (`running`), and the subprocess object (`proc`).
- **Data Persistence:** Results are saved to a simple CSV file (`leads.csv`), acting as a basic persistent store between runs and decoupling data storage from the application's runtime state.
- **API Abstraction (Implicit):** The `crawl4ai` library abstracts the complexities of browser automation (Playwright) and LLM interaction (Gemini) for the crawling task. The `groq` library abstracts the Groq API interaction.
- **Environment Variable Configuration:** API keys are configured via environment variables (`.env` file), keeping sensitive credentials out of the source code.
- **Modular Script (`crawl.py`):** `crawl.py` is designed to be executable both as a standalone script (using `argparse`) and as a module callable by `app.py` (though the current implementation uses it only as a script via `subprocess`).
