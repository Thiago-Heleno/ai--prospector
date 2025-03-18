import asyncio
import random

from crawl4ai import AsyncWebCrawler
from dotenv import load_dotenv
import litellm

from config import BASE_URL, CSS_SELECTOR, REQUIRED_KEYS
from utils.data_utils import save_venues_to_csv
from utils.scraper_utils import (
    fetch_and_process_page,
    get_browser_config,
    get_llm_strategy,
    get_llm_website_strategy,
    fetch_website_details,
)

load_dotenv()


async def crawl_venues():
    """
    Main function to crawl data from the Google search page.
    """
    # Initialize configurations
    browser_config = get_browser_config()
    llm_strategy = get_llm_strategy()
    session_id = "venue_crawl_session"
    max_page = 1  # Limit to 5 pages, adjust as needed

    # Initialize state variables
    page_number = 1
    all_venues = []
    seen_titles = set()

    # Start the web crawler context for crawling Google search results
    async with AsyncWebCrawler(config=browser_config) as crawler:
        while page_number <= max_page: #True:
            # Fetch and process data from the current page
            venues, no_results_found = await fetch_and_process_page(
                crawler,
                page_number,
                BASE_URL,
                CSS_SELECTOR,
                llm_strategy,
                session_id,
                REQUIRED_KEYS,
                seen_titles,  # using title as duplicate key
            )

            if no_results_found:
                print("No more venues found. Ending crawl.")
                break

            if not venues:
                print(f"No venues extracted from page {page_number}.")
                break

            # Add the venues from this page to the total list
            all_venues.extend(venues)
            page_number += 1

            # Pause between requests to be polite and avoid rate limits
            await asyncio.sleep(2)

    if not all_venues:
        print("No venues were found during the crawl.")
        return

    # Now, for each venue (search result), enter its website and extract additional details.
    llm_website_strategy = get_llm_website_strategy()
    
    async with AsyncWebCrawler(config=browser_config) as website_crawler:
        for venue in all_venues:
            await asyncio.sleep(random.randint(10, 20))
            retries = 0
            max_retries = 3  # Maximum retry attempts

            while retries < max_retries:
                try:
                    # Fetch website details
                    extra_info = await fetch_website_details(website_crawler, venue["url"], llm_website_strategy)
                    venue.update(extra_info)
                    break  # Exit the retry loop if successful
                except Exception as e:
                    retries += 1
                    print(f"Error fetching details for {venue['url']} (Attempt {retries}/{max_retries}): {e}")
                    
                    if retries < max_retries:
                        print("Waiting 60 seconds before retrying...")
                        await asyncio.sleep(60)  # Wait before retrying
                    else:
                        print(f"Skipping {venue['url']} after {max_retries} failed attempts.")
            

    # Save the collected data to a CSV file
    save_venues_to_csv(all_venues, "complete_venues.csv")
    print(f"Saved {len(all_venues)} venues to 'complete_venues.csv'.")

    # Display usage statistics for the LLM strategy
    llm_strategy.show_usage()


async def main():
    """
    Entry point of the script.
    """
    await crawl_venues()


if __name__ == "__main__":
    asyncio.run(main())