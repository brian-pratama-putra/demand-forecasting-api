from aplikasi import (log, secret_key_forecast_request)
from aplikasi.others.response import (response_forecast_service)
from aplikasi.others.format import generate_checksum
from aplikasi.dao.api.db_dao import delete_product_data
from aplikasi.dao.api.redis_dao import cache_delete_forecast

async def delete_product_data_controller(request):
    data = await request.json()

    v_method = data.get("method", "")
    v_product_id = data.get("product_id", "")
    v_datetime = data.get("datetime", "")
    v_checksum = data.get("checksum", "")

    if not all([v_method, v_product_id, v_datetime, v_checksum]):
        return await response_forecast_service(request, v_method, 422, 400, "Invalid Request Data")

    app_payload = f"{v_method}#{v_product_id}#{v_datetime}#{secret_key_forecast_request}"
    app_checksum = generate_checksum(app_payload)

    if v_checksum != app_checksum:
        return await response_forecast_service(request, v_method, 406, 401, "Invalid Key")

    v_result = await delete_product_data(v_product_id)

    if v_result["status"] == "T":
        await cache_delete_forecast(v_product_id)
        
        return await response_forecast_service(
            request, v_method, 200, 200, "Success",
            {
                "product_id": v_product_id,
                "message": "Product data and forecast history deleted successfully"
            }
        )
    else:
        return await response_forecast_service(
            request, v_method, 500, 500, v_result["message"]
        )
