"""
database.py

Handles the MongoDB connection for the Deep Behavioral Biometrics
Authentication Platform backend.

Uses Motor, the official asynchronous MongoDB driver for Python, so that
database calls integrate cleanly with FastAPI's async request handlers
without blocking the event loop.

This module exposes:
    - `client`: the raw Motor client instance (rarely used directly).
    - `db`: the specific database object used across the app.
    - Individual collection references (users, auth_history, alerts,
      risk_scores) so route/service modules can import exactly what
      they need without repeating `db["collection_name"]` everywhere.
    - `connect_to_mongo()` / `close_mongo_connection()`: lifecycle hooks
      called from main.py on FastAPI startup/shutdown events.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings

# ---------------------------------------------------------------------------
# Motor client and database handle
# ---------------------------------------------------------------------------

# The Motor client manages a connection pool to MongoDB internally, so it
# is safe to create a single client instance and reuse it for the entire
# lifetime of the application.
client: AsyncIOMotorClient = AsyncIOMotorClient(settings.MONGO_URI)

# The actual database object we will interact with for all queries.
db = client[settings.DATABASE_NAME]

# ---------------------------------------------------------------------------
# Collection references
# ---------------------------------------------------------------------------
# Defining these here means every other module can do:
#     from backend.database import users_collection
# instead of repeating db["users"] throughout the codebase.

users_collection = db["users"]
auth_history_collection = db["auth_history"]
alerts_collection = db["alerts"]
risk_scores_collection = db["risk_scores"]


# ---------------------------------------------------------------------------
# Lifecycle helper functions
# ---------------------------------------------------------------------------

async def connect_to_mongo() -> None:
    """
    Verifies the MongoDB connection when the FastAPI application starts.

    Motor connects lazily, so this function forces an early connection
    check by issuing a lightweight 'ping' command. If MongoDB is
    unreachable, this will raise an exception immediately at startup
    instead of failing silently on the first real request.
    """
    try:
        # The 'ping' command is the standard lightweight way to verify
        # that a MongoDB server is reachable and responding.
        await client.admin.command("ping")
        print(f"[MongoDB] Connected successfully to database: {settings.DATABASE_NAME}")
    except Exception as error:
        print(f"[MongoDB] Connection failed: {error}")
        raise error


async def close_mongo_connection() -> None:
    """
    Cleanly closes the MongoDB client connection when the FastAPI
    application shuts down. This releases the underlying connection
    pool resources gracefully.
    """
    client.close()
    print("[MongoDB] Connection closed.")


async def create_indexes() -> None:
    """
    Creates required database indexes for performance and data integrity.

    - `users_collection`: unique index on 'username' and 'email' so no
      two users can register with the same username/email (enforced at
      the database level, not just application level).
    - `auth_history_collection`: index on 'user_id' and 'timestamp' to
      speed up history lookups per user, sorted by recency.
    - `alerts_collection`: index on 'user_id' and 'created_at' for the
      same reason (fast per-user alert retrieval).

    This function is called once at application startup.
    """
    await users_collection.create_index("username", unique=True)
    await users_collection.create_index("email", unique=True)

    await auth_history_collection.create_index([("user_id", 1), ("timestamp", -1)])

    await alerts_collection.create_index([("user_id", 1), ("created_at", -1)])

    print("[MongoDB] Indexes verified/created successfully.")