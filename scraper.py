import feedparser
import requests
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
import time
from tqdm import tqdm
from langdetect import detect, LangDetectException
import pandas as pd
from bs4 import BeautifulSoup
import re

from utils import (
    clean_text,
    parse_date,
    is_within_timeframe,
    deduplicate_entries,
    save_to_csv,
    save_to_json
)

logger = logging.getLogger(__name__)

class RSSScraper:
    def __init__(self, feed_info: Dict[str, str]):
        self.url = feed_info['url']
        self.agency = feed_info['agency']
        self.country = feed_info['country']
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def detect_language(self, text: str) -> str:
        """
        Detect the language of the given text.

        """
        try:
            return detect(text)
        except LangDetectException:
            return 'unknown'

    def fetch_feed(self) -> List[Dict[str, Any]]:
        """
        Fetch and parse RSS feed.
        
        Returns:
            List of dictionaries containing parsed feed entries
        """
        try:
            # Add delay to respect rate limits
            time.sleep(1)
            
            # Fetch feed with custom headers
            response = requests.get(self.url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # Parse feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"Feed parsing issues for {self.url}: {feed.bozo_exception}")
            
            entries = []
            for entry in feed.entries:
                try:
                    # Extract and clean data
                    title = clean_text(entry.get('title', ''))
                    
                    # Try different possible fields for description/summary
                    description = ''
                    if 'description' in entry:
                        description = clean_text(entry['description'])
                    elif 'summary' in entry:
                        description = clean_text(entry['summary'])
                    elif 'content' in entry:
                        description = clean_text(entry['content'][0]['value'])
                    
                    # Get the article URL
                    link = entry.get('link', '')
                    
                    # Parse publication date
                    published = parse_date(entry.get('published', ''))
                    if published.tzinfo is not None:
                        published = published.replace(tzinfo=None)
                    
                    # Only include entries within the last year
                    if not is_within_timeframe(published):
                        continue
                    
                    # Detect language from title and description
                    combined_text = f"{title} {description}"
                    language = self.detect_language(combined_text)
                    
                    entries.append({
                        'title': title,
                        'description': description,
                        'url': link,
                        'published_date': published.isoformat(),
                        'source': self.agency,
                        'country': self.country,
                        'language': language
                    })
                except Exception as e:
                    logger.error(f"Error processing entry from {self.url}: {str(e)}")
                    continue
            
            return deduplicate_entries(entries)
            
        except requests.RequestException as e:
            logger.error(f"Error fetching feed {self.url}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error processing {self.url}: {str(e)}")
            return []

    def fetch_historical_feed(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Fetch historical feed data between start_date and end_date"""
        all_entries = []
        current_date = start_date
        
        while current_date <= end_date:
            try:
                # Add date parameter to feed URL if supported
                date_str = current_date.strftime('%Y-%m-%d')
                feed_url = f"{self.url}?date={date_str}"
                
                # Fetch feed with rate limiting
                time.sleep(2)  # Rate limiting
                feed = feedparser.parse(feed_url, request_headers=self.headers)
                
                if feed.entries:
                    for entry in feed.entries:
                        entry_date = self._parse_date(entry.get('published', ''))
                        if start_date <= entry_date <= end_date:
                            all_entries.append(self._process_entry(entry))
                
                current_date += timedelta(days=1)
                
            except Exception as e:
                logging.error(f"Error fetching historical feed for {date_str}: {str(e)}")
                continue
                
        return all_entries
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        try:
            return pd.to_datetime(date_str).to_pydatetime()
        except:
            return datetime.now()
    
    def _process_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single feed entry"""
        # Try different possible fields for description/summary
        description = ''
        if 'description' in entry:
            description = self._clean_text(entry['description'])
        elif 'summary' in entry:
            description = self._clean_text(entry['summary'])
        elif 'content' in entry:
            description = self._clean_text(entry['content'][0]['value'])
        
        return {
            'title': self._clean_text(entry.get('title', '')),
            'description': description,
            'url': entry.get('link', ''),
            'published_date': self._parse_date(entry.get('published', '')).isoformat(),
            'source': self.agency,
            'country': self.country
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean HTML and special characters from text"""
        if not text:
            return ''
        # Remove HTML tags
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text()
        # Remove special characters
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()

def scrape_all_feeds(feeds: List[Dict[str, str]], historical: bool = False) -> pd.DataFrame:
    """Scrape all feeds and return as DataFrame"""
    all_entries = []
    
    for feed_info in feeds:
        scraper = RSSScraper(feed_info)
        
        if historical:
            # Fetch last year's data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            entries = scraper.fetch_historical_feed(start_date, end_date)
        else:
            # Fetch current feed
            entries = scraper.fetch_feed()
            
        all_entries.extend(entries)
        
    return pd.DataFrame(all_entries)

def scrape_all_feeds(feeds: List[Dict[str, str]], output_format: str = 'csv') -> None:
    """
    Scrape all provided RSS feeds and save the results.
    
    Args:
        feeds: List of feed information dictionaries
        output_format: Output format ('csv' or 'json')
    """
    all_entries = []
    
    # Create progress bar
    for feed_info in tqdm(feeds, desc="Scraping feeds"):
        scraper = RSSScraper(feed_info)
        entries = scraper.fetch_feed()
        all_entries.extend(entries)
        
        # Save individual feed data
        if entries:
            filename = f"data/{feed_info['country']}_{feed_info['agency']}_{datetime.now().strftime('%Y%m%d')}.{output_format}"
            if output_format == 'csv':
                save_to_csv(entries, filename)
            else:
                save_to_json(entries, filename)
    
    # Save combined data
    if all_entries:
        combined_filename = f"data/all_news_{datetime.now().strftime('%Y%m%d')}.{output_format}"
        if output_format == 'csv':
            save_to_csv(all_entries, combined_filename)
        else:
            save_to_json(all_entries, combined_filename)
        
        logger.info(f"Total entries collected: {len(all_entries)}") 