# AI Prospector 📸✨

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/) **AI Prospector** is a powerful tool designed for efficient **Instagram lead generation** and **prospecting**. It leverages Google Search and cutting-edge AI models (Google Gemini and Groq Llama3) to automate the tedious process of finding relevant Instagram profiles and extracting key information. Built with a user-friendly Streamlit interface, it simplifies finding potential leads, contacts, or influencers based on your specific criteria.

**Keywords:** Instagram Leads, Prospecting Tool, Lead Generation, Web Scraping, AI Assistant, Streamlit App, Google Search Scraper, Instagram Scraper, Gemini API, Groq API, Llama3, Automated Prospecting, Contact Extraction.

---

## Features

- **🔍 Intelligent Search:** Uses Google Search to find Instagram profiles matching your criteria.
- **🤖 AI-Powered Query Generation (Optional):** Utilizes Groq's Llama3 model to generate optimized Google Search queries based on natural language descriptions (requires `GROQ_API_KEY`).
- **🧠 AI Data Extraction:** Employs Google Gemini Flash (via the `crawl4ai` library) to intelligently extract structured data from Instagram profiles (bio, contact info, follower counts, etc.).
- **🖥️ User-Friendly Interface:** Simple, step-by-step Streamlit web application for easy operation.
- **⚙️ Background Processing:** Runs the intensive web crawling task as a separate background process, keeping the UI responsive.
- **📊 Real-time Logging:** Monitor the crawler's progress and status directly within the app.
- **📄 CSV Output:** Saves all collected leads neatly into a `leads.csv` file for easy access and further use.
- **🔄 Data Persistence & Refresh:** View collected leads directly in the app and refresh the view on demand.

---

## How It Works

The application follows a clear workflow:

1.  **Describe Leads:** User provides a description of the desired Instagram leads (e.g., "coffee shops in São Paulo").
2.  **(Optional) Generate Query:** The app can send the description to the Groq API (Llama3) to generate an effective Google Search query string like `site:instagram.com "coffee shop" "São Paulo"`.
3.  **Finalize Query:** The user reviews the generated query or enters/modifies their own final Google Search query (ensuring `site:instagram.com` is included for best results).
4.  **Start Prospecting:** The user clicks "Start Prospecting". The Streamlit app launches the `crawl.py` script as a separate background process.
5.  **Crawling & Extraction (`crawl.py`):**
    - Searches Google using the provided query.
    - Identifies Instagram profile URLs within the search results.
    - Visits each Instagram profile.
    - Uses `crawl4ai` and the configured Gemini model to analyze the profile page's HTML and extract data according to a predefined schema (username, bio, website, email, phone, etc.).
    - Progressively saves the extracted data into `leads.csv`.
6.  **Monitoring & Results:**
    - The Streamlit app captures and displays log output from `crawl.py` in real-time.
    - Users can view the data collected in `leads.csv` within the app's "Leads Found" table, refreshing as needed.

```mermaid
graph LR
User --> App[Streamlit App: app.py]
App -- Optional --> Groq[Groq API: Llama3 Query Gen]
App -- Manages --> Crawler[Crawler Process: crawl.py]
Crawler -- Searches --> Google[Google]
Crawler -- Scrapes --> Instagram[Instagram]
Crawler -- Extracts Data --> Gemini[Gemini API: Extraction]
Crawler -- Writes --> CSV[leads.csv]
App -- Reads --> CSV
App -- Displays Logs/Results --> User
Crawler -- Streams Logs --> App
```

---

## Technology Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **Backend & Orchestration:** Python
- **Web Crawling & Automation:** [crawl4ai](https://www.google.com/search?q=https://github.com/Datasetante/crawl4ai) (using Playwright)
- **AI Data Extraction:** Google Gemini Flash (via `crawl4ai`)
- **AI Query Generation:** Groq API / Llama3 (via `groq` library)
- **Data Handling:** [Pandas](https://pandas.pydata.org/)
- **Data Validation:** [Pydantic](https://www.google.com/search?q=https://docs.pydantic.dev/)
- **Process Management:** Python `subprocess`
- **Concurrency (Logging):** Python `threading`

---

## Installation & Setup

1.  **Clone the Repository:**

    ```bash
    git clone [https://github.com/Thiago-Heleno/ai-prospector-new.git](https://github.com/Thiago-Heleno/ai-prospector-new.git) # Replace with actual URL if different
    cd ai-prospector-new
    ```

2.  **Python Version:**
    Ensure you have Python 3.8 or newer installed.

3.  **Create a Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    _(Note: This might take a moment as it needs to install Playwright browsers if not already present)._

5.  **Set Up Environment Variables:**
    Create a file named `.env` in the project's root directory. Add your API keys to this file:

    ```dotenv
    # .env file
    GEMINI_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"
    GROQ_API_KEY="YOUR_GROQ_API_KEY"
    ```

    - `GEMINI_API_KEY`: Required for the `crawl.py` script to extract data from Instagram profiles. Get one from [Google AI Studio](https://aistudio.google.com/app/apikey).
    - `GROQ_API_KEY`: Required for the optional AI query generation feature in the Streamlit app. Get one from [GroqCloud](https://console.groq.com/keys).

---

## Usage

1.  **Run the Streamlit Application:**

    ```bash
    streamlit run app.py
    ```

    This will open the application in your web browser.

2.  **Follow the Steps in the UI:**

    - **(Optional) Generate Query:** Enter a description of the leads you want and click "Generate Google Query".
    - **Final Query:** Review, modify, or enter the Google Search query you want to use. Remember to include `site:instagram.com`.
    - **Start Prospecting:** Click the "Start Prospecting" button.
    - **Monitor Log:** Observe the progress in the "Crawler Log" section.
    - **View Leads:** Check the "Leads Found" table. Click "Refresh Leads" to update the table with the latest data from `leads.csv`. The table also refreshes automatically when the crawler finishes.
    - **Stop Crawler:** You can stop the crawling process at any time using the "Stop Crawler" button.

---

## Output (`leads.csv`)

The application saves the extracted information into the `leads.csv` file in the project root. The columns include:

- `google_title`: Title of the Google search result.
- `google_url`: URL from the Google search result (often the Instagram profile URL).
- `google_snippet`: Description snippet from the Google search result.
- `instagram_username`: Profile's Instagram handle (e.g., `@username`).
- `instagram_full_name`: Profile's display name.
- `instagram_bio`: Profile's biography text.
- `instagram_followers`: Number of followers (as text, e.g., '10.5k').
- `instagram_following`: Number of accounts followed (as text).
- `instagram_posts_count`: Number of posts (as text).
- `instagram_website`: Website link found in the bio.
- `instagram_email`: Contact email found in the bio or contact options.
- `instagram_phone`: Contact phone number found in the bio or contact options.
- `instagram_location`: Location mentioned in the profile/bio.
- `instagram_category`: Business category if specified.
- `instagram_profile_url`: The actual Instagram profile URL that was scraped.

---

## Important Notes & Caveats

- **Scraping Reliability:** Web scraping (especially Google and Instagram) can be unreliable. Websites frequently change their structure (HTML/CSS), which can break the crawler (`crawl.py`). The CSS Selectors or extraction logic might need updates.
- **Anti-Bot Measures:** Websites may employ anti-bot measures. While `crawl4ai` attempts to mimic human behavior, excessive or rapid scraping could lead to temporary IP blocks or CAPTCHAs. The script includes random delays to mitigate this.
- **API Keys Required:** The core data extraction relies on a `GEMINI_API_KEY`. The optional query generation requires a `GROQ_API_KEY`. The respective features will be disabled or fail if keys are missing or invalid.
- **Rate Limits:** Be mindful of potential rate limits on Google Search and the AI APIs (Gemini, Groq).
- **Resource Usage:** Web crawling can consume significant CPU, RAM, and network resources.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details (if one exists in the repository).

---

## Author

- **Thiago Heleno** - [GitHub](https://github.com/Thiago-Heleno)
