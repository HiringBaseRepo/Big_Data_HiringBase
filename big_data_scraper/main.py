import asyncio
import sys
import structlog

from Big_Data_HiringBase.big_data_scraper.config import KEYWORDS, DELAY_BETWEEN_REQUESTS
from Big_Data_HiringBase.big_data_scraper.scraper import fetch_jobs_for_keyword
from Big_Data_HiringBase.big_data_scraper.mongodb import (
    ensure_unique_index,
    upsert_jobs,
    close_client
)

logger = structlog.get_logger()

async def run_scraper():
    logger.info("scraper_job_started")
    try:
        # 1. Initialize MongoDB indices
        await ensure_unique_index()
        
        # 2. Iterate and scrape each keyword
        total_upserted = 0
        for i, keyword in enumerate(KEYWORDS):
            try:
                jobs = await fetch_jobs_for_keyword(keyword)
                if jobs:
                    upserted = await upsert_jobs(jobs)
                    total_upserted += upserted
            except Exception as e:
                logger.error("scraper_keyword_failed", keyword=keyword, error=str(e))
                
            # Add delay between keyword requests to avoid rate limits
            if i < len(KEYWORDS) - 1:
                logger.debug("sleeping_between_keywords", seconds=DELAY_BETWEEN_REQUESTS)
                await asyncio.sleep(DELAY_BETWEEN_REQUESTS)
                
        logger.info("scraper_job_finished", total_changes=total_upserted)
        
    except Exception as e:
        logger.critical("scraper_fatal_error", error=str(e))
        sys.exit(1)
    finally:
        await close_client()

if __name__ == "__main__":
    asyncio.run(run_scraper())
