from aplikasi import (log, secret_key_forecast_request)
from aplikasi.others.response import (response_forecast_service)
from aplikasi.others.format import generate_checksum
from aplikasi.dao.api.db_dao import save_sales_data
from aplikasi.dao.api.redis_dao import cache_delete_forecast

async def upload_sales_data(request):
    data = await request.json()

    v_method = data.get("method", "")
    v_product_id = data.get("product_id", "")
    v_product_name = data.get("product_name", "")
    v_sales_data = data.get("sales_data", [])
    v_datetime = data.get("datetime", "")
    v_checksum = data.get("checksum", "")

    if not all([v_method, v_product_id, v_product_name, v_sales_data, v_datetime, v_checksum]):
        return await response_forecast_service(request, v_method, 422, 400, "Invalid Request Data")

    app_payload = f"{v_method}#{v_product_id}#{v_product_name}#{v_datetime}#{secret_key_forecast_request}"
    app_checksum = generate_checksum(app_payload)

    if v_checksum != app_checksum:
        return await response_forecast_service(request, v_method, 406, 401, "Invalid Key")

    if not isinstance(v_sales_data, list) or len(v_sales_data) < 2:
        return await response_forecast_service(
            request, v_method, 422, 400, 
            "Sales data harus berupa list dengan minimal 2 data point"
        )

    for item in v_sales_data:
        if 'date' not in item or 'quantity' not in item:
            return await response_forecast_service(
                request, v_method, 422, 400,
                "Setiap data harus memiliki 'date' dan 'quantity'"
            )

    v_result = await save_sales_data(v_product_id, v_product_name, v_sales_data)

    if v_result["status"] == "T":
        await cache_delete_forecast(v_product_id)
        
        return await response_forecast_service(
            request, v_method, 200, 200, "Success",
            {
                "product_id": v_product_id,
                "product_name": v_product_name,
                "data_points": len(v_sales_data)
            }
        )
    else:
        return await response_forecast_service(
            request, v_method, 500, 500, v_result["message"]
        )
