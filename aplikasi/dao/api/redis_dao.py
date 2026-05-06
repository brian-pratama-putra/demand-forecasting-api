from aplikasi.dao.query_file import connection_redis_async
from aplikasi import log
import json

async def cache_get_forecast(p_product_id: str, p_forecast_days: int):
    """
    Get cached forecast result dari Redis
    """
    try:
        v_redis = await connection_redis_async()
        v_cache_key = f"forecast:{p_product_id}:{p_forecast_days}"
        
        v_cached_data = await v_redis.get(v_cache_key)
        
        if v_cached_data:
            return json.loads(v_cached_data)
        
        return None
        
    except Exception as e:
        log.error(f"Error cache_get_forecast: {str(e)}")
        return None

async def cache_set_forecast(p_product_id: str, p_forecast_days: int, p_forecast_data: dict, p_ttl: int = 3600):
    """
    Set forecast result ke Redis cache
    TTL default 1 jam (3600 detik)
    """
    try:
        v_redis = await connection_redis_async()
        v_cache_key = f"forecast:{p_product_id}:{p_forecast_days}"
        
        v_json_data = json.dumps(p_forecast_data)
        
        await v_redis.setex(v_cache_key, p_ttl, v_json_data)
        
        log.info(f"Forecast cached for {p_product_id} - {p_forecast_days} days")
        return True
        
    except Exception as e:
        log.error(f"Error cache_set_forecast: {str(e)}")
        return False

async def cache_delete_forecast(p_product_id: str):
    """
    Hapus semua cache forecast untuk product tertentu
    """
    try:
        v_redis = await connection_redis_async()
        v_pattern = f"forecast:{p_product_id}:*"
        
        v_keys = []
        async for key in v_redis.scan_iter(match=v_pattern):
            v_keys.append(key)
        
        if v_keys:
            await v_redis.delete(*v_keys)
            log.info(f"Deleted {len(v_keys)} cache keys for product {p_product_id}")
        
        return True
        
    except Exception as e:
        log.error(f"Error cache_delete_forecast: {str(e)}")
        return False
