import structlog
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import UpdateOne

from Big_Data_HiringBase.big_data_scraper.config import MONGODB_URL, DB_NAME, COLLECTION_NAME

logger = structlog.get_logger()

_client = None

def get_mongo_client():
    global _client
    if _client is None:
        if not MONGODB_URL:
            raise ValueError("MONGODB_URL is not set in environment variables")
        # Ensure timeout and connection settings are configured
        _client = AsyncIOMotorClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
    return _client

async def close_client():
    global _client
    if _client is not None:
        _client.close()
        _client = None
        logger.info("mongodb_connection_closed")

async def ensure_unique_index():
    client = get_mongo_client()
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    # Create unique index on job_id
    index_name = await collection.create_index("job_id", unique=True)
    logger.info("mongodb_index_ensured", index=index_name)

async def upsert_jobs(jobs_list: list) -> int:
    """
    Perform bulk upserts on job list based on job_id.
    """
    if not jobs_list:
        return 0
        
    client = get_mongo_client()
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    operations = []
    for job in jobs_list:
        job_id = job["job_id"]
        # Pop keyword so it is only set on insert to prevent generic overrides
        kw = job.pop("keyword", "")
        operations.append(
            UpdateOne(
                {"job_id": job_id},
                {
                    "$setOnInsert": {"keyword": kw},
                    "$set": job
                },
                upsert=True
            )
        )
        
    if operations:
        result = await collection.bulk_write(operations, ordered=False)
        upserted_count = result.upserted_count
        matched_count = result.matched_count
        modified_count = result.modified_count
        logger.info(
            "mongodb_bulk_write_complete",
            matched=matched_count,
            modified=modified_count,
            upserted=upserted_count
        )
        return upserted_count + modified_count
        
    return 0
