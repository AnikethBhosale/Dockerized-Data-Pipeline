#!/usr/bin/env python3
"""
Standalone Stock Data Fetcher

This script fetches stock market data from Alpha Vantage API and stores it in PostgreSQL.
It can be run independently or as part of the Dagster pipeline.

Usage:
    python data_fetcher.py --symbols IBM,AAPL,MSFT --interval 5min
"""

import os
import sys
import argparse
import logging
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, text, inspect

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StockDataFetcher:
    """Standalone stock data fetcher and database updater"""
    
    def __init__(self, api_key: Optional[str] = None, db_url: Optional[str] = None):
        """
        Initialize the stock data fetcher
        
        Args:
            api_key: Alpha Vantage API key (defaults to environment variable)
            db_url: PostgreSQL connection URL (defaults to environment variables)
        """
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        self.base_url = "https://www.alphavantage.co/query"
        
        # Build database URL from environment variables if not provided
        if not db_url:
            db_url = (
                f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:"
                f"{os.getenv('POSTGRES_PASSWORD', 'admin123')}@"
                f"{os.getenv('POSTGRES_HOST', 'localhost')}:5432/"
                f"{os.getenv('POSTGRES_DB', 'stock_data')}"
            )
        
        self.db_url = db_url
        self.engine = None
        self._connect_db()
    
    def _connect_db(self):
        """Establish database connection"""
        try:
            self.engine = create_engine(self.db_url)
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise
    
    def check_table_exists(self) -> bool:
        """Check if stock_data table exists"""
        try:
            inspector = inspect(self.engine)
            return 'stock_data' in inspector.get_table_names()
        except Exception as e:
            logger.error(f"Error checking table existence: {str(e)}")
            return False
    
    def fetch_stock_data(self, symbol: str, interval: str = "5min") -> Dict[str, Any]:
        """
        Fetch stock data from Alpha Vantage API
        
        Args:
            symbol: Stock symbol (e.g., 'IBM', 'AAPL')
            interval: Time interval ('1min', '5min', '15min', '30min', '60min')
        
        Returns:
            Dictionary containing the API response
        """
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
            raise
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            raise
    
    def parse_stock_data(self, data: Dict[str, Any], symbol: str) -> pd.DataFrame:
        """
        Parse API response into structured DataFrame
        
        Args:
            data: Raw API response
            symbol: Stock symbol
        
        Returns:
            DataFrame with parsed stock data
        """
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
            raise
    
    def update_database(self, data: pd.DataFrame) -> int:
        """
        Update PostgreSQL table with stock data
        
        Args:
            data: DataFrame containing stock data
        
        Returns:
            Number of records inserted/updated
        """
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
            
            # Insert data with conflict resolution
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
            
            logger.info(f"Successfully inserted/updated {len(records)} records")
            return len(records)
            
        except Exception as e:
            logger.error(f"Error updating database: {str(e)}")
            raise
    
    def process_symbol(self, symbol: str, interval: str = "5min") -> Dict[str, Any]:
        """
        Process a single stock symbol: fetch, parse, and store data
        
        Args:
            symbol: Stock symbol to process
            interval: Time interval for data
        
        Returns:
            Dictionary with processing results
        """
        try:
            logger.info(f"Processing symbol: {symbol}")
            
            # Fetch data from API
            raw_data = self.fetch_stock_data(symbol, interval)
            
            if not raw_data:
                return {
                    'symbol': symbol,
                    'status': 'failed',
                    'reason': 'No data received from API',
                    'records_processed': 0
                }
            
            # Parse data
            df = self.parse_stock_data(raw_data, symbol)
            
            if df.empty:
                return {
                    'symbol': symbol,
                    'status': 'failed',
                    'reason': 'No data parsed successfully',
                    'records_processed': 0
                }
            
            # Store in database
            records_processed = self.update_database(df)
            
            return {
                'symbol': symbol,
                'status': 'success',
                'records_processed': records_processed,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to process {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'status': 'failed',
                'reason': str(e),
                'records_processed': 0
            }
    
    def process_multiple_symbols(self, symbols: List[str], interval: str = "5min") -> Dict[str, Any]:
        """
        Process multiple stock symbols
        
        Args:
            symbols: List of stock symbols to process
            interval: Time interval for data
        
        Returns:
            Dictionary with summary of all processing results
        """
        logger.info(f"Starting batch processing of {len(symbols)} symbols")
        
        results = []
        total_records = 0
        successful_symbols = []
        failed_symbols = []
        
        for symbol in symbols:
            result = self.process_symbol(symbol, interval)
            results.append(result)
            
            if result['status'] == 'success':
                successful_symbols.append(symbol)
                total_records += result['records_processed']
            else:
                failed_symbols.append(symbol)
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_symbols': len(symbols),
            'successful_symbols': successful_symbols,
            'failed_symbols': failed_symbols,
            'total_records_processed': total_records,
            'success_rate': len(successful_symbols) / len(symbols) if symbols else 0,
            'detailed_results': results
        }
        
        logger.info(f"Batch processing completed. Summary: {summary}")
        return summary

def main():
    """Main function for command-line execution"""
    parser = argparse.ArgumentParser(description='Fetch and store stock market data')
    parser.add_argument(
        '--symbols', 
        type=str, 
        default='IBM,AAPL,MSFT,GOOGL',
        help='Comma-separated list of stock symbols'
    )
    parser.add_argument(
        '--interval', 
        type=str, 
        default='5min',
        choices=['1min', '5min', '15min', '30min', '60min'],
        help='Time interval for data'
    )
    parser.add_argument(
        '--api-key', 
        type=str, 
        help='Alpha Vantage API key (defaults to environment variable)'
    )
    parser.add_argument(
        '--db-url', 
        type=str, 
        help='Database connection URL (defaults to environment variables)'
    )
    
    args = parser.parse_args()
    
    # Parse symbols
    symbols = [s.strip() for s in args.symbols.split(',') if s.strip()]
    
    if not symbols:
        logger.error("No valid symbols provided")
        sys.exit(1)
    
    try:
        # Initialize fetcher
        fetcher = StockDataFetcher(api_key=args.api_key, db_url=args.db_url)
        
        # Check if table exists
        if not fetcher.check_table_exists():
            logger.error("stock_data table does not exist. Please run the database initialization.")
            sys.exit(1)
        
        # Process symbols
        summary = fetcher.process_multiple_symbols(symbols, args.interval)
        
        # Print summary
        print("\n" + "="*50)
        print("PROCESSING SUMMARY")
        print("="*50)
        print(f"Total symbols processed: {summary['total_symbols']}")
        print(f"Successful: {len(summary['successful_symbols'])}")
        print(f"Failed: {len(summary['failed_symbols'])}")
        print(f"Success rate: {summary['success_rate']:.2%}")
        print(f"Total records processed: {summary['total_records_processed']}")
        
        if summary['successful_symbols']:
            print(f"\nSuccessful symbols: {', '.join(summary['successful_symbols'])}")
        
        if summary['failed_symbols']:
            print(f"\nFailed symbols: {', '.join(summary['failed_symbols'])}")
        
        print("="*50)
        
        # Exit with error if no symbols were processed successfully
        if not summary['successful_symbols']:
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Script execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
