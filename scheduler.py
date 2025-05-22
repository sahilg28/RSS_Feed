import schedule
import time
import logging
from datetime import datetime
from main import main as run_scraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/scheduler_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def job():
    """
    Job function to run the scraper.
    """
    try:
        logger.info("Starting scheduled scraping job...")
        run_scraper()
        logger.info("Scheduled scraping job completed successfully!")
    except Exception as e:
        logger.error(f"Error in scheduled job: {str(e)}")

def main():
    """
    Main function to set up and run the scheduler.
    """
    # Schedule the job to run every 6 hours
    schedule.every(6).hours.do(job)
    
    # Run the job immediately on startup
    job()
    
    logger.info("Scheduler started. Running every 6 hours.")
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 