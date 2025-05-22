# RSS Feed News Aggregator

A Python-based RSS feed aggregator that collects news articles from major news agencies across multiple countries. The project extracts structured data from RSS feeds, including headlines, summaries, publication dates, and source information.

[![GitHub](https://img.shields.io/badge/GitHub-RSS_Feed-blue)](https://github.com/sahilg28/RSS_Feed.git)

## Features

- Collects news from 22 countries with multiple sources per country
- Extracts structured data including:
  - News Title
  - Publication Date
  - Source (News Agency)
  - Country
  - Summary/Description
  - News URL (Link to Full Article)
- Supports historical data collection
- Automatic language detection
- Data deduplication
- Rate limiting to respect feed providers
- Error handling and logging
- Data export in CSV format

## News Coverage Summary

| Country | News Agencies | Total Articles | Historical Data |
|---------|--------------|----------------|-----------------|
| India | Times of India, The Hindu, Indian Express | 307 | Since 2024 |
| USA | CNN, NPR, New York Times | 47 | Since 2024 |
| UK | BBC News, The Guardian, The Telegraph, The Independent | 391 | Since 2024 |
| Japan | NHK | 9 | Since 2024 |
| Germany | Deutsche Welle | 94 | Since 2024 |
| France | Le Monde, Le Figaro | 42 | Since 2024 |
| Canada | CBC News | 21 | Since 2024 |
| Australia | ABC News, Sydney Morning Herald | 49 | Since 2024 |
| Russia | TASS | 102 | Since 2024 |
| South Korea | Korea Times | 13 | Since 2024 |
| Singapore | The Straits Times | 172 | Since 2024 |
| Indonesia | Antara News | 52 | Since 2024 |
| Brazil | G1 | 102 | Since 2024 |
| Mexico | Mexico News Daily | 12 | Since 2024 |
| Italy | ANSA | 30 | Since 2024 |
| New Zealand | Stuff | 89 | Since 2024 |

Total Articles Collected: 1,484

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sahilg28/RSS_Feed.git
cd RSS_Feed
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
To collect current news articles:
```bash
python main.py
```

### Historical Data Collection
To collect historical data (past year):
```bash
python main.py --historical
```

### Data Visualization
To view the collected data in a web interface:
```bash
streamlit run streamlit_app.py
```

## Project Structure

- `main.py`: Main script to run the RSS feed collection
- `scraper.py`: Core scraping functionality
- `rss_links.py`: Configuration of RSS feed sources
- `utils.py`: Utility functions for data processing
- `streamlit_app.py`: Web interface for data visualization
- `scheduler.py`: Automated scheduling of data collection
- `data/`: Directory containing collected data
- `logs/`: Directory containing log files

## Dependencies

- feedparser: RSS feed parsing
- requests: HTTP requests
- pandas: Data manipulation
- beautifulsoup4: HTML parsing
- langdetect: Language detection
- streamlit: Web interface
- tqdm: Progress bars

## Issues and Solutions

1. **RSS Feed Availability**
   - Some news agencies have changed their RSS feed URLs
   - Solution: Regular updates to feed URLs and multiple sources per country

2. **Rate Limiting**
   - Some feeds have strict rate limits
   - Solution: Implemented delays between requests

3. **Data Consistency**
   - Different RSS feed formats
   - Solution: Standardized data processing and cleaning

## Bonus Features

1. **Language Detection**
   - Automatically detects article language
   - Helps in filtering and categorization

2. **Data Deduplication**
   - Removes duplicate articles across sources
   - Ensures data quality

3. **Web Interface**
   - Interactive data visualization
   - Filtering and search capabilities

4. **Automated Scheduling**
   - Regular data collection
   - Configurable collection intervals

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Repository

The project is hosted on GitHub: [RSS_Feed](https://github.com/sahilg28/RSS_Feed.git)
