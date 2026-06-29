import random
from datetime import datetime, timezone
import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from Big_Data_HiringBase.big_data_scraper.config import USER_AGENTS, REQUEST_TIMEOUT

logger = structlog.get_logger()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def fetch_jobs_for_keyword(keyword: str) -> list:
    """
    Fetch remote jobs from Remotive API for a specific keyword.
    Uses rotating user-agent and handles retries.
    """
    url = "https://remotive.com/api/remote-jobs"
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json"
    }
    params = {"search": keyword}
    
    logger.info("fetching_jobs_start", keyword=keyword)
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        response = await client.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            logger.warn("fetching_jobs_failed_status", keyword=keyword, status=response.status_code)
            response.raise_for_status()
            
        data = response.json()
        jobs_list = data.get("jobs", [])
        logger.info("fetching_jobs_success", keyword=keyword, count=len(jobs_list))
        
        normalized_jobs = []
        for job in jobs_list:
            # Validate essential fields
            job_id = job.get("id")
            if not job_id:
                continue
                
            # Normalize fields
            # Handle date parsing from remotive's string format (e.g. 2023-10-24T12:00:00)
            pub_date = job.get("publication_date")
            
            normalized_jobs.append({
                "job_id": str(job_id),  # Store as string for flexibility
                "title": job.get("title", ""),
                "company": job.get("company_name", ""),
                "category": job.get("category", ""),
                "tags": job.get("tags", []),
                "job_type": job.get("job_type", ""),
                "publication_date": pub_date,
                "candidate_required_location": job.get("candidate_required_location", ""),
                "salary": job.get("salary", ""),
                "url": job.get("url", ""),
                "keyword": keyword,
                "scrape_time": datetime.now(timezone.utc).isoformat()
            })
            
        return normalized_jobs
