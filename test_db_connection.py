#!/usr/bin/env python3
"""
Test database connection
"""

from sqlalchemy import create_engine, text

def test_connection():
    try:
        # Try connecting to postgres database first
        engine = create_engine("postgresql://postgres:admin@localhost:5432/postgres")
        
        with engine.connect() as conn:
            print("✅ Connected to postgres database")
            
            # Check if stock_data exists
            result = conn.execute(text("SELECT datname FROM pg_database WHERE datname = 'stock_data'"))
            if result.fetchone():
                print("✅ stock_data database exists")
                
                # Try connecting to stock_data
                engine2 = create_engine("postgresql://postgres:admin@localhost:5432/stock_data")
                with engine2.connect() as conn2:
                    result2 = conn2.execute(text("SELECT COUNT(*) FROM stock_data"))
                    count = result2.scalar()
                    print(f"✅ Connected to stock_data database - {count} records found")
                    
            else:
                print("❌ stock_data database does not exist")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
