import os
from dotenv import load_dotenv

# Load local .env if exists (mostly for local development)
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
# DB settings
DB_NAME = "hiringbase_bigdata"
COLLECTION_NAME = "jobs"

# Search parameters
KEYWORDS = [
    "python", "java", "flutter", "react", "data", "machine learning",
    "ui ux", "backend", "frontend", "android", "devops", "full stack"
]

# Scraping settings
REQUEST_TIMEOUT = 15.0
MAX_RETRIES = 3
DELAY_BETWEEN_REQUESTS = 2.0  # seconds

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0"
]
