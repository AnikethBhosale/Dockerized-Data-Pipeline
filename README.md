# Dockerized Stock Data Pipeline with Dagster

A robust, scalable data pipeline that automatically fetches stock market data from Alpha Vantage API and stores it in PostgreSQL using Dagster for orchestration.

## 🚀 Features

- **Automated Data Fetching**: Retrieves stock data from Alpha Vantage API on a scheduled basis
- **Robust Error Handling**: Comprehensive error management and graceful handling of missing data
- **Scalable Architecture**: Docker-based deployment with PostgreSQL and Dagster
- **Real-time Monitoring**: Dagster UI for pipeline monitoring and management
- **Data Integrity**: Conflict resolution and data validation
- **Security**: Environment variable management for sensitive information

## 📋 Prerequisites

- Docker and Docker Compose installed
- Alpha Vantage API key (free tier available at [Alpha Vantage](https://www.alphavantage.co/support/#api-key))
- At least 2GB of available RAM
- Ports 3000 and 5432 available

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Alpha Vantage │    │     Dagster     │    │   PostgreSQL    │
│      API        │◄───┤   Orchestrator  │───►│    Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Stock Data    │
                       │   Pipeline      │
                       └─────────────────┘
```

## 🚀 Quick Start

### 1. Clone and Navigate

```bash
cd assignment
```

### 2. Set Environment Variables

Create a `.env` file in the assignment directory:

```bash
# Alpha Vantage API Key (get one at https://www.alphavantage.co/support/#api-key)
ALPHA_VANTAGE_API_KEY=your_api_key_here

# Database Configuration (optional - defaults provided)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin123
POSTGRES_DB=stock_data
POSTGRES_HOST=postgres
```

### 3. Build and Run

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

### 4. Access the Application

- **Dagster UI**: http://localhost:3000
- **PostgreSQL**: localhost:5432

## 📊 Pipeline Components

### 1. Docker Compose (`docker-compose.yml`)

Orchestrates the entire pipeline with:
- **PostgreSQL**: Database for storing stock data
- **Dagster**: Data orchestration and monitoring
- **Health checks**: Ensures services start in correct order

### 2. Dagster Pipeline (`stock_pipeline/stock_pipeline.py`)

Main pipeline asset that:
- Fetches data from Alpha Vantage API
- Parses JSON responses into structured data
- Stores data in PostgreSQL with error handling
- Provides comprehensive logging and monitoring

### 3. Data Fetcher Script (`stock_pipeline/data_fetcher.py`)

Standalone Python script for:
- Independent data fetching and processing
- Command-line interface for manual execution
- Batch processing of multiple stock symbols

### 4. Database Schema (`init.sql`)

PostgreSQL table structure with:
- Optimized indexes for performance
- Automatic timestamp management
- Conflict resolution for data updates

## 🔧 Configuration

### Pipeline Configuration

The pipeline can be configured through the Dagster UI or by modifying the `StockDataConfig` class:

```python
class StockDataConfig(Config):
    symbols: list[str] = ["IBM", "AAPL", "MSFT", "GOOGL"]  # Stock symbols
    interval: str = "5min"  # Time interval (1min, 5min, 15min, 30min, 60min)
    api_key: Optional[str] = None  # API key (defaults to environment variable)
```

### Supported Time Intervals

- `1min`: 1-minute intraday data
- `5min`: 5-minute intraday data (default)
- `15min`: 15-minute intraday data
- `30min`: 30-minute intraday data
- `60min`: 60-minute intraday data

## 📈 Usage

### Using Dagster UI

1. Open http://localhost:3000 in your browser
2. Navigate to the "Assets" tab
3. Find the "stock_data_pipeline" asset
4. Click "Materialize" to run the pipeline
5. Monitor execution in real-time

### Using Command Line

```bash
# Run the standalone data fetcher
docker-compose exec dagster python stock_pipeline/data_fetcher.py --symbols IBM,AAPL --interval 5min

# Or run with custom configuration
docker-compose exec dagster python stock_pipeline/data_fetcher.py \
    --symbols IBM,AAPL,MSFT,GOOGL \
    --interval 15min \
    --api-key your_api_key
```

### Manual Database Queries

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d stock_data

# Query recent data
SELECT symbol, timestamp, close_price, volume 
FROM stock_data 
WHERE symbol = 'IBM' 
ORDER BY timestamp DESC 
LIMIT 10;
```

## 🔍 Monitoring and Logging

### Dagster UI Features

- **Asset Materialization**: Track pipeline execution
- **Logs**: View detailed execution logs
- **Metrics**: Monitor performance and success rates
- **Retry Management**: Automatic retry on failures

### Log Levels

- **INFO**: General pipeline operations
- **WARNING**: Non-critical issues (rate limits, missing data)
- **ERROR**: Critical failures requiring attention

## 🛡️ Error Handling

### API Error Handling

- **Rate Limiting**: Graceful handling of API rate limits
- **Network Failures**: Automatic retry with exponential backoff
- **Invalid Responses**: Validation and error reporting

### Database Error Handling

- **Connection Failures**: Automatic reconnection
- **Data Validation**: Type checking and constraint validation
- **Conflict Resolution**: Upsert operations for duplicate data

### Pipeline Resilience

- **Retry Policy**: 3 retries with 60-second delay
- **Partial Failures**: Continue processing other symbols if one fails
- **Data Integrity**: Transaction rollback on critical errors

## 📊 Data Schema

### Stock Data Table

```sql
CREATE TABLE stock_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open_price DECIMAL(10,4),
    high_price DECIMAL(10,4),
    low_price DECIMAL(10,4),
    close_price DECIMAL(10,4),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

- `idx_stock_data_symbol_timestamp`: Optimized queries by symbol and time
- `idx_stock_data_timestamp`: Time-based queries

## 🔧 Development

### Local Development Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up local PostgreSQL (or use Docker)
# Create database and run init.sql

# Run pipeline locally
python -m dagster dev -w workspace.yaml
```

### Testing

```bash
# Test data fetcher
python stock_pipeline/data_fetcher.py --symbols IBM --interval 5min

# Test database connection
python -c "
from stock_pipeline.stock_pipeline import DatabaseManager
db = DatabaseManager()
print('Database connection successful')
"
```

## 🚀 Scaling and Performance

### Horizontal Scaling

- **Multiple Dagster Workers**: Scale processing capacity
- **Database Connection Pooling**: Optimize database connections
- **Load Balancing**: Distribute API requests

### Performance Optimization

- **Batch Processing**: Process multiple symbols efficiently
- **Indexed Queries**: Optimized database performance
- **Caching**: Reduce API calls for frequently accessed data

## 🔒 Security

### Environment Variables

- **API Keys**: Stored in environment variables
- **Database Credentials**: Secure credential management
- **Network Security**: Containerized deployment

### Best Practices

- **Input Validation**: Validate all API responses
- **SQL Injection Prevention**: Parameterized queries
- **Error Sanitization**: Prevent information leakage

## 🐛 Troubleshooting

### Common Issues

1. **API Rate Limiting**
   ```
   Solution: Wait for rate limit reset or upgrade API plan
   ```

2. **Database Connection Failed**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps
   
   # Check logs
   docker-compose logs postgres
   ```

3. **Pipeline Not Starting**
   ```bash
   # Check Dagster logs
   docker-compose logs dagster
   
   # Verify workspace configuration
   docker-compose exec dagster cat workspace.yaml
   ```

4. **No Data Retrieved**
   ```bash
   # Check API key
   echo $ALPHA_VANTAGE_API_KEY
   
   # Test API manually
   curl "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=YOUR_API_KEY"
   ```

### Debug Mode

```bash
# Run with debug logging
docker-compose exec dagster python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from stock_pipeline.data_fetcher import StockDataFetcher
fetcher = StockDataFetcher()
fetcher.process_symbol('IBM')
"
```

## 📝 API Documentation

### Alpha Vantage API

- **Base URL**: https://www.alphavantage.co/query
- **Function**: TIME_SERIES_INTRADAY
- **Rate Limits**: 5 calls per minute (free tier)
- **Documentation**: https://www.alphavantage.co/documentation/

### Dagster API

- **UI**: http://localhost:3000
- **Documentation**: https://docs.dagster.io/
- **Asset Materialization**: Programmatic pipeline execution

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Alpha Vantage](https://www.alphavantage.co/) for providing free stock market data
- [Dagster](https://dagster.io/) for the excellent data orchestration platform
- [PostgreSQL](https://www.postgresql.org/) for the robust database system

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs: `docker-compose logs`
3. Open an issue with detailed error information

---

**Happy Data Pipeline Building! 🚀**
