import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("agentsec")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        extra = {
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
        }

        logger.info("Request started", extra=extra)

        try:
            response = await call_next(request)
            extra["status_code"] = response.status_code
            logger.info(f"Request completed with status {response.status_code}", extra=extra)
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}", extra=extra, exc_info=True)
            raise