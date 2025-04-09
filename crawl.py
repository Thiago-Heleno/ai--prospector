import asyncio, os
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig, LXMLWebScrapingStrategy
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
from typing import List, Union

# Update this value frequently, Google changes it often.
CSS_SELECTOR = "div.dURPMd" 

class GoogleSearch(BaseModel):
    title: str = Field(..., description="Title of the website.")
    url: str = Field(..., description="The website url.")
    snippet: str = Field(..., description="The short description of the website.")
    
class InstagramSearch(BaseModel):
    title: str = Field(..., description="Title of the website.")
    url: str = Field(..., description="The website url.")
    snippet: str = Field(..., description="The short description of the website.")


browser_config = BrowserConfig(
  viewport={'width': 1920, 'height': 1080},
  extra_args=[
    "--disable-web-security",
    "--disable-features=IsolateOrigins",
    "--disable-site-isolation-trials",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--enable-cookies",
    "--disable-blink-features=AutomationControlled",
  ],
  headless=False,
  user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
  verbose=True
)

google_run_config = CrawlerRunConfig(
  extraction_strategy = LLMExtractionStrategy(
    llm_config = LLMConfig(provider="gemini/gemini-2.0-flash", api_token=os.getenv('GEMINI_API_KEY')),
    schema=GoogleSearch.model_json_schema(),
    extraction_type="schema",
    input_format="html",
    instruction=
    """
    From the crawled content matching the CSS selector, extract the details for each search result.
    For each result, provide the title, the full URL, and the descriptive snippet.
    Ensure the output strictly follows the provided JSON schema: {"title": "string", "url": "string", "snippet": "string"}.
    Extract information only from the distinct search result blocks identified.
    """
  ),
  css_selector=CSS_SELECTOR,
  wait_for=CSS_SELECTOR,
  scan_full_page=True,
  cache_mode=CacheMode.BYPASS,
  simulate_user=True,
  magic=True,
  override_navigator=True,
  delay_before_return_html=5.0,
  scraping_strategy=LXMLWebScrapingStrategy(),
  excluded_tags=['form', 'header', 'footer', 'nav', 'script', 'img'],
  exclude_external_images=True,
  verbose=True,
)

instagram_run_config = CrawlerRunConfig(
  extraction_strategy = LLMExtractionStrategy(
    llm_config = LLMConfig(provider="gemini/gemini-2.0-flash", api_token=os.getenv('GEMINI_API_KEY')),
    schema=InstagramSearch.model_json_schema(),
    extraction_type="schema",
    input_format="html",
    instruction=
    """
    
    """
  ),
  scraping_strategy=LXMLWebScrapingStrategy(),
  css_selector=CSS_SELECTOR,
  wait_for=CSS_SELECTOR,
  scan_full_page=True,
  cache_mode=CacheMode.BYPASS,
  simulate_user=True,
  magic=True,
  override_navigator=True,
  delay_before_return_html=5.0,
  excluded_tags=['form', 'header', 'footer', 'nav', 'script', 'img'],
  exclude_external_images=True,
  verbose=True,
)

async def quick_parallel_example(google_search_result: GoogleSearch):
    urls = []
    for google_search_result in google_search_result:
      urls.append(google_search_result.url)
    
    async with AsyncWebCrawler() as crawler:
        # Stream results as they complete
        async for result in await crawler.arun_many(urls, config=instagram_run_config):
            if result.success:
                print(f"[OK] {result.url}, length: {len(result.markdown.raw_markdown)}")
                #Add to leads.csv
            else:
                print(f"[ERROR] {result.url} => {result.error_message}")

async def main():
  
    google_results
  
    # Scrape Google Serp
    async with AsyncWebCrawler(config=browser_config) as google_crawler:
        result = await google_crawler.arun(
            url="https://www.google.com/search?q=doceria-instagram&oq=doceria-instagram&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQABgeMgYIAhAAGB4yBggDEAAYHjIGCAQQABgeMggIBRAAGAgYHjIICAYQABgIGB4yCAgHEAAYCBgeMggICBAAGAgYHjIICAkQABgIGB7SAQg2MTA3ajBqN6gCALACAA&sourceid=chrome&ie=UTF-8",
            config=google_run_config
        )
        
        google_results = result.extracted_content
        #Add to leads.csv
        google_crawler.close()
        
    
    # Scrape Each Instagram page
    for instagram_page in google_results:    
      async with AsyncWebCrawler(config=browser_config) as instagram_crawler:
            result = await instagram_crawler.arun(
                url=instagram_page.url,
                config=instagram_run_config
            )
            

      

if __name__ == "__main__":
    asyncio.run(main())
