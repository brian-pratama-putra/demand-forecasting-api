from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.openapi.utils import get_openapi
from aplikasi.settings import settings
from fastapi_limiter import FastAPILimiter
from zoneinfo import ZoneInfo
from common.custom_log import Logger

log = Logger()

common_args = {
    "title": "Demand Forecasting API",
    "version": "1.0.0",
    "description": "API untuk forecasting demand produk dan rekomendasi stok",
    "contact": {
        "name": "Developer",
        "email": "developer@example.com",
    },
    "openapi_tags": [
        {"name": "Inquiry", "description": "Semua metode untuk endpoint /inquiry"},
    ]
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    from aplikasi.dao.query_file import get_redis_limiter_client
    
    limiter_client = await get_redis_limiter_client()
    await FastAPILimiter.init(limiter_client)

    try:
        yield
    finally:
        pass

if settings.STATUS_APP == "DEV":
    app = FastAPI(**common_args, debug=True, lifespan=lifespan)
else:
    app = FastAPI(**common_args, docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)

router = APIRouter()

secret_key_forecast_request   = settings.SECRET_KEY_FORECAST_REQUEST
secret_key_forecast_response  = settings.SECRET_KEY_FORECAST_RESPONSE
secret_key_forecast_header    = settings.SECRET_KEY_FORECAST_HEADER

TZ_JAKARTA = ZoneInfo("Asia/Jakarta")

from aplikasi.routes import register_error_handlers, set_security_headers, SecurityMiddleware

if settings.STATUS_APP == "DEV":
    app.middleware("http")(set_security_headers)
else:
    app.add_middleware(SecurityMiddleware)

register_error_handlers(app)

from aplikasi.controllers.api import api_controller
app.include_router(api_controller.router)

from aplikasi.models.api_model import (
    inquiry_examples,
    UploadSalesDataRequest,
    ForecastDemandRequest,
    GetForecastHistoryRequest,
    GetProductListRequest,
    DeleteProductDataRequest
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Demand Forecasting API",
        version="1.0.0",
        description="Dokumentasi metode `method` di endpoint `/inquiry`",
        routes=app.routes,
    )

    models = [
        UploadSalesDataRequest,
        ForecastDemandRequest,
        GetForecastHistoryRequest,
        GetProductListRequest,
        DeleteProductDataRequest
    ]

    openapi_schema["paths"]["/inquiry-docs"]["post"]["requestBody"] = {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "oneOf": [{"$ref": f"#/components/schemas/{model.__name__}"} for model in models]
                },
                "examples": inquiry_examples,
            }
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
