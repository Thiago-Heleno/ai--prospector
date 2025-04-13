# Project Brief: AI Prospector

## Core Goal

To create a Streamlit application that helps users find Instagram leads based on Google Search results.

## Key Features

- User interface via Streamlit.
- Ability to input a search query description.
- (Optional) AI-powered generation of an effective Google Search query using Groq.
- Execution of a web crawler (`crawl.py`) as a separate process to perform the Google Search and subsequent Instagram profile scraping.
- Real-time logging of the crawler's progress within the Streamlit app.
- Display of the collected leads (from `leads.csv`) within the Streamlit app.
- Results saved persistently to `leads.csv`.

## Target User

Individuals or businesses looking for potential leads or contacts on Instagram based on specific search criteria.
