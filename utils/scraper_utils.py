import json
import os
from typing import List, Set, Tuple
import asyncio
from bs4 import BeautifulSoup, SoupStrainer
import re

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMExtractionStrategy,
)

from models.venue import Venue
from utils.data_utils import is_complete_venue, is_duplicate_venue


def get_browser_config() -> BrowserConfig:
    """
    Returns the browser configuration for the crawler.

    Returns:
        BrowserConfig: The configuration settings for the browser.
    """
    # https://docs.crawl4ai.com/core/browser-crawler-config/
    return BrowserConfig(
        browser_type="chromium",  # Type of browser to simulate
        headless=False,  # Whether to run in headless mode (no GUI)
        verbose=True,  # Enable verbose logging
        # New Features
        extra_args=[
            "--disable-web-security",
            "--disable-features=IsolateOrigins",
            "--disable-site-isolation-trials",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--enable-cookies",
        ],
        # Use a realistic user agent
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    )


def get_llm_strategy() -> LLMExtractionStrategy:
    """
    Returns the configuration for the language model extraction strategy.

    Returns:
        LLMExtractionStrategy: The settings for how to extract data using LLM.
    """
    # https://docs.crawl4ai.com/api/strategies/#llmextractionstrategy
    return LLMExtractionStrategy(
        provider="groq/deepseek-r1-distill-llama-70b",  # Name of the LLM provider
        api_token=os.getenv("GROQ_API_KEY"),  # API token for authentication
        schema=Venue.model_json_schema(),  # JSON schema of the Google result model
        extraction_type="schema",  # Type of extraction to perform
        instruction=(
            "Extract all Google search result objects with 'title', 'url', and 'snippet' "
            "from the following content."
        ),
        input_format="markdown",  # Format of the input content
        verbose=True,  # Enable verbose logging
    )


def get_llm_website_strategy() -> LLMExtractionStrategy:
    """
    Returns the LLM extraction strategy for extracting website details.
    Extracts emails, additional links, and a summary of the company description.
    """
    return LLMExtractionStrategy(
        provider="groq/deepseek-r1-distill-llama-70b",  # adjust as needed
        api_token=os.getenv("GROQ_API_KEY"),
        schema={
            "type": "object",
            "properties": {
                "emails": {"type": "array", "items": {"type": "string"}},
                "contact_links": {"type": "array", "items": {"type": "string"}},
                "summary": {"type": "string"},
            },
            "required": ["emails", "contact_links", "summary"],
        },
        extraction_type="schema",
        instruction=(
            "Given the website content, extract all email addresses found on the page, "
            "extract relevant links (such as links to the contact page), "
            "and provide a brief summary of what the company does."
        ),
        input_format="plain_text",
        verbose=True,
    )


def clean_instagram_html(html: str) -> str:
    """Minify HTML by removing unnecessary elements and scripts"""
    # Parse only relevant portions of the HTML
    strainer = SoupStrainer(["main", "article", "meta", "script"])
    soup = BeautifulSoup(html, "lxml", parse_only=strainer)

    # Remove all scripts except JSON-LD data
    for script in soup.find_all("script"):
        if "application/ld+json" not in script.get("type", ""):
            script.decompose()

    # Remove unnecessary attributes and empty containers
    for tag in soup.find_all(True):
        attrs_to_keep = ["content", "property", "name"]
        tag.attrs = {k: v for k, v in tag.attrs.items() if k in attrs_to_keep}

    # Remove comments and whitespace
    cleaned_html = re.sub(r"<!--.*?-->", "", str(soup), flags=re.DOTALL)
    return re.sub(r"\s+", " ", cleaned_html).strip()



async def fetch_website_details(crawler: AsyncWebCrawler, url: str, llm_website_strategy: LLMExtractionStrategy):
    """
    Fetch the content of the website using the crawler and extract additional info.
    """

    try:
        result = await crawler.arun(
            url=url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                session_id="instagram_scraper",
                page_timeout=30000,  # Increased timeout
                wait_for="article",  # Wait for posts to load
            ),
        )

        await asyncio.sleep(5)
        # Get the full rendered HTML

        # Clean and minify HTML before extraction
        minified_html = clean_instagram_html(result.html)
        print("HTML reduced from", len(result.html), "to", len(minified_html))

        # content = result.html  # or result.content depending on library version

        # Pass minified HTML directly to the strategy
        extracted_data = llm_website_strategy.extract(
            url=url, html=minified_html, ix=0  # Required by the library
        )

    except Exception as e:
        print("Error during scraping:", str(e))
        print("Rate limit error encountered. Waiting 60 seconds...")
        await asyncio.sleep(60)
        raise

    print(extracted_data)
    return extracted_data[0] or {}


async def check_no_results(
    crawler: AsyncWebCrawler,
    url: str,
    session_id: str,
) -> bool:
    """
    Checks if the "No Results Found" message is present on the page.

    Args:
        crawler (AsyncWebCrawler): The web crawler instance.
        url (str): The URL to check.
        session_id (str): The session identifier.

    Returns:
        bool: True if "No Results Found" message is found, False otherwise.
    """
    # Fetch the page without any CSS selector or extraction strategy
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            session_id=session_id,
        ),
    )

    if result.success:
        if "No Results Found" in result.cleaned_html:
            return True
    else:
        print(
            f"Error fetching page for 'No Results Found' check: {result.error_message}"
        )

    return False


async def fetch_and_process_page(
    crawler: AsyncWebCrawler,
    page_number: int,
    base_url: str,
    css_selector: str,
    llm_strategy: LLMExtractionStrategy,
    session_id: str,
    required_keys: List[str],
    seen_names: Set[str],
) -> Tuple[List[dict], bool]:
    """
    Fetches and processes a single page of venue data.

    Args:
        crawler (AsyncWebCrawler): The web crawler instance.
        page_number (int): The page number to fetch.
        base_url (str): The base URL of the website.
        css_selector (str): The CSS selector to target the content.
        llm_strategy (LLMExtractionStrategy): The LLM extraction strategy.
        session_id (str): The session identifier.
        required_keys (List[str]): List of required keys in the venue data.
        seen_names (Set[str]): Set of venue names that have already been seen.

    Returns:
        Tuple[List[dict], bool]:
            - List[dict]: A list of processed venues from the page.
            - bool: A flag indicating if the "No Results Found" message was encountered.
    """
    # For Google search results, calculate the start value.
    if page_number == 1:
        url = base_url
    else:
        start = (page_number - 1) * 10
        url = f"{base_url}&start={start}"
    print(f"Loading page {page_number} with URL: {url}...")

    # Check if "No Results Found" message is present
    no_results = await check_no_results(crawler, url, session_id)
    if no_results:
        return [], True  # No more results, signal to stop crawling

    # Fetch page content with the extraction strategy
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,  # Do not use cached data
            extraction_strategy=llm_strategy,  # Strategy for data extraction
            css_selector=css_selector,  # Target specific content on the page
            session_id=session_id,  # Unique session ID for the crawl
        ),
    )

    if not (result.success and result.extracted_content):
        print(f"Error fetching page {page_number}: {result.error_message}")
        return [], False

    # Parse extracted content
    extracted_data = json.loads(result.extracted_content)
    if not extracted_data:
        print(f"No venues found on page {page_number}.")
        return [], False

    # After parsing extracted content
    print("Extracted data:", extracted_data)

    # Process venues
    complete_venues = []
    for venue in extracted_data:
        print("Processing venue:", venue)

        # Remove error key if present and False
        if venue.get("error") is False:
            venue.pop("error", None)

        if not is_complete_venue(venue, required_keys):
            continue

        if is_duplicate_venue(venue["title"], seen_names):
            print(f"Duplicate Result '{venue['title']}' found. Skipping.")
            continue

        seen_names.add(venue["title"])
        complete_venues.append(venue)

    if not complete_venues:
        print(f"No complete venues found on page {page_number}.")
        return [], False

    print(f"Extracted {len(complete_venues)} venues from page {page_number}.")
    return complete_venues, False  # Continue crawling
