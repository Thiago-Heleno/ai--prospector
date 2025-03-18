# Deep Seek Prospector Crawler

This project is a web crawler built with Python that extracts emails, phone numbers and contact information from various websites using asynchronous programming with Crawl4AI. It utilizes a language model-based extraction strategy and saves the collected data to a CSV file.

The interface was made using Streamlit

## Features

- Asynchronous web crawling using [Crawl4AI](https://pypi.org/project/Crawl4AI/)
- Data extraction powered by a language model (LLM) using [Groq-Cloud](https://console.groq.com/)
- CSV export of extracted leads information
- Modular and easy-to-follow code structure ideal for beginners

## Project Structure
```
.
├── main.py # Main entry point for the crawler
├── config.py # Contains configuration constants (Base URL, CSS selectors, etc.)
├── models
│ └── venue.py # Defines the Venue data model using Pydantic
├── utils
│ ├── init.py # (Empty) Package marker for utils
│ ├── data_utils.py # Utility functions for processing and saving data
│ └── scraper_utils.py # Utility functions for configuring and running the crawler
├── requirements.txt # Python package dependencies
├── .gitignore # Git ignore file (e.g., excludes .env and CSV files)
└── README.MD # This file
```

## Installation

1. **Create and Activate a Conda Environment**

   ```bash
   conda create -n deep-seek-crawler python=3.12 -y
   conda activate deep-seek-crawler
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Your Environment Variables**

   Create a `.env` file in the root directory with content similar to:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

   *(Note: The `.env` file is in your .gitignore, so it won’t be pushed to version control.)*

## Usage

To start the crawler, run:

```bash
python main.py
```

The script will crawl the specified website, extract data page by page, and save the complete venues to a `complete_venues.csv` file in the project directory. Additionally, usage statistics for the LLM strategy will be displayed after crawling.

## Configuration

The `config.py` file contains key constants used throughout the project:

- **BASE_URL**: The URL of the website from which to extract venue data.
- **CSS_SELECTOR**: CSS selector string used to target venue content.
- **REQUIRED_KEYS**: List of required fields to consider a venue complete.

You can modify these values as needed.

## Additional Notes

- **Logging:** The project currently uses print statements for status messages. For production or further development, consider integrating Python’s built-in `logging` module.
- **Improvements:** The code is structured in multiple modules to maintain separation of concerns, making it easier for beginners to follow and extend the functionality.
- **Dependencies:** Ensure that the package versions specified in `requirements.txt` are installed to avoid compatibility issues.

## License

The MIT License (MIT)

Copyright (c) 2025 Thiago Heleno

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.