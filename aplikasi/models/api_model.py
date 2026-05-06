from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

inquiry_examples = {
    "upload_sales_data": {
        "summary": "Upload historical sales data",
        "value": {
            "method": "upload_sales_data",
            "product_id": "PROD001",
            "product_name": "Indomie Goreng",
            "sales_data": [
                {"date": "2024-01-01", "quantity": 45},
                {"date": "2024-01-02", "quantity": 52},
                {"date": "2024-01-03", "quantity": 38}
            ],
            "datetime": "2025-01-30 14:00:00",
            "checksum": "abc123"
        }
    },
    "forecast_demand": {
        "summary": "Forecast demand untuk produk",
        "value": {
            "method": "forecast_demand",
            "product_id": "PROD001",
            "forecast_days": 7,
            "datetime": "2025-01-30 14:00:00",
            "checksum": "def456"
        }
    },
    "get_forecast_history": {
        "summary": "Lihat history forecast",
        "value": {
            "method": "get_forecast_history",
            "product_id": "PROD001",
            "datetime": "2025-01-30 14:00:00",
            "checksum": "ghi789"
        }
    },
    "get_product_list": {
        "summary": "Lihat daftar produk",
        "value": {
            "method": "get_product_list",
            "datetime": "2025-01-30 14:00:00",
            "checksum": "jkl012"
        }
    },
    "delete_product_data": {
        "summary": "Hapus data produk",
        "value": {
            "method": "delete_product_data",
            "product_id": "PROD001",
            "datetime": "2025-01-30 14:00:00",
            "checksum": "mno345"
        }
    }
}

class BaseRequest(BaseModel):
    method: str = Field(..., example="upload_sales_data")

class UploadSalesDataRequest(BaseModel):
    method: str
    product_id: str
    product_name: str
    sales_data: List[Dict[str, Any]]
    datetime: str
    checksum: str

class ForecastDemandRequest(BaseModel):
    method: str
    product_id: str
    forecast_days: int
    datetime: str
    checksum: str

class GetForecastHistoryRequest(BaseModel):
    method: str
    product_id: str
    datetime: str
    checksum: str

class GetProductListRequest(BaseModel):
    method: str
    datetime: str
    checksum: str

class DeleteProductDataRequest(BaseModel):
    method: str
    product_id: str
    datetime: str
    checksum: str
