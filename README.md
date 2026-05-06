# Demand Forecasting API

API untuk forecasting demand produk dan rekomendasi stok menggunakan Machine Learning (Prophet).

## Features

- 📊 **Upload Historical Sales Data** - Upload data penjualan historis
- 🔮 **Demand Forecasting** - Prediksi demand produk untuk N hari ke depan
- 📈 **Stock Recommendation** - Rekomendasi jumlah stok yang harus disiapkan
- 💾 **Forecast History** - Simpan dan lihat history forecasting
- ⚡ **Redis Caching** - Cache hasil forecast untuk performa optimal
- 🔒 **Security** - Checksum validation, rate limiting, security headers

## Tech Stack

- **Framework**: FastAPI
- **ML Model**: Prophet (Facebook)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Language**: Python 3.11

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd demand-forecasting-api
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database

```bash
# Buat database PostgreSQL
createdb demand_forecast_db

# Import schema
psql -d demand_forecast_db -f database_schema.sql
```

### 5. Configure Environment

Copy `.env` dan sesuaikan konfigurasi:

```bash
cp .env.example .env
```

Edit `.env`:
```
STATUS_APP=DEV
SECRET_KEY_FORECAST_REQUEST=your-secret-key
POSTGRES_DB_USER=postgres
POSTGRES_DB_PASS=your-password
POSTGRES_DB_HOST=localhost
POSTGRES_DB_PORT=5432
POSTGRES_DB_DATA=demand_forecast_db
CONNECTION_STRING_REDIS=redis://localhost:6379/0
```

### 6. Run Application

```bash
python main.py
```

API akan berjalan di: `http://localhost:8080`

Dokumentasi API: `http://localhost:8080/docs`

## API Endpoints

### 1. Upload Sales Data

**Endpoint**: `POST /inquiry`

**Request**:
```json
{
  "method": "upload_sales_data",
  "product_id": "PROD001",
  "product_name": "Indomie Goreng",
  "sales_data": [
    {"date": "2024-01-01", "quantity": 45},
    {"date": "2024-01-02", "quantity": 52},
    {"date": "2024-01-03", "quantity": 38}
  ],
  "datetime": "2025-01-30 14:00:00",
  "checksum": "generated-checksum"
}
```

**Response**:
```json
{
  "err_code": 200,
  "err_msg": "Success",
  "product_id": "PROD001",
  "product_name": "Indomie Goreng",
  "data_points": 15,
  "datetime": "2025-01-30 14:00:00",
  "checksum": "response-checksum"
}
```

### 2. Forecast Demand

**Endpoint**: `POST /inquiry`

**Request**:
```json
{
  "method": "forecast_demand",
  "product_id": "PROD001",
  "forecast_days": 7,
  "datetime": "2025-01-30 14:00:00",
  "checksum": "generated-checksum"
}
```

**Response**:
```json
{
  "err_code": 200,
  "err_msg": "Success",
  "product_id": "PROD001",
  "forecast_period": "7_days",
  "recommendations": [
    {
      "date": "2025-01-31",
      "predicted_demand": 48,
      "lower_bound": 42,
      "upper_bound": 54,
      "stock_needed": 53
    }
  ],
  "total_stock_needed": 350,
  "confidence_level": "85%",
  "forecast_date": "2025-01-30 14:00:00",
  "datetime": "2025-01-30 14:00:00",
  "checksum": "response-checksum"
}
```

### 3. Get Forecast History

**Endpoint**: `POST /inquiry`

**Request**:
```json
{
  "method": "get_forecast_history",
  "product_id": "PROD001",
  "datetime": "2025-01-30 14:00:00",
  "checksum": "generated-checksum"
}
```

### 4. Get Product List

**Endpoint**: `POST /inquiry`

**Request**:
```json
{
  "method": "get_product_list",
  "datetime": "2025-01-30 14:00:00",
  "checksum": "generated-checksum"
}
```

### 5. Delete Product Data

**Endpoint**: `POST /inquiry`

**Request**:
```json
{
  "method": "delete_product_data",
  "product_id": "PROD001",
  "datetime": "2025-01-30 14:00:00",
  "checksum": "generated-checksum"
}
```

## Checksum Generation

Checksum menggunakan SHA256:

```python
import hashlib

def generate_checksum(payload: str) -> str:
    return hashlib.sha256(payload.encode()).hexdigest()

# Example untuk upload_sales_data:
payload = f"{method}#{product_id}#{product_name}#{datetime}#{SECRET_KEY}"
checksum = generate_checksum(payload)
```

## Docker Deployment

### Build Image

```bash
docker build -t demand-forecasting-api .
```

### Run Container

```bash
docker run -d \
  -p 8080:8080 \
  -e POSTGRES_DB_HOST=your-db-host \
  -e POSTGRES_DB_PASS=your-password \
  -e CONNECTION_STRING_REDIS=redis://your-redis:6379/0 \
  demand-forecasting-api
```

## Project Structure

```
demand-forecasting-api/
├── aplikasi/
│   ├── controllers/
│   │   └── api/
│   │       ├── api_controller.py
│   │       ├── upload_sales_data_controller.py
│   │       ├── forecast_demand_controller.py
│   │       ├── get_forecast_history_controller.py
│   │       ├── get_product_list_controller.py
│   │       └── delete_product_data_controller.py
│   ├── dao/
│   │   ├── query_file.py
│   │   └── api/
│   │       ├── db_dao.py
│   │       └── redis_dao.py
│   ├── models/
│   │   └── api_model.py
│   ├── ml_models/
│   │   └── forecasting_model.py
│   ├── others/
│   │   ├── format.py
│   │   ├── response.py
│   │   └── utility.py
│   ├── __init__.py
│   ├── routes.py
│   └── settings.py
├── common/
│   └── custom_log/
│       └── __init__.py
├── log/
├── main.py
├── requirements.txt
├── database_schema.sql
├── Dockerfile
├── .env
├── .gitignore
└── README.md
```

## ML Model Details

### Prophet Configuration

- **Daily Seasonality**: Enabled
- **Weekly Seasonality**: Enabled
- **Yearly Seasonality**: Disabled
- **Changepoint Prior Scale**: 0.05
- **Seasonality Prior Scale**: 10.0
- **Confidence Interval**: 95%

### Stock Recommendation Logic

```
stock_needed = predicted_demand * 1.1  (10% buffer)
```

## Performance

- **Redis Caching**: Forecast results di-cache selama 1 jam
- **Connection Pooling**: PostgreSQL connection pool (min: 1, max: 10)
- **Rate Limiting**: 50 requests per 60 seconds

## Testing

### Test dengan cURL

```bash
# Upload sales data
curl -X POST http://localhost:8080/inquiry \
  -H "Content-Type: application/json" \
  -d '{
    "method": "upload_sales_data",
    "product_id": "TEST001",
    "product_name": "Test Product",
    "sales_data": [
      {"date": "2024-01-01", "quantity": 45},
      {"date": "2024-01-02", "quantity": 52}
    ],
    "datetime": "2025-01-30 14:00:00",
    "checksum": "your-checksum"
  }'
```

## Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

MIT License

## Contact

Developer - developer@example.com

Project Link: [https://github.com/yourusername/demand-forecasting-api](https://github.com/yourusername/demand-forecasting-api)
