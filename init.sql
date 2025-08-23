-- Create stock_data table
CREATE TABLE IF NOT EXISTS stock_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open_price DECIMAL(10,4),
    high_price DECIMAL(10,4),
    low_price DECIMAL(10,4),
    close_price DECIMAL(10,4),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp)
);

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_stock_data_symbol_timestamp 
ON stock_data(symbol, timestamp);

-- Create index for time-based queries
CREATE INDEX IF NOT EXISTS idx_stock_data_timestamp 
ON stock_data(timestamp);

-- Create a function to update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_stock_data_updated_at 
    BEFORE UPDATE ON stock_data 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
