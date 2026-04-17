-- Enable pgcrypto for gen_random_uuid() if needed
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Pharma Sales Table Definition
CREATE TABLE IF NOT EXISTS pharma_sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    product_id UUID NOT NULL,
    doctor_id UUID NOT NULL,
    product_name TEXT NOT NULL,
    composition TEXT,
    sales_price NUMERIC(10, 2) NOT NULL,
    purchase_price NUMERIC(10, 2) NOT NULL,
    combo_type TEXT,
    total_strips INT DEFAULT 0,
    total_tablets INT DEFAULT 0,
    scheme TEXT,
    gift_sample TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster searching on product names
CREATE INDEX IF NOT EXISTS idx_product_name ON pharma_sales (product_name);
