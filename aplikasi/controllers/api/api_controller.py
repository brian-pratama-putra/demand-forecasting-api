from aplikasi import app
from fastapi import Request, Depends, Body
from fastapi_limiter.depends import RateLimiter
from fastapi.responses import JSONResponse, Response
from typing import Union

from aplikasi import (log, router, secret_key_forecast_request, secret_key_forecast_response, secret_key_forecast_header, settings)
import traceback

from aplikasi.controllers.api.upload_sales_data_controller import (upload_sales_data)
from aplikasi.controllers.api.forecast_demand_controller import (forecast_demand)
from aplikasi.controllers.api.get_forecast_history_controller import (get_forecast_history_controller)
from aplikasi.controllers.api.get_product_list_controller import (get_product_list_controller)
from aplikasi.controllers.api.delete_product_data_controller import (delete_product_data_controller)

from aplikasi.others.response import response_forecast_service
from aplikasi.others.utility import (safe_json, validate_request_datetime)

from aplikasi.models.api_model import (
    UploadSalesDataRequest,
    ForecastDemandRequest,
    GetForecastHistoryRequest,
    GetProductListRequest,
    DeleteProductDataRequest
)

InquiryRequestUnion = Union[
    UploadSalesDataRequest,
    ForecastDemandRequest,
    GetForecastHistoryRequest,
    GetProductListRequest,
    DeleteProductDataRequest
]

@router.post("/inquiry-docs", response_model=None, summary="Dokumentasi Skema /inquiry", tags=["Inquiry"])
async def inquiry_docs(body: InquiryRequestUnion = Body(...)):
    """
    Endpoint ini hanya untuk dokumentasi semua bentuk payload `method` dari `/inquiry`.
    Tidak dipakai oleh frontend secara langsung.
    """
    return {"message": "Hanya untuk dokumentasi schema"}

@router.post("/inquiry", dependencies=[Depends(RateLimiter(times=50, seconds=60))], include_in_schema=False)
async def inquiry(request: Request):
    try:
        data_request    = await safe_json(request)
        v_method        = data_request.get("method", "")
        v_datetime      = data_request.get("datetime", "")

        v_is_valid, v_msg = validate_request_datetime(v_datetime)
        if not v_is_valid:
            return await response_forecast_service(request, v_method, 405, 405, v_msg)
        
        if not secret_key_forecast_request:
            return await response_forecast_service(request, v_method, 500, 500, "Internal Server Error: Missing SECRET_KEY_FORECAST_REQUEST")
        if not secret_key_forecast_response:
            return await response_forecast_service(request, v_method, 500 , 500, "Internal Server Error: Missing SECRET_KEY_FORECAST_RESPONSE")
        if not secret_key_forecast_header:
            return await response_forecast_service(request, v_method, 500 , 500, "Internal Server Error: Missing SECRET_KEY_FORECAST_HEADER")
        
        if v_method == "upload_sales_data":
            return await upload_sales_data(request)
        elif v_method == "forecast_demand":
            return await forecast_demand(request)
        elif v_method == "get_forecast_history":
            return await get_forecast_history_controller(request)
        elif v_method == "get_product_list":
            return await get_product_list_controller(request)
        elif v_method == "delete_product_data":
            return await delete_product_data_controller(request)
        else:
            return await response_forecast_service(request, v_method, 405, 405, "Internal Server Error: Invalid Method")
    except Exception as e:
        log.error(f"===== ERROR INQUIRY ===== : {e}")
        traceback.print_exc()  
        return await response_forecast_service(request, v_method, 405, 401, "Internal Server Error: Forecast Service Inquiry")

@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204) 

@router.get("/health/connections", include_in_schema=False)
async def connection_health():
    from aplikasi.dao.query_file import get_pool_stats, REDIS_TEXT_CLIENT
    try:
        db_stats = get_pool_stats()
        
        redis_stats = {
            "text_client": "connected" if REDIS_TEXT_CLIENT else "not_initialized",
            "connection_type": "single_client"
        }
        
        return {
            "status": "ok",
            "postgresql": db_stats,
            "redis": redis_stats,
            "note": "Demand Forecasting API"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/")
async def root():
    return {"status": "running", "service": "Demand Forecasting API"}
