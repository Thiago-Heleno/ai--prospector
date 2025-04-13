import asyncio, os
import pandas as pd
import urllib.parse
import json
import argparse
import random # Added for delays
import traceback # Added for detailed exception logging
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig, LXMLWebScrapingStrategy
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
from typing import List, Union, Optional

# Update this value frequently, Google changes it often.
CSS_SELECTOR = "div.dURPMd" 

class GoogleSearch(BaseModel):
    title: str = Field(..., description="Title of the website.")
    url: str = Field(..., description="The website url.")
    snippet: Optional[str] = Field(None, description="The short description of the website.") # Made optional

class InstagramSearch(BaseModel):
    username: Optional[str] = Field(None, description="Instagram handle (e.g., @examplebakery)")
    full_name: Optional[str] = Field(None, description="Profile's display name (e.g., Example Bakery)")
    bio: Optional[str] = Field(None, description="The profile's biography text.")
    followers: Optional[str] = Field(None, description="Number of followers (as text, e.g., '10.5k', '1.2m').")
    following: Optional[str] = Field(None, description="Number of accounts followed (as text).")
    posts_count: Optional[str] = Field(None, description="Number of posts (as text).")
    website: Optional[str] = Field(None, description="Link from the bio, if present.")
    email: Optional[str] = Field(None, description="Contact email, if publicly available in bio/contact options.")
    phone: Optional[str] = Field(None, description="Contact phone number, if publicly available.")
    location: Optional[str] = Field(None, description="Location mentioned in the profile/bio, if available.")
    category: Optional[str] = Field(None, description="Business category, if specified (e.g., Bakery, Restaurant).")
    profile_url: str = Field(..., description="The original URL of the Instagram profile.")


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
  semaphore_count=1, # Limit concurrent scrapes/extractions to 1 (Reduced concurrency)
  extraction_strategy = LLMExtractionStrategy(
    llm_config = LLMConfig(provider="gemini/gemini-2.0-flash", api_token=os.getenv('GEMINI_API_KEY')),
    schema=InstagramSearch.model_json_schema(),
    extraction_type="schema",
    input_format="html",
    instruction=
    """
    Analyze the HTML of the **main Instagram profile page provided**. Extract information **only** for the primary profile displayed on this page. Ignore any suggested accounts, related profiles, or other peripheral information. Return **only a single JSON object** containing the following details for the main profile:
    - username: The Instagram handle (e.g., @examplebakery)
    - full_name: The profile's display name (e.g., Example Bakery)
    - bio: The profile's biography text.
    - followers: The number of followers (e.g., '10.5k', '1.2m').
    - following: The number of accounts the profile is following.
    - posts_count: The total number of posts.
    - website: The website URL listed in the bio, if any.
    - email: Any contact email address found in the bio or contact options.
    - phone: Any contact phone number found in the bio or contact options.
    - location: Any location mentioned in the bio or profile details.
    - category: The business category if specified (e.g., Bakery, Restaurant, Artist).
    Ensure the output strictly follows the provided JSON schema. If a field is not found, omit it or return null/None. Include the original profile_url.

    Output JSON schema format:
    {
      "username": "string | null",
      "full_name": "string | null",
      "bio": "string | null",
      "followers": "string | null",
      "following": "string | null",
      "posts_count": "string | null",
      "website": "string | null",
      "email": "string | null",
      "phone": "string | null",
      "location": "string | null",
      "category": "string | null",
      "profile_url": "string"
    }
    """
  ),
  css_selector="main",
  wait_for="main",
  cache_mode=CacheMode.BYPASS,
  simulate_user=True,
  magic=True,
  delay_before_return_html=5.0,
  excluded_tags=['form', 'header', 'footer', 'nav', 'script', 'img'],
  exclude_external_images=True,
  verbose=True,
)

# Define CSV file path and headers
CSV_FILE = 'leads.csv'
CSV_HEADERS = [
    'google_title', 'google_url', 'google_snippet', 
    'instagram_username', 'instagram_full_name', 'instagram_bio', 
    'instagram_followers', 'instagram_following', 'instagram_posts_count', 
    'instagram_website', 'instagram_email', 'instagram_phone', 
    'instagram_location', 'instagram_category', 'instagram_profile_url'
]

async def main(query: str): 
    """
    Main function to scrape Google for a query, find Instagram links, 
    scrape those profiles, and save results to CSV.
    """
    if not query:
        print("[ERROR] Query cannot be empty.")
        return

    google_results_list: List[GoogleSearch] = []
    parsed_content = None 

    encoded_query = urllib.parse.quote_plus(query) 
    google_search_url = f"https://www.google.com/search?q={encoded_query}" 
  
    print(f"Starting Google Search scraping for query: '{query}'") 
    print(f"Using URL: {google_search_url}") 
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # --- Google Search ---
        google_search_result = await crawler.arun(
            url=google_search_url, 
            config=google_run_config
        )
        
        if google_search_result.success and google_search_result.extracted_content:
            content = google_search_result.extracted_content
            
            if isinstance(content, str):
                try:
                    parsed_content = json.loads(content)
                    print("[INFO] Successfully parsed JSON string from Google results.")
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Failed to parse JSON string from Google results: {e}")
                    print(f"   -> Content was: {content[:500]}...") 
                    parsed_content = None 
            elif isinstance(content, (list, dict)):
                 parsed_content = content 
            else:
                 print(f"[WARNING] Unexpected format for Google results (not str, list, or dict): {type(content)}")
                 parsed_content = None

            # Validate Google results with Pydantic
            temp_google_results = []
            if isinstance(parsed_content, list):
                for item in parsed_content:
                    if isinstance(item, dict):
                        try:
                            temp_google_results.append(GoogleSearch(**item))
                        except Exception as val_e:
                            print(f"[WARNING] Skipping Google result due to validation error: {val_e}")
                            print(f"   -> Invalid item: {item}")
            elif isinstance(parsed_content, dict):
                 try:
                     temp_google_results.append(GoogleSearch(**parsed_content))
                 except Exception as val_e:
                     print(f"[WARNING] Skipping Google result due to validation error: {val_e}")
                     print(f"   -> Invalid item: {parsed_content}")

            google_results_list = temp_google_results
            print(f"Found {len(google_results_list)} valid potential leads from Google.")

            # --- Phase 1: Save Initial Google Data ---
            if google_results_list:
                initial_data_list = []
                for result in google_results_list:
                    row_data = {header: "" for header in CSV_HEADERS}
                    row_data['google_title'] = result.title
                    row_data['google_url'] = result.url
                    row_data['google_snippet'] = result.snippet if result.snippet else "" # Ensure empty string if None
                    initial_data_list.append(row_data)
                
                initial_df = pd.DataFrame(initial_data_list, columns=CSV_HEADERS)
                try:
                    initial_df.to_csv(CSV_FILE, mode='w', header=True, index=False, encoding='utf-8')
                    print(f"Initial Google data saved to {CSV_FILE}")
                except Exception as save_e:
                    print(f"[ERROR] Failed to save initial Google data to {CSV_FILE}: {save_e}")
                    return # Stop if initial save fails
            else:
                print("No valid Google results found to process.")
                try:
                    pd.DataFrame(columns=CSV_HEADERS).to_csv(CSV_FILE, mode='w', header=True, index=False, encoding='utf-8')
                    print(f"Created empty {CSV_FILE} with headers.")
                except Exception as save_e:
                    print(f"[ERROR] Failed to create empty {CSV_FILE}: {save_e}")
                return # Stop if no Google results
            # --- End Phase 1 ---

        else:   
            print(f"[ERROR] Google Search failed or returned no content: {google_search_result.error_message}")
            return # Exit if Google search failed
          
   
        instagram_urls_to_scrape = []
        for result in google_results_list: # Iterate through the validated list
            if 'instagram.com' in result.url:
                instagram_urls_to_scrape.append(result.url)
            else:
                print(f"[INFO] Skipping non-Instagram URL from Google: {result.url}")

        if not instagram_urls_to_scrape:
            print("No Instagram URLs found in Google results to scrape.")
            # No need to return here, the initial CSV is already saved.
        else:
            # --- Phase 2: Read CSV and Update with Instagram Data ---
            try:
                # Read CSV ensuring all columns are treated as objects (strings) to avoid dtype issues
                leads_df = pd.read_csv(CSV_FILE, encoding='utf-8', dtype='object')
                # Fill potential NaN values read from empty cells with empty strings
                leads_df.fillna('', inplace=True)
            except FileNotFoundError:
                print(f"[ERROR] {CSV_FILE} not found after initial save. Cannot update.")
                return
            except Exception as e:
                 print(f"[ERROR] Failed to read {CSV_FILE} for updating: {e}")
                 return

            # Wrap the main scraping loop in a try-except block
            try:
                print(f"\nStarting sequential Instagram scraping for {len(instagram_urls_to_scrape)} URLs with delays...")
                for url in instagram_urls_to_scrape:
                    # Add random delay before scraping each URL
                    delay = random.uniform(5, 15) # Random delay between 5 and 15 seconds
                    print(f"[DEBUG] Before sleep for {url}") # DEBUG
                    print(f"Waiting {delay:.2f} seconds before scraping {url}...")
                    await asyncio.sleep(delay)
                    print(f"[DEBUG] After sleep for {url}") # DEBUG

                    print(f"Scraping Instagram URL: {url}")
                    print(f"[DEBUG] Before arun for {url}") # DEBUG
                    result = await crawler.arun(url, config=instagram_run_config)
                    print(f"[DEBUG] After arun for {url}") # DEBUG
                    original_url = result.url # Keep track of the URL processed

                    # Debug: Print raw LLM output
                    if result.success and result.extracted_content:
                        print(f"[DEBUG] Raw LLM content for {original_url}:\n{result.extracted_content}\n---")
                    elif result.success:
                        print(f"[DEBUG] LLM extraction successful but no content returned for {original_url}")
                    else:
                        print(f"[DEBUG] LLM extraction failed for {original_url}: {result.error_message}")

                    data_dict = None # Initialize variable to hold the final dictionary
                    if result.success and result.extracted_content:
                        raw_content = result.extracted_content
                        # 1. Check if it's already a dictionary
                        if isinstance(raw_content, dict):
                            # Check if this dict matches the URL, otherwise ignore
                            if raw_content.get('profile_url') == original_url:
                                data_dict = raw_content
                            else:
                                print(f"[WARNING] Received dict profile_url '{raw_content.get('profile_url')}' does not match target {original_url}")
                        # 2. Check if it's a string, try parsing as JSON
                        elif isinstance(raw_content, str):
                            try:
                                parsed_data = json.loads(raw_content)
                                # 2a. Check if parsed data is a list (like "[{...}]")
                                if isinstance(parsed_data, list):
                                    # Find the dictionary in the list that matches the original_url
                                    found_match = False
                                    for item in parsed_data:
                                        if isinstance(item, dict) and item.get('profile_url') == original_url:
                                            data_dict = item
                                            found_match = True
                                            print(f"[INFO] Found matching profile data in list for {original_url}")
                                            break # Stop searching once found
                                    if not found_match:
                                        print(f"[WARNING] Could not find matching profile data in parsed list for {original_url}")
                                # 2b. Check if parsed data is directly a dictionary
                                elif isinstance(parsed_data, dict):
                                    # Check if this dict matches the URL, otherwise ignore
                                    if parsed_data.get('profile_url') == original_url:
                                        data_dict = parsed_data
                                        print(f"[INFO] Parsed JSON string (dict) matches {original_url}")
                                    else:
                                        print(f"[WARNING] Parsed JSON dict profile_url '{parsed_data.get('profile_url')}' does not match target {original_url}")
                                else:
                                    print(f"[WARNING] Parsed JSON string for {original_url} was not a list or dict: {type(parsed_data)}")
                            except json.JSONDecodeError:
                                print(f"[ERROR] Failed to parse JSON string received from Instagram LLM for {original_url}")
                                print(f"   -> Received content (string): {raw_content[:500]}...")
                        else:
                            # Handle cases where it's neither dict nor string
                             print(f"[ERROR] Unexpected data format received from Instagram LLM (not dict or str) for {original_url}: {type(raw_content)}")

                        # 3. If we successfully obtained a matching dictionary, process it
                        if data_dict:
                            try:
                                # Ensure profile_url is present before validation
                                if 'profile_url' not in data_dict or not data_dict['profile_url']:
                                     data_dict['profile_url'] = original_url # Add/overwrite if missing or empty

                                insta_data = InstagramSearch(**data_dict)
                                print(f"[OK] Successfully validated data for: {original_url}")

                                # Find index in DataFrame to update
                                matching_indices = leads_df.index[leads_df['google_url'] == original_url].tolist()
                                if matching_indices:
                                    index_to_update = matching_indices[0] # Update the first match

                                    # Update DataFrame row (use .get with default '')
                                    leads_df.loc[index_to_update, 'instagram_username'] = insta_data.username if insta_data.username else ''
                                    leads_df.loc[index_to_update, 'instagram_full_name'] = insta_data.full_name if insta_data.full_name else ''
                                    leads_df.loc[index_to_update, 'instagram_bio'] = insta_data.bio if insta_data.bio else ''
                                    leads_df.loc[index_to_update, 'instagram_followers'] = insta_data.followers if insta_data.followers else ''
                                    leads_df.loc[index_to_update, 'instagram_following'] = insta_data.following if insta_data.following else ''
                                    leads_df.loc[index_to_update, 'instagram_posts_count'] = insta_data.posts_count if insta_data.posts_count else ''
                                    leads_df.loc[index_to_update, 'instagram_website'] = insta_data.website if insta_data.website else ''
                                    leads_df.loc[index_to_update, 'instagram_email'] = insta_data.email if insta_data.email else ''
                                    leads_df.loc[index_to_update, 'instagram_phone'] = insta_data.phone if insta_data.phone else ''
                                    leads_df.loc[index_to_update, 'instagram_location'] = insta_data.location if insta_data.location else ''
                                    leads_df.loc[index_to_update, 'instagram_category'] = insta_data.category if insta_data.category else ''
                                    leads_df.loc[index_to_update, 'instagram_profile_url'] = insta_data.profile_url # Should always exist now
                                    print(f"   -> Updated lead data in DataFrame for {original_url}")

                                    # --- Progressive Save ---
                                    try:
                                        print(f"[DEBUG] Attempting progressive save after updating {original_url}...")
                                        leads_df.to_csv(CSV_FILE, mode='w', header=True, index=False, encoding='utf-8')
                                        print(f"[DEBUG] Progressive save successful for {original_url}.")
                                    except Exception as save_e:
                                        print(f"[ERROR] Failed progressive save after updating {original_url}: {save_e}")
                                    # --- End Progressive Save ---
                                else:
                                    print(f"[WARNING] Could not find matching row in CSV for {original_url} to update.")

                            except Exception as e: # Catch Pydantic validation errors or others during processing
                                print(f"[ERROR] Failed to process or update data for {original_url} after parsing/validation: {e}")
                                print(f"   -> Parsed data (dict): {data_dict}")
                    # else: data_dict remained None, error logged above if parsing failed or type was wrong

                else: # Handle cases where scraping failed or returned no content initially
                    print(f"[ERROR] Failed to scrape {original_url}: {result.error_message}")
                # End of for loop for instagram_urls_to_scrape

                print("[DEBUG] Instagram scraping loop finished successfully.") # Moved outside loop, inside outer try

            except Exception as e: # Outer except block for the whole Phase 2 loop
                print(f"[DEBUG] UNHANDLED EXCEPTION occurred during Instagram scraping loop: {type(e).__name__}: {e}")
                print(traceback.format_exc()) # Print the full traceback
            # --- End Phase 2 ---

    print("\nScraping process finished.")

# --- Command-Line Execution ---
if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description="Scrape Google for Instagram leads based on a query.")
    parser.add_argument("query", help="The search query to use on Google (e.g., 'bakery london instagram').")
    args = parser.parse_args()

    if not os.getenv('GEMINI_API_KEY'):
        print("Error: GEMINI_API_KEY environment variable not set. Please set it before running.")
    else:
        asyncio.run(main(args.query))
