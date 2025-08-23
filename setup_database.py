#!/usr/bin/env python3
"""
Setup database manually
"""

from sqlalchemy import create_engine, text

def setup_database():
    try:
        # Connect to default postgres database with autocommit
        engine = create_engine("postgresql://postgres:admin@localhost:5432/postgres", isolation_level="AUTOCOMMIT")
        
        with engine.connect() as conn:
            print("🔧 Setting up stock_data database...")
            
            # Create stock_data database
            conn.execute(text("CREATE DATABASE stock_data"))
            print("✅ Created stock_data database")
            
    except Exception as e:
        if "already exists" in str(e):
            print("✅ stock_data database already exists")
        else:
            print(f"❌ Error creating database: {e}")
            return False
    
    try:
        # Connect to stock_data database
        engine2 = create_engine("postgresql://postgres:admin@localhost:5432/stock_data")
        
        with engine2.connect() as conn:
            print("🔧 Creating stock_data table...")
            
            # Create the table
            create_table_sql = """
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
            """
            conn.execute(text(create_table_sql))
            
            # Create indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stock_data_symbol_timestamp ON stock_data(symbol, timestamp)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stock_data_timestamp ON stock_data(timestamp)"))
            
            # Create function and trigger
            conn.execute(text("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            """))
            
            conn.execute(text("""
            CREATE TRIGGER update_stock_data_updated_at 
                BEFORE UPDATE ON stock_data 
                FOR EACH ROW 
                EXECUTE FUNCTION update_updated_at_column();
            """))
            
            # Commit the transaction
            conn.commit()
            print("✅ Created stock_data table and indexes")
            
            # Verify the table exists
            result = conn.execute(text("SELECT COUNT(*) FROM stock_data"))
            count = result.scalar()
            print(f"✅ stock_data table has {count} records")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

if __name__ == "__main__":
    setup_database()
