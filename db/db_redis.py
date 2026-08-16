from fastapi import Request
import redis.asyncio as redis
from  redis.exceptions import ConnectionError
from utils.logger_handler import logger
redis_pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    decode_responses=True,
    encoding='utf-8',
)
async def redis_connect():
    try:
        redis_client = redis.Redis(connection_pool=redis_pool)
        return redis_client
    except ConnectionError:
        logger.error("Redis connection error")
        raise
async def get_redis_client(request: Request):
    return await request.app.state.redis
