import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def scrape_instagram_page():
    instagram_url = "https://www.instagram.com/nasa/"
    
    # Enhanced stealth configuration
    config = BrowserConfig(
        browser_type="chromium",
        headless=False,  # Keep headless to avoid detection
        verbose=True,
        extra_args=[
            "--disable-web-security",
            "--disable-features=IsolateOrigins",
            "--disable-site-isolation-trials",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        ],
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    )
    
    async with AsyncWebCrawler(config=config) as crawler:
        print(f"Fetching Instagram page: {instagram_url}...")
        try:
            result = await crawler.arun(
                url=instagram_url,
                config=CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    session_id="instagram_scraper",
                    page_timeout=30000,  # Increased timeout
                    wait_for="article",  # Wait for posts to load
                    #before_capture="async () => { delete navigator.webdriver; }",  # Remove automation flags
                )
            )

            await asyncio.sleep(5)
            # Get the full rendered HTML
            content = result.html  # or result.content depending on library version
            
            print("Fetched content length:", len(content))
            
            # Save for debugging
            with open("instagram_debug.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("Debug HTML saved successfully")
            
            return content
            
        except Exception as e:
            print("Error during scraping:", str(e))
            raise

async def main():
    await scrape_instagram_page()

if __name__ == "__main__":
    asyncio.run(main())