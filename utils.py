import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import re
from bs4 import BeautifulSoup
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    """
    if not text:
        return ""
    
    # Remove HTML tags
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    return text.strip()

def parse_date(date_str: str) -> datetime:
    """
    Parse various date formats to datetime object.
    Returns a timezone-naive datetime object.
    """
    if not date_str:
        return datetime.now()
        
    try:
        # Try parsing with pandas (handles most common formats)
        dt = pd.to_datetime(date_str)
        # Convert to naive datetime
        if dt.tzinfo is not None:
            dt = dt.tz_localize(None)
        return dt
    except:
        try:
            # Try parsing with datetime (ISO format with timezone)
            dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
            return dt.replace(tzinfo=None)
        except:
            try:
                # Try parsing without timezone
                dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
                return dt
            except:
                try:
                    # Try parsing just the date
                    dt = datetime.strptime(date_str, '%Y-%m-%d')
                    return dt
                except:
                    logger.warning(f"Could not parse date: {date_str}")
                    return datetime.now()

def is_within_timeframe(date: datetime, days: int = 365) -> bool:
    """
    Check if the date is within the specified timeframe.
    Handles offset-naive and offset-aware datetime comparison.
    """
    cutoff_date = datetime.now()
    # Convert both to naive UTC for comparison
    if date.tzinfo is not None:
        date = date.replace(tzinfo=None)
    if cutoff_date.tzinfo is not None:
        cutoff_date = cutoff_date.replace(tzinfo=None)
    cutoff_date = cutoff_date - timedelta(days=days)
    return date >= cutoff_date

def deduplicate_entries(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate entries based on title and URL.
    """
    seen = set()
    unique_entries = []
    
    for entry in entries:
        # Create a unique identifier using title and URL
        identifier = f"{entry['title']}_{entry['url']}"
        
        if identifier not in seen:
            seen.add(identifier)
            unique_entries.append(entry)
    
    return unique_entries

def save_to_csv(data: List[Dict[str, Any]], filename: str) -> None:
    """
    Save data to CSV file.
    """
    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"Successfully saved data to {filename}")
    except Exception as e:
        logger.error(f"Error saving data to {filename}: {str(e)}")

def save_to_json(data: List[Dict[str, Any]], filename: str) -> None:
    """
    Save data to JSON file.
    """
    try:
        df = pd.DataFrame(data)
        df.to_json(filename, orient='records', lines=True)
        logger.info(f"Successfully saved data to {filename}")
    except Exception as e:
        logger.error(f"Error saving data to {filename}: {str(e)}") 