from aplikasi import (log, secret_key_forecast_request)
from aplikasi.others.response import (response_forecast_service)
from aplikasi.others.format import generate_checksum
from aplikasi.dao.api.db_dao import get_forecast_history
import json

async def get_forecast_history_controller(request):
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

    v_result = await get_forecast_history(v_product_id, p_limit=10)

    if v_result["status"] == "T":
        v_history_list = []
        for record in v_result["result"]:
            v_forecast_data = json.loads(record["forecast_data"])
            v_history_list.append({
                "id": record["id"],
                "forecast_date": str(record["created_at"]),
                "forecast_period": v_forecast_data.get("forecast_period", ""),
                "total_stock_needed": v_forecast_data.get("total_stock_needed", 0),
                "confidence_level": v_forecast_data.get("confidence_level", "")
            })

        return await response_forecast_service(
            request, v_method, 200, 200, "Success",
            {
                "product_id": v_product_id,
                "history": v_history_list
            }
        )
    else:
        return await response_forecast_service(
            request, v_method, 500, 500, v_result["message"]
        )
