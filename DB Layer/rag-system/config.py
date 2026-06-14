# config.py

# Purpose

# Stores configuration.

# Without this:

# redis.Redis(host="localhost")

# would be repeated everywhere.

# Instead:

# from config import REDIS_HOST

# Cleaner and easier.

POSTGRES_URL = "postgresql://user:password@localhost:5432/ragdb"

REDIS_HOST = "localhost"
REDIS_PORT = 6379

QDRANT_URL = "http://localhost:6333"

COLLECTION_NAME = "documents"