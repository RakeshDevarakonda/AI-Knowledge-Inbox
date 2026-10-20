from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from ai_knowledge_inbox.config import logger

def sanitize_error_message(raw_msg: str) -> str:
    """
    Guarantees internal stack traces, system paths, vendor JSON dumps,
    and developer technical errors are NEVER exposed to the client.
    Converts errors into clean, professional, actionable messages.
    """
    msg = str(raw_msg).strip()

    # Pass through already sanitized clean messages
    if msg.startswith("AI Service Unavailable:") or msg.startswith("Unable to ") or msg.startswith("Field '"):
        return msg

    lower = msg.lower()

    # Rate limits
    if any(k in lower for k in ["resource_exhausted", "429", "rate limit", "too many requests"]):
        return "AI Service Unavailable: Rate limit reached. Please wait a moment and try again."

    # Missing API Keys
    if "gemini_api_key" in lower or "gemini api key" in lower:
        return "Gemini API Key not configured. Please add GEMINI_API_KEY in Backend/.env."

    # Authentication
    if any(k in lower for k in ["api_key_invalid", "401", "unauthorized", "forbidden"]):
        return "AI Service Unavailable: Authentication failed. Please verify API key in Backend/.env."

    # Service overloaded / 503
    if any(k in lower for k in ["503", "unavailable", "service unavailable", "overloaded", "bad gateway", "502"]):
        return "AI Service Unavailable: Service is temporarily overloaded. Please try again shortly."

    # Web scraper errors
    if "failed to fetch url" in lower or "network error while connecting to url" in lower:
        return "Unable to fetch webpage. The site is unreachable or blocked requests. Please verify the URL."

    # Timeouts
    if "timeout" in lower or "timed out" in lower:
        return "AI Service Unavailable: Request timed out. Please try again."

    # Model deprecated
    if "is no longer available" in lower or "not_found" in lower:
        return "AI Service Unavailable: The requested AI model is retired or unavailable. Switched to fallback."

    # Mask any raw JSON or Python dictionaries
    if "{" in msg and "}" in msg:
        return "AI Service Unavailable: External provider error. Please try '✨ Gemini' or try again later."

    # Mask any Python stack trace leaks
    if any(k in msg for k in ["Traceback", "File \"", "Exception:", "line "]):
        return "Service Temporarily Unavailable: An unexpected error occurred. Please try again later."

    return msg

def format_validation_error(exc: RequestValidationError) -> str:
    """Transforms cryptic Pydantic validation error objects into human-readable text."""
    messages = []
    for error in exc.errors():
        loc = [str(l) for l in error.get("loc", []) if l != "body"]
        field = ".".join(loc) if loc else "input"
        msg = error.get("msg", "Invalid value")
        error_type = error.get("type", "")

        if error_type == "missing":
            messages.append(f"Field '{field}' is required.")
        else:
            messages.append(f"Invalid '{field}': {msg}.")

    return " ".join(messages) if messages else "Invalid request body."

def register_error_handlers(app: FastAPI) -> None:
    """
    Registers comprehensive global exception handlers across the FastAPI application.
    Guarantees every error returns a clean, predictable JSON payload:
    {
      "success": false,
      "detail": "<Human-readable explanation>",
      "message": "<Human-readable explanation>",
      "status_code": <HTTP status>,
      "error_type": "<Category>",
      "path": "<Request URL Path>"
    }
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        friendly_message = format_validation_error(exc)
        logger.warning("Validation failed for %s %s: %s", request.method, request.url.path, friendly_message)
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "detail": friendly_message,
                "message": friendly_message,
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "error_type": "ValidationError",
                "path": request.url.path,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        cleaned_detail = sanitize_error_message(str(exc.detail))
        logger.warning("HTTP %d on %s %s: %s", exc.status_code, request.method, request.url.path, exc.detail)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "detail": cleaned_detail,
                "message": cleaned_detail,
                "status_code": exc.status_code,
                "error_type": "ClientError" if exc.status_code < 500 else "ServerError",
                "path": request.url.path,
            },
        )

    @app.exception_handler(Exception)
    async def global_unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled Exception on %s %s: %s", request.method, request.url.path, exc)
        cleaned_message = sanitize_error_message(str(exc))

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "detail": cleaned_message,
                "message": cleaned_message,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error_type": "InternalServerError",
                "path": request.url.path,
            },
        )
