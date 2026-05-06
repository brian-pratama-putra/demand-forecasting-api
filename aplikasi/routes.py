from fastapi import FastAPI, Request
from aplikasi.others.response import (response_forecast_service)
from aplikasi.others.utility import (safe_json)
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, PlainTextResponse, Response
import re

def register_error_handlers(app: FastAPI):
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        data = await safe_json(request)
        v_method = data.get("method", "")
        return await response_forecast_service(request, v_method, 404, 404, "Route not found.")
    
    @app.exception_handler(StarletteHTTPException)
    async def default_http_exception_handler(request: Request, exc: StarletteHTTPException):
        data = await safe_json(request)
        v_method = data.get("method", "")
        return await response_forecast_service(
            request,
            v_method,
            exc.status_code,
            exc.status_code,
            str(exc.detail)
        )

async def set_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Permissions-Policy"] = "browsing-topics=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; object-src 'none'"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    return response

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_agent = request.headers.get("user-agent", "").lower()
        scanner_patterns = ["censys", "zgrab", "modtscanner", "nmap", "masscan"]
        if any(p in user_agent for p in scanner_patterns):
            return PlainTextResponse("Blocked", status_code=403)
        
        invalid_paths = [r"/\.env", r"/security\.txt", r"/\.git", r"/phpmyadmin", r"/aaa\d*", r"/wp-.*"]
        if any(re.match(p, request.url.path, re.IGNORECASE) for p in invalid_paths):
            return PlainTextResponse("Blocked", status_code=404)
        
        if request.headers.get("x-forwarded-proto", "http") != "https":
            return JSONResponse(
                status_code=403,
                content={"detail": "HTTPS Required"},
                headers={"Content-Type": "application/json"}
            )

        try:
            response: Response = await call_next(request)
            path = request.url.path
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

            if not (path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi.json")):
                response.headers["Content-Security-Policy"] = (
                    "default-src 'none'; "
                    "script-src 'self'; "
                    "style-src 'self'; "
                    "img-src 'self' data:; "
                    "connect-src 'self'; "
                    "frame-ancestors 'none'; "
                    "base-uri 'none'; "
                    "form-action 'self'; "
                )

            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Permissions-Policy"] = (
                "accelerometer=(), autoplay=(), camera=(), geolocation=(), gyroscope=(), "
                "magnetometer=(), microphone=(), payment=(), usb=(), browsing-topics=()"
            )

            response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
            response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
            response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

            return response
        
        except StarletteHTTPException as e:
            return PlainTextResponse("Not Found", status_code=404)

        except Exception as e:
            return PlainTextResponse("Internal Server Error", status_code=500)
