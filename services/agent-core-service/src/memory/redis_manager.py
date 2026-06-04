import os
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

def get_redis_chat_history(session_id: str) -> BaseChatMessageHistory:
    """基于 Redis 实现的分布式会话历史管理器，保证多实例部署时 Session 不丢失"""
    return RedisChatMessageHistory(
        session_id=session_id,
        url=REDIS_URL,
        ttl=3600  # 会话过期时间设置 1 小时
    )
