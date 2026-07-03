from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

client: AsyncIOMotorClient = None
db = None


async def connect_db():
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DB_NAME]
    # Create indexes
    await db.scan_reports.create_index("agent_id")
    await db.shield_logs.create_index([("agent_id", 1), ("timestamp", -1)])
    await db.eval_results.create_index([("agent_id", 1), ("run_at", -1)])
    await db.checkpoints.create_index("checkpoint_id")
    print("MongoDB connected")


async def close_db():
    global client
    if client:
        client.close()


def get_db():
    return db
