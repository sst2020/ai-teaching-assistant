"""
Simple in-memory rate limiting middleware.

Note: This is a lightweight limiter for development/testing. For production,
consider a distributed limiter backed by Redis.
"""
import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from core.config import settings


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    """Basic rate limiter using an in-memory sliding window per client IP."""

    def __init__(self, app):
        super().__init__(app)
        self.limit = settings.RATE_LIMIT_REQUESTS
        self.period = settings.RATE_LIMIT_PERIOD
        self._requests: Dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        if self.limit <= 0 or self.period <= 0:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self.period

        queue = self._requests[client_ip]
        while queue and queue[0] <= window_start:
            queue.popleft()

        if len(queue) >= self.limit:
            retry_after = max(1, int(queue[0] + self.period - now))
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={"Retry-After": str(retry_after)},
            )

        queue.append(now)
        return await call_next(request)
