from aplikasi.dao.query_file import CreateConnectionDb, QueryStringDb
from aplikasi import log
import json

async def save_sales_data(p_product_id: str, p_product_name: str, p_sales_data: list):
    """
    Simpan historical sales data ke database
    """
    try:
        with CreateConnectionDb({"read": False, "write": True}) as db:
            query_db = QueryStringDb(db)
            
            v_sales_json = json.dumps(p_sales_data)
            
            v_query = """
                INSERT INTO tbl_product_sales 
                (product_id, product_name, sales_data, created_at, updated_at)
                VALUES (%(product_id)s, %(product_name)s, %(sales_data)s, NOW(), NOW())
                ON CONFLICT (product_id) 
                DO UPDATE SET 
                    product_name = EXCLUDED.product_name,
                    sales_data = EXCLUDED.sales_data,
                    updated_at = NOW()
            """
            
            v_kondisi = {
                "product_id": p_product_id,
                "product_name": p_product_name,
                "sales_data": v_sales_json
            }
            
            v_result = query_db.execute(
                v_query,
                v_kondisi,
                "Sales data saved successfully!"
            )
            
            return v_result
            
    except Exception as e:
        log.error(f"Error save_sales_data: {str(e)}")
        return {
            "status_code": 500,
            "status": "F",
            "message": f"Error: {str(e)}",
            "result": None
        }

async def get_sales_data(p_product_id: str):
    """
    Ambil historical sales data dari database
    """
    try:
        with CreateConnectionDb({"read": True, "write": False}) as db:
            query_db = QueryStringDb(db)
            
            v_query = """
                SELECT product_id, product_name, sales_data, created_at, updated_at
                FROM tbl_product_sales
                WHERE product_id = %(product_id)s
            """
            
            v_kondisi = {
                "product_id": p_product_id
            }
            
            v_result = query_db.select(
                v_query,
                v_kondisi,
                "Sales data retrieved successfully!"
            )
            
            return v_result
            
    except Exception as e:
        log.error(f"Error get_sales_data: {str(e)}")
        return {
            "status_code": 500,
            "status": "F",
            "message": f"Error: {str(e)}",
            "result": []
        }

async def save_forecast_result(p_product_id: str, p_forecast_data: dict):
    """
    Simpan hasil forecast ke database
    """
    try:
        with CreateConnectionDb({"read": False, "write": True}) as db:
            query_db = QueryStringDb(db)
            
            v_forecast_json = json.dumps(p_forecast_data)
            
            v_query = """
                INSERT INTO tbl_forecast_history
                (product_id, forecast_data, created_at)
                VALUES (%(product_id)s, %(forecast_data)s, NOW())
            """
            
            v_kondisi = {
                "product_id": p_product_id,
                "forecast_data": v_forecast_json
            }
            
            v_result = query_db.execute(
                v_query,
                v_kondisi,
                "Forecast result saved successfully!"
            )
            
            return v_result
            
    except Exception as e:
        log.error(f"Error save_forecast_result: {str(e)}")
        return {
            "status_code": 500,
            "status": "F",
            "message": f"Error: {str(e)}",
            "result": None
        }

async def get_forecast_history(p_product_id: str, p_limit: int = 10):
    """
    Ambil history forecast dari database
    """
    try:
        with CreateConnectionDb({"read": True, "write": False}) as db:
            query_db = QueryStringDb(db)
            
            v_query = """
                SELECT id, product_id, forecast_data, created_at
                FROM tbl_forecast_history
                WHERE product_id = %(product_id)s
                ORDER BY created_at DESC
                LIMIT %(limit)s
            """
            
            v_kondisi = {
                "product_id": p_product_id,
                "limit": p_limit
            }
            
            v_result = query_db.select(
                v_query,
                v_kondisi,
                "Forecast history retrieved successfully!"
            )
            
            return v_result
            
    except Exception as e:
        log.error(f"Error get_forecast_history: {str(e)}")
        return {
            "status_code": 500,
            "status": "F",
            "message": f"Error: {str(e)}",
            "result": []
        }

async def get_all_products():
    """
    Ambil semua produk yang ada
    """
    try:
        with CreateConnectionDb({"read": True, "write": False}) as db:
            query_db = QueryStringDb(db)
            
            v_query = """
                SELECT product_id, product_name, created_at, updated_at
                FROM tbl_product_sales
                ORDER BY updated_at DESC
            """
            
            v_result = query_db.select(
                v_query,
                (),
                "Product list retrieved successfully!"
            )
            
            return v_result
            
    except Exception as e:
        log.error(f"Error get_all_products: {str(e)}")
        return {
            "status_code": 500,
            "status": "F",
            "message": f"Error: {str(e)}",
            "result": []
        }

async def delete_product_data(p_product_id: str):
    """
    Hapus data produk dan forecast history
    """
    try:
        with CreateConnectionDb({"read": False, "write": True}) as db:
            query_db = QueryStringDb(db)
            
            v_kondisi = {
                "product_id": p_product_id
            }
            
            v_query1 = "DELETE FROM tbl_forecast_history WHERE product_id = %(product_id)s"
            query_db.execute_no_commit(v_query1, v_kondisi)
            
            v_query2 = "DELETE FROM tbl_product_sales WHERE product_id = %(product_id)s"
            v_result = query_db.execute(
                v_query2,
                v_kondisi,
                "Product data deleted successfully!"
            )
            
            return v_result
            
    except Exception as e:
        log.error(f"Error delete_product_data: {str(e)}")
        return {
            "status_code": 500,
            "status": "F",
            "message": f"Error: {str(e)}",
            "result": None
        }
