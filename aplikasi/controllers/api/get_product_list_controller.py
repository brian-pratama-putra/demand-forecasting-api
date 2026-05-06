from aplikasi import (log, secret_key_forecast_request)
from aplikasi.others.response import (response_forecast_service)
from aplikasi.others.format import generate_checksum
from aplikasi.dao.api.db_dao import get_all_products

async def get_product_list_controller(request):
    data = await request.json()

    v_method = data.get("method", "")
    v_datetime = data.get("datetime", "")
    v_checksum = data.get("checksum", "")

    if not all([v_method, v_datetime, v_checksum]):
        return await response_forecast_service(request, v_method, 422, 400, "Invalid Request Data")

    app_payload = f"{v_method}#{v_datetime}#{secret_key_forecast_request}"
    app_checksum = generate_checksum(app_payload)

    if v_checksum != app_checksum:
        return await response_forecast_service(request, v_method, 406, 401, "Invalid Key")

    v_result = await get_all_products()

    if v_result["status"] == "T":
        v_product_list = []
        for record in v_result["result"]:
            v_product_list.append({
                "product_id": record["product_id"],
                "product_name": record["product_name"],
                "created_at": str(record["created_at"]),
                "updated_at": str(record["updated_at"])
            })

        return await response_forecast_service(
            request, v_method, 200, 200, "Success",
            {
                "total_products": len(v_product_list),
                "products": v_product_list
            }
        )
    else:
        return await response_forecast_service(
            request, v_method, 500, 500, v_result["message"]
        )
