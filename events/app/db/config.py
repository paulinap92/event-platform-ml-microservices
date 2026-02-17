from dotenv import load_dotenv
from os import getenv

# Load .env file
load_dotenv()

# -----------------------------------------------------------------------------------------
# Application metadata (optional)
# -----------------------------------------------------------------------------------------
AUTHOR = getenv("AUTHOR", "KM")
VERSION = getenv("VERSION", "1.0")

# -----------------------------------------------------------------------------------------
# Database configuration for the EVENTS microservice
# -----------------------------------------------------------------------------------------
DB_USERNAME = getenv("DB_USERNAME", "user")
DB_PASSWORD = getenv("DB_PASSWORD", "user1234")

# Default port for events database: 3311 (as defined in docker-compose)
DB_PORT = getenv("DB_PORT", 3311)

# Default DB name: db_events
DB_NAME = getenv("DB_NAME", "db_events")

# Default hostname: mysql-events (Docker Compose service name)
DB_HOSTNAME = getenv("DB_HOST", "mysql-events")

# SQLAlchemy-compatible database URL
DB_URL = f"mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}"
