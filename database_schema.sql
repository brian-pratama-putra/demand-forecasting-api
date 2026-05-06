-- Database: demand_forecast_db

-- Table untuk menyimpan historical sales data
CREATE TABLE IF NOT EXISTS tbl_product_sales (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    sales_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index untuk performa
CREATE INDEX idx_product_sales_updated ON tbl_product_sales(updated_at DESC);

-- Table untuk menyimpan forecast history
CREATE TABLE IF NOT EXISTS tbl_forecast_history (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    forecast_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES tbl_product_sales(product_id) ON DELETE CASCADE
);

-- Index untuk performa
CREATE INDEX idx_forecast_history_product ON tbl_forecast_history(product_id);
CREATE INDEX idx_forecast_history_created ON tbl_forecast_history(created_at DESC);

-- Sample data untuk testing
INSERT INTO tbl_product_sales (product_id, product_name, sales_data) VALUES
('PROD001', 'Indomie Goreng', '[
    {"date": "2024-01-01", "quantity": 45},
    {"date": "2024-01-02", "quantity": 52},
    {"date": "2024-01-03", "quantity": 38},
    {"date": "2024-01-04", "quantity": 61},
    {"date": "2024-01-05", "quantity": 55},
    {"date": "2024-01-06", "quantity": 48},
    {"date": "2024-01-07", "quantity": 42},
    {"date": "2024-01-08", "quantity": 50},
    {"date": "2024-01-09", "quantity": 58},
    {"date": "2024-01-10", "quantity": 47},
    {"date": "2024-01-11", "quantity": 53},
    {"date": "2024-01-12", "quantity": 49},
    {"date": "2024-01-13", "quantity": 56},
    {"date": "2024-01-14", "quantity": 44},
    {"date": "2024-01-15", "quantity": 51}
]'::jsonb)
ON CONFLICT (product_id) DO NOTHING;

COMMENT ON TABLE tbl_product_sales IS 'Tabel untuk menyimpan historical sales data produk';
COMMENT ON TABLE tbl_forecast_history IS 'Tabel untuk menyimpan history hasil forecasting';
