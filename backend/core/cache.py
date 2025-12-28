"""
Redis Cache Layer - 高性能缓存服务

提供以下功能:
- 通用数据缓存（支持 TTL）
- 会话存储
- 速率限制存储
- 优雅降级（Redis 不可用时的回退）
"""
import json
import hashlib
import asyncio
from typing import Optional, Any, Callable, TypeVar, Union
from functools import wraps
from datetime import timedelta
import logging

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from core.config import settings

logger = logging.getLogger(__name__)

# 类型变量
T = TypeVar('T')


class CacheBackend:
    """缓存后端抽象基类"""
    
    async def get(self, key: str) -> Optional[str]:
        raise NotImplementedError
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        raise NotImplementedError
    
    async def delete(self, key: str) -> bool:
        raise NotImplementedError
    
    async def exists(self, key: str) -> bool:
        raise NotImplementedError
    
    async def incr(self, key: str) -> int:
        raise NotImplementedError
    
    async def expire(self, key: str, ttl: int) -> bool:
        raise NotImplementedError
    
    async def ttl(self, key: str) -> int:
        raise NotImplementedError


class MemoryCache(CacheBackend):
    """内存缓存后端（Redis 不可用时的回退方案）"""
    
    def __init__(self):
        self._cache: dict[str, tuple[str, Optional[float]]] = {}
        self._lock = asyncio.Lock()
    
    async def _cleanup_expired(self):
        """清理过期的缓存项"""
        import time
        current_time = time.time()
        expired_keys = [
            k for k, (_, exp) in self._cache.items()
            if exp is not None and exp < current_time
        ]
        for key in expired_keys:
            del self._cache[key]
    
    async def get(self, key: str) -> Optional[str]:
        import time
        async with self._lock:
            await self._cleanup_expired()
            if key in self._cache:
                value, exp = self._cache[key]
                if exp is None or exp > time.time():
                    return value
                del self._cache[key]
        return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        import time
        async with self._lock:
            exp = time.time() + ttl if ttl else None
            self._cache[key] = (value, exp)
        return True
    
    async def delete(self, key: str) -> bool:
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
        return False
    
    async def exists(self, key: str) -> bool:
        return await self.get(key) is not None
    
    async def incr(self, key: str) -> int:
        async with self._lock:
            if key in self._cache:
                value, exp = self._cache[key]
                new_value = int(value) + 1
                self._cache[key] = (str(new_value), exp)
                return new_value
            self._cache[key] = ("1", None)
            return 1
    
    async def expire(self, key: str, ttl: int) -> bool:
        import time
        async with self._lock:
            if key in self._cache:
                value, _ = self._cache[key]
                self._cache[key] = (value, time.time() + ttl)
                return True
        return False
    
    async def ttl(self, key: str) -> int:
        import time
        async with self._lock:
            if key in self._cache:
                _, exp = self._cache[key]
                if exp is None:
                    return -1
                remaining = int(exp - time.time())
                return max(0, remaining)
        return -2


class RedisCache(CacheBackend):
    """Redis 缓存后端"""
    
    def __init__(self, url: str):
        self._url = url
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
    
    async def connect(self):
        """建立 Redis 连接"""
        if self._pool is None:
            self._pool = redis.ConnectionPool.from_url(
                self._url,
                max_connections=20,
                decode_responses=True
            )
            self._client = redis.Redis(connection_pool=self._pool)
            # 测试连接
            await self._client.ping()
            logger.info("✅ Redis 连接成功")
    
    async def disconnect(self):
        """关闭 Redis 连接"""
        if self._client:
            await self._client.close()
        if self._pool:
            await self._pool.disconnect()

    async def get(self, key: str) -> Optional[str]:
        if self._client is None:
            await self.connect()
        return await self._client.get(key)

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        if self._client is None:
            await self.connect()
        if ttl:
            await self._client.setex(key, ttl, value)
        else:
            await self._client.set(key, value)
        return True

    async def delete(self, key: str) -> bool:
        if self._client is None:
            await self.connect()
        result = await self._client.delete(key)
        return result > 0

    async def exists(self, key: str) -> bool:
        if self._client is None:
            await self.connect()
        return await self._client.exists(key) > 0

    async def incr(self, key: str) -> int:
        if self._client is None:
            await self.connect()
        return await self._client.incr(key)

    async def expire(self, key: str, ttl: int) -> bool:
        if self._client is None:
            await self.connect()
        return await self._client.expire(key, ttl)

    async def ttl(self, key: str) -> int:
        if self._client is None:
            await self.connect()
        return await self._client.ttl(key)


class CacheService:
    """
    缓存服务 - 统一的缓存接口

    支持 Redis 和内存缓存的自动切换
    """

    # 缓存键前缀
    PREFIX_DATA = "data:"
    PREFIX_SESSION = "session:"
    PREFIX_RATE_LIMIT = "rate:"

    # 默认 TTL（秒）
    TTL_SHORT = 60  # 1 分钟
    TTL_MEDIUM = 300  # 5 分钟
    TTL_LONG = 3600  # 1 小时
    TTL_SESSION = 86400  # 24 小时

    def __init__(self):
        self._backend: Optional[CacheBackend] = None
        self._initialized = False

    async def initialize(self):
        """初始化缓存后端"""
        if self._initialized:
            return

        if REDIS_AVAILABLE and settings.REDIS_URL:
            try:
                redis_cache = RedisCache(settings.REDIS_URL)
                await redis_cache.connect()
                self._backend = redis_cache
                logger.info("🚀 使用 Redis 缓存后端")
            except Exception as e:
                logger.warning(f"⚠️ Redis 连接失败，回退到内存缓存: {e}")
                self._backend = MemoryCache()
        else:
            logger.info("📦 使用内存缓存后端")
            self._backend = MemoryCache()

        self._initialized = True

    async def _ensure_initialized(self):
        """确保缓存已初始化"""
        if not self._initialized:
            await self.initialize()

    # ==================== 通用缓存操作 ====================

    async def get(self, key: str, prefix: str = PREFIX_DATA) -> Optional[Any]:
        """获取缓存值"""
        await self._ensure_initialized()
        full_key = f"{prefix}{key}"
        value = await self._backend.get(full_key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = TTL_MEDIUM,
        prefix: str = PREFIX_DATA
    ) -> bool:
        """设置缓存值"""
        await self._ensure_initialized()
        full_key = f"{prefix}{key}"
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False, default=str)
        elif not isinstance(value, str):
            value = str(value)
        return await self._backend.set(full_key, value, ttl)

    async def delete(self, key: str, prefix: str = PREFIX_DATA) -> bool:
        """删除缓存"""
        await self._ensure_initialized()
        full_key = f"{prefix}{key}"
        return await self._backend.delete(full_key)

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        按模式失效缓存（仅 Redis 支持）

        对于内存缓存，此操作不执行任何操作
        """
        await self._ensure_initialized()
        if isinstance(self._backend, RedisCache) and self._backend._client:
            keys = []
            async for key in self._backend._client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await self._backend._client.delete(*keys)
        return 0

    # ==================== 会话存储 ====================

    async def set_session(self, session_id: str, data: dict, ttl: int = TTL_SESSION) -> bool:
        """存储会话数据"""
        return await self.set(session_id, data, ttl, self.PREFIX_SESSION)

    async def get_session(self, session_id: str) -> Optional[dict]:
        """获取会话数据"""
        return await self.get(session_id, self.PREFIX_SESSION)

    async def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        return await self.delete(session_id, self.PREFIX_SESSION)

    # ==================== 速率限制 ====================

    async def check_rate_limit(
        self,
        identifier: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> tuple[bool, int, int]:
        """
        检查速率限制

        Args:
            identifier: 唯一标识符（如 IP 地址、用户 ID）
            max_requests: 窗口期内最大请求数
            window_seconds: 时间窗口（秒）

        Returns:
            tuple: (是否允许, 剩余请求数, 重置时间秒数)
        """
        await self._ensure_initialized()
        key = f"{self.PREFIX_RATE_LIMIT}{identifier}"

        current = await self._backend.get(key)
        if current is None:
            await self._backend.set(key, "1", window_seconds)
            return True, max_requests - 1, window_seconds

        count = int(current)
        if count >= max_requests:
            ttl = await self._backend.ttl(key)
            return False, 0, max(0, ttl)

        new_count = await self._backend.incr(key)
        ttl = await self._backend.ttl(key)
        return True, max_requests - new_count, max(0, ttl)

    # ==================== 缓存装饰器 ====================


def cached(
    ttl: int = CacheService.TTL_MEDIUM,
    key_prefix: str = "",
    key_builder: Optional[Callable[..., str]] = None
):
    """
    缓存装饰器

    用法:
        @cached(ttl=300, key_prefix="student")
        async def get_student(student_id: str):
            ...

    Args:
        ttl: 缓存过期时间（秒）
        key_prefix: 缓存键前缀
        key_builder: 自定义键生成函数
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # 生成缓存键
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # 默认键生成：函数名 + 参数哈希
                key_parts = [key_prefix or func.__name__]
                for arg in args:
                    if hasattr(arg, '__dict__'):
                        continue  # 跳过复杂对象（如 db session）
                    key_parts.append(str(arg))
                for k, v in sorted(kwargs.items()):
                    if k == 'db':
                        continue  # 跳过数据库会话
                    key_parts.append(f"{k}:{v}")
                cache_key = ":".join(key_parts)

            # 尝试从缓存获取
            cached_value = await cache_service.get(cache_key)
            if cached_value is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_value

            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            if result is not None:
                await cache_service.set(cache_key, result, ttl)
                logger.debug(f"缓存写入: {cache_key}")

            return result
        return wrapper
    return decorator


def generate_cache_key(*args, **kwargs) -> str:
    """生成缓存键的辅助函数"""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.md5(key_data.encode()).hexdigest()


# ==================== 全局缓存服务实例 ====================

cache_service = CacheService()


# ==================== 常用缓存键生成器 ====================

class CacheKeys:
    """缓存键生成器"""

    @staticmethod
    def student(student_id: Union[str, int]) -> str:
        return f"student:{student_id}"

    @staticmethod
    def assignment(assignment_id: Union[str, int]) -> str:
        return f"assignment:{assignment_id}"

    @staticmethod
    def submission(submission_id: Union[str, int]) -> str:
        return f"submission:{submission_id}"

    @staticmethod
    def grading_result(grading_id: Union[str, int]) -> str:
        return f"grading:{grading_id}"

    @staticmethod
    def grading_by_student(student_id: Union[str, int]) -> str:
        return f"grading:student:{student_id}"

    @staticmethod
    def grading_by_assignment(assignment_id: Union[str, int]) -> str:
        return f"grading:assignment:{assignment_id}"

    @staticmethod
    def grading_by_submission(submission_id: Union[str, int]) -> str:
        return f"grading:submission:{submission_id}"

    @staticmethod
    def rubric(rubric_id: Union[str, int]) -> str:
        return f"rubric:{rubric_id}"

    @staticmethod
    def user_session(user_id: Union[str, int]) -> str:
        return f"user:{user_id}"

