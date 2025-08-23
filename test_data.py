#!/usr/bin/env python3
"""
Simple test script to verify data storage
"""

import os
from sqlalchemy import create_engine, text

def test_data_storage():
    """Test if data was stored in the database"""
    try:
        # Build database URL
        db_url = (
            f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:"
            f"{os.getenv('POSTGRES_PASSWORD', 'admin')}@"
            f"{os.getenv('POSTGRES_HOST', 'localhost')}:5432/"
            f"{os.getenv('POSTGRES_DB', 'stock_data')}"
        )
        
        # Create engine and test connection
        engine = create_engine(db_url)
        
        # Query total records
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM stock_data"))
            total_records = result.scalar()
            print(f"✅ Total records in database: {total_records}")
            
            # Query records by symbol
            result = conn.execute(text("SELECT symbol, COUNT(*) as count FROM stock_data GROUP BY symbol"))
            for row in result:
                print(f"   {row.symbol}: {row.count} records")
                
            # Show latest records
            result = conn.execute(text("""
                SELECT symbol, timestamp, close_price, volume 
                FROM stock_data 
                ORDER BY timestamp DESC 
                LIMIT 5
            """))
            print("\n📊 Latest 5 records:")
            for row in result:
                print(f"   {row.symbol} | {row.timestamp} | ${row.close_price} | {row.volume}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_data_storage()
