import os
# Ensure directories exist before logging is configured
os.makedirs('data', exist_ok=True)
os.makedirs('logs', exist_ok=True)

import logging
from datetime import datetime
from rss_links import RSS_FEEDS
from scraper import scrape_all_feeds

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/scraper_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting RSS feed scraping...")
        logger.info(f"Total feeds to process: {len(RSS_FEEDS)}")
        
        # Scrape all feeds and save as CSV
        scrape_all_feeds(RSS_FEEDS, output_format='csv')
        
        logger.info("RSS feed scraping completed successfully!")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main() 