from dotenv import load_dotenv
from os import getenv

# Load .env file (only effective outside Docker)
load_dotenv()

# -----------------------------------------------------------------------------------------
# Application metadata (optional)
# -----------------------------------------------------------------------------------------
AUTHOR = getenv("AUTHOR", "KM")
VERSION = getenv("VERSION", "1.0")

# -----------------------------------------------------------------------------------------
# Database configuration for the SENTIMENT microservice
# -----------------------------------------------------------------------------------------
DB_USERNAME = getenv("DB_USERNAME", "user")
DB_PASSWORD = getenv("DB_PASSWORD", "user1234")

# Default port for sentiment DB: 3312 (can be changed if you want)
DB_PORT = getenv("DB_PORT", 3313)

# Default database name
DB_NAME = getenv("DB_NAME", "db_1")

# Default Docker hostname for the sentiment MySQL container
DB_HOSTNAME = getenv("DB_HOST", "mysql-sentiment")

# -----------------------------------------------------------------------------------------
# SQLAlchemy DB URL
# -----------------------------------------------------------------------------------------
DB_URL = f"mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}"
