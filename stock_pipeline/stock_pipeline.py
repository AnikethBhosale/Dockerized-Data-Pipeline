import os
import logging
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import create_engine, text, inspect
from dagster import (
    asset, 
    AssetExecutionContext, 
    Config, 
    get_dagster_logger,
    Failure,
    RetryPolicy
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = get_dagster_logger()

class StockDataConfig(Config):
    """Configuration for stock data pipeline"""
    symbols: list[str] = ["IBM", "AAPL", "MSFT", "GOOGL"]
    interval: str = "5min"
    api_key: Optional[str] = None

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.engine = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            db_url = (
                f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:"
                f"{os.getenv('POSTGRES_PASSWORD', 'admin123')}@"
                f"{os.getenv('POSTGRES_HOST', 'localhost')}:5432/"
                f"{os.getenv('POSTGRES_DB', 'stock_data')}"
            )
            self.engine = create_engine(db_url)
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise Failure(f"Database connection failed: {str(e)}")
    
    def check_table_exists(self) -> bool:
        """Check if stock_data table exists"""
        try:
            inspector = inspect(self.engine)
            return 'stock_data' in inspector.get_table_names()
        except Exception as e:
            logger.error(f"Error checking table existence: {str(e)}")
            return False
    
    def insert_stock_data(self, data: pd.DataFrame) -> int:
        """Insert stock data into database"""
        try:
            if data.empty:
                logger.warning("No data to insert")
                return 0
            
            # Prepare data for insertion
            records = []
            for _, row in data.iterrows():
                record = {
                    'symbol': row['symbol'],
                    'timestamp': row['timestamp'],
                    'open_price': row.get('open_price'),
                    'high_price': row.get('high_price'),
                    'low_price': row.get('low_price'),
                    'close_price': row.get('close_price'),
                    'volume': row.get('volume')
                }
                records.append(record)
            
            # Insert data
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        INSERT INTO stock_data 
                        (symbol, timestamp, open_price, high_price, low_price, close_price, volume)
                        VALUES (:symbol, :timestamp, :open_price, :high_price, :low_price, :close_price, :volume)
                        ON CONFLICT (symbol, timestamp) DO UPDATE SET
                        open_price = EXCLUDED.open_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        close_price = EXCLUDED.close_price,
                        volume = EXCLUDED.volume
                    """),
                    records
                )
                conn.commit()
            
            logger.info(f"Successfully inserted {len(records)} records")
            return len(records)
            
        except Exception as e:
            logger.error(f"Error inserting data: {str(e)}")
            raise Failure(f"Database insertion failed: {str(e)}")

class AlphaVantageAPI:
    """Handles Alpha Vantage API interactions"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        self.base_url = "https://www.alphavantage.co/query"
    
    def fetch_stock_data(self, symbol: str, interval: str = "5min") -> Dict[str, Any]:
        """Fetch stock data from Alpha Vantage API"""
        try:
            params = {
                'function': 'TIME_SERIES_INTRADAY',
                'symbol': symbol,
                'interval': interval,
                'apikey': self.api_key
            }
            
            logger.info(f"Fetching data for {symbol}")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                raise Exception(f"API Error: {data['Error Message']}")
            
            if 'Note' in data:
                logger.warning(f"API Rate Limit: {data['Note']}")
                return {}
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {symbol}: {str(e)}")
            raise Failure(f"API request failed for {symbol}: {str(e)}")
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            raise Failure(f"Data fetching failed for {symbol}: {str(e)}")
    
    def parse_stock_data(self, data: Dict[str, Any], symbol: str) -> pd.DataFrame:
        """Parse API response into structured DataFrame"""
        try:
            if not data:
                return pd.DataFrame()
            
            # Extract time series data
            time_series_key = f"Time Series ({data.get('Meta Data', {}).get('4. Interval', '5min')})"
            
            if time_series_key not in data:
                logger.warning(f"No time series data found for {symbol}")
                return pd.DataFrame()
            
            time_series_data = data[time_series_key]
            
            # Parse data into DataFrame
            records = []
            for timestamp, values in time_series_data.items():
                try:
                    record = {
                        'symbol': symbol,
                        'timestamp': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
                        'open_price': float(values.get('1. open', 0)),
                        'high_price': float(values.get('2. high', 0)),
                        'low_price': float(values.get('3. low', 0)),
                        'close_price': float(values.get('4. close', 0)),
                        'volume': int(values.get('5. volume', 0))
                    }
                    records.append(record)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing record for {symbol} at {timestamp}: {str(e)}")
                    continue
            
            df = pd.DataFrame(records)
            logger.info(f"Parsed {len(df)} records for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error parsing data for {symbol}: {str(e)}")
            raise Failure(f"Data parsing failed for {symbol}: {str(e)}")

@asset(
    description="Fetch and store stock market data from Alpha Vantage API",
    retry_policy=RetryPolicy(
        max_retries=3,
        delay=60
    )
)
def stock_data_pipeline(context: AssetExecutionContext, config: StockDataConfig) -> Dict[str, Any]:
    """
    Main pipeline asset that fetches stock data and stores it in PostgreSQL.
    
    This asset:
    1. Fetches stock data from Alpha Vantage API for multiple symbols
    2. Parses the JSON response into structured data
    3. Stores the data in PostgreSQL with error handling
    4. Provides comprehensive logging and monitoring
    """
    
    logger.info("Starting stock data pipeline")
    
    # Initialize components
    db_manager = DatabaseManager()
    api_client = AlphaVantageAPI(config.api_key)
    
    # Check if table exists
    if not db_manager.check_table_exists():
        logger.error("stock_data table does not exist. Please run the database initialization.")
        raise Failure("Database table not found")
    
    total_records = 0
    successful_symbols = []
    failed_symbols = []
    
    # Process each symbol
    for symbol in config.symbols:
        try:
            logger.info(f"Processing symbol: {symbol}")
            
            # Fetch data from API
            raw_data = api_client.fetch_stock_data(symbol, config.interval)
            
            if not raw_data:
                logger.warning(f"No data received for {symbol}")
                failed_symbols.append(symbol)
                continue
            
            # Parse data
            df = api_client.parse_stock_data(raw_data, symbol)
            
            if df.empty:
                logger.warning(f"No parsed data for {symbol}")
                failed_symbols.append(symbol)
                continue
            
            # Store in database
            records_inserted = db_manager.insert_stock_data(df)
            total_records += records_inserted
            
            successful_symbols.append(symbol)
            logger.info(f"Successfully processed {symbol}: {records_inserted} records")
            
        except Exception as e:
            logger.error(f"Failed to process {symbol}: {str(e)}")
            failed_symbols.append(symbol)
            continue
    
    # Prepare result summary
    result = {
        "timestamp": datetime.now().isoformat(),
        "total_records_inserted": total_records,
        "successful_symbols": successful_symbols,
        "failed_symbols": failed_symbols,
        "total_symbols_processed": len(config.symbols),
        "success_rate": len(successful_symbols) / len(config.symbols) if config.symbols else 0
    }
    
    logger.info(f"Pipeline completed. Summary: {result}")
    
    # Raise failure if no symbols were processed successfully
    if not successful_symbols:
        raise Failure("No symbols were processed successfully")
    
    return result
