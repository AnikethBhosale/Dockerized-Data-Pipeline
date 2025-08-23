#!/usr/bin/env python3
"""
Check what databases and tables exist
"""

from sqlalchemy import create_engine, text

def check_database():
    try:
        # Connect to default postgres database
        engine = create_engine("postgresql://postgres:admin@localhost:5432/postgres")
        
        with engine.connect() as conn:
            print("🔍 Checking PostgreSQL setup...")
            print("=" * 50)
            
            # List all databases
            print("📋 All databases:")
            result = conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false"))
            databases = [row[0] for row in result.fetchall()]
            for db in databases:
                print(f"  - {db}")
            
            print("\n" + "=" * 50)
            
            # Check if stock_data database exists
            result = conn.execute(text("SELECT datname FROM pg_database WHERE datname = 'stock_data'"))
            if result.fetchone():
                print("✅ stock_data database exists")
                
                # Try to connect to stock_data and check tables
                try:
                    engine2 = create_engine("postgresql://postgres:admin@localhost:5432/stock_data")
                    with engine2.connect() as conn2:
                        print("\n📋 Tables in stock_data database:")
                        result2 = conn2.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
                        tables = [row[0] for row in result2.fetchall()]
                        for table in tables:
                            print(f"  - {table}")
                        
                        if 'stock_data' in tables:
                            result3 = conn2.execute(text("SELECT COUNT(*) FROM stock_data"))
                            count = result3.scalar()
                            print(f"\n✅ stock_data table has {count} records")
                        else:
                            print("\n❌ stock_data table does not exist")
                            
                except Exception as e:
                    print(f"❌ Cannot connect to stock_data database: {e}")
                    
            else:
                print("❌ stock_data database does not exist")
                
                # Check if there are any tables in the current database
                print("\n📋 Tables in current (postgres) database:")
                result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
                tables = [row[0] for row in result.fetchall()]
                for table in tables:
                    print(f"  - {table}")
                
                if 'stock_data' in tables:
                    result = conn.execute(text("SELECT COUNT(*) FROM stock_data"))
                    count = result.scalar()
                    print(f"\n✅ stock_data table exists in postgres database with {count} records")
                else:
                    print("\n❌ No stock_data table found anywhere")
                    
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    check_database()
