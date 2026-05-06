from aplikasi import TZ_JAKARTA
import datetime
from fastapi import Request

async def safe_json(request: Request):
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            return await request.json()
        except:
            return {}
    return {}

def validate_request_datetime(v_datetime: str):
    from zoneinfo import ZoneInfo
    JAKARTA_TZ = ZoneInfo("Asia/Jakarta")

    try:
        v_request_dt = datetime.datetime.strptime(v_datetime, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return False, "Format datetime tidak valid. Gunakan YYYY-MM-DD HH:MM:SS"

    v_request_dt = v_request_dt.replace(tzinfo=JAKARTA_TZ)
    v_now_jakarta = datetime.datetime.now(JAKARTA_TZ)
    v_24_hour = datetime.timedelta(hours=24)

    if not (v_now_jakarta - v_24_hour <= v_request_dt <= v_now_jakarta + v_24_hour):
        return False, "Datetime request harus dalam rentang ±24 jam dari waktu Sekarang"
    
    if v_request_dt.date() != v_now_jakarta.date():
        if abs((v_request_dt - v_now_jakarta).total_seconds()) > 86400:
            return False, "Tanggal request tidak valid. Tidak boleh berbeda lebih dari 24 jam dari tanggal hari ini."

    return True, "OK"
