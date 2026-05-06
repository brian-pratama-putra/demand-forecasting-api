from aplikasi import (log, secret_key_forecast_request)
from aplikasi.others.response import (response_forecast_service)
from aplikasi.others.format import generate_checksum
from aplikasi.dao.api.db_dao import get_sales_data, save_forecast_result
from aplikasi.dao.api.redis_dao import cache_get_forecast, cache_set_forecast
from aplikasi.ml_models.forecasting_model import DemandForecastModel
import json

async def forecast_demand(request):
    data = await request.json()

    v_method = data.get("method", "")
    v_product_id = data.get("product_id", "")
    v_forecast_days = data.get("forecast_days", 7)
    v_datetime = data.get("datetime", "")
    v_checksum = data.get("checksum", "")

    if not all([v_method, v_product_id, v_datetime, v_checksum]):
        return await response_forecast_service(request, v_method, 422, 400, "Invalid Request Data")

    app_payload = f"{v_method}#{v_product_id}#{v_forecast_days}#{v_datetime}#{secret_key_forecast_request}"
    app_checksum = generate_checksum(app_payload)

    if v_checksum != app_checksum:
        return await response_forecast_service(request, v_method, 406, 401, "Invalid Key")

    if v_forecast_days < 1 or v_forecast_days > 90:
        return await response_forecast_service(
            request, v_method, 422, 400,
            "Forecast days harus antara 1-90 hari"
        )

    v_cached = await cache_get_forecast(v_product_id, v_forecast_days)
    if v_cached:
        log.info(f"Returning cached forecast for {v_product_id}")
        return await response_forecast_service(
            request, v_method, 200, 200, "Success (Cached)",
            v_cached
        )

    v_sales_result = await get_sales_data(v_product_id)

    if v_sales_result["status"] == "F" or not v_sales_result["result"]:
        return await response_forecast_service(
            request, v_method, 404, 404,
            "Data penjualan tidak ditemukan. Upload data terlebih dahulu."
        )

    try:
        v_sales_record = v_sales_result["result"][0]
        v_sales_data = json.loads(v_sales_record["sales_data"])

        model = DemandForecastModel()
        model.train(v_sales_data, v_product_id)
        
        v_forecast_result = model.predict(v_forecast_days)

        await save_forecast_result(v_product_id, v_forecast_result)
        
        await cache_set_forecast(v_product_id, v_forecast_days, v_forecast_result, ttl=3600)

        return await response_forecast_service(
            request, v_method, 200, 200, "Success",
            v_forecast_result
        )

    except Exception as e:
        log.error(f"Error forecasting: {str(e)}")
        return await response_forecast_service(
            request, v_method, 500, 500,
            f"Error saat melakukan forecasting: {str(e)}"
        )
