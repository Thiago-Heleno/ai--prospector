# Product Context: AI Prospector

## Problem Solved

Manually searching Google for Instagram profiles based on specific criteria (e.g., "bakeries in London") and then visiting each profile to extract contact information or other details is time-consuming and inefficient.

## How It Works

1.  **Input:** The user provides a description of the leads they are looking for (e.g., "photographers in NYC specializing in weddings").
2.  **(Optional) AI Query Generation:** The application uses Groq's AI (Llama3-70b) to generate an optimized Google Search query string (e.g., `site:instagram.com "wedding photographer" "NYC"`) based on the user's description.
3.  **Query Refinement:** The user can review and modify the generated query or enter their own final query.
4.  **Crawling:** The application launches the `crawl.py` script as a background process using the final query.
    - `crawl.py` searches Google.
    - It identifies Instagram URLs from the search results.
    - It visits each Instagram profile URL.
    - It uses an LLM (Gemini Flash via `crawl4ai`) to extract relevant profile details (username, bio, contact info, etc.).
    - It saves the extracted data progressively to `leads.csv`.
5.  **Monitoring:** The user can monitor the crawler's progress via a log output displayed in the Streamlit interface.
6.  **Results:** Once the crawler finishes (or during the process via a refresh button), the user can view the collected leads directly within the Streamlit app as a table/dataframe loaded from `leads.csv`.

## User Experience Goals

- **Simplicity:** Easy-to-understand workflow with clear steps.
- **Efficiency:** Automate the tedious process of searching and data extraction.
- **Transparency:** Provide real-time feedback on the crawler's status via logs.
- **Control:** Allow users to refine the search query and refresh results on demand.
- **Optional AI Assistance:** Offer AI query generation as a helpful starting point without making it mandatory.
