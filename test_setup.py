#!/usr/bin/env python3
"""
Test script to verify the stock data pipeline setup

This script tests:
1. Database connection
2. Table existence
3. API connectivity
4. Basic data fetching
"""

import os
import sys
import requests
from sqlalchemy import create_engine, text, inspect

def test_database_connection():
    """Test database connection and table existence"""
    print("🔍 Testing database connection...")
    
    try:
        # Build database URL
        db_url = (
            f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:"
            f"{os.getenv('POSTGRES_PASSWORD', 'admin123')}@"
            f"{os.getenv('POSTGRES_HOST', 'localhost')}:5432/"
            f"{os.getenv('POSTGRES_DB', 'stock_data')}"
        )
        
        # Create engine and test connection
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        print("✅ Database connection successful!")
        
        # Check if table exists
        inspector = inspect(engine)
        if 'stock_data' in inspector.get_table_names():
            print("✅ stock_data table exists!")
            return True
        else:
            print("❌ stock_data table not found!")
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def test_api_connection():
    """Test Alpha Vantage API connection"""
    print("🔍 Testing API connection...")
    
    try:
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        
        # Test API with IBM symbol
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': 'IBM',
            'interval': '5min',
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Check for API errors
        if 'Error Message' in data:
            print(f"❌ API Error: {data['Error Message']}")
            return False
        
        if 'Note' in data:
            print(f"⚠️  API Rate Limit: {data['Note']}")
            return True  # Rate limit is not a connection failure
        
        if 'Time Series (5min)' in data:
            print("✅ API connection successful!")
            return True
        else:
            print("❌ Unexpected API response format")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API connection failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False

def test_pipeline_imports():
    """Test if pipeline modules can be imported"""
    print("🔍 Testing pipeline imports...")
    
    try:
        from stock_pipeline.stock_pipeline import stock_data_pipeline, DatabaseManager, AlphaVantageAPI
        from stock_pipeline.data_fetcher import StockDataFetcher
        print("✅ All pipeline modules imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Stock Data Pipeline Setup Tests")
    print("=" * 50)
    
    tests = [
        ("Pipeline Imports", test_pipeline_imports),
        ("Database Connection", test_database_connection),
        ("API Connection", test_api_connection),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your pipeline is ready to run.")
        print("\nNext steps:")
        print("1. Set your Alpha Vantage API key in .env file")
        print("2. Run: docker-compose up --build")
        print("3. Access Dagster UI at: http://localhost:3000")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Ensure PostgreSQL is running")
        print("2. Check your API key")
        print("3. Verify all dependencies are installed")
        sys.exit(1)

if __name__ == "__main__":
    main()
